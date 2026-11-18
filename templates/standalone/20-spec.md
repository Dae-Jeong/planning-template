# __PROJECT_NAME__ Spec

최종 수정: __DATE__

__PROJECT_NAME__(`__PROJECT_CODE__`)의 기능, UX, 정책, Acceptance Criteria 계약 맵입니다.
상세 계약은 `20-spec/` 아래 기능·화면 단위 SPEC 문서에 둡니다.

## Scope

### In Scope (v1)

- 기획·의사결정·실행·품질 검증 하네스 (`__PROJECT_CODE__-SPEC-001`)
- <!-- 핵심 기능 1 -->
- <!-- 핵심 기능 2 -->

### Out Of Scope (v1 제외)

- <!-- 추후 확장 예정이거나 의도적으로 제외한 기능을 여기에 고정합니다 -->

## 도메인 용어 사전

| 용어 | 의미 |
| --- | --- |
| Planning | `10-decision` · `20-spec` · `30-work`를 포함하는 제품 계약 정본 |
| WP | Work Package. 구현·테스트·검증 실행 단위 |
| Baseline | 특정 시점 검토에 사용한 프로토타입 · 정찰 · 리서치 스냅샷 |
| REQ | Quality Evidence Harness가 `PASS / FAIL / UNKNOWN`으로 판정하는 정책 요구사항 단위 |

## SPEC List

| ID | 제목 | 영역 | Status | 파일 |
| --- | --- | --- | --- | --- |
| __PROJECT_CODE__-SPEC-001 | 프로젝트 Planning Harness | project | active | [spec-001-bootstrap-harness.md](20-spec/spec-001-bootstrap-harness.md) |

## 데이터 / DDD 경계

- **SPEC (`20-spec/`)**: 사용자 · FE · QA · 외부 연동자가 알아야 하는 도메인 용어, 외부 API의 resource/status/enum, 사용자 관점 lifecycle, Given/When/Then Acceptance Criteria.
<!-- IF_API -->- **API Baseline ([`20-spec/api/`](20-spec/api/README.md))**: HTTP method/path, request/response shape, `{ data }` envelope, `RFC 9457 Problem Details` 오류 계약.<!-- END_IF_API -->
- **WP (`30-work/`)**: Aggregate/Entity 초안, Service/Repository 경계, 락/멱등성/트랜잭션 전략, 마이그레이션 순서.
- **코드 정본**: 실제 DB 스키마(테이블/컬럼/인덱스/FK)와 ORM/SQL 구현 전체.
- 2개 이상 SPEC/WP가 공유하는 장기 invariant는 [`40-architecture/`](40-architecture/README.md)로 승격합니다.
