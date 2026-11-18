# __PROJECT_CODE__-SPEC-001 프로젝트 Planning Harness

__PROJECT_NAME__의 문서 소유권, 변경 전파 경로, 역할 위임 및 검증 완료 기준이 프로젝트 시작 시점부터 일관되게 적용됨을 보장합니다.

## 1. 개요

- Status: active
- Owner: owner
- Decision Reference: `__PROJECT_CODE__-DEC-001`
- Baseline Reference: -
- Related WP: `__PROJECT_CODE__-WP-001`
- Last updated: __DATE__

## 2. 핵심 계약

1. 모든 제품 범위·정책·비용 변경은 `10-decision.md`에서 출발합니다.
2. 사용자-facing 동작과 화면·API 계약은 `20-spec/`에 기록하고, QA는 `Given / When / Then` Acceptance Criteria로 판정합니다.
3. 구현 단위는 `30-work.md` 보드에 등록하되, 상세 `work-NNN-*.md` 파일은 착수 시점에만 생성합니다.
4. 구현과 단위 테스트가 끝나더라도 사람 확인이나 실기동 증거가 남아 있으면 상태를 `done`으로 올리지 않고 `ready_for_qa`에 둡니다.

## 3. Acceptance Criteria

| ID | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| AC-001 | 새 기능이나 정책 변경이 제안됨 | `rules/document-pipeline.md` 기준으로 라우팅함 | 결정(`10-decision`), 계약(`20-spec`), 실행(`30-work`) 중 단일 소유 위치에만 반영됨 | `qa-alone`: 문서 변경 diff 검토 |
| AC-002 | 구현 워커가 WP 작업을 마침 | 완료 상태를 기록함 | Log/DB/FE 근거가 없으면 `ready_for_qa`로 유지되고 근거를 남김 | `qa-alone`: `30-work.md` 및 `log.md` 기록 |
