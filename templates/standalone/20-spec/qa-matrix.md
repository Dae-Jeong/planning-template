# __PROJECT_NAME__ QA Scenario Matrix

최종 수정: __DATE__

`20-spec/`의 Acceptance Criteria를 실행 가능한 QA 시나리오와 증거 요구사항으로 내린 기준선입니다.
상세 판정 규칙은 [`../rules/quality-evidence-harness.md`](../rules/quality-evidence-harness.md)를, 점검 축은 [`../rules/policy-qa-checklist.md`](../rules/policy-qa-checklist.md)를 따릅니다.

## 1. 테스트 가능성 라벨

| Label | 의미 |
| --- | --- |
| `qa-alone` | 화면·문서만으로 QA 직접 검증 가능 |
| `dev-setup` | 시드 데이터, mock, 다중 계정/컨테이너 setup 필요 |
| `external-schedule` | 외부 연동, 배치 주기, 장기 관찰 등 별도 일정 필요 |
| `alternative-needed` | 직접 재현 불가 → replay fixture · forced state · log 증거 필요 |
| `design-review` | 문구 · 대비 · 반응형 · 가독성 검수 중심 |

## 2. Scenario Matrix

| ID | Release | Lens | Surface | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| QA-001 | bootstrap | Process | Planning | 기획/정책 변경 발생 | `document-pipeline.md` 라우팅 적용 | 단일 소유 정본만 갱신되고 체크 스크립트 통과 | `qa-alone`: `check_planning` 통과 + git diff |

## 3. Release Gate 승격 규칙

- 개발 단계에서는 mock/forced state evidence를 허용합니다.
- Release Gate에서는 핵심 정책 REQ(`인증`, `권한`, `데이터 정합성`, `부작용 차단`)를 실제 API/DB/Log/E2E 근거로 승격합니다.
