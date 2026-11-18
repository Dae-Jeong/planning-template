# __PROJECT_NAME__ Agent Guide (Implementation Repo)

<!-- IF_OBSIDIAN -->
공통 작업 탐색·기록·인수는 글로벌 `AGENTS.md`가 연결하는 중앙 작업 규약(`Obsidian/wiki/notes/agents/work-management-policy.md`)을 따릅니다.

---
<!-- END_IF_OBSIDIAN -->
## 1. 문서 소유권 & 읽는 순서

- 제품 기획 · 결정 · 정책 · UX/API 계약 단일 진실(SoT): 중앙 기획 저장소(`__CENTRAL_REF__/planning/`)
- 이 저장소의 소유권 경계 및 문서 라우팅: `wiki/README.md` → `wiki/_map.md` → `wiki/document-ownership.md`
- 구현 작업 및 1차 검증 증거 추적: `tasks/README.md` (중앙 `__PROJECT_CODE__-WP-*` 연결)

## 2. 충돌 및 Spec Drift 처리

1. 기획·정책 충돌 시 중앙 기획 저장소(`__CENTRAL_REF__/planning/`)를 우선합니다.
2. 구현 사실 충돌 시 이 저장소의 실제 코드와 마이그레이션을 우선합니다.
3. 중앙 SPEC과 현재 구현이 다르면 조용히 덮어쓰지 않고 `spec drift`로 기록해 제품 변경인지 구현 버그인지 분리합니다.
4. 구현 repo `wiki/`에는 중앙 SPEC 전문이나 아카이브를 복제하지 않고 경로와 WP ID만 링크합니다.
