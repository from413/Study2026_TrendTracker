import streamlit as st
from typing import Optional
from utils.input_handler import preprocess_keyword

def render_search_form() -> Optional[str]:
    """
    메인 화면의 검색 폼을 렌더링합니다.
    사용자로부터 키워드를 입력받고 전처리하여 반환합니다.
    
    Returns:
        Optional[str]: 전처리된 키워드 (입력이 없거나 유효하지 않으면 None)
    """
    with st.container():
        keyword_input = st.text_input(
            "검색어 입력",
            placeholder="예: 인공지능 트렌드, 삼성전자 뉴스 등",
            help="검색하고자 하는 최신 뉴스 키워드를 입력하세요."
        )
        
        search_button = st.button("검색", type="primary", use_container_width=True)
        
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
