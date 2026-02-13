import streamlit as st

def render_header() -> str:
    """
    애플리케이션의 상단 카테고리 네비게이션을 렌더링합니다.
    Daum 뉴스 상단 스타일을 참고하여 구현합니다.
    """
    # Vercel 스타일의 클린한 네비게이션을 위한 CSS
    st.markdown(
        """
        <style>
        .nav-wrapper {
            display: flex;
            justify-content: center;
            width: 100%;
            border-bottom: 1px solid #eaeaea;
            margin-bottom: 2rem;
        }
        /* segmented_control 중앙 정렬을 위한 추가 스타일 */
        div[data-testid="stHorizontalBlock"] {
            justify-content: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    categories = ["홈", "기후/환경", "사회", "경제", "정치", "국제", "문화", "생활", "IT/과학", "인물", "지식/칼럼", "연재"]
    
    # 3개 컬럼 중 중앙 컬럼을 넓게 잡아 중앙 정렬 효과
    _, center_col, _ = st.columns([1, 8, 1])
    
    with center_col:
        selected = st.segmented_control(
            "카테고리",
            options=categories,
            default="홈",
            label_visibility="collapsed",
            selection_mode="single",
            key="nav_categories",
        )
    
    return selected
