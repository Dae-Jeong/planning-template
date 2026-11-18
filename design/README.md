# Planning Template Design System

`planning-template`의 설계 정본 인덱스입니다. 이 디렉터리는 템플릿 파일이 **왜** 그렇게 나뉘었는지, **어떤 순서로 전파되는지**, 그리고 **에이전트와 사람이 어떻게 역할을 나누어 운영하는지**를 정의합니다.

---

## 1. 설계 문서 목록

| 문서 | 다루는 범위 | 주요 출처 계보 |
| --- | --- | --- |
| [`pipeline-architecture.md`](./pipeline-architecture.md) | 7단계 문서 파이프라인(`00-baseline`~`90-archive`), 변경 라우팅표, DDD 4층 경계, QA 중심 10섹션 SPEC 표준, Policy QA Checklist | `mediness` · `onjaewa` · `NEXUS` |
| [`agent-operations.md`](./agent-operations.md) | Anti-Bloat JIT, 2커밋 사이클, 3자 역할 분리, `ready_for_qa` 멈춤 게이트, Red Line 위임, 3종 1차 증거, 5-WP 디자인 리뷰, 3단계 QA Sweep | `lets_talk` 실전 운용 |
| [`quality-evidence-harness.md`](./quality-evidence-harness.md) | `REQ-*` 분해 규칙, Evidence Plan 스키마, `PASS / FAIL / UNKNOWN` 판정 규약, AI 기능 비단독 승인, 자동화 승격 및 Release Gate Report | `mediness` Quality Evidence Harness |
| [`obsidian-integration.md`](./obsidian-integration.md) | 단독 레포(`standalone`) vs `Obsidian` 오케스트레이션 연동(이중 정본 방지) vs 멀티 레포 분리(`multi-repo-central` / `multi-repo-impl`) + 지식 적재 원칙 | `Obsidian` · `thready` · `lets_talk` · `fde-skills` |

---

## 2. 3가지 토폴로지 선택 기준

| 프로젝트 형태 | 권장 `--mode` | 실행 진행 상태 정본 |
| --- | --- | --- |
| 단일 서비스 레포 (고객 납품/독립 운영) | `standalone` | 타겟 레포 `planning/30-work.md` |
| 단일 서비스 레포 + Obsidian 오케스트레이터 사용 | `standalone --obsidian` | `Obsidian/wiki/projects/<id>/tasks/` (`30-work.md`는 WP 카탈로그/커버리지 탐색용) |
| 다중 레포 제품 — 기획 전용 중앙 저장소 | `multi-repo-central` | 중앙 `planning/30-work.md` (또는 `Obsidian Task`) |
| 다중 레포 제품 — 구현 전용 서비스 저장소 | `multi-repo-impl` | `wiki/`는 라우팅만, 실행/검증 증거는 `tasks/` + `docs/` |

---

## 3. 정본 호환 계약

- 백엔드 API 응답(`{ data }` envelope) 및 오류(`RFC 9457 Problem Details`) 계약은 [`../backend-template/design/backend.md`](../../backend-template/design/backend.md)와 정렬합니다.
- 프론트엔드 URL 상태·폼 어댑터·L1~L4 품질 게이트는 [`../frontend-template/design/README.md`](../../frontend-template/design/README.md)와 정렬합니다.
- 사전 고객 정찰·도메인 시뮬레이션·더티 데이터 Spike 역산 계획은 [`../fde-skills/README.md`](../../fde-skills/README.md) 출력을 `00-baseline/` 및 `10-decision.md` 초기 근거로 받아 연결합니다.
