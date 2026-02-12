import streamlit as st
from typing import List
from domain.news_article import NewsArticle

def render_summary(title: str, summary: str):
    """
    AI가 생성한 뉴스 요약 내용을 화면에 표시합니다.
    
    Args:
        title (str): 섹션 제목 (예: '키워드 요약')
        summary (str): 요약 텍스트 내용
    """
    st.subheader(f"✨ AI 요약: {title}")
    if summary:
        st.info(summary)
    else:
        st.warning("요약 내용을 생성하는 중 오류가 발생했거나 내용이 없습니다.")

def render_news_list(articles: List[NewsArticle]):
    """
    검색된 뉴스 기사 목록을 확장형(expander) 레이아웃으로 표시합니다.
    
    Args:
        articles (List[NewsArticle]): 기사 객체 리스트
    """
    st.subheader("📰 관련 뉴스 기사")
    
    if not articles:
        st.write("표시할 기사가 없습니다.")
        return

    for article in articles:
        # expander 제목: 기사 제목 + (발행일)
        expander_title = article.title
        if article.pub_date:
            expander_title += f" ({article.pub_date})"
            
        with st.expander(expander_title):
            if article.pub_date:
                st.markdown(f"**📅 발행일:** {article.pub_date}")
            
            st.markdown(f"**내용 요약:**  \n{article.snippet}")
            st.markdown(f"[[🔗 기사 보기]({article.url})]")
