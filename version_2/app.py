import streamlit as st
from datetime import datetime
from typing import List, Optional

# 설정 및 도메인
from config.settings import settings
from domain.news_article import NewsArticle
from domain.search_result import SearchResult

# 서비스 및 리포지토리
from services.search_service import search_news
from services.ai_service import summarize_news
from repositories.search_repository import SearchRepository

# 유틸리티 및 예외 처리
from utils.exceptions import AppError
from utils.error_handler import handle_error
from utils.key_generator import generate_search_key

# UI 컴포넌트
from components.search_form import render_search_form
from components.sidebar import (
    render_sidebar_header, render_settings, render_info, 
    render_history_list, render_download_button
)
from components.result_section import render_summary, render_news_list
from components.loading import show_loading

def init_session_state():
    """세션 상태 초기화 및 기본값 설정"""
    if "current_mode" not in st.session_state:
        st.session_state.current_mode = "new_search"
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "selected_key" not in st.session_state:
        st.session_state.selected_key = None

def main():
    """메인 애플리케이션 실행 함수"""
    # 1. 페이지 설정
    st.set_page_config(page_title="TrendTracker", layout="wide", page_icon="📈")
    
    # 2. 초기화 및 설정 로드
    try:
        # settings가 싱글톤으로 로드될 때 환경변수 검증 수행
        from config.settings import settings
    except ValueError as e:
        st.error(str(e))
        st.stop()
        
    init_session_state()
    repository = SearchRepository(settings.CSV_PATH)
    
    # 3. 사이드바 렌더링
    render_sidebar_header()
    num_results = render_settings()
    render_info()
    st.sidebar.markdown("---")
    
    # 검색 기록 가져오기
    search_keys = repository.get_all_keys()
    # 키워드 매핑 (표시용)
    keywords_map = {key: key.rsplit('-', 1)[0] for key in search_keys}
    
    # 사이드바에서 기록 선택 시
    selected_key_sidebar = render_history_list(search_keys, keywords_map)
    
    # 사이드바 선택값이 변경되었을 때 처리
    if selected_key_sidebar and selected_key_sidebar != st.session_state.selected_key:
        st.session_state.selected_key = selected_key_sidebar
        st.session_state.current_mode = "history"
        st.session_state.last_result = repository.find_by_key(selected_key_sidebar)
        st.rerun()

    # 다운로드 버튼
    csv_data = repository.get_all_as_csv()
    render_download_button(csv_data, len(search_keys) == 0)
    
    # 4. 메인 영역 렌더링
    st.title("📈 TrendTracker")
    
    # 검색 폼
    keyword = render_search_form()
    
    if keyword:
        # 새 검색 시작
        st.session_state.current_mode = "new_search"
        st.session_state.selected_key = None
        
        try:
            # 1. 뉴스 검색
            with show_loading("🔍 뉴스를 검색하고 있습니다..."):
                articles = search_news(keyword, num_results)
            
            if not articles:
                st.info("검색 결과가 없습니다.")
                st.session_state.last_result = None
            else:
                # 2. AI 요약
                with show_loading("🤖 AI가 요약하고 있습니다..."):
                    summary = summarize_news(articles)
                
                # 3. 결과 생성 및 저장
                with show_loading("💾 결과를 저장하고 있습니다..."):
                    search_key = generate_search_key(keyword)
                    result = SearchResult(
                        search_key=search_key,
                        search_time=datetime.now(),
                        keyword=keyword,
                        articles=articles,
                        ai_summary=summary
                    )
                    repository.save(result)
                
                # 4. 성공 알림 및 상태 기록
                st.success(f"'{keyword}' 검색 완료! {len(articles)}건의 뉴스를 찾았습니다.")
                st.session_state.last_result = result
                
        except AppError as e:
            handle_error(e.error_type)
        except Exception as e:
            st.error(f"알 수 없는 오류가 발생했습니다: {str(e)}")

    # 5. 결과 표시 영역
    if st.session_state.last_result:
        result = st.session_state.last_result
        
        if st.session_state.current_mode == "new_search":
            title_prefix = f"✨ '{result.keyword}' 최신 트렌드 요약"
        else:
            title_prefix = f"📜 검색 기록: {result.keyword} ({result.search_time.strftime('%Y-%m-%d %H:%M')})"
            
        st.markdown("---")
        render_summary(title_prefix, result.ai_summary)
        render_news_list(result.articles)
    
    # 초기 화면 또는 빈 상태 안내
    elif not keyword:
        if not search_keys:
            st.info("👋 환영합니다! 아직 검색 기록이 없습니다. 상단에 키워드를 입력하여 첫 검색을 시작해보세요.")
        else:
            st.info("검색어를 입력하거나 왼쪽 사이드바에서 과거 기록을 선택해주세요.")

if __name__ == "__main__":
    main()
