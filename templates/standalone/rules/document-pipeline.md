# __PROJECT_NAME__ Document Pipeline

최종 수정: __DATE__

<!-- IF_OBSIDIAN -->
> 작업 인수·세션 바인딩 정본은 `Obsidian/wiki/projects/__PROJECT_SLUG__/tasks/`가 소유합니다. 이 `planning/` 트리는 제품 결정·계약·WP 설계·QA 근거를 소유합니다.
<!-- END_IF_OBSIDIAN -->

문서를 무작정 늘리지 않고 **단일 수정 지점(Single Writer)과 변경 전파 경로**를 고정합니다.

## 1. 변경 라우팅표

| 변경 내용 | 직접 수정할 정본 위치 | 자동 동기화 대상 |
| --- | --- | --- |
| 제품 범위, 정책, 비용, 일정, 운영 리스크, 고객 약속 | `10-decision.md` | `30-work.md` (`OPEN_MIRROR`) |
| UX 상태, 문구, 사용자 흐름, 도메인 용어, Acceptance Criteria | `20-spec/spec-NNN-*.md`, `20-spec.md` | `30-work.md` (`SPEC_COVERAGE`) |
<!-- IF_API -->| endpoint별 request/response, `ProblemDetails`, `errorCode` | `20-spec/api/` | - |<!-- END_IF_API -->
<!-- IF_QA -->| SPEC AC를 케이스별 evidence 요구사항으로 내린 QA 기준 | `20-spec/qa-matrix.md` | - |<!-- END_IF_QA -->
| 구현 계획, 도메인 초안, `Status`, `Human Check`, `REQ-*`, Release Gate | `30-work/work-NNN-*.md` | `30-work.md` (`HUMAN_QUEUE`, `WP_BOARD`, `SPEC_COVERAGE`) |
| 미착수 신규 기능 후보 (1줄 요약) | `30-work.md` (`신규 기능 로드맵` 표) | 착수 시 `work-NNN-*.md` 생성 후 표에서 제거 |
| 검토용 wireframe, prototype, FDE 사전 정찰, 비교 리서치 스냅샷 | `00-baseline/` | - |
| 2개+ SPEC/WP가 공유하는 invariant, 상태 머신 | `40-architecture/` | - |
| 작업 회수, `리뷰 기준 WP`, 릴리스 cut | `log.md` | - |

> **중요**: `30-work.md`의 `<!-- AUTO:... -->` 블록 4곳은 직접 손으로 수정하지 않고 `sync_planning.py --target <repo>`로 갱신합니다.

## 2. Anti-Bloat JIT & 2커밋 실행 규칙

1. **로드맵 1줄 원칙**: 미착수 WP는 `30-work.md` 로드맵 표에 1줄로만 등록합니다. `30-work/work-NNN-*.md` 파일은 **착수 시점에만** 만들고, 파일을 만든 즉시 로드맵 표에서는 제거합니다.
2. **plan → execute 2커밋 사이클**: WP 착수 시 계획 파일(`work-NNN-*.md`) + `sync_planning.py`를 먼저 커밋하고, 구현·검증 후 결과/증거와 `sync_planning.py`·`log.md`를 함께 회수합니다.
3. **해소된 `OPEN-*` 즉시 정리**: `10-decision.md`에서 `OPEN-NNN`이 `DEC`로 확정되면 `남은 결정 (OPEN)` 표에서 제거하고, `20-spec*`·`30-work*`에 남아 있던 `OPEN-NNN` 참조도 확정된 `DEC` 기준으로 갱신합니다(`check_planning.py`가 잔존 시 차단).

## 3. DDD / 데이터 4층 경계

- **SPEC (`20-spec/`)**: 사용자·FE·QA가 알아야 하는 도메인 용어, 외부 API resource/status/enum, lifecycle, AC.
<!-- IF_API -->- **API Baseline (`20-spec/api/`)**: HTTP method/path, header/query/body, `{ data }` envelope, RFC 9457 `ProblemDetails`.<!-- END_IF_API -->
- **WP (`30-work/`)**: Aggregate/Entity 초안, Service/Repository 경계, 락/멱등성/트랜잭션 전략, migration 순서.
- **코드 (`src/`, `migrations/`)**: 실제 DB schema(테이블/컬럼/인덱스/FK)와 ORM/SQL 전체의 최종 정본.

## 4. 2트랙 검증 & WP Status 게이트

| Status | 의미 | 진입 조건 / 규칙 |
| --- | --- | --- |
| `draft` | 계획 작성 중 | 아직 구현 미착수 |
| `in_dev` | 구현·테스트 진행 중 | `work-NNN-*.md` 활성 상태 |
| `qa_blocked` | 결함 또는 환경 blocker 존재 | `Blocker:` 필드에 구체적 해소 조건 필수 |
| **`agent_verified`** | 에이전트 1차 증거 완결 (사람 확인 불필요) | `Human Check: none` + 기술 Release Gate 전부 `[x]` |
| **`awaiting_human`** | 에이전트 검증 완료 · 사람 확인 대기 | `Human Check:`에 확인할 내용 1줄 명시 + 기술 Gate 전부 `[x]` |
| `done` | 최종 승인 완료 | 사람 확인 후 `sync_planning.py --accept` 또는 `--accept-verified`로 전환 (미체크 `[ ]` 0개) |
| `cancelled` | 착수/진행 취소 | 취소 사유 기록 유지 |
| `superseded` | 후속 WP로 대체됨 | 대체 WP ID 명시 |
