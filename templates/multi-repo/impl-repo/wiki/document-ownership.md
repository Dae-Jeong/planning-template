# __PROJECT_NAME__ Document Ownership

최종 수정: __DATE__

제품 기획과 정책은 중앙 기획 저장소(`__CENTRAL_REF__`)가 소유합니다.
이 구현 저장소는 실제 코드, 운영, 릴리스, 테스트·런타임 검증 증거를 소유하며 `wiki/`는 두 저장소 사이의 위치와 읽는 순서를 안내하는 라우터입니다.

## 경계 표

| 영역 | 기준 소유자 | 포함 내용 |
| --- | --- | --- |
| 제품 기획 · 범위 | 중앙 `__CENTRAL_REF__/planning/` | 제품 정의, 범위(In/Out), 결정(`DEC/OPEN`) |
| 사용자 정책 · SPEC | 중앙 `__CENTRAL_REF__/planning/20-spec/` | UX 계약, API 공개 계약, Acceptance Criteria |
| Work Package 기획 | 중앙 `__CENTRAL_REF__/planning/30-work/` | WP 범위 및 정책 QA 기준 |
| 코드 구현 · 스키마 | 이 구현 저장소 | 소스 코드, DB migration, 단위/통합 테스트 |
| 실행 추적 · 1차 증거 | 이 저장소 [`../tasks/README.md`](../tasks/README.md) | 중앙 WP ID 연결, `Log / DB / FE` 증거 |
| 문서 라우팅 | 이 저장소 [`_map.md`](_map.md) · [`rules/document-pipeline.md`](rules/document-pipeline.md) | 탐색 경로 및 소유권 경계 (원문 복제 금지) |

## 충돌 처리 규칙

1. 기획 · 정책 · UX 계약이 충돌하면 중앙 `__CENTRAL_REF__/planning/`을 우선합니다.
2. 현재 코드 구현 상태가 문서와 다르면 이 저장소의 실제 코드와 migration을 우선 확인합니다.
3. 중앙 SPEC과 현재 구현이 어긋나면 조용히 덮어쓰지 않고 `spec drift`로 기록한 뒤 중앙 계약 수정인지 구현 버그 수정인지 분리합니다.
4. `wiki/`에 중앙 SPEC/정책 전문을 복제하지 않고 경로와 WP ID만 링크합니다.
