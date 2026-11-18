# __PROJECT_CODE__-SPEC-001 프로젝트 Planning Harness

__PROJECT_NAME__의 문서 소유권, 변경 전파 경로, 자동 보드 동기화, 역할 위임 및 2트랙 검증 게이트가 프로젝트 시작 시점부터 일관되게 적용됨을 보장합니다.

## 1. 개요

- Status: active
- Owner: owner
- Decision Reference: `__PROJECT_CODE__-DEC-001`
- Baseline Reference: -
- Related WP: `__PROJECT_CODE__-WP-001`
- Last updated: __DATE__

## 2. 핵심 계약

1. 모든 제품 범위·정책·비용 변경은 `10-decision.md`에서 출발하며, 해소된 `OPEN-*`가 `20-spec/`이나 `30-work`에 미결로 남지 않도록 관리합니다.
2. 사용자-facing 동작과 화면·API 계약은 `20-spec/`에 기록하고, QA는 `Given / When / Then` Acceptance Criteria로 판정합니다.
3. 미착수 기능은 `30-work.md` 로드맵 표에 1줄로만 등록하고, 상세 `work-NNN-*.md` 파일은 착수 시점에만 생성한 뒤 `sync_planning.py`로 보드 표를 자동 동기화합니다.
4. 구현과 검증이 끝난 WP는 `Human Check: none`이면 `agent_verified`로, 사람 확인이 필요하면 `awaiting_human`으로 전환하며 에이전트가 임의로 `done`으로 올리지 않습니다.

## 3. Acceptance Criteria

| ID | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| AC-001 | WP 메타나 `10-decision.md`가 변경됨 | `sync_planning.py` 후 `check_planning.py` 실행 | `30-work.md`의 4개 `AUTO` 블록이 일치하고 `stale-open-reference` 0건으로 통과함 | `qa-alone`: `check_planning` 통과 |
| AC-002 | 구현 워커가 WP 작업을 마침 | 완료 상태를 기록함 | `Human Check` 유무에 따라 `agent_verified` 또는 `awaiting_human`으로 분기되고 사람 승인 시에만 `done`으로 전환됨 | `qa-alone`: `30-work.md` 및 `log.md` 기록 |
