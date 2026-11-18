# __PROJECT_NAME__ Planning

최종 수정: __DATE__

__PROJECT_NAME__(`__PROJECT_CODE__`)의 제품 기획·의사결정·실행 추적·품질 근거 source of truth입니다.

## 제품 개요

- 핵심 목표: <!-- 이 서비스가 해결하는 핵심 문제와 v1 범위를 2~3줄로 기록하세요 -->
- Out of Scope (v1 제외): <!-- v1에 넣지 않을 항목을 먼저 고정해 범위 팽창을 막습니다 -->

## 먼저 볼 문서

| 역할 | 시작 경로 |
| --- | --- |
| 새 작업자 / AI Agent | [20-spec.md](20-spec.md) → [30-work.md](30-work.md) |
| Decision Owner | [00-baseline/](00-baseline/) → [10-decision.md](10-decision.md) |
| Product / PM | [20-spec.md](20-spec.md) → [20-spec/](20-spec/) → [rules/policy-direction.md](rules/policy-direction.md) |
| Backend / Frontend | [30-work.md](30-work.md) → [30-work/](30-work/) → [40-architecture/](40-architecture/README.md) |
<!-- IF_API -->| API 계약 (FE/BE 공유) | [20-spec/api/](20-spec/api/README.md) |<!-- END_IF_API -->
<!-- IF_QA -->| QA / 검증 | [20-spec/qa-matrix.md](20-spec/qa-matrix.md) → [rules/policy-qa-checklist.md](rules/policy-qa-checklist.md) → [rules/quality-evidence-harness.md](rules/quality-evidence-harness.md) |<!-- END_IF_QA -->
<!-- IF_NO_QA -->| QA / 검증 | [rules/policy-qa-checklist.md](rules/policy-qa-checklist.md) → [rules/quality-evidence-harness.md](rules/quality-evidence-harness.md) |<!-- END_IF_NO_QA -->
| 변경 이력 · 리뷰 기준선 | [log.md](log.md) |

## 폴더 구조

```text
planning/
├── 00-baseline/                 # 검토용 프로토타입 · 정찰 · 리서치 스냅샷
├── 10-decision.md               # OPEN(미결) · DEC(확정) 의사결정 원장
├── 20-spec.md                   # SPEC 전체 맵 · 용어 · DDD 경계
├── 20-spec/                     # 사용자-facing 기능/화면/API 계약
├── 30-work.md                   # WP 보드 · 로드맵 · Spec Coverage · Release Gate
├── 30-work/                     # 착수 시점에만 생성(JIT)하는 실행 WP
├── 40-architecture/             # 2개+ WP 공유 불변식 · 상태 머신 승격본
├── 90-archive/                  # 버전 cut 스냅샷 (현재 문서는 최신본만 유지)
├── log.md                       # 번호 매긴 시간순 작업·검증·리뷰 회수 기록
├── rules/                       # 파이프라인 · 위임 방향 · 정책 QA · 품질 하네스
└── templates/                   # 신규 DEC / SPEC / WP / QA Sweep 작성 템플릿
```

## 소유권 경계

- 제품 범위 · 비용 · 일정 · 정책 · 고객 약속: [`10-decision.md`](10-decision.md)
- 사용자-facing UX · 정책 · Given/When/Then AC: [`20-spec/`](20-spec.md)
<!-- IF_API -->- FE/BE 공유 HTTP Request/Response · RFC 9457 Error 계약: [`20-spec/api/`](20-spec/api/README.md)<!-- END_IF_API -->
- 구현 순서 · 도메인 초안 · 검증 계획 · Release Gate: [`30-work/`](30-work.md)
- 장기 domain invariant · 공통 상태 머신: [`40-architecture/`](40-architecture/README.md)
- 실제 DB 스키마 · 마이그레이션 · 코드 구현: 제품 소스 코드(`src/` 등)
<!-- IF_OBSIDIAN -->- 오케스트레이션 작업 할당 · 활성 세션 · 최종 수락 상태: `Obsidian/wiki/projects/__PROJECT_SLUG__/tasks/`<!-- END_IF_OBSIDIAN -->
