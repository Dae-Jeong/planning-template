# __PROJECT_CODE__-WP-NNN QA Sweep (기능별 → 통합 → Adversarial)

누적된 기능 WP 묶음에 대해 3단계(기능별 · 통합 E2E · Adversarial 공격표면) QA를 일괄 수행하고, 발견된 실제 결함만 후속 수정 WP로 회수합니다.

## 메타

- Status: draft
- Owner: Verifier / Decision Owner (GUI 시각)
- Covers: (대상 WP 목록)
- Dependencies:

## QA 대상 목록

| 기능 | WP | 핵심 검증 포인트 |
| --- | --- | --- |
|  |  |  |

## Stage 1: 기능별 QA

### 1-A. 에이전트 자동/API/DB/Playwright 검증

-

### 1-B. 사람 GUI 시각 · OS 연동 손검증

-

## Stage 2: 통합 시나리오 QA (End-to-End)

실제 사용자 흐름 1~2개로 여러 기능을 묶어 검증합니다 (배포 이미지/볼륨/환경변수/URL 누락 탐지):

1.
2.
3.

## Stage 3: Adversarial 공격표면 점검

- 권한 우회 (타 사용자/비멤버 접근, 삭제 권한 누락)
- 입력 정규화 (제어문자, zero-width, RTL/bidi, 초장문 DoS)
- 동시성 / 멱등성 / 재시도 중복
- 미존재 참조 / 파일 위장(magic bytes, MIME) / 경로 탈출

### 분류 결과 (거짓 양성 제거 후 확정본만 기록)

| # | 결함 | Severity | 코드 근거 (`Code`) | 조치 방향 (즉시 Fix WP / 보류) |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Release Gate

- [ ] Stage 1 자동/수동 항목 구분 및 실행 완료
- [ ] Stage 2 통합 시나리오 Log/DB/FE 확인 완료
- [ ] Stage 3 Adversarial 실위험 항목만 후속 Fix WP 또는 백로그로 분리 완료
