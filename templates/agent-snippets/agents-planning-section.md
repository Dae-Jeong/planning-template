# __PROJECT_NAME__ Agent Guide

<!-- IF_OBSIDIAN -->
공통 작업 탐색·기록·인수는 글로벌 `AGENTS.md`가 연결하는 중앙 작업 규약(`Obsidian/wiki/notes/agents/work-management-policy.md`)을 따릅니다. 활성 작업 할당·인계 정본은 `Obsidian/wiki/projects/__PROJECT_SLUG__/tasks/`에 둡니다.

---
<!-- END_IF_OBSIDIAN -->
## 1. 읽는 순서 & Source of Truth 경계

| 영역 | 먼저 읽을 문서 | 소유 책임 |
| --- | --- | --- |
| 기획 / 결정 / 스펙 / WP | `planning/README.md`, `planning/20-spec.md`, `planning/30-work.md` | 제품 범위, 결정(`DEC/OPEN`), UX/API 계약, `REQ-*` QA 계획, 릴리스 게이트 |
| 문서 생성 / 변경 위치 판단 | `planning/rules/document-pipeline.md` | 변경 전파 경로 및 4층 DDD 소유권 경계 |
| 정책 위임 & Red Line | `planning/rules/policy-direction.md` | 에이전트 자율 결정 범위 vs 사람 전용 6대 금지선 |
| QA 체크 & 품질 하네스 | `planning/rules/policy-qa-checklist.md`, `planning/rules/quality-evidence-harness.md` | `REQ-*` 기반 `PASS / FAIL / UNKNOWN` 판정 |

- **제품 정책이나 UX 계약은 `planning/`에서 시작합니다.** 구현 중 계약이 바뀌면 코드에 숨기지 말고 `planning/` 정본으로 환류합니다.
- **Anti-Bloat JIT**: 미착수 WP는 `planning/30-work.md` 로드맵 표에 1줄로만 두고, 상세 `work-NNN-*.md` 파일은 착수 시점에만 생성합니다.

---

## 2. 운용 루프 & 역할 게이트

1. **2커밋 실행 사이클**: WP 착수 시 `planning/30-work/work-NNN-*.md` 계획을 먼저 고정하고, 구현·검증 후 결과/증거와 `30-work.md`·`planning/log.md`를 함께 회수합니다.
2. **`ready_for_qa` 멈춤 규칙**: 에이전트는 구현과 자동 테스트가 끝났더라도 실기동·GUI·사람 최종 확인이 남아 있으면 상태를 임의로 `done`으로 올리지 않고 `ready_for_qa`에서 멈춥니다.
3. **6대 Red Line (사람 승인 전용)**: 아래 항목은 `10-decision.md`의 `OPEN` 또는 질문으로 남기며 에이전트가 단독 확정하지 않습니다:
   - v1 Scope 기능 추가/삭제 · 인증/보안 구조 변경 · 데이터 영구삭제/보존기한/백업 정책 · 외부 노출/공개 가입 · 비용 발생 인프라/외부 API · 미결 `OPEN-*` 확정
4. **정기 디자인 패턴 리뷰 브레이크**: Phase 완료 시 또는 누적 **5개 WP**마다 직전 기준 커밋 이후 `git diff <기준>...HEAD`의 DDD 경계/레이어/과잉 추상화를 점검하고 `planning/log.md`에 다음 기준 커밋을 기록합니다.
5. **무결성 점검**: 문서/WP 변경 후 `planning-template`의 `check_planning.py`로 링크 · ID 중복 · `done` 게이트 정합성을 확인합니다.

---

## 3. 성공 판단 1차 증거 & 라벨

Build · Typecheck · Unit Test 통과는 전제일 뿐 완료 증거가 아닙니다. 완료/QA 보고는 근거 출처(`Source`, `Code`, `Tool`, `Inference`, `Unknown`)를 구분하고 아래 3종 1차 증거를 확인합니다:

- **Log**: 기대한 처리 흐름이 구조화 로그에 남고 예상치 못한 에러/경고가 없음
- **DB 데이터 정합성**: 실제 저장 row, 상태 전이, 멱등성 중복 0건이 DB와 일치함
- **FE 기능 동작 (+ Network negative)**: 실제 화면 동작과 함께, 발생하지 말아야 할 요청이 실제로 전송되지 않음을 확인함
