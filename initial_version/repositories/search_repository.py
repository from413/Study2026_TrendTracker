import os
from typing import List, Optional
import pandas as pd
from datetime import datetime
from domain.news_article import NewsArticle
from domain.search_result import SearchResult

class SearchRepository:
    """CSV 파일을 이용한 검색 결과 저장 및 로드 관리를 담당하는 리포지토리 클래스"""
    
    def __init__(self, csv_path: str):
        """
        리포지토리 초기화
        
        Args:
            csv_path (str): 데이터가 저장될 CSV 파일 경로
        """
        self.csv_path = csv_path
        self.columns = [
            "search_key", "search_time", "keyword", "article_index",
            "title", "url", "snippet", "pub_date", "ai_summary"
        ]
        self._ensure_directory()

    def _ensure_directory(self):
        """데이터 저장 폴더가 없으면 생성합니다."""
        directory = os.path.dirname(self.csv_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def load(self) -> pd.DataFrame:
        """
        CSV 파일에서 데이터를 로드합니다.
        파일이 없거나 읽기 실패 시 빈 DataFrame을 반환합니다.
        """
        if not os.path.exists(self.csv_path):
            return pd.DataFrame(columns=self.columns)
        
        try:
            df = pd.read_csv(self.csv_path)
            # 저장된 컬럼이 다를 수 있으므로 필수 컬럼 확인 및 정합성 유지
            for col in self.columns:
                if col not in df.columns:
                    df[col] = ""
            return df[self.columns]
        except Exception as e:
            print(f"로그: 파일 읽기 실패 - {e}")
            return pd.DataFrame(columns=self.columns)

    def save(self, search_result: SearchResult) -> bool:
        """
        검색 결과를 CSV 파일에 추가 저장합니다.
        """
        try:
            new_df = search_result.to_dataframe()
            
            if os.path.exists(self.csv_path):
                existing_df = pd.read_csv(self.csv_path)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                combined_df = new_df
            
            combined_df.to_csv(self.csv_path, index=False, encoding='utf-8-sig')
            return True
        except Exception as e:
            print(f"로그: 데이터 저장 실패 - {e}")
            return False

    def get_all_keys(self) -> List[str]:
        """
        저장된 모든 search_key를 최신순으로 반환합니다.
        """
        df = self.load()
        if df.empty:
            return []
        
        # search_time 기준으로 정렬 후 unique한 search_key 추출
        df['search_time'] = pd.to_datetime(df['search_time'])
        sorted_keys = df.sort_values(by="search_time", ascending=False)["search_key"].unique().tolist()
        return sorted_keys

    def find_by_key(self, search_key: str) -> Optional[SearchResult]:
        """
        search_key에 해당하는 검색 결과를 SearchResult 객체로 반환합니다.
        """
        df = self.load()
        filtered_df = df[df["search_key"] == search_key]
        
        if filtered_df.empty:
            return None
        
        # 첫 번째 행에서 기본 정보 추출
        first_row = filtered_df.iloc[0]
        
        articles = []
        for _, row in filtered_df.sort_values(by="article_index").iterrows():
            articles.append(NewsArticle(
                title=str(row["title"]),
                url=str(row["url"]),
                snippet=str(row["snippet"]),
                pub_date=str(row.get("pub_date", ""))
            ))
            
        return SearchResult(
            search_key=str(first_row["search_key"]),
            search_time=pd.to_datetime(first_row["search_time"]),
            keyword=str(first_row["keyword"]),
            articles=articles,
            ai_summary=str(first_row["ai_summary"])
        )

    def get_all_as_csv(self) -> str:
        """
        전체 데이터를 CSV 형식의 문자열로 반환합니다.
        """
        df = self.load()
        if df.empty:
            return ""
        return df.to_csv(index=False, encoding='utf-8-sig')
