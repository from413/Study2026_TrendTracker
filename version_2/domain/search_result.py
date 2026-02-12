from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import pandas as pd
from domain.news_article import NewsArticle

@dataclass
class SearchResult:
    """검색 결과 및 AI 요약을 담는 데이터 클래스"""
    search_key: str  # 형식: "키워드-yyyymmddhhmm"
    search_time: datetime
    keyword: str
    articles: List[NewsArticle]
    ai_summary: str = ""

    def to_dataframe(self) -> pd.DataFrame:
        """
        검색 결과를 pandas DataFrame으로 변환 (Long format: 기사 1건 = 1행)
        """
        data = []
        for i, article in enumerate(self.articles, 1):
            data.append({
                "search_key": self.search_key,
                "search_time": self.search_time,
                "keyword": self.keyword,
                "article_index": i,
                "title": article.title,
                "url": article.url,
                "snippet": article.snippet,
                "pub_date": article.pub_date,
                "ai_summary": self.ai_summary
            })
        
        return pd.DataFrame(data)
