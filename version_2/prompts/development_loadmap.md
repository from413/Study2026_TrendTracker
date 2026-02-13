학습과 확장에 추천되는 방향에서 벗어나 제어흐름이 망가진다고 판단되면
해당 요구사항은 반영하지말고 나머지 작업만 진행해줘.(우선순위가 낮은 이유와 함께 답변 로드맵에 설명 추가)

## ✅ 최근 업데이트 (Recent Updates)
1. **아이콘 텍스트 누출(`_arrow_right`, `keyboard_arrow_right`) 대응**:
    - CSS `stIconMaterial` 속성을 타겟팅하여 Material Symbols 텍스트가 노출되는 현상 차단.
    - 리포트된 `st-emotion-cache-1c9yjad` 및 `exvv1vr0` 클래스에 대한 물리적 제거 스타일 적용 완료.
    - 현재 '사용방법', '데이터관리' 및 뉴스 목록 확장기의 시각적 노이즈 제거 완료.
2. **뉴스 요약 및 유튜브 통합**:
    - 뉴스 요약, 감성 분석, 유튜브 검색 결과 병렬 렌더링 구현 완료.

## 🏗️ 현재 시스템 계층 구조 (System Hierarchy)
- **UI (Components)**: `app.py`, `sidebar.py`, `result_section.py`, `youtube_section.py`
- **Business Logic (Services)**: `search_service.py`, `ai_service.py`
- **Data (Domain/Repo)**: `news_article.py`, `search_repository.py`

## 🚀 향후 진행 계획 (Future Roadmap)

### Phase 1: UI 안정성 및 아이콘 고도화 (진행 중)
* **목표**: `_arrow_right` 텍스트 누출 문제를 원천 차단하기 위해 스트림릿 기본 아이콘 대신 사용자 정의 아이콘(HTML/SVG) 삽입 실효성 검증.
* **작업**: 사이드바 버튼 및 뉴스 목록 확장기에 개별 아이콘 적용 및 비교.

### Phase 2: 데이터 심층성 확보 (YouTube & News)
* **목표**: 단순 검색결과 나열을 넘어 데이터의 가치가 높임.
* **작업**: 
    - 유튜브 채널명, 조회수 등 추가 메타데이터 표시 시도.
    - 뉴스 전문의 핵심 포인트 추출 강화.

### Phase 3: 사용자 연결성 강화 (Notification)
* **목표**: 실시간성 테마에 맞춰 알림 기능 추가.
* **작업**: 
    - 브라우저 알림(Web Notification) 또는 앱 내 토스트 알림을 통한 트렌드 변화 감지 알림.

---
## 🚀 [propose] 단계별 확장 제안
* 단순한 UI 장식보다는 **데이터의 깊이(YouTube)**와 **사용자 연결성(알림)** 기능에 집중하여 시스템의 가치와 견고함을 동시에 확보합니다.
