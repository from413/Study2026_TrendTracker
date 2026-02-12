import os
from dotenv import load_dotenv
from google import genai

def main():
    # 1. .env 파일에서 환경변수 로드
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    model_id = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash-lite")
    
    if not api_key:
        print("Error: GOOGLE_API_KEY is not set in .env file.")
        return

    # 2. prompt.md 파일 내용 읽기
    try:
        with open("prompt.md", "r", encoding="utf-8") as f:
            prompt_text = f.read()
    except FileNotFoundError:
        print("Error: prompt.md file not found.")
        return

    # 3. google-genai Client 객체 생성
    client = genai.Client(api_key=api_key)

    # 4. Gemini 모델 호출
    print(f"Calling model: {model_id}...")
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt_text
        )
        # 5. 응답 출력
        print("\n--- Gemini Response ---")
        print(response.text)
    except Exception as e:
        print(f"Error during API call: {e}")

if __name__ == "__main__":
    main()
