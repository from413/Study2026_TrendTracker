import streamlit as st

ERROR_MESSAGES = {
    # 공통 및 입력
    "api_key_invalid": "API 키를 확인해주세요. 유효하지 않거나 권한이 없습니다.",
    "empty_input": "검색어를 입력해주세요.",
    "no_results": "검색 결과가 없습니다.",
    
    # Tavily API 관련
    "tavily_bad_request": "잘못된 검색 요청입니다. (API 키 또는 파라미터 확인 필요)",
    "tavily_unauthorized": "Tavily API 키가 유효하지 않습니다.",
    "tavily_rate_limit": "월간/분당 검색 한도를 초과했습니다. (Tavily)",
    "tavily_server_error": "검색 서버 오류가 발생했습니다. 잠시 후 재시도해주세요.",
    
    # Gemini API 관련
    "gemini_rate_limit": "분당 호출 제한을 초과했습니다. 약 30초 후 다시 시도해주세요.",
    "gemini_bad_request": "AI 요약 요청 형식이 잘못되었습니다.",
    "ai_error": "AI 요약 중 오류가 발생했습니다.",
    
    # 네트워크/파일
    "network_error": "네트워크 연결이 원활하지 않습니다. 타임아웃 또는 연결 오류입니다.",
    "rate_limit_exceeded": "잠시 후 다시 시도해주세요. (호출 제한 초과)",
    "file_error": "파일 접근에 실패했습니다. (data 폴더 또는 CSV 파일 확인)"
}

def handle_error(error_type: str, level: str = "error"):
    """
    에러 타입에 따라 Streamlit UI에 메시지를 출력합니다.
    """
    message = ERROR_MESSAGES.get(error_type, "알 수 없는 에러가 발생했습니다")
    
    if level == "error":
        st.error(message)
    elif level == "warning":
        st.warning(message)
    elif level == "info":
        st.info(message)
    else:
        st.write(message)
