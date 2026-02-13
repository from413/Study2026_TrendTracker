import streamlit as st
from typing import List, Optional
from domain.news_article import NewsArticle

import pandas as pd

def render_summary(keyword: str, summary: str, is_history: bool = False):
    """
    AI가 생성한 뉴스 요약 내용을 화면에 표시합니다.
    """
    icon = "📜" if is_history else "✨"
    st.subheader(f"{icon} AI 요약: {keyword}")
    if summary:
        st.container(border=True).markdown(summary)
    else:
        st.warning("요약 내용을 생성하는 중 오류가 발생했거나 내용이 없습니다.")

def render_news_image(image_data: Optional[bytes]):
    """
    AI가 생성한 이미지를 표시합니다.
    """
    if image_data:
        st.image(image_data, use_container_width=True, caption="AI Generated Editorial Illustration")
        st.markdown("<br>", unsafe_allow_html=True)

def render_sentiment_chart(sentiment_data: dict):
    """
    감성 분석 결과를 차트로 시각화합니다.
    """
    st.subheader("📊 여론 분석 (Sentiment Analysis)")
    
    if not sentiment_data:
        st.write("감성 분석 데이터가 없습니다.")
        return

    # 데이터 준비
    df = pd.DataFrame({
        '감성': ['긍정', '중립', '부정'],
        '비율(%)': [
            sentiment_data.get('positive', 0),
            sentiment_data.get('neutral', 0),
            sentiment_data.get('negative', 0)
        ]
    })
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("😊 긍정", f"{sentiment_data.get('positive', 0)}%")
    with col2:
        st.metric("😐 중립", f"{sentiment_data.get('neutral', 0)}%")
    with col3:
        st.metric("😡 부정", f"{sentiment_data.get('negative', 0)}%")

    # 바 차트 표시 - Vercel 스타일에 맞춰 높이 조절
    st.bar_chart(df.set_index('감성'), height=200)

def render_news_list(articles: List[NewsArticle]):
    """
    검색된 뉴스 기사 목록을 표시합니다.
    """
    st.subheader("📰 관련 뉴스 기사")
    
    if not articles:
        st.write("표시할 기사가 없습니다.")
        return

    for article in articles:
        title = article.title
        if article.pub_date:
            title = f"[{article.pub_date}] {title}"
            
        with st.expander(title):
            st.markdown(f"**기사 요약:** {article.snippet}")
            st.markdown(f"[🔗 기사 원문 보기]({article.url})")
