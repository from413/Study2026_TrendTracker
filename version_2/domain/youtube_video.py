from dataclasses import dataclass
from typing import Optional

@dataclass
class YouTubeVideo:
    """YouTube 영상 정보를 담는 데이터 클래스"""
    title: str
    url: str
    thumbnail_url: str
    video_id: str
    published_date: str = ""
    description: str = ""
