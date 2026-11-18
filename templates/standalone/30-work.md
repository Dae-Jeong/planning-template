# __PROJECT_NAME__ Work Board

최종 수정: __DATE__

<!-- IF_OBSIDIAN -->
> **Obsidian 오케스트레이션 연동 모드**: 활성 작업 할당, 세션 바인딩, 최종 인수 상태 정본은 `Obsidian/wiki/projects/__PROJECT_SLUG__/tasks/`가 소유합니다. 이 파일은 **제품 WP 카탈로그 · Spec Coverage · Release Gate · 로드맵 탐색 입력**으로만 사용하며 독립적인 진행 상태를 이중으로 관리하지 않습니다.
<!-- END_IF_OBSIDIAN -->
<!-- IF_NOT_OBSIDIAN -->
> __PROJECT_NAME__(`__PROJECT_CODE__`)의 구현 · QA · 릴리스 추적 보드입니다. 상세 작업 문서는 착수 시점에만 `30-work/` 아래 `1 파일 = 1 WP`로 생성합니다.
<!-- END_IF_NOT_OBSIDIAN -->

허용 Status: `draft`, `in_dev`, `ready_for_qa`, `qa_blocked`, `ready_for_release`, `done`, `cancelled`, `superseded`

## Status Board

| Phase | WP | Covers SPEC | Status | Owner | Blocker | 다음 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | [__PROJECT_CODE__-WP-001 Bootstrap Harness](30-work/work-001-bootstrap-harness.md) | __PROJECT_CODE__-SPEC-001 | done | owner | - | 도메인 Decision 확정 및 초기 기능 WP 착수 |

## WP List

| ID | 제목 | Status | Owner | 파일 | Covers SPEC |
| --- | --- | --- | --- | --- | --- |
| __PROJECT_CODE__-WP-001 | Bootstrap Harness | done | owner | [work-001-bootstrap-harness.md](30-work/work-001-bootstrap-harness.md) | __PROJECT_CODE__-SPEC-001 |

## 신규 기능 로드맵 (착수 전까지는 1줄만 유지)

> 아직 착수하지 않은 기능은 미리 `work-NNN-*.md` 파일을 만들지 말고 아래 표에만 걸어둡니다.

| WP | 제목 | Context | 크기 | 의존성 | Stage |
| --- | --- | --- | --- | --- | --- |
| __PROJECT_CODE__-WP-002 | 핵심 도메인 1차 골격 (예시 — 착수 시 파일 생성) | core | M | __PROJECT_CODE__-OPEN-001 | 1 |

## Spec Coverage

| Spec ID | Covering WP | 상태 | 비고 |
| --- | --- | --- | --- |
| __PROJECT_CODE__-SPEC-001 | __PROJECT_CODE__-WP-001 | active | 기본 파이프라인 · 규칙 · 템플릿 세팅 완료 |

## Open Decisions Mirror

> 정본은 [`10-decision.md`](10-decision.md)입니다. 여기에만 단독 결정을 추가하지 않습니다.

| ID | 결정 필요 항목 | Source |
| --- | --- | --- |
| __PROJECT_CODE__-OPEN-001 | 핵심 도메인/인증/배포 아키텍처 초기 결정 | [10-decision.md](10-decision.md) |
