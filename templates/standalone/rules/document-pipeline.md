# __PROJECT_NAME__ Document Pipeline

최종 수정: __DATE__

<!-- IF_OBSIDIAN -->
> 작업 인수·세션 바인딩 정본은 `Obsidian/wiki/projects/__PROJECT_SLUG__/tasks/`가 소유합니다. 이 `planning/` 트리는 제품 결정·계약·WP 설계·QA 근거를 소유합니다.
<!-- END_IF_OBSIDIAN -->

문서를 무작정 늘리지 않고 **변경 전파 경로와 단일 소유권**을 고정합니다.

## 1. 변경 라우팅표

| 변경 내용 | 기록할 위치 |
| --- | --- |
| 제품 범위, 정책, 비용, 일정, 운영 리스크, 고객 약속 | `10-decision.md` |
| UX 상태, 문구, 사용자 흐름, 도메인 용어, Acceptance Criteria | `20-spec/spec-NNN-*.md` |
<!-- IF_API -->| endpoint별 request/response, `ProblemDetails`, `errorCode` | `20-spec/api/` |<!-- END_IF_API -->
<!-- IF_QA -->| SPEC AC를 케이스별 evidence 요구사항으로 내린 QA 기준 | `20-spec/qa-matrix.md` |<!-- END_IF_QA -->
| 구현 순서, 도메인/트랜잭션 초안, PR 분할, 테스트 계획, Release Gate | `30-work/work-NNN-*.md` |
| SPEC/WP 추가, 상태 변경, 커버리지 갱신 | `20-spec.md`, `30-work.md` |
| 검토용 wireframe, prototype, FDE 사전 정찰, 비교 리서치 스냅샷 | `00-baseline/` |
| 2개+ SPEC/WP가 공유하는 invariant, 상태 머신 | `40-architecture/` |
| 작업 회수, 리뷰 기준 커밋, 릴리스 cut | `log.md` |

## 2. Anti-Bloat JIT & 2커밋 실행 규칙

1. **로드맵 1줄 원칙**: 미착수 WP는 `30-work.md` 로드맵 표에 1줄로만 등록합니다. `30-work/work-NNN-*.md` 파일은 **착수 시점에만** 만듭니다.
2. **plan → execute 2커밋 사이클**: WP 착수 시 계획 파일(`work-NNN-*.md`)을 먼저 고정하고, 구현·검증 후 결과/증거와 `30-work.md`·`log.md`를 함께 회수합니다.
3. **Baseline 환류**: `00-baseline/` 검토에서 사용자 흐름·문구가 바뀌면 `20-spec/`으로, 범위·비용·고객 약속이 바뀌면 `10-decision.md`로 승격합니다.

## 3. DDD / 데이터 4층 경계

- **SPEC (`20-spec/`)**: 사용자·FE·QA가 알아야 하는 도메인 용어, 외부 API resource/status/enum, lifecycle, AC.
<!-- IF_API -->- **API Baseline (`20-spec/api/`)**: HTTP method/path, header/query/body, `{ data }` envelope, RFC 9457 `ProblemDetails`.<!-- END_IF_API -->
- **WP (`30-work/`)**: Aggregate/Entity 초안, Service/Repository 경계, 락/멱등성/트랜잭션 전략, migration 순서.
- **코드 (`src/`, `migrations/`)**: 실제 DB schema(테이블/컬럼/인덱스/FK)와 ORM/SQL 전체의 최종 정본.

## 4. WP Status & Done 게이트

| Status | 의미 | 비고 |
| --- | --- | --- |
| `draft` | 계획 작성 중 | 아직 구현 미착수 |
| `in_dev` | 구현·테스트 진행 중 | `work-NNN-*.md` 활성 상태 |
| `ready_for_qa` | 구현 완료 · 검증 대기 | 권한 환경 실기동 또는 사람 손검증 대기 (기본 멈춤 지점) |
| `qa_blocked` | 결함 또는 환경 blocker 존재 | 해소 조건 명시 필수 |
| `ready_for_release` | QA 통과 · 배포 대기 | Release Gate 체크 완료 |
| `done` | 검증 및 수락 최종 완료 | Release Gate 미체크(`- [ ]`) 잔존 금지 |
| `cancelled` | 착수/진행 취소 | 결정 근거 기록 유지 |
| `superseded` | 후속 WP로 대체됨 | 대체 WP ID 링크 명시 |

**완료(`done`) 승격 최소 조건**:
- 연결된 `10-decision` / `20-spec`이 최신 상태다.
- Build/Unit test 통과 외에 **Log + DB 정합성 + FE 동작** 등 필요한 `Tool` 1차 증거가 기록됐다.
- Release Gate 항목에 미체크(`- [ ]`)가 없고 `Unknown` 잔여 리스크가 분리됐다.
- 에이전트는 사람 확인·GUI 검수가 남아 있으면 `done`으로 올리지 않고 `ready_for_qa`에서 멈춘다.
