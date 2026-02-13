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
            <div style="
                margin-top: 15px;
                padding: 8px 12px;
                background: #eef2ff;
                border-radius: 8px;
                border: 1px solid #c7d2fe;
                display: flex;
                align-items: center;
                gap: 8px;
            ">
                <span style="position: relative; display: flex; h: 10px; w: 10px;">
                    <span style="animate: ping; position: absolute; display: inline-flex; height: 100%; width: 100%; border-radius: 100%; background: #4f46e5; opacity: 0.75;"></span>
                    <span style="position: relative; display: inline-flex; border-radius: 100%; height: 8px; width: 8px; background: #4f46e5;"></span>
                </span>
                <span style="font-size: 0.75rem; color: #4338ca; font-weight: 600;">실시간 트렌드 분석 활성화 중</span>
            </div>
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
    with st.sidebar.expander("💡 사용 방법 안내", expanded=False):
        st.markdown("""
        <div style="font-size: 0.9rem; line-height: 1.6;">
        1. 🔍 <b>키워드</b>를 입력하거나 상단 <b>카테고리</b>를 선택하세요.<br>
        2. ✨ <b>AI 요약</b>과 📊 <b>감성 분석</b> 결과를 확인합니다.<br>
        3. 📺 관련 <b>YouTube 영상</b>으로 입체적인 정보를 얻으세요.
        </div>
        """, unsafe_allow_html=True)
    
    with st.sidebar.expander("📂 데이터 및 기록 관리", expanded=False):
        st.markdown("""
        <div style="font-size: 0.9rem; line-height: 1.6;">
        - 검색 기록은 <code>data/search_history.csv</code>에 안전하게 저장됩니다.<br>
        - 과거 기록을 선택하여 언제든 다시 분석할 수 있습니다.
        </div>
        """, unsafe_allow_html=True)

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
