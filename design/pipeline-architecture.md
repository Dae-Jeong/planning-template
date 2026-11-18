# 문서 파이프라인 아키텍처 & DDD 경계

이 문서는 문서를 무작정 늘리지 않고 **변경 전파 경로를 고정**해 결정·명세·구현·검증 간 드리프트를 막는 표준 구조를 정의합니다.

---

## 1. 핵심 질문 4가지

프로젝트의 모든 문서 흐름은 아래 4가지 질문에 즉시 답할 수 있어야 합니다:

1. **무엇이 결정됐는가?** → `10-decision.md` (`DEC-*` vs `OPEN-*`)
2. **어떤 사용자-facing 동작과 UX/API 계약이 제품 계약인가?** → `20-spec/` (+ 선택적 `20-spec/api/`)
3. **어떤 WP와 QA 범위가 그것을 구현하고 검증하는가?** → `30-work.md`, `30-work/work-*.md`, `20-spec/qa-matrix.md`
4. **어떤 코드·테스트·로그·DB·브라우저/네트워크 근거가 완료를 증명하는가?** → WP 검증 섹션 + `log.md`

---

## 2. 표준 디렉터리 구조 (`planning/`)

```text
planning/
├── README.md                    # 제품의 무엇/왜, 대상 범위, 역할별 읽는 순서
├── 00-baseline/                 # 특정 시점 검토용 wireframe, prototype HTML, 리서치, FDE recon 산출물
├── 10-decision.md               # 범위, 정책, 비용, 일정, 운영 리스크, 미결 OPEN-NNN vs 확정 DEC-NNN
├── 20-spec.md                   # SPEC 전체 맵, 용어 사전, 범위(In/Out), DDD 경계
├── 20-spec/
│   ├── spec-NNN-{slug}.md       # 사용자-facing UX/정책/API/Acceptance Criteria 계약
│   ├── api/                     # (선택) FE/BE 공유 HTTP Method/Path/DTO/RFC 9457 ProblemDetail 계약
│   └── qa-matrix.md             # (선택) SPEC AC → QA 시나리오/검증 라벨 매트릭스
├── 30-work.md                   # Status Board, WP List, 로드맵 표, Spec Coverage, Release Gate
├── 30-work/
│   └── work-NNN-{slug}.md       # 1 파일 = 1 실행형 WP (착수 시점에만 JIT 생성)
├── 40-architecture/             # (승격형) 2개 이상 SPEC/WP가 공유하는 domain invariant / status map
├── 90-archive/                  # 버전 cut snapshot (현재 문서에는 최신 결론만 유지)
├── log.md                       # 번호 매긴 시간순 변경·검증 회수 기록 & Cut History
├── rules/
│   ├── document-pipeline.md     # 변경 라우팅표 & 상태 규칙
│   ├── policy-direction.md      # 에이전트 위임 가드레일 & Red Line
│   ├── policy-qa-checklist.md   # SPEC 발행 전 7범주 · 11렌즈 · 내적 정합성 점검표
│   └── quality-evidence-harness.md # REQ-* → PASS/FAIL/UNKNOWN 판정 규약
└── templates/                   # 신규 DEC/SPEC/WP/QA Sweep 작성용 빈 템플릿
```

---

## 3. 변경 라우팅 규칙 (Single Owner)

| 변경 성격 | 기록할 유일한 정본 위치 |
| --- | --- |
| 제품 범위, 정책, 비용, 일정, 운영 리스크, 고객 약속 | `10-decision.md` (`DEC-*` / `OPEN-*`) |
| UX 상태, 문구, 사용자 흐름, 도메인 용어, Acceptance Criteria | `20-spec/spec-NNN-*.md` |
| HTTP endpoint, request/response DTO, `ProblemDetail`, `errorCode` | `20-spec/api/` (또는 `spec-NNN` §3) |
| SPEC AC를 실행 케이스별 evidence 요구사항으로 내린 표 | `20-spec/qa-matrix.md` |
| 구현 순서, 도메인/트랜잭션 초안, PR 분할, 테스트·QA 계획, Release Gate | `30-work/work-NNN-*.md` |
| SPEC/WP 추가, 상태 전환, Spec Coverage 변경 | `20-spec.md`, `30-work.md` |
| 검토용 prototype, FDE 사전 정찰/도메인 시뮬레이션, 비교표 스냅샷 | `00-baseline/` (제품 계약을 직접 수정하지 않음) |
| 2개 이상 SPEC/WP가 공유하는 invariant, state machine, 도메인 지도 | `40-architecture/` |
| 작업 회수, 리뷰 기준 커밋, 배포/릴리스 컷 이력 | `log.md` |

> **Baseline 환류 규칙**: `00-baseline/` 검토에서 사용자-facing 흐름/문구가 바뀌면 `20-spec/`으로, 제품 범위·비용·고객 약속이 바뀌면 `10-decision.md`로 승격합니다.

---

## 4. DDD / 데이터 4층 소유권 경계

같은 기술 정보를 SPEC과 코드 양쪽에 복제하지 않습니다. 아래 4계층으로 소유권을 나눕니다:

1. **SPEC (`20-spec/`)**: 사용자·FE·QA·외부 연동자가 알아야 하는 도메인 용어, 외부 API에 드러나는 resource/ID/status/enum, 사용자 관점 lifecycle, Given-When-Then AC.
2. **API Baseline (`20-spec/api/`)**: HTTP method/path, header/query/body shape, 성공 `{ data }` envelope, `RFC 9457 Problem Details` (`type`, `title`, `status`, `detail`, `errorCode`) 매핑 규칙.
3. **WP (`30-work/work-*.md`)**: Aggregate/Entity/Value Object 초안, Service/Repository/Adapter 경계, 락/멱등성/트랜잭션 경계, DB 마이그레이션 적용 순서.
4. **코드 (`src/`, `migrations/`)**: 실제 DB 테이블 스키마·컬럼·인덱스·FK·ORM 필드 전체 및 함수 시그니처의 최종 정본.

**`40-architecture/` 승격 조건** (하나라도 해당할 때만 생성):
- 2개 이상의 SPEC/WP가 같은 Aggregate 경계나 invariant를 공유할 때
- 동일한 state machine이나 원장(ledger) 규칙이 반복될 때
- FE state·BE guard·QA evidence가 동일한 status 집합을 참조해야 할 때

---

## 5. QA·기획자 중심 SPEC 표준 (10섹션 골격)

SPEC이 개발자 메모로 흐르면 기획·QA 검토가 막힙니다. 화면/기능 단위 SPEC은 **`spec-screen.md` 템플릿**을 우선 적용합니다:

1. `§0 기획/QA 빠른 판독` (핵심 계약 요약, 결정 포인트, 검수 매트릭스)
2. `§1 목적` → `§2 Surface / Route` → `§3 Entry / Exit / Return` → `§4 State / Lifecycle`
3. `§5 UX Contract` → `§6 Functional Rules` → `§7 Empty / Error / Feedback`
4. `§8 Acceptance Criteria` (Given / When / Then + 테스트 라벨) → `§9 Open Questions / Known Limitations`
5. `§10 기술 Reference / Implementation Notes` (**API 경로·DB·코드 참조는 항상 문서 맨 마지막에 배치**)

### QA 검증형 문장 규칙

- `OOO가 안 된다` / `보이면 안 된다` / `미구현` 같은 모호한 부정형 단독 결론을 피합니다.
- 대신 **`조건 → 기대 동작(화면/상태/CTA/문구) → 사용자 결과 → QA 확인 기준`** 4요소로 서술합니다.
  - 예: *"권한 없는 사용자가 상세 URL에 직접 접근하면 상세 내용을 열지 않고 권한 안내 화면(`이 항목을 볼 권한이 없어요`)과 목록 복귀 버튼을 표시한다."*

---

## 6. Policy QA Checklist & 테스트 가능성 라벨

SPEC 발행 전 `rules/policy-qa-checklist.md`로 아래 3가지를 점검합니다:

1. **7대 케이스 범주**: Happy Path · Failure · Boundary(정책 변수명 명시) · Empty State · Permission · State Exposure(화면 간 상태 용어 일치) · E2E Flow.
2. **내적 정합성 반례 체크**: `10-decision.md`의 Out-of-Scope나 전제 조건과 충돌하는 UX 약속이 섞이지 않았는지 점검.
3. **5대 테스트 가능성 라벨**:
   - `qa-alone` (화면만으로 검증 가능)
   - `dev-setup` (테스트 데이터/모킹/다중 계정 필요)
   - `external-schedule` (외부 연동/배치/장기 관찰 필요)
   - `alternative-needed` (직접 재현 불가 → replay/강제 상태 필요)
   - `design-review` (문구/가독성/레이아웃 검수 중심)
