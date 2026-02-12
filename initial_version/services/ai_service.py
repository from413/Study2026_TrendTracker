import time
from typing import List
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

    def summarize_news(self, articles: List[NewsArticle], retry_count: int = 1) -> str:
        """
        Gemini API를 사용해 뉴스 기사들을 요약합니다.
        
        Args:
            articles (List[NewsArticle]): 요약할 기사 리스트
            retry_count (int): 재시도 횟수 (기본 1회)
            
        Returns:
            str: 요약된 텍스트
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

            # 2. Gemini 호출 (재시도 로직)
            error_occurred = None
            for attempt in range(retry_count + 1):
                try:
                    response = self.client.models.generate_content(
                        model=settings.GEMINI_MODEL,
                        contents=prompt
                    )
                    return response.text
                except Exception as e:
                    error_occurred = e
                    if attempt < retry_count:
                        time.sleep(30) # 429 에러 등을 대비해 넉넉히 대기
                        continue
                    raise e

        except Exception as e:
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

def summarize_news(articles: List[NewsArticle]) -> str:
    """AI 서비스 싱글톤을 통한 요약 함수"""
    return ai_service.summarize_news(articles)
