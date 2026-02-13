import time
import asyncio
from typing import List, Optional
from google import genai
from domain.news_article import NewsArticle
from config.settings import settings
from utils.exceptions import AppError

class AIService:
    """Gemini API를 이용한 뉴스 요약 서비스 클래스"""
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            raise AppError("api_key_invalid")
        self.client = genai.Client(api_key=self.api_key)

    async def summarize_news_async(self, articles: List[NewsArticle], retry_count: int = 1) -> str:
        """
        Gemini API를 비동기로 사용해 뉴스 기사들을 요약합니다.
        """
        if not articles:
            return "요약할 기사가 없습니다."

        try:
            # 1. 프롬프트 구성
            news_content = ""
            for i, article in enumerate(articles, 1):
                news_content += f"{i}. 제목: {article.title}\n   내용: {article.snippet}\n\n"

            prompt = f"""다음 뉴스 기사들의 핵심 내용을 한국어로 요약해주세요:
- 불릿 포인트 형식으로 최대 5개 항목
- 각 항목은 1~2문장

[뉴스 목록]
{news_content}
"""

            # 2. Gemini 호출 (비동기 재시도 로직)
            error_occurred = None
            for attempt in range(retry_count + 1):
                try:
                    response = await self.client.aio.models.generate_content(
                        model=settings.GEMINI_MODEL,
                        contents=prompt
                    )
                    return response.text
                except Exception as e:
                    error_occurred = e
                    if attempt < retry_count:
                        await asyncio.sleep(30) # 429 에러 등을 대비해 넉넉히 대기
                        continue
                    raise e

        except Exception as e:
            self._handle_error(e)

    async def analyze_sentiment_async(self, articles: List[NewsArticle]) -> dict:
        """
        뉴스 기사들의 감성을 비동기로 분석합니다.
        
        Returns:
            dict: {"positive": int, "neutral": int, "negative": int} (합계 100)
        """
        if not articles:
            return {"positive": 0, "neutral": 100, "negative": 0}

        try:
            news_titles = "\n".join([f"- {a.title}" for a in articles])
            prompt = f"""다음 뉴스 기사 제목들을 분석하여 전반적인 여론의 감성을 positive, neutral, negative 백분율로 평가해주세요.
결과는 반드시 다음과 같은 JSON 형식으로만 응답해주세요:
{{"positive": 숫자, "neutral": 숫자, "negative": 숫자}}
(세 숫자의 합은 반드시 100이 되어야 합니다.)

[기사 제목 목록]
{news_titles}
"""
            response = await self.client.aio.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                }
            )
            
            import json
            result_text = response.text.strip()
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            sentiment = json.loads(result_text)
            return sentiment
        except Exception:
            return {"positive": 33, "neutral": 34, "negative": 33}

    def _handle_error(self, e: Exception):
        error_str = str(e).lower()
        if "invalid api key" in error_str or "unauthorized" in error_str:
            raise AppError("api_key_invalid")
        elif "429" in error_str or "quota" in error_str:
            raise AppError("gemini_rate_limit")
        elif "400" in error_str:
            raise AppError("gemini_bad_request")
        else:
            raise AppError("ai_error")

# 싱글톤 인스턴스
ai_service = AIService()

async def summarize_news(articles: List[NewsArticle]) -> str:
    """AI 서비스 싱글톤을 통한 비동기 요약 함수"""
    return await ai_service.summarize_news_async(articles)

async def analyze_sentiment(articles: List[NewsArticle]) -> dict:
    """AI 서비스 싱글톤을 통한 비동기 감성 분석 함수"""
    return await ai_service.analyze_sentiment_async(articles)

async def generate_news_image(summary: str) -> Optional[bytes]:
    """AI 서비스 싱글톤을 통한 비동기 이미지 생성 함수"""
    try:
        # 요약에서 핵심 키워드 중심의 프롬프트 생성
        image_prompt = f"Editorial style professional news illustration, minimalist, related to: {summary[:200]}"
        response = await ai_service.client.aio.models.generate_images(
            model='imagen-3.0-generate-001',
            prompt=image_prompt,
            config={'number_of_images': 1}
        )
        if response.generated_images:
            return response.generated_images[0].image.data
        return None
    except Exception as e:
        print(f"이미지 생성 실패: {e}")
        return None
