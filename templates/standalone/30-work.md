# __PROJECT_NAME__ Work Board

최종 수정: __DATE__

<!-- IF_OBSIDIAN -->
> **Obsidian 오케스트레이션 연동 모드**: 활성 작업 할당, 세션 바인딩, 최종 인수 상태 정본은 `Obsidian/wiki/projects/__PROJECT_SLUG__/tasks/`가 소유합니다. 아래 `AUTO` 영역은 `30-work/work-*.md`, `20-spec.md`, `10-decision.md`로부터 `sync_planning.py`가 자동 생성합니다(수동 편집 금지).
<!-- END_IF_OBSIDIAN -->
<!-- IF_NOT_OBSIDIAN -->
> 각 WP의 상태·메타 정본은 `30-work/work-NNN-*.md` 파일 1곳만 수정합니다. 아래 `AUTO` 영역 4곳은 `sync_planning.py`가 자동 렌더링하므로 직접 손으로 고치지 않습니다.
<!-- END_IF_NOT_OBSIDIAN -->

허용 Status: `draft`, `in_dev`, `qa_blocked`, `agent_verified`, `awaiting_human`, `done`, `cancelled`, `superseded`

## Human Sign-off Queue (`awaiting_human` 전용 슬림 큐)

> 사람이 시각·실단말·비즈니스 관점으로 확인할 항목만 자동 집결됩니다. 확인 후 `sync_planning.py --target <repo> --accept <WP-ID>`로 닫습니다.

<!-- AUTO:HUMAN_QUEUE:START -->
_현재 사람 확인 대기(`awaiting_human`) 항목이 없습니다._
<!-- AUTO:HUMAN_QUEUE:END -->

## WP Board (자동 집계)

<!-- AUTO:WP_BOARD:START -->
_동기화 대기 중_
<!-- AUTO:WP_BOARD:END -->

## 신규 기능 로드맵 (착수 전 1줄 대기열 — 수동 관리)

> 아직 착수하지 않은 기능은 `work-NNN-*.md` 파일을 미리 만들지 말고 아래 표에만 걸어둡니다. 착수하여 `30-work/work-NNN-*.md`를 생성하면 이 표에서 해당 행을 제거합니다.

| WP | 제목 | Context | 크기 | 의존성 | Stage |
| --- | --- | --- | --- | --- | --- |
| __PROJECT_CODE__-WP-002 | 핵심 도메인 1차 골격 (착수 시 파일 생성 후 이 행 제거) | core | M | - | 1 |

## Spec Coverage (자동 집계)

<!-- AUTO:SPEC_COVERAGE:START -->
_동기화 대기 중_
<!-- AUTO:SPEC_COVERAGE:END -->

## Open Decisions Mirror (자동 미러링)

> 정본은 [`10-decision.md`](10-decision.md)입니다. 여기에 직접 행을 추가하지 않습니다.

<!-- AUTO:OPEN_MIRROR:START -->
_동기화 대기 중_
<!-- AUTO:OPEN_MIRROR:END -->
