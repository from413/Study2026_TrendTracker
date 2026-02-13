import streamlit as st
import asyncio
from services.search_service import search_news
from typing import List
from domain.news_article import NewsArticle

async def render_home_sections():
    """
    홈 화면에서 '주요 뉴스', '추천 뉴스', '사람들의 이야기' 섹션을 렌더링합니다.
    (비동기 병렬 처리를 통해 속도를 개선합니다.)
    """
    st.markdown("---")
    
    # 3가지 섹션 뉴스를 병렬로 가져옵니다.
    try:
        main_task = search_news("최신 주요 뉴스", num_results=3)
        people_task = search_news("실시간 인물 뉴스 인터뷰", num_results=3)
        rec_task = search_news("오늘의 추천 트렌드 뉴스", num_results=3)
        
        main_news, people_news, rec_news = await asyncio.gather(main_task, people_task, rec_task)
    except Exception as e:
        st.error(f"홈 섹션 데이터를 가져오는 중 오류가 발생했습니다: {e}")
        main_news, people_news, rec_news = [], [], []

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔝 오늘의 주요 뉴스")
        if main_news:
            for article in main_news:
                with st.container():
                    st.markdown(f"**[{article.title}]({article.url})**")
                    st.caption(f"{article.pub_date} | {article.snippet[:100]}...")
                    st.divider()
        else:
            st.info("주요 뉴스를 불러올 수 없습니다.")

    with col2:
        st.subheader("👤 사람들의 이야기")
        if people_news:
            for article in people_news:
                st.markdown(f"• [{article.title}]({article.url})")
        else:
            st.info("데이터가 없습니다.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.subheader("💡 추천 뉴스")
        if rec_news:
            for article in rec_news:
                st.markdown(f"• [{article.title}]({article.url})")
        else:
            st.info("추천 뉴스가 없습니다.")
