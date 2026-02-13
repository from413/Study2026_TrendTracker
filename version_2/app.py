import streamlit as st
import asyncio
from datetime import datetime
from typing import List, Optional

# 설정 및 도메인
from config.settings import settings
from domain.news_article import NewsArticle
from domain.search_result import SearchResult

# 서비스 및 리포지토리
from services.search_service import search_news, search_youtube
from services.ai_service import summarize_news, analyze_sentiment, generate_news_image
from repositories.search_repository import SearchRepository

# 유틸리티 및 예외 처리
from utils.exceptions import AppError
from utils.error_handler import handle_error
from utils.key_generator import generate_search_key

# UI 컴포넌트
from components.search_form import render_search_form
from components.header import render_header
from components.sidebar import (
    render_sidebar_header, render_settings, render_info, 
    render_history_list, render_download_button
)
from components.result_section import (
    render_summary, render_sentiment_chart, render_news_list, render_news_image
)
from components.youtube_section import render_youtube_list
from components.loading import show_loading

from components.home_sections import render_home_sections

def init_session_state():
    """세션 상태 초기화 및 기본값 설정"""
    if "current_mode" not in st.session_state:
        st.session_state.current_mode = "new_search"
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "selected_key" not in st.session_state:
        st.session_state.selected_key = None

async def run_search_logic(keyword: str, num_results: int, repository: SearchRepository):
    """
    비동기 검색 및 분석 로직 통합 실행
    """
    try:
        # 1. 뉴스 검색 (Async)
        with show_loading(f"🔍 '{keyword}' 뉴스를 검색하고 있습니다..."):
            articles = await search_news(keyword, num_results)
        
        if not articles:
            st.info("검색 결과가 없습니다.")
            st.session_state.last_result = None
            return

        # 2. AI 요약, 감성 분석, 유튜브 검색 및 이미지 생성 (Async Parallel)
        with show_loading("🤖 AI가 분석하고 관련 영상을 찾고 있습니다..."):
            # gather를 통해 여러 작업을 동시에 수행하여 시간을 절약합니다.
            summary, sentiment, youtube_videos = await asyncio.gather(
                summarize_news(articles),
                analyze_sentiment(articles),
                search_youtube(keyword)
            )
            
            # 이미지는 요약문을 기반으로 생성
            image_data = await generate_news_image(summary)
        
        # 3. 결과 생성 및 저장
        with show_loading("💾 결과를 저장하고 있습니다..."):
            search_key = generate_search_key(keyword)
            result = SearchResult(
                search_key=search_key,
                search_time=datetime.now(),
                keyword=keyword,
                articles=articles,
                ai_summary=summary,
                sentiment_data=sentiment,
                ai_image=image_data,
                youtube_videos=youtube_videos
            )
            # 이미지는 용량 문제로 CSV 저장에서 제외될 수 있습니다. (SearchRepository 수정 필요시 대응)
            repository.save(result)
        
        # 4. 성공 알림 및 상태 기록
        st.toast(f"✅ '{keyword}' 분석이 완료되었습니다!", icon="🚀")
        st.success(f"'{keyword}' 검색 완료! {len(articles)}건의 뉴스를 찾았습니다.")
        st.session_state.last_result = result
        
    except AppError as e:
        handle_error(e.error_type)
    except Exception as e:
        st.error(f"알 수 없는 오류가 발생했습니다: {str(e)}")

def main():
    """메인 애플리케이션 실행 함수"""
    # 1. 페이지 설정
    st.set_page_config(page_title="TrendTracker", layout="wide", page_icon="📈")
    
    # 2. 초기화 및 설정 로드
    try:
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
    keywords_map = {key: key.rsplit('-', 1)[0] for key in search_keys}
    
    # 사이드바에서 기록 선택 및 관리
    history_status = render_history_list(search_keys, keywords_map)
    selected_key_sidebar = history_status["selected_key"]
    action = history_status["action"]
    
    # 삭제 액션 처리
    if action == "delete" and selected_key_sidebar:
        if repository.delete_by_key(selected_key_sidebar):
            st.toast(f"기록이 삭제되었습니다.")
            st.session_state.selected_key = None
            st.session_state.last_result = None
            st.rerun()
    elif action == "clear_all":
        if repository.clear_all():
            st.toast("모든 기록이 삭제되었습니다.")
            st.session_state.selected_key = None
            st.session_state.last_result = None
            st.rerun()

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
    st.markdown(
        """
        <style>
        /* Vercel / Carbon 스타일의 세련된 UI */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        /* 폰트 설정 */
        html, body, [class*="st-"] {
            font-family: 'Inter', sans-serif !important;
        }

        .stApp {
            background-color: #FFFFFF;
            color: #000000;
        }
        
        /* 헤더 섹션 */
        .main-title {
            text-align: center;
            font-size: 3.5rem !important;
            font-weight: 800;
            letter-spacing: -0.05rem;
            padding: 3rem 0 1rem 0;
            color: #000000 !important;
        }
        
        /* 아이콘 텍스트 누출(_arrow_right) 문제 해결을 위한 초강력 스타일 */
        /* 1. 아이콘이 포함될 수 있는 모든 컨테이너의 합자 효과를 제거하여 텍스트 노출 차단 */
        button, div, span, select, p, header {
            font-variant-ligatures: none !important;
            -webkit-font-variant-ligatures: none !important;
            font-feature-settings: "liga" 0, "clig" 0 !important;
        }

        /* 2. 스트림릿 내부 아이콘 및 화살표 요소들을 물리적으로 제거 */
        /* 버튼 내 화살표, 확장기 헤더 화살표, 선택박스 화살표 등을 타겟팅 */
        button div[data-testid="stMarkdownContainer"] svg,
        button svg,
        div[data-testid="stExpander"] header svg,
        div[data-testid="stExpander"] header span[data-testid="stIcon"],
        div[data-testid="stIconMaterial"], /* Material Icon 텍스트 누출 방지 */
        [data-testid="stIconMaterial"],
        div[data-baseweb="select"] svg,
        [data-testid="stSidebar"] [data-testid="stIcon"],
        .st-emotion-cache-1vt4y43, /* 아이콘 컨테이너 */
        .st-emotion-cache-1idxhyc, /* 화살표 컨테이너 */
        .st-emotion-cache-1c9yjad, /* 유저가 리포트한 특정 클래스 */
        .exvv1vr0 {
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
            height: 0 !important;
            font-size: 0 !important;
            color: transparent !important;
            line-height: 0 !important;
        }

        /* 3. 사이드바 확장기(사용방법 등) 내부 텍스트 겹침 방지 */
        div[data-testid="stExpander"] div[role="button"] {
            padding-right: 1rem !important; /* 화살표 제거 후 여백 조정 */
        }

        /* 카테고리 네비게이션 중앙 정렬 */
        div[data-testid="stHorizontalBlock"] {
            justify-content: center !important;
        }
        
        /* 사이드바 및 위젯 아이콘 보정 */
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            font-size: 0.95rem;
        }

        /* 카드 및 컨테이너 스타일 */
        div[data-testid="stExpander"] {
            border: 1px solid #eaeaea !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* 버튼 스타일 최적화 */
        .stButton > button {
            border-radius: 8px !important;
            font-weight: 600 !important;
            border: 1px solid #eaeaea !important;
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        .stButton > button:hover {
            border-color: #000000 !important;
            background-color: #fafafa !important;
        }
        
        /* 사이드바 스타일 */
        [data-testid="stSidebar"] {
            background-color: #FAFAFA !important;
            border-right: 1px solid #eaeaea !important;
        }
        
        hr {
            margin: 2rem 0 !important;
            border: 0;
            border-top: 1px solid #eaeaea;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown('<h1 class="main-title">TrendTracker</h1>', unsafe_allow_html=True)
    
    # 상단 헤더 카테고리
    selected_category = render_header()
    
    form_keyword = render_search_form()
    nav_keyword = selected_category if selected_category != "홈" else None
    keyword = form_keyword if form_keyword else nav_keyword
    
    if keyword:
        st.session_state.current_mode = "new_search"
        st.session_state.selected_key = None
        # 비동기 로직 실행
        asyncio.run(run_search_logic(keyword, num_results, repository))

    # 5. 결과 표시 영역
    if st.session_state.last_result:
        result = st.session_state.last_result
        is_history = (st.session_state.current_mode == "history")
        st.markdown("---")
        
        # 2컬럼 레이아웃으로 요약과 이미지 배치
        col_text, col_img = st.columns([1.5, 1])
        with col_text:
            render_summary(result.keyword, result.ai_summary, is_history=is_history)
        with col_img:
            render_news_image(result.ai_image)
            
        render_sentiment_chart(result.sentiment_data)
        render_news_list(result.articles)
        
        # 유튜브 영상 렌더링 추가
        if hasattr(result, 'youtube_videos') and result.youtube_videos:
            render_youtube_list(result.youtube_videos)
    elif not keyword:
        # 홈 섹션 비동기 실행
        asyncio.run(render_home_sections())

if __name__ == "__main__":
    main()
