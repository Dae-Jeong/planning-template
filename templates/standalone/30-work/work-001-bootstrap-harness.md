# __PROJECT_CODE__-WP-001 Bootstrap Planning Harness

__PROJECT_NAME__ 프로젝트의 Decision / Spec / Work / Architecture / QA / Log 정본 체계를 초기화합니다.

## 메타

- Status: done
- Owner: owner
- Covers SPEC: __PROJECT_CODE__-SPEC-001
- Related Decision: __PROJECT_CODE__-DEC-001
- Dependencies: -

## Scope

### In

- `planning/` 기본 계층(`00-baseline` ~ `90-archive`, `rules/`, `templates/`, `log.md`) 초기화
- `check_planning` 무결성 기준 충족

### Out

- 제품 비즈니스 기능 코드 구현

## Execution Plan

1. `10-decision.md`, `20-spec.md`, `30-work.md` 및 `rules/`·`templates/` 생성
2. 무결성 검사(`check_planning`) 통과 확인
3. `10-decision.md`의 `__PROJECT_CODE__-OPEN-001` 구체화 및 첫 기능 WP 착수

## 요구사항 대비 완성도 매트릭스

| REQ-ID | 내용 | 상태 | 근거 | 누락 사유 |
| --- | --- | --- | --- | --- |
| __PROJECT_CODE__-REQ-001 | planning 정본 파일과 링크·ID 무결성이 성립한다 | PASS | `init_planning.py` 및 `check_planning.py` 초기 검증 | - |

## Release Gate

- [x] `10-decision.md`, `20-spec.md`, `30-work.md`, `log.md`가 존재한다
- [x] `rules/` 4종과 `templates/`가 연결되어 있다
- [x] 깨진 링크와 미치환 placeholder가 없다
