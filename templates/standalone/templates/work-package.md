# __PROJECT_CODE__-WP-NNN <WP 제목>

<이 WP가 무엇을 구현하고 어떤 근거로 닫히는지 1~2줄로 설명합니다.>

## 메타

- Phase: 1
- Status: draft
- Owner:
- Covers SPEC: __PROJECT_CODE__-SPEC-NNN
- Related Decision: __PROJECT_CODE__-DEC-NNN
- Dependencies: -
- Blocker: -
- Human Check: none
- Reusable Insight: none

> `Human Check` 작성 규칙: 순수 백엔드/DB/자동화 테스트로 검증이 완결되면 `none`으로 두고 검증 후 `Status: agent_verified`로 전환합니다. 사람 눈(시각 레이아웃·실단말·외부 알림 등) 확인이 필요하면 확인할 내용을 1줄로 구체적으로 적고 `Status: awaiting_human`으로 전환합니다.

## Scope

### In

-

### Out

-

## Code Surface

- FE:
- BE:
- Infra:
- Planning:

## Domain / Contract

- Aggregate / Entity 초안:
- 상태 전이 / Invariant:
- 락 / 멱등성 / 트랜잭션 경계:
- Migration 필요 여부:
- SPEC / API baseline 환류 필요 사항:

## Execution Plan

1.
2.
3.

## Test / QA Plan

- Unit / Contract:
- Integration (DB / Container):
- Browser / Network (+ Network negative):
- Infra / Deploy check:

## 요구사항 대비 완성도 매트릭스 (`REQ-*`)

| REQ-ID | 내용 | 판정 | 1차 증거 (`Log / DB / FE`) | 누락/UNKNOWN 사유 |
| --- | --- | --- | --- | --- |
| __PROJECT_CODE__-REQ-001 |  | UNKNOWN |  | 미실행 |

## Release Gate

- [ ] 연결된 SPEC / Decision 최신화 (해소된 `OPEN-*` 잔존 없음)
- [ ] Log / DB 정합성 / FE 동작(`Tool` 근거) 확인
- [ ] Residual risk / Unknown 분리 기록
- [ ] Decision Owner / Human Check 최종 확인 (`sync_planning.py --accept` 또는 `--accept-verified` 시 자동 체크)

## Residual Risk / Verification Log

- Verification Date:
- Remaining Limits:
