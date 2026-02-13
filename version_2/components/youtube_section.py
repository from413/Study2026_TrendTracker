import streamlit as st
from typing import List
from domain.youtube_video import YouTubeVideo

def render_youtube_list(videos: List[YouTubeVideo]):
    """유튜브 검색 결과를 세련된 카드 형태로 렌더링"""
    if not videos:
        return

    st.markdown("---")
    st.markdown("### 🎥 관련 YouTube 영상")
    
    # 2x2 또는 1x4 그리드 레이아웃 (영상이 4개인 경우)
    cols = st.columns(2)
    
    for i, video in enumerate(videos):
        col = cols[i % 2]
        with col:
            # 폰트 및 스타일 적용된 카드
            st.markdown(
                f"""
                <div style="
                    border: 1px solid #eaeaea;
                    border-radius: 12px;
                    padding: 12px;
                    margin-bottom: 20px;
                    background-color: #ffffff;
                    transition: transform 0.2s ease;
                " onmouseover="this.style.transform='translateY(-4px)'" onmouseout="this.style.transform='translateY(0)'">
                    <a href="{video.url}" target="_blank" style="text-decoration: none; color: inherit;">
                        <img src="{video.thumbnail_url}" style="width: 100%; border-radius: 8px; margin-bottom: 10px;">
                        <p style="
                            font-weight: 600;
                            font-size: 0.95rem;
                            margin: 0 0 8px 0;
                            display: -webkit-box;
                            -webkit-line-clamp: 2;
                            -webkit-box-orient: vertical;
                            overflow: hidden;
                            color: #000000;
                        ">{video.title}</p>
                        <p style="
                            font-size: 0.8rem;
                            color: #666666;
                            margin: 0;
                        ">출시일: {video.published_date[:10] if video.published_date else '정보 없음'}</p>
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )
