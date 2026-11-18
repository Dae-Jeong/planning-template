# __PROJECT_NAME__ Decision Log

최종 수정: __DATE__

제품 범위, 정책, 비용, 일정, 운영 리스크, 고객 약속이 바뀌는 결정을 기록합니다.
상세 근거가 긴 결정은 [`templates/decision.md`](templates/decision.md) 형식으로 보완하고 여기에는 결론과 링크를 요약합니다.

## 현재 결론

- 문서 파이프라인은 `00-baseline → 10-decision → 20-spec → 30-work → 40-architecture → log` 단방향 전파 규칙을 따른다.
- 구현 착수 전 미결 결정은 아래 `OPEN-*`에 두고, 결정 전에 구현이 특정 가정에 조용히 묶이지 않게 유지한다.
- 에이전트의 세부 정책 위임 범위와 사람 전용 Red Line은 [`rules/policy-direction.md`](rules/policy-direction.md)가 소유한다.

## 결정 현황 (`DEC`)

| ID | 결정 | 결론 | Owner | Status |
| --- | --- | --- | --- | --- |
| __PROJECT_CODE__-DEC-001 | planning harness 도입 | Decision / Spec / Work / Baseline / Log 분리 및 `planning/` 정본 체계 채택 | owner | accepted |

## 남은 결정 (`OPEN`)

| ID | 결정 필요 항목 | 영향 문서 | Owner |
| --- | --- | --- | --- |
| __PROJECT_CODE__-OPEN-001 | 핵심 도메인/인증/배포 아키텍처 초기 결정 (프로젝트 착수 시 구체화) | `20-spec.md`, `30-work.md` | owner |

## 주요 리스크

| 리스크 | 대응 |
| --- | --- |
| 기획과 구현 간 drift | SPEC/WP 변경 시 `20-spec.md`, `30-work.md`, `log.md`를 같은 커밋 단위에서 갱신 |
| 미착수 WP 파일 과다 생성 | 로드맵은 `30-work.md` 표에 1줄로만 두고 `30-work/work-*.md`는 착수 시점에만 생성(JIT) |
| 테스트 통과를 완료로 오인 | `Log + DB 정합성 + FE 동작` 3종 증거와 `ready_for_qa` 멈춤 게이트 준수 |
