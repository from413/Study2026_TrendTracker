import time
import asyncio
from typing import List
from tavily import TavilyClient, AsyncTavilyClient
from domain.news_article import NewsArticle
from domain.youtube_video import YouTubeVideo
from config.settings import settings
from utils.exceptions import AppError

class SearchService:
    """Tavily API를 이용한 뉴스 및 유튜브 검색 서비스 클래스"""
    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        if not self.api_key:
            raise AppError("api_key_invalid")
        self.client = TavilyClient(api_key=self.api_key)
        self.async_client = AsyncTavilyClient(api_key=self.api_key)

    async def search_youtube_async(self, keyword: str, num_results: int = 4) -> List[YouTubeVideo]:
        """
        Tavily API를 이용해 관련 유튜브 영상을 검색합니다.
        """
        try:
            # YouTube를 명시적으로 검색하기 위해 query에 site prefix 추가
            youtube_query = f"site:youtube.com {keyword}"
            
            response = await self.async_client.search(
                query=youtube_query,
                search_depth="basic",
                max_results=num_results * 2 # 여유있게 가져옴
            )
            
            results = response.get('results', [])
            videos = []
            
            for item in results:
                url = item.get('url', '')
                if 'youtube.com/watch?v=' in url:
                    video_id = url.split('watch?v=')[1].split('&')[0]
                elif 'youtu.be/' in url:
                    video_id = url.split('youtu.be/')[1].split('?')[0]
                else:
                    continue
                
                # 중복 추천 방지
                if any(v.video_id == video_id for v in videos):
                    continue
                    
                videos.append(YouTubeVideo(
                    title=item.get('title', 'YouTube Video'),
                    url=url,
                    thumbnail_url=f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
                    video_id=video_id,
                    published_date=item.get('published_date', ''),
                    description=item.get('content', '')
                ))
                
                if len(videos) >= num_results:
                    break
                    
            return videos
            
        except Exception:
            return [] # YouTube 검색 실패는 치명적이지 않으므로 빈 리스트 반환

    async def search_news_async(self, keyword: str, num_results: int = 5, retry_count: int = 1) -> List[NewsArticle]:
        """
        Tavily API를 비동기로 사용해 최신 뉴스를 검색하고 NewsArticle 리스트를 반환합니다.
        """
        try:
            max_results_to_fetch = max(num_results * 3, 20)
            
            error_occurred = None
            for attempt in range(retry_count + 1):
                try:
                    response = await self.async_client.search(
                        query=keyword,
                        search_depth="advanced",
                        include_domains=settings.SEARCH_DOMAINS,
                        max_results=max_results_to_fetch,
                        topic="news"
                    )
                    break 
                except Exception as e:
                    error_occurred = e
                    if attempt < retry_count:
                        await asyncio.sleep(2) # 2초 대기 후 재시도
                        continue
                    raise e

            results = response.get('results', [])
            if not results:
                return []
            
            # 2. 결과 처리 및 정렬 (최신순)
            sorted_results = sorted(
                results,
                key=lambda x: x.get('published_date', ''),
                reverse=True
            )
            
            # 3. NewsArticle 객체로 변환
            articles = []
            for item in sorted_results[:num_results]:
                articles.append(NewsArticle(
                    title=item.get('title', '제목 없음'),
                    url=item.get('url', ''),
                    snippet=item.get('content', ''),
                    pub_date=item.get('published_date', '')
                ))
                
            return articles

        except Exception as e:
            self._handle_error(e)

    def search_news(self, keyword: str, num_results: int = 5, retry_count: int = 1) -> List[NewsArticle]:
        """
        기존 동기 방식 검색 (하위 호환성 유지)
        """
        try:
            max_results_to_fetch = max(num_results * 3, 20)
            response = self.client.search(
                query=keyword,
                search_depth="advanced",
                include_domains=settings.SEARCH_DOMAINS,
                max_results=max_results_to_fetch,
                topic="news"
            )
            results = response.get('results', [])
            sorted_results = sorted(results, key=lambda x: x.get('published_date', ''), reverse=True)
            return [NewsArticle(
                title=item.get('title', '제목 없음'),
                url=item.get('url', ''),
                snippet=item.get('content', ''),
                pub_date=item.get('published_date', '')
            ) for item in sorted_results[:num_results]]
        except Exception as e:
            self._handle_error(e)

    def _handle_error(self, e: Exception):
        error_str = str(e).lower()
        if "status code 401" in error_str or "invalid api key" in error_str:
            raise AppError("tavily_unauthorized")
        elif "status code 429" in error_str:
            raise AppError("tavily_rate_limit")
        elif "status code 400" in error_str:
            raise AppError("tavily_bad_request")
        elif "status code 5" in error_str: # 5xx 에러
            raise AppError("tavily_server_error")
        else:
            raise AppError("network_error")

# 싱글톤 인스턴스
search_service = SearchService()

async def search_news(keyword: str, num_results: int = 5) -> List[NewsArticle]:
    """검색 서비스 싱글톤을 통한 비동기 뉴스 검색 함수"""
    return await search_service.search_news_async(keyword, num_results)

async def search_youtube(keyword: str, num_results: int = 4) -> List[YouTubeVideo]:
    """검색 서비스 싱글톤을 통한 비동기 유튜브 검색 함수"""
    return await search_service.search_youtube_async(keyword, num_results)
