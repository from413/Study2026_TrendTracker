# TrendTracker (TrendTracker - 뉴스 요약기)

키워드로 최신 뉴스를 검색하고 Gemini AI를 통해 핵심 내용을 요약해주는 Streamlit 웹 애플리케이션입니다.

## ✨ 주요 기능

- **실시간 뉴스 검색**: Tavily API를 사용하여 신뢰할 수 있는 뉴스 도메인에서 최신 정보를 가져옵니다.
- **AI 핵심 요약**: Google Gemini (Direct SDK)를 활용하여 여러 뉴스의 맥락을 파악하고 한국어로 요약해줍니다.
- **검색 기록 저장**: 모든 검색 결과는 로컬 CSV 파일(`data/search_history.csv`)에 자동 저장되어 언제든 다시 확인할 수 있습니다.
- **데이터 내보내기**: 저장된 전체 검색 기록을 CSV 파일로 다운로드할 수 있습니다.
- **반응형 UI**: Streamlit 기반의 깔끔하고 직관적인 인터페이스를 제공합니다.

## 🚀 설치 및 실행 방법

### 1. 전제 조건

이 프로젝트는 패키지 관리자로 `uv`를 사용합니다. `uv`가 설치되어 있지 않다면 아래 명령어로 설치하세요.

- **Windows (PowerShell)**:
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **macOS/Linux**:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### 2. 프로젝트 설정

프로젝트 폴더로 이동한 후 의존성을 설치합니다.

```bash
uv sync
```

### 3. 환경변수 설정

API 키 설정을 위해 `.env` 파일을 생성해야 합니다.

```bash
cp .env.example .env
```

생성된 `.env` 파일을 열어 다음 키들을 입력하세요:

- `TAVILY_API_KEY`: [Tavily AI](https://tavily.com/)에서 발급받은 API 키
- `GEMINI_API_KEY`: [Google AI Studio](https://aistudio.google.com/)에서 발급받은 Gemini API 키
- `SEARCH_DOMAINS`: 검색을 허용할 도메인 목록 (예: `naver.com, donga.com, chosun.com`)

### 4. 앱 실행

```bash
uv run streamlit run app.py
```

## 📂 폴더 구조

```text
initial_version/
├── app.py                # 메인 애플리케이션 실행 파일
├── config/               # 설정 관리
├── domain/               # 데이터 모델 (NewsArticle, SearchResult)
├── services/             # 비즈니스 로직 (Search, AI 요약)
├── repositories/         # 데이터 관리 (CSV 저장소)
├── components/           # UI 컴포넌트
├── utils/                # 유틸리티 및 예외 처리
└── data/                 # 검색 기록 CSV 저장 위치
```

## ⚠️ 주의사항

- **데이터 보존**: `data/search_history.csv` 파일을 삭제하면 과거 검색 기록이 모두 소멸됩니다. 중요한 데이터는 주기적으로 다운로드 기능을 통해 백업하세요.
- **API 한도**: Tavily와 Gemini의 무료 플랜 한도를 확인하여 사용하시기 바랍니다.

## 🚫 라이선스

이 프로젝트는 학습 및 포트폴리오 용도로 제작되었습니다.
