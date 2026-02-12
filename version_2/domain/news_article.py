from dataclasses import dataclass

@dataclass(frozen=True)
class NewsArticle:
    """뉴스 기사 정보를 담는 데이터 클래스"""
    title: str
    url: str
    snippet: str
    pub_date: str = ""
