import os
from dotenv import load_dotenv

class Settings:
    """애플리케이션 환경 설정을 관리하는 클래스"""
    def __init__(self):
        load_dotenv()
        
        # 필수 환경변수 체크
        self.TAVILY_API_KEY = self._get_env("TAVILY_API_KEY", required=True)
        self.GEMINI_API_KEY = self._get_env("GEMINI_API_KEY", required=True)
        self.CSV_PATH = self._get_env("CSV_PATH", required=True)
        
        # 선택 환경변수 (기본값 제공)
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        # SEARCH_DOMAINS는 리스트로 변환
        search_domains_raw = os.getenv("SEARCH_DOMAINS", "")
        self.SEARCH_DOMAINS = [d.strip() for d in search_domains_raw.split(",") if d.strip()] if search_domains_raw else []

    def _get_env(self, key: str, required: bool = False):
        """환경변수를 가져오고 필수 항목 누락 시 사용자 친화적인 에러를 발생시킵니다."""
        value = os.getenv(key)
        if required and not value:
            error_msg = f"""
❌ 필수 환경변수 '{key}'가 설정되지 않았습니다.

설정 방법:
1. .env.example 파일을 .env로 복사합니다 (cp .env.example .env)
2. .env 파일을 열어 '{key}' 값을 입력합니다.

API 키 발급 안내:
- Tavily API: https://tavily.com/ (검색 API)
- Google AI Studio: https://aistudio.google.com/ (Gemini 요약 API)

문제가 지속되면 프로젝트 루트의 .env 파일을 다시 확인해주세요.
"""
            raise ValueError(error_msg)
        return value

# 싱글톤 인스턴스
settings = Settings()
