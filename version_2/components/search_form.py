import streamlit as st
from typing import Optional
from utils.input_handler import preprocess_keyword

def render_search_form() -> Optional[str]:
    """
    메인 화면의 검색 폼을 렌더링합니다. (Vercel Style)
    사용자로부터 키워드를 입력받고 전처리하여 반환합니다.
    """
    # 중앙 배치를 위해 컬럼 사용
    _, col2, _ = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(
            """
            <style>
            /* 검색창 스타일 (Vercel Style) */
            .stTextInput > div > div > input {
                border-radius: 8px !important;
                padding: 12px 16px !important;
                height: 48px !important;
                border: 1px solid #eaeaea !important;
                background-color: #FFFFFF !important;
                color: #000000 !important;
                transition: all 0.2s ease !important;
                box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
            }
            .stTextInput > div > div > input:focus {
                border-color: #000000 !important;
                box-shadow: 0 0 0 2px rgba(0,0,0,0.1) !important;
                outline: none !important;
            }
            
            /* 검색 버튼 스타일 */
            div[data-testid="stColumn"] > div > div > div > button {
                border-radius: 8px !important;
                height: 48px !important;
                background-color: #000000 !important;
                color: #FFFFFF !important;
                border: none !important;
                font-weight: 600 !important;
                transition: opacity 0.2s ease !important;
            }
            div[data-testid="stColumn"] > div > div > div > button:hover {
                opacity: 0.8 !important;
                background-color: #000000 !important;
                color: #FFFFFF !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        input_col, button_col = st.columns([4, 1])
        
        with input_col:
            keyword_input = st.text_input(
                "검색어 입력",
                placeholder="뉴스 키워드를 입력하세요 (예: 엔비디아 실적)",
                label_visibility="collapsed"
            )
        
        with button_col:
            search_button = st.button("검색", type="primary")
        
        if search_button:
            if not keyword_input:
                st.warning("검색어를 입력해주세요")
                return None
            
            processed_keyword = preprocess_keyword(keyword_input)
            if not processed_keyword:
                st.warning("유효한 검색어를 입력해주세요")
                return None
                
            return processed_keyword
            
    return None
