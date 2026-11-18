# Quality Evidence Harness (`REQ-*` 판정 레이어)

이 문서는 `mediness`의 **Quality Evidence Harness**를 범용 프로젝트에 이식한 규약입니다.
핵심 철학은 단 한 줄입니다: **실행 성공(`exit 0`, HTTP `200`)과 정책 품질 통과(`PASS`)를 분리하고, 근거가 비면 `PASS`가 아니라 `UNKNOWN`으로 남긴다.**

---

## 1. 실행 파이프라인 vs 판정 레이어

```text
SPEC / WP
  └─▶ REQ-* (보장해야 하는 정책 요구사항)
        └─▶ Evidence Plan (어떤 FE / DB / Log / AI 증거로 닫을 것인가)
              └─▶ 실행 (Unit / Integration / E2E / Manual)
                    ├─ 증거 모두 일치 ────────▶ PASS ──▶ 자동화 승격 검토
                    ├─ 정책과 1개 이상 충돌 ───▶ FAIL ──▶ Bug/Fix WP 생성
                    └─ 필요 증거 미수집/제약 ──▶ UNKNOWN ─▶ 계측 보강 후 재실행
```

---

## 2. `REQ-*` 분해 규칙

`REQ-*`는 클릭 절차가 아니라 **제품이 반드시 지켜야 하는 정책 불변식**입니다.

- **좋은 REQ**:
  - `REQ-001`: 주문 생성 요청이 PG 승인 전 실패하면 재고와 포인트는 차감되지 않아야 한다.
  - `REQ-002`: 비인증 또는 타 지점 사용자가 관리자 API를 호출하면 데이터를 반환하지 않고 권한 오류(`403`)를 반환해야 한다.
  - `REQ-003`: 임시저장 수정 시에는 외부 발행/웹훅 요청이 발생하지 않아야 한다.
- **나쁜 REQ (작성 금지)**:
  - "저장 버튼을 누른다" (UI 절차)
  - "API가 200을 반환한다" (상태 코드만으로는 정합성 불명)
  - "정상 동작한다 / 적절히 표시한다" (판정 불가)

모든 `REQ-*`는 반드시 `policy_source` (`20-spec/...` 또는 `30-work/...`)를 링크합니다.

---

## 3. Evidence Plan YAML 스키마

주요 기능 WP나 `20-spec/qa-matrix.md`는 아래 필드를 기준으로 검증 계약을 명시합니다:

```yaml
req_id: __PROJECT_CODE__-REQ-001
policy_source: planning/20-spec/spec-002-core.md#ac-001
tc_id: TC-CORE-001
required_evidence:
  - fe        # 화면 상태, 문구, Network negative 포함
  - db        # 실제 저장 row, 상태 전이, 중복/음수 방지
  - log       # request_id 기준 완료 로그 및 에러 부재
pass_criteria:
  - 화면에 완료 상태와 생성 ID가 표시된다.
  - DB order row status가 CONFIRMED이고 inventory가 1 감소한다.
  - 백엔드 로그에 동일 request_id의 완료 로그가 남고 ERROR 로그가 0건이다.
fail_criteria:
  - 화면엔 성공 메시지가 떴으나 DB row가 없거나 백엔드 500 로그가 발생한다.
unknown_criteria:
  - DB 또는 백엔드 로그에 접근하지 못해 화면과 저장 상태의 일치를 검증할 수 없다.
automation_candidate: true
```

---

## 4. 판정 기준 (`PASS / FAIL / UNKNOWN`)

| 판정 | 정의 | 예시 |
| --- | --- | --- |
| **`PASS`** | 요구된 evidence 축(`FE / DB / Log` 등)이 모두 수집됐고, 정책과 일치함 | FE 성공 + DB row 일치 + Log 200/completed |
| **`FAIL`** | 수집된 evidence 중 하나 이상이 정책 계약과 충돌함 | FE는 성공 토스트 노출, DB에는 미저장 또는 에러 로그 |
| **`UNKNOWN`** | 필수 evidence 중 하나 이상을 수집하지 못해 정합성을 닫지 못함 | FE/Log는 봤으나 DB 조회 권한이 없어 저장 상태 미확인 |

> **LLM / AI 기능 특별 규칙**: AI 생성·분류 기능은 **"에러 없이 응답이 생성됨"**과 **"정책상 품질 기준을 만족함"**을 분리합니다. 또한 **LLM Judge 단독 점수로 `PASS`를 확정하지 않고**, 사람이 보정(calibration)한 루브릭 또는 결정론적 가드 검사를 함께 통과해야 합니다.

---

## 5. 자동화 승격 & Release Gate Report

### 자동화 승격 대상

모든 테스트를 100% E2E로 만들지 않고, 아래 4가지에 해당하는 REQ만 우선 자동화(`Contract / Integration / Smoke E2E`)로 승격합니다:
1. 릴리스마다 절대 깨지면 안 되는 핵심 정책(인증·권한·결제/재고)
2. 이미 한 번 이상 회귀했던 버그
3. 화면만으로 검증이 안 되는 DB·할당량·부작용(`side effect`) 케이스
4. 회귀 데이터셋으로 고정 가능한 AI 출력 가드/형식 검사

### Release Gate Report 필수 요약 6항목

배포 전 `30-work.md` 또는 릴리스 기록에는 "테스트 N개 통과" 대신 다음을 요약합니다:
1. `PASS` 완료된 `REQ-*` 목록과 증거 경로
2. `FAIL` 이슈 및 수정/보류 여부
3. `UNKNOWN`으로 남은 리스크와 허용/차단 판단
4. 이번에 자동화 테스트로 승격된 `REQ-*`
5. 수동 QA(GUI 시각·외부 연동)로 유지할 항목
6. Staging / Prod 배포 직후 추가로 닫을 smoke 확인 항목
