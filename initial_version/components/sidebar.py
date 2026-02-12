import streamlit as st
from typing import List, Optional
from datetime import datetime

def render_sidebar_header():
    """사이드바 헤더 렌더링"""
    st.sidebar.title("Trend Tracker")
    st.sidebar.markdown("**키워드로 뉴스를 검색하고 AI가 요약해드립니다**")
    st.sidebar.markdown("---")

def render_settings() -> int:
    """설정 섹션 렌더링 및 검색 건수 반환"""
    st.sidebar.header("⚙️ 설정")
    num_results = st.sidebar.slider(
        "검색 건수",
        min_value=1,
        max_value=10,
        value=5,
        help="가져올 뉴스 기사의 개수를 설정합니다."
    )
    return num_results

def render_info():
    """사용법 및 데이터 안내 렌더링"""
    with st.sidebar.expander("ℹ️ 사용법", expanded=False):
        st.markdown("""
        1. 메인 화면에 **검색어**를 입력합니다.
        2. **검색** 버튼을 누르면 최신 뉴스를 가져옵니다.
        3. AI가 뉴스 내용을 분석하여 **핵심 요약**을 제공합니다.
        4. 기사 제목을 클릭하여 **상세 내용**을 확인하세요.
        """)
    
    with st.sidebar.expander("📊 API 한도", expanded=False):
        st.markdown("- Tavily 무료 플랜: 월 1,000건 검색 가능")
        st.markdown("- Gemini: 분당 호출 제한 확인 필요")

    with st.sidebar.expander("💾 데이터 저장 안내", expanded=False):
        st.markdown("""
        - 검색 기록은 CSV 파일(`data/search_history.csv`)에 저장됩니다.
        - CSV 파일을 삭제하거나 경로를 변경하면 이전 검색 기록이 모두 사라집니다.
        - 중요한 기록은 CSV 다운로드 기능을 통해 백업해주세요.
        """)

def render_history_list(search_keys: List[str], keywords_map: dict) -> Optional[str]:
    """검색 기록 목록 렌더링 및 선택된 키 반환"""
    st.sidebar.header("📜 검색 기록")
    
    if not search_keys:
        st.sidebar.info("저장된 검색 기록이 없습니다")
        return None
    
    # 표시용 형식 생성: "키워드 (yyyy-mm-dd HH:MM)"
    options = []
    key_to_option = {}
    
    for key in search_keys:
        try:
            # key 형식: "키워드-yyyyMMddHHmm"
            parts = key.rsplit('-', 1)
            keyword = parts[0]
            timestamp_str = parts[1]
            dt = datetime.strptime(timestamp_str, "%Y%m%d%H%M")
            formatted_date = dt.strftime("%Y-%m-%d %H:%M")
            display_text = f"{keyword} ({formatted_date})"
        except:
            display_text = key
            
        options.append(display_text)
        key_to_option[display_text] = key
        
    selected_option = st.sidebar.selectbox(
        "과거 결과 선택",
        options=["선택하세요..."] + options,
        label_visibility="collapsed"
    )
    
    if selected_option and selected_option != "선택하세요...":
        return key_to_option[selected_option]
        
    return None

def render_download_button(csv_data: str, is_empty: bool):
    """CSV 다운로드 버튼 렌더링"""
    st.sidebar.markdown("---")
    filename = f"trendtracker_export_{datetime.now().strftime('%Y%m%d')}.csv"
    
    if is_empty:
        st.sidebar.button("📥 CSV 다운로드", disabled=True, help="저장된 데이터가 없습니다.")
    else:
        st.sidebar.download_button(
            label="📥 CSV 다운로드",
            data=csv_data,
            file_name=filename,
            mime="text/csv"
        )
