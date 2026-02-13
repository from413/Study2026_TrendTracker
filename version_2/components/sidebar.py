import streamlit as st
from typing import List, Optional
from datetime import datetime

def render_sidebar_header():
    """사이드바 헤더 렌더링"""
    # 폰트와 간격을 조정한 타이틀
    st.sidebar.markdown(
        """
        <div style="padding: 10px 0;">
            <h1 style="font-size: 1.5rem; font-weight: 800; margin: 0;">📰 TrendTracker</h1>
            <p style="font-size: 0.85rem; color: #666; margin-top: 5px;">AI 뉴스 통합 및 분석 서비스</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.markdown("---")

def render_settings() -> int:
    """설정 섹션 렌더링"""
    st.sidebar.subheader("⚙️ 설정")
    num_results = st.sidebar.slider(
        "최대 검색 결과 수",
        min_value=1,
        max_value=10,
        value=5
    )
    return num_results

def render_info():
    """사용법 안내"""
    with st.sidebar.expander("ℹ️ 사용 방법", expanded=False):
        st.markdown("""
        1. **키워드**를 입력하거나 **카테고리**를 선택하세요.
        2. **AI 요약**과 **감성 분석** 결과를 확인합니다.
        3. 개별 기사를 클릭하여 상세 내용을 확인하세요.
        """)
    
    with st.sidebar.expander("💾 데이터 관리", expanded=False):
        st.markdown("""
        - 검색 기록은 `data/search_history.csv`에 저장됩니다.
        - 아래 버튼을 사용하여 기록을 관리할 수 있습니다.
        """)

def render_history_list(search_keys: List[str], keywords_map: dict) -> dict:
    """검색 기록 관리 UI"""
    st.sidebar.subheader("📜 검색 기록")
    
    result = {"selected_key": None, "action": None}
    
    if not search_keys:
        st.sidebar.info("저장된 기록이 없습니다.")
        return result
    
    options = []
    option_to_key = {}
    
    for key in search_keys:
        try:
            parts = key.rsplit('-', 1)
            keyword = parts[0]
            timestamp_str = parts[1]
            dt = datetime.strptime(timestamp_str, "%Y%m%d%H%M")
            display_text = f"{keyword} ({dt.strftime('%m/%d %H:%M')})"
        except:
            display_text = key
            
        options.append(display_text)
        option_to_key[display_text] = key
        
    selected_option = st.sidebar.selectbox(
        "과거 기록 선택",
        options=["선택..."] + options,
        label_visibility="collapsed",
        key="history_selectbox"
    )
    
    if selected_option and selected_option != "선택...":
        result["selected_key"] = option_to_key[selected_option]
        
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🗑️ 선택 삭제", use_container_width=True, key="del_btn"):
            result["action"] = "delete"
    with col2:
        if st.button("🔥 전체 삭제", use_container_width=True, key="clear_btn"):
            result["action"] = "clear_all"
        
    return result

def render_download_button(csv_data: str, is_empty: bool):
    """CSV 다운로드"""
    st.sidebar.markdown("---")
    if is_empty:
        st.sidebar.button("📥 CSV 내보내기", disabled=True)
    else:
        st.sidebar.download_button(
            label="📥 CSV 내보내기",
            data=csv_data,
            file_name=f"trendtracker_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
