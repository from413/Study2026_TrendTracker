import streamlit as st
from contextlib import contextmanager

@contextmanager
def show_loading(message: str = "처리 중입니다..."):
    """
    st.spinner를 context manager로 래핑하여 사용하기 쉽게 합니다.
    
    사용 예:
    with show_loading("뉴스를 검색하고 있습니다..."):
        # 작업 수행
    """
    with st.spinner(message):
        yield
