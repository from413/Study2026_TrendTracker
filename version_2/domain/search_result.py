from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import pandas as pd
from domain.news_article import NewsArticle
from domain.youtube_video import YouTubeVideo

@dataclass
class SearchResult:
    """검색 결과 및 AI 요약을 담는 데이터 클래스"""
    search_key: str  # 형식: "키워드-yyyymmddhhmm"
    search_time: datetime
    keyword: str
    articles: List[NewsArticle]
    ai_summary: str = ""
    sentiment_data: dict = field(default_factory=lambda: {"positive": 50, "neutral": 30, "negative": 20})
    ai_image: Optional[bytes] = None
    youtube_videos: List[YouTubeVideo] = field(default_factory=list)

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
                "ai_summary": self.ai_summary,
                "positive": self.sentiment_data.get("positive", 0),
                "neutral": self.sentiment_data.get("neutral", 0),
                "negative": self.sentiment_data.get("negative", 0)
            })
        
        return pd.DataFrame(data)
