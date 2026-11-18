# 토폴로지별 세팅 & Obsidian / Knowledge 연동 경계

프로젝트 크기와 저장소 구성에 따라 **단독 레포형**, **Obsidian 오케스트레이션 연동형**, **멀티 레포 분리형** 중 하나를 선택합니다. 또한 **제품 기획/실행 정본(`planning/`)**과 **재사용 도메인 지식(`wiki/` 또는 중앙 Knowledge Hub)**의 경계를 섞지 않도록 분리합니다.

---

## 1. 모드 A: `standalone` (단독 레포 완결형)

- **적합한 대상**: 1개 레포 안에 FE·BE·Infra가 함께 있거나(예: `lets_talk`, `onjaewa`), 프로젝트 종료 후 고객사에 레포 통째로 인계(`Handoff`)해야 하는 FDE 프로젝트.
- **소유권**:
  - `planning/10-decision.md` · `20-spec/` · `30-work.md` · `30-work/` · `40-architecture/` · `log.md`가 제품 기획부터 실행 상태, QA, 릴리스 이력까지 모두 소유합니다.
  - `AGENTS.md`는 `planning/`과 코드 디렉터리로 라우팅합니다.

---

## 2. 모드 B: `standalone --obsidian` (Obsidian 오케스트레이션 연동형)

[`Obsidian`](../Obsidian/README.md) 하네스·스케줄러(`scheduler`, `project-orchestrator`)와 함께 사용할 때 가장 흔한 함정은 **`Obsidian/wiki/projects/<id>/tasks/`의 Task**와 **타겟 레포 `planning/30-work.md` Status Board**가 둘 다 "진행 중 상태 정본"을 주장해 어긋나는 **이중 정본(Dual-SSOT)** 문제입니다.

이를 방지하기 위해 다음과 같이 소유권을 명확히 가릅니다:

| 영역 | 단일 정본 소유자 | 역할 |
| --- | --- | --- |
| 작업 할당, 활성 세션(`work bind`), 현재 진행 상태(`active`/`review`/`done`), 워커 수락 | **`Obsidian/wiki/projects/<id>/tasks/*.md`** | 오케스트레이터와 세션 간 작업 인계 정본 |
| 제품 결정(`DEC/OPEN`), 사용자 계약(`20-spec/`), WP 설계·`REQ-*` QA 계획(`30-work/work-*.md`), 아키텍처 불변식 | **제품 저장소 `planning/`** | 제품 자체가 소유하는 영구 설계·계약 자산 |
| `planning/30-work.md` | **제품 저장소 (WP 카탈로그 & 커버리지 뷰)** | 독립 진행 상태를 복제하지 않고, 대응하는 **Obsidian Task ID 링크**와 **Spec Coverage / Release Gate**를 연결하는 탐색 입력으로 사용 |
| `planning/log.md` vs `Obsidian/wiki/log/` | 목적 분리 | `planning/log.md` = 제품 마일스톤/WP 회수; `Obsidian/wiki/log/` = 문서 스냅샷·세션 작업 기록 |

---

## 3. 모드 C: `multi-repo-central` + `multi-repo-impl` (`mediness ↔ thready` 분리형)

하나의 제품이 중앙 기획 저장소와 여러 구현 저장소(`be`, `fe`, `ai`)로 나뉜 경우의 구성입니다:

- **중앙 기획 저장소 (`multi-repo-central`)**:
  - `planning/`이 제품 기획·정책·SPEC·WP·아카이빙의 유일한 정본을 가집니다.
  - 구현 저장소의 코드 diff나 로컬 테스트 raw 로그를 중앙 기획 레포에 복사하지 않습니다.
- **하위 구현 저장소 (`multi-repo-impl`)**:
  - `planning/` 전체를 복제하지 않고 **얇은 `wiki/` 라우터**만 둡니다:
    - `wiki/document-ownership.md` — 중앙 기획 vs 구현 repo(`docs/`, `tasks/`, 코드) 경계 고정
    - `wiki/rules/document-pipeline.md` — 충돌 시 기획은 중앙 우선, 구현 현재 상태는 코드 우선, 불일치는 `spec drift`로 기록
    - `wiki/_map.md` / `wiki/_log.md` — 탐색 지도와 문서 맵 변경 기록
    - `tasks/README.md` — 중앙 WP ID를 참조하는 하위 구현/검증 실행 추적
  - 구현 repo는 **최신본만 유지**하고, 과거 이력 아카이빙은 중앙 `planning/90-archive/`에 맡깁니다.

---

## 4. 정보·지식 적재(`wiki/` / Knowledge)와의 분리 원칙

`planning/`은 **"우리가 지금 만들고 검증하는 제품 계약"**이고, 외부 도메인 리서치·재사용 엔지니어링 노하우·고객사 정찰 인사이트는 **"지식 적재 레이어"**입니다. 둘을 섞지 않기 위해 `thready`, `NEXUS`, `Obsidian`, `fde-skills`에서 검증된 4가지 원칙을 따릅니다:

1. **근거 원장과 확정 계약 분리**: `00-baseline/`이나 외부 리서치·고객사 정찰(`fde-client-recon`의 `S#/H#/Q#/U#`)은 원시/가설 근거일 뿐 즉시 제품 계약이 되지 않습니다. 채택된 내용만 `10-decision.md` 또는 `20-spec/`으로 승격합니다.
2. **Authority Label 명시**: 지식/조사 문서에는 `Current canonical`, `Target design`, `Evidence ledger`, `Historical snapshot`, `Review-needed`, `Local-only` 중 성격을 표시해 과거 조사본을 현재 스펙으로 오독하지 않게 합니다.
3. **적재 단위 규칙 (`1원본 = 1엔트리`)**: 조사 자료나 피드백을 검색용 지식으로 적재할 때 한 문서를 3~7개 파편으로 과도하게 쪼개면 검색 노이즈만 폭증합니다(`thready` 실측 `174→66` 회귀 사례). **원본 주제/문서 1건 = 지식 엔트리 1개 + 명확한 통제 어휘(tags)** 단위를 유지합니다.
4. **지식-제품 분리 적재**: 여러 프로젝트에서 공통으로 재사용할 엔지니어링·도메인 지식은 중앙 `Obsidian/wiki/notes/`에 적재하고 프로젝트에서는 링크만 걸며, 이 제품에만 한정된 계약·운영 이력만 제품 레포에 남깁니다.
