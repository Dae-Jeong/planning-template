# __PROJECT_NAME__ Quality Evidence Harness (`REQ-*`)

최종 수정: __DATE__

실행 성공(`exit 0`, HTTP `200`)과 정책 품질 통과(`PASS`)를 분리해 판정하는 공통 QA 운영 규약입니다.

## 1. 핵심 원칙

1. **정책 기준 판정**: QA evidence는 구현 편의가 아니라 `10-decision` / `20-spec` 요구사항을 기준으로 요구합니다.
2. **실행 성공 ≠ 품질 통과**: HTTP `200`이나 UI 토스트만 보고 `PASS` 처리하지 않습니다.
3. **근거 부재 = `UNKNOWN`**: 필요한 evidence를 수집하지 못했으면 `PASS`가 아니라 **`UNKNOWN`** 으로 남깁니다.
4. **반복·치명 결함의 자동화 승격**: 릴리스 핵심 정책, 1회 이상 회귀 결함, DB·부작용 검증 항목은 자동화 테스트(Contract/Integration/Smoke)로 승격합니다.
5. **AI/LLM 기능 분리**: AI 출력은 "응답 생성됨"과 "품질 기준 충족"을 분리하고 LLM Judge 단독 점수로 `PASS`를 확정하지 않습니다.

## 2. `REQ-*` 작성 기준

- **좋은 REQ**: "실패한 생성/결제 요청은 사용자 할당량·재고를 차감하지 않는다" (정책 불변식)
- **나쁜 REQ**: "버튼을 누른다", "API가 200을 반환한다", "적절히 표시된다"

## 3. 1차 Evidence 3축 (+ Network negative / AI quality)

| 축 | 확인 내용 | 예시 |
| --- | --- | --- |
| **Log** | 기대 처리 흐름이 찍히고 예상치 못한 error/warn이 없는가 | `request_id` 완료 로그, 스케줄러 실행, 500 부재 |
| **DB 정합성** | 화면/API 결과와 실제 저장 데이터가 일치하는가 | row 생성/상태 전이, tombstone, 멱등성 unique 중복 0 |
| **FE 동작 (+Network)** | 실제 화면 흐름과 비요청(Network negative)이 맞는가 | 화면 전환·새로고침 잔존, 저장만으로 발행 API 미호출 |
| **AI Quality** *(해당 시)* | 정책 가드 + 보정된 품질 루브릭 기준을 통과했는가 | 금지 표현 0건, 형식/사실 일치, 사람 샘플 검수 |

## 4. 판정 기준 (`PASS / FAIL / UNKNOWN`)

| 상태 | 기준 | 후속 조치 |
| --- | --- | --- |
| **`PASS`** | 요구된 모든 evidence 축이 수집됐고 정책과 일치함 | 자동화 승격 대상 검토 후 Release Gate 반영 |
| **`FAIL`** | 수집된 evidence 중 하나 이상이 정책과 충돌함 | 즉시 수정 또는 Bugfix WP 등록 후 재검증 |
| **`UNKNOWN`** | 필수 evidence 중 하나 이상을 환경/권한 제약으로 미수집 | 계측·접근 보강 후 재실행, 미해소 시 잔여 리스크 명시 |

## 5. 정기 리뷰 & QA Sweep 연결

- **정기 디자인 패턴 리뷰**: Phase 완료 또는 **누적 5개 WP마다** `git diff <직전기준커밋>...HEAD` 패턴 리뷰 → 채택분만 신규 WP 등록 → `log.md`에 새 기준 커밋 기록.
- **3단계 QA Sweep (`templates/qa-sweep.md`)**: 기능 묶음 완료 시 ① 기능별 QA → ② 통합 E2E 시나리오 → ③ Adversarial 공격표면 점검으로 갭을 한 번에 털어냅니다.
