# __PROJECT_NAME__ Multi-Repo Boundary (중앙 기획 저장소)

최종 수정: __DATE__

이 저장소는 __PROJECT_NAME__(`__PROJECT_CODE__`)의 **제품 기획 · 정책 · SPEC · WP · 아카이빙의 유일한 정본**입니다.
구현 코드, 실행 diff, 로컬 테스트 raw 로그는 각 구현 저장소(`be`, `fe`, `ai`)가 소유합니다.

## 저장소 간 소유권

| 위치 | 소유 내용 | 두지 않는 내용 |
| --- | --- | --- |
| 중앙 `planning/` (이 저장소) | `10-decision`, `20-spec`, `30-work` WP, `90-archive` | 코드 diff, DB 스키마 전문, raw 로그 |
| 구현 저장소 (`wiki/`, `docs/`, `tasks/`) | 코드 인접 아키텍처, `tasks/` 실행 근거, `docs/` 운영·릴리스, `wiki/` 라우터 | 제품 기획/정책 복제본, 장기 아카이브 |

## 충돌 & Spec Drift 처리

1. 기획·UX·정책 충돌 시 **이 중앙 저장소(`planning/`)를 우선**합니다.
2. 현재 코드 구현 사실이 문서와 다르면 `spec drift`로 기록하고, 제품 계약을 바꿀지 코드 버그를 고칠지 분리합니다.
3. 구현 저장소가 자체 판단으로 제품 계약을 변경·확정하지 않습니다.
