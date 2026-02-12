# TrendTracker 학습 가이드

이 문서는 프로젝트를 7단계 프롬프트 순서에 따라 이해하기 위한 학습 가이드입니다.
각 Phase별로 **프롬프트 역할**, **핵심 개념**, **주요 코드**, **데이터 흐름**을 설명합니다.

---

# 목차

1. [Phase 1: 프로젝트 초기화 및 환경 설정](#phase-1-프로젝트-초기화-및-환경-설정)
2. [Phase 2: 도메인 모델 및 유틸리티 함수](#phase-2-도메인-모델-및-유틸리티-함수)
3. [Phase 3: 서비스 레이어 - API 연동](#phase-3-서비스-레이어---api-연동)
4. [Phase 4: 리포지토리 레이어 - 데이터 관리](#phase-4-리포지토리-레이어---데이터-관리)
5. [Phase 5: UI 컴포넌트](#phase-5-ui-컴포넌트)
6. [Phase 6: 메인 앱 통합](#phase-6-메인-앱-통합)
7. [Phase 7: 에러 핸들링 강화 및 마무리](#phase-7-에러-핸들링-강화-및-마무리)
8. [전체 데이터 흐름 다이어그램](#전체-데이터-흐름-다이어그램)

---

# Phase 1: 프로젝트 초기화 및 환경 설정

## 이 프롬프트의 역할
- 프로젝트의 기반이 되는 폴더 구조를 생성하고 가상환경 및 의존성을 설정합니다.
- 외부 API 연동을 위한 환경변수 관리 체계를 구축합니다.
- **생성된 파일 목록:** `pyproject.toml`, `.env.example`, `config/settings.py`, 각 폴더의 `__init__.py`

## 학습 목표
- `uv` 패키지 관리자를 이용한 Python 프로젝트 초기화 방법 이해
- `python-dotenv`를 활용한 보안 환경변수 관리 기법 습득
- 설정 정보를 싱글톤(Singleton) 형태로 관리하는 이유 파악

## 이해를 위한 핵심 개념

### 1.1 uv 패키지 관리자
기존의 `pip`보다 훨씬 빠른 속도와 의존성 해결 능력을 가진 현대적인 Python 패키지 관리 도구입니다. `uv init`으로 프로젝트를 시작하고 `uv add`로 라이브러리를 추가합니다.

### 1.2 환경변수와 Settings 클래스
API 키와 같은 민감한 정보는 코드에 하드코딩하지 않고 `.env` 파일에 기록합니다. `Settings` 클래스는 이를 읽어와 애플리케이션 전역에서 사용 가능한 객체로 변환하며, 누락된 필수 변수가 있을 경우 명확한 가이드를 제공합니다.

## 주요 코드 인용

### config/settings.py - 환경변수 로드
```python
# config/settings.py:10-12
        # 필수 환경변수 체크
        self.TAVILY_API_KEY = self._get_env("TAVILY_API_KEY", required=True)
        self.GEMINI_API_KEY = self._get_env("GEMINI_API_KEY", required=True)
        self.CSV_PATH = self._get_env("CSV_PATH", required=True)
```

**코드 설명:**
- `_get_env`: 지정된 키의 환경변수를 가져오며, `required=True`일 때 값이 없으면 `ValueError`를 발생시킵니다.
- `settings` 인스턴스: 파일 하단에서 `Settings()`를 미리 상주시켜 다른 모듈에서 즉시 임포트해 사용할 수 있게 합니다.

## 데이터 흐름에서의 역할

```
┌─────────────────────────────────────┐
│         Phase 1 데이터 흐름          │
├─────────────────────────────────────┤
│                                     │
│  [.env] → [settings.py] → [App 전역] │
│                                     │
└─────────────────────────────────────┘
```

---

# Phase 2: 도메인 모델 및 유틸리티 함수

## 이 프롬프트의 역할
- 프로젝트에서 다루는 데이터의 구조(Entity)를 정의합니다.
- 문자열 처리, 키 생성 등 반복적으로 사용되는 로직을 공통 함수로 분리합니다.
- **생성된 파일 목록:** `domain/news_article.py`, `domain/search_result.py`, `utils/key_generator.py`, `utils/input_handler.py`, `utils/error_handler.py`

## 학습 목표
- Python `dataclass`를 사용하여 구조화된 데이터 모델 정의
- 데이터 간의 관계(SearchResult와 NewsArticle의 1:N 관계) 표현
- 입력값 검증(Validation) 및 전처리 레이어 구축

## 이해를 위한 핵심 개념

### 2.1 도메인 모델 (Data Class)
비즈니스 로직에서 사용되는 핵심 데이터를 객체 형태로 정의한 것입니다. `dataclass`를 사용하면 `__init__`, `__repr__` 등을 수동으로 작성하지 않고도 속성을 명확히 정의할 수 있습니다.

### 2.2 검색 키 생성 기법
과거 기록을 구분하기 위해 "키워드-시간(yyyymmddhhmm)" 형태의 유니크한 키를 생성합니다. 이는 결과 조회 및 CSV 저장 시 기본 키(Primary Key) 역할을 합니다.

## 주요 코드 인용

### domain/search_result.py - DataFrame 변환 로직
```python
# domain/search_result.py:16-34
    def to_dataframe(self) -> pd.DataFrame:
        """
        검색 결과를 pandas DataFrame으로 변환 (Long format: 기사 1건 = 1행)
        """
        data = []
        for i, article in enumerate(self.articles, 1):
            data.append({
                "search_key": self.search_key,
                "search_time": self.search_time,
                "keyword": self.keyword,
                "article_index": i,
                "title": article.title,
                "url": article.url,
                "snippet": article.snippet,
                "pub_date": article.pub_date,
                "ai_summary": self.ai_summary
            })
        
        return pd.DataFrame(data)
```

**코드 설명:**
- `to_dataframe`: 객체 형태의 검색 결과를 CSV 저장이 용이한 표(DataFrame) 형태로 변환합니다. 여러 기사를 가로가 아닌 세로로 나열하는 Long Format을 사용합니다.

## 데이터 흐름에서의 역할

```
┌─────────────────────────────────────┐
│         Phase 2 데이터 흐름          │
├─────────────────────────────────────┤
│                                     │
│  [사용자 입력] → [전처리] → [모델 생성] │
│                                     │
└─────────────────────────────────────┘
```

---

# Phase 3: 서비스 레이어 - API 연동

## 이 프롬프트의 역할
- 뉴스 검색 엔진(Tavily)과 인공지능 요약 엔진(Gemini)을 실제 코드로 연결합니다.
- 외부 API 호출 시 발생할 수 있는 다양한 에러 상황(한도 초과, 인증 실패 등)을 처리합니다.
- **생성된 파일 목록:** `services/search_service.py`, `services/ai_service.py`, `utils/exceptions.py`

## 학습 목표
- 외부 라이브러리(SDK)를 이용한 API 통신 구현
- 커스텀 예외(`AppError`)를 통한 에러 전파 관리
- 네트워크 불안정성에 대비한 재시도(Retry) 로직 구현

## 이해를 위한 핵심 개념

### 3.1 서비스 레이어 (Service Layer)
브라우저 전면부(UI)와 데이터 저장소(Repository) 중간에서 핵심적인 비즈니스 로직(검색, 요약)을 수행하는 계층입니다. 중복 코드를 방지하고 모듈화된 기능을 제공합니다.

### 3.2 Granular Error Handling
외부 서버에서 응답하는 에러 코드와 메시지를 분석하여, 사용자에게 친절한 한글 메시지로 매핑해주는 과정입니다.

## 주요 코드 인용

### services/search_service.py - 재시도 로직
```python
# services/search_service.py:35-51
            error_occurred = None
            for attempt in range(retry_count + 1):
                try:
                    response = self.client.search(
                        query=keyword,
                        search_depth="advanced",
                        include_domains=settings.SEARCH_DOMAINS,
                        max_results=max_results_to_fetch,
                        topic="news"
                    )
                    break 
                except Exception as e:
                    error_occurred = e
                    if attempt < retry_count:
                        time.sleep(2) # 2초 대기 후 재시도
                        continue
                    raise e
```

**코드 설명:**
- `retry_count`: 일시적인 네트워크 오류 시 1회 더 시도하여 안정성을 높입니다.
- `error_str` 매핑: 401, 429 등의 에러를 `AppError`로 변환하여 상위 레이어로 전달합니다.

## 데이터 흐름에서의 역할

```
┌──────────────────────────────────────────┐
│             Phase 3 데이터 흐름            │
├──────────────────────────────────────────┤
│                                          │
│  [키워드] → [Tavily API] → [Gemini API]    │
│            (뉴스 검색)     (내용 요약)    │
│                                          │
└──────────────────────────────────────────┘
```

---

# Phase 4: 리포지토리 레이어 - 데이터 관리

## 이 프롬프트의 역할
- 메모리상의 뉴스 데이터를 로컬 파일(CSV)로 영구 저장하는 기능을 구현합니다.
- 과거 검색 기록을 불러와 다시 보여주는 조회 로직을 처리합니다.
- **생성된 파일 목록:** `repositories/search_repository.py`, `components/sidebar.py`

## 학습 목표
- `pandas`를 이용한 데이터 영속화(Persistence) 관리
- 데이터 복구(DataFrame → Object) 과정 이해
- 저장 공간 부족이나 파일 쓰기 권한 등의 예외 상황 방어

## 이해를 위한 핵심 개념

### 4.1 리포지토리 패턴
데이터 소스가 무엇이든(DB나 CSV) 상관없이 일관된 인터페이스(`load`, `save`)를 제공하여 비즈니스 로직이 데이터 저장 방식에 의존하지 않게 합니다.

### 4.2 CSV 인코딩 (utf-8-sig)
엑셀 등에서 한글 검색 결과가 깨지지 않도록 BOM(Byte Order Mark)을 포함하는 인코딩 방식을 사용합니다.

## 주요 코드 인용

### repositories/search_repository.py - 저장 로직
```python
# repositories/search_repository.py:51-67
    def save(self, search_result: SearchResult) -> bool:
        """
        검색 결과를 CSV 파일에 추가 저장합니다.
        """
        try:
            new_df = search_result.to_dataframe()
            
            if os.path.exists(self.csv_path):
                existing_df = pd.read_csv(self.csv_path)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                combined_df = new_df
            
            combined_df.to_csv(self.csv_path, index=False, encoding='utf-8-sig')
            return True
```

**코드 설명:**
- `pd.concat`: 새로운 검색 결과를 기존 데이터 파일 뒤에 붙여 넣습니다.
- `encoding='utf-8-sig'`: 윈도우용 엑셀 호환성을 위한 설정입니다.

## 데이터 흐름에서의 역할

```
┌───────────────────────────────────────┐
│          Phase 4 데이터 흐름           │
├───────────────────────────────────────┤
│                                       │
│  [Object] → [Repo.save] → [CSV 파일]  │
│  [CSV 파일] → [Repo.load] → [Object]  │
│                                       │
└───────────────────────────────────────┘
```

---

# Phase 5: UI 컴포넌트

## 이 프롬프트의 역할
- Streamlit의 위젯들을 사용하여 사용자에게 보여질 화면 요소들을 구성합니다.
- 각 기능을 독립적인 파이썬 파일로 분리하여 코드 재사용성과 가독성을 높입니다.
- **생성된 파일 목록:** `components/search_form.py`, `components/sidebar.py` (업데이트), `components/result_section.py`, `components/loading.py`

## 학습 목표
- Streamlit 컴포넌트 기반 UI 개발 방법 숙지
- Context Manager(`with`)를 사용한 로딩 처리 기법 습득
- 사용자 피드백(진행바, 알림 메시지) 구현

## 이해를 위한 핵심 개념

### 5.1 모듈형 UI 개발
한 화면의 모든 코드를 `app.py`에 넣는 대신, 검색창/사이드바/결과창을 각각의 함수로 분리하여 관리합니다. 이는 나중에 UI만 변경하고 싶을 때 매우 유용합니다.

### 5.2 Streamlit Expander
많은 양의 뉴스 기사를 화면에 효율적으로 배치하기 위해 클릭 시에만 펼쳐지는 `st.expander`를 사용합니다.

## 주요 코드 인용

### components/loading.py - Context Manager 기반 로딩
```python
# components/loading.py:4-15
@contextmanager
def show_loading(message: str = "처리 중입니다..."):
    """
    st.spinner를 context manager로 래핑하여 사용하기 쉽게 합니다.
    """
    with st.spinner(message):
        yield
```

**코드 설명:**
- `@contextmanager`: `with show_loading(...):` 구문을 사용할 수 있게 하여, 비즈니스 로직 수행 중에만 로딩 스피너가 보이도록 제어합니다.

## 데이터 흐름에서의 역할

```
┌──────────────────────────────────────┐
│         Phase 5 데이터 흐름           │
├──────────────────────────────────────┤
│                                      │
│  [사용자 입력] → [UI 위젯] → [로직 전송] │
│  [로직 결과] → [UI 위젯] → [화면 표시] │
│                                      │
└──────────────────────────────────────┘
```

---

# Phase 6: 메인 앱 통합

## 이 프롬프트의 역할
- 부품처럼 만들어진 모든 레이어(서비스, 리포지토리, UI)를 하나로 조립합니다.
- 앱의 생명주기 및 사용자 상태(세션)를 관리합니다.
- **생성된 파일 목록:** `app.py`

## 학습 목표
- `st.session_state`를 통한 휘발성 데이터 관리
- 사용자 액션(버튼 클릭, 히스토리 선택)에 따른 모드 전환 로직 이해
- 전체적인 애플리케이션 오케스트레이션(Orchestration) 능력 배양

## 이해를 위한 핵심 개념

### 6.1 st.session_state
웹 앱의 특성상 페이지가 리프레시될 때마다 변수들이 초기화되는데, `session_state`를 사용하면 현재 사용자가 보고 있는 모드(검색 모드/조회 모드)나 선택된 기록 등의 상태를 유지할 수 있습니다.

### 6.2 조건부 렌더링
사용자가 검색을 했는지, 아니면 과거 기록을 선택했는지에 따라 메인 화면의 내용을 다르게 보여주는 로직입니다.

## 주요 코드 인용

### app.py - 기록 조회 모드 전환
```python
# app.py:69-73
    if selected_key_sidebar and selected_key_sidebar != st.session_state.selected_key:
        st.session_state.selected_key = selected_key_sidebar
        st.session_state.current_mode = "history"
        st.session_state.last_result = repository.find_by_key(selected_key_sidebar)
        st.rerun()
```

**코드 설명:**
- `st.rerun()`: 상태가 변경되었을 때 즉시 화면을 다시 그려 변경된 내용을 반영합니다.

## 데이터 흐름에서의 역할

```
┌───────────────────────────────────────┐
│          Phase 6 데이터 흐름           │
├───────────────────────────────────────┤
│                                       │
│  [Sidebar Action] → [State Change]    │
│          → [Main Area Rerender]       │
│                                       │
└───────────────────────────────────────┘
```

---

# Phase 7: 에러 핸들링 강화 및 마무리

## 이 프롬프트의 역할
- 실사용자가 겪을 수 있는 예외 상황에 대한 안내를 강화하여 완성도를 높입니다.
- 설치 가이드(`README.md`)를 작성하고 최종 결과물을 검수합니다.
- **생성된 파일 목록:** `README.md`, 업데이트된 `settings.py`, `error_handler.py`, `app.py` 등

## 학습 목표
- 기술적인 에러(SDK 에러)를 사용자 중심의 안내 메시지로 변환하는 기법 마무리
- 가이드 문서 작성을 통한 프로젝트 인수인계 준비
- 전체 E2E(End-to-End) 흐름에 대한 최종 품질 검증

## 이해를 위한 핵심 개념

### 7.1 사용자 중심 UX (User-Centric)
에러 발생 시 단순한 영어 에러 코드를 보여주는 대신, "API 한도를 초과했습니다. 잠시 후 시도해주세요"와 같이 구체적인 해결 방법이 포함된 한글 메시지를 제공합니다.

### 7.2 프로젝트 배포 패키징
누구나 바로 실행해 볼 수 있도록 환경 구축 방법과 설정 단계를 문서화하여 배포 준비를 마칩니다.

## 주요 코드 인용

### config/settings.py - 누락 환경변수 가이드
```python
# config/settings.py:25-37
            error_msg = f"""
❌ 필수 환경변수 '{key}'가 설정되지 않았습니다.
...
API 키 발급 안내:
- Tavily API: https://tavily.com/ (검색 API)
- Google AI Studio: https://aistudio.google.com/ (Gemini 요약 API)
"""
```

**코드 설명:**
- 단순한 `KeyError` 대신, 어디에서 키를 발급받아야 하는지 링크를 제공함으로써 초보 사용자의 이탈을 방지합니다.

## 데이터 흐름에서의 역할

```
┌─────────────────────────────────────────┐
│            Phase 7 데이터 흐름           │
├─────────────────────────────────────────┤
│                                         │
│  [System Error] → [Custom Message]      │
│          → [Friendly UI Alert]          │
│                                         │
└─────────────────────────────────────────┘
```

---

# 전체 데이터 흐름

## 시나리오 1: 새로운 키워드 검색 및 요약

```
사용자 키워드 입력 ("인공지능 트렌드")
    │
    ▼ [input_handler.py]
앞뒤 공백 제거 및 길이 제한 (전처리)
    │
    ▼ [search_service.py]
Tavily API 호출 → 뉴스 기사 리스트 획득 (최신순 정렬)
    │
    ▼ [ai_service.py]
Gemini API 호출 → 뉴스 본문 요약 생성
    │
    ▼ [search_repository.py]
객체 생성 및 CSV 파일에 저장
    │
    ▼ [result_section.py]
화면에 AI 요약 정보 및 기사 목록 표시
```

## 시나리오 2: 과거 검색 기록 조회

```
사이드바 '검색 기록' selectbox 선택
    │
    ▼ [app.py]
선택된 Key를 세션에 저장하고 모드 전환 (history)
    │
    ▼ [search_repository.py]
CSV 파일 로드 → Key 기반 필터링 → SearchResult 객체 복구
    │
    ▼ [result_section.py]
저장된 과거의 AI 요약과 뉴스 기사들을 화면에 즉시 표시
```

## 폴더 구조 요약

```
TrendTracker/
├── config/           ← [Phase 1] 환경변수(API 키) 로드 및 싱글톤 관리
├── domain/           ← [Phase 2] 뉴스 및 검색 결과 데이터 구조 정의
├── services/         ← [Phase 3] Tavily 뉴스 검색 및 Gemini AI 요약 로직
├── repositories/     ← [Phase 4] 로컬 CSV 파일 저장 및 조회 로직
├── components/       ← [Phase 5] 검색창, 사이드바, 결과창 등 UI 조각들
├── utils/            ← [Phase 2, 7] 에러 핸들링, 입력 검증, 키 생성 유틸리티
├── data/             ← [Phase 1, 4] 검색 결과 데이터가 저장되는 실제 위치
└── app.py            ← [Phase 6] 전체 레이어를 조립하는 메인 어플리케이션
```

---

## 학습 체크리스트

### Phase 1
- [x] `.env` 설정 방식과 보안상의 이유를 설명할 수 있는가?
- [x] 프로젝트 레이어 구조(Config, Service, Repo 등)를 이해했는가?

### Phase 2
- [x] `dataclass`를 사용하여 객체를 정의했을 때의 장점을 아는가?
- [x] 복합적인 시계열 Key를 생성하는 로직을 이해했는가?

### Phase 3
- [x] 외부 API 연동 시 네트워크 타임아웃 및 재시도 로직의 필요성을 아는가?
- [x] `AppError`를 통해 에러를 통합 관리하는 구조를 이해했는가?

### Phase 4
- [x] Pandas를 사용하여 데이터를 저장하고 불러올 때의 인코딩 문제(BOM)를 해결할 수 있는가?
- [x] 리포지토리 패턴이 왜 테스트나 환경 변화에 유리한지 설명할 수 있는가?

### Phase 5 & 6
- [x] Streamlit의 세션 상태(`st.session_state`)가 웹 앱에서 어떤 역할을 하는지 이해했는가?
- [x] 대형 프로젝트에서 코드를 파일별로 분리(Modularity)하는 이유를 아는가?

### Phase 7
- [x] 개발자 전용 로그와 사용자용 에러 안내를 분리하여 처리할 수 있는가?
- [x] 프로젝트 인수인계를 위한 문서화(README.md)의 중요성을 이해했는가?
