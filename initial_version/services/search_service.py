import time
from typing import List
from tavily import TavilyClient
from domain.news_article import NewsArticle
from config.settings import settings
from utils.exceptions import AppError

class SearchService:
    """Tavily API를 이용한 뉴스 검색 서비스 클래스"""
    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        if not self.api_key:
            raise AppError("api_key_invalid")
        self.client = TavilyClient(api_key=self.api_key)

    def search_news(self, keyword: str, num_results: int = 5, retry_count: int = 1) -> List[NewsArticle]:
        """
        Tavily API를 사용해 최신 뉴스를 검색하고 NewsArticle 리스트를 반환합니다.
        
        Args:
            keyword (str): 검색 키워드
            num_results (int): 반환할 결과 수
            retry_count (int): 재시도 횟수 (기본 1회)
            
        Returns:
            List[NewsArticle]: 검색된 기사 리스트
        """
        try:
            # 1. Tavily 검색 호출 (10초 타임아웃 개념은 SDK 내부 로직에 의존하거나 래핑 필요)
            # SDK가 타임아웃 파라미터를 지원하지 않을 경우, 별도의 래퍼가 필요할 수 있음.
            # 여기서는 기본 동작에 재시도 로직을 추가함.
            
            max_results_to_fetch = max(num_results * 3, 20)
            
            error_occurred = None
            for attempt in range(retry_count + 1):
                try:
                    response = self.client.search(
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
                        time.sleep(2) # 2초 대기 후 재시도
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
            error_str = str(e).lower()
            # 상세 에러 매핑
            if "status code 401" in error_str or "invalid api key" in error_str:
                raise AppError("tavily_unauthorized")
            elif "status code 429" in error_str:
                raise AppError("tavily_rate_limit")
            elif "status code 400" in error_str:
                raise AppError("tavily_bad_request")
            elif "status code 5" in error_str: # 5xx 에러
                raise AppError("tavily_server_error")
            elif "timeout" in error_str or "connection" in error_str:
                raise AppError("network_error")
            else:
                raise AppError("network_error")

# 싱글톤 인스턴스
search_service = SearchService()

def search_news(keyword: str, num_results: int = 5) -> List[NewsArticle]:
    """검색 서비스 싱글톤을 통한 뉴스 검색 함수"""
    return search_service.search_news(keyword, num_results)
