# Planning Template — Agent Entry

공통 작업 탐색·기록·인수는 `/Users/marin/.agents/AGENTS.md`가 연결하는 [중앙 작업 규약](../Obsidian/wiki/notes/agents/work-management-policy.md)을 따른다. 프로젝트 Task 정본은 Obsidian의 [`wiki/projects/planning-template/`](../Obsidian/wiki/projects/planning-template/index.md)에 둔다.

이 파일은 `planning-template` 저장소의 고유 목적과 설계·템플릿·도구 라우팅만 소유한다. 세부 규약은 아래 문서에 위임하며 중복 복제하지 않는다.

---

## 핵심 원칙

1. **Anti-Bloat JIT (부풀음 방지)**:
   - 모든 산출물은 `README → 10-decision → 20-spec → 30-work → 40-architecture → log → 90-archive` 단일 변경 전파 경로를 따른다.
   - 로드맵은 `30-work.md` 표에 1줄로 걸고, 상세 `work-NNN-*.md` 파일은 착수 시점에만 만든다.
2. **역할·권한 경계와 Red Line 위임**:
   - Tier 2/3 세부 정책은 `policy-direction.md` 가드레일 안에서 에이전트가 확정하고, 6대 Red Line(scope/보안/영구삭제/외부노출/비용/미결 `OPEN`)은 사람(Decision Owner) 승인 전용으로 남긴다.
   - 에이전트는 구현·테스트 완료 시 `done`으로 임의 승격하지 않고 `ready_for_qa`에서 멈춘다(사람 확인/인수 후 `done`).
3. **실행 성공 ≠ 정책 통과**:
   - Build/Unit test 통과만으로 완료를 주장하지 않는다. `Log + DB 정합성 + FE 동작(Network negative 포함)` 3종 1차 증거와 `REQ-*` 기반 `PASS / FAIL / UNKNOWN` 판정으로 닫는다.

---

## 정본 문서 및 자산 라우팅

| 목적 | 정본 위치 |
| --- | --- |
| **저장소 소개 및 1커맨드 빠른 시작** | [`README.md`](./README.md) |
| **설계 개요 및 3가지 지원 토폴로지** | [`design/README.md`](./design/README.md) |
| **문서 계층, 변경 라우팅, DDD 4층 경계, 10섹션 SPEC 표준** | [`design/pipeline-architecture.md`](./design/pipeline-architecture.md) |
| **에이전트 실전 운용 플레이북 (2커밋 JIT, 위임, 5-WP 리뷰, QA Sweep)** | [`design/agent-operations.md`](./design/agent-operations.md) |
| **품질 근거 하네스 (`REQ-*` → `PASS/FAIL/UNKNOWN`, Release Gate)** | [`design/quality-evidence-harness.md`](./design/quality-evidence-harness.md) |
| **단독 레포 / 멀티 레포 / Obsidian 오케스트레이션 연동 경계** | [`design/obsidian-integration.md`](./design/obsidian-integration.md) |
| **타겟 프로젝트 부트스트랩 및 무결성 검사 CLI** | [`scripts/init_planning.py`](./scripts/init_planning.py) · [`scripts/check_planning.py`](./scripts/check_planning.py) |
| **에이전트 부트스트랩 스킬 (`SKILL.md` + 설치기)** | [`skills/planning-bootstrap/SKILL.md`](./skills/planning-bootstrap/SKILL.md) · [`scripts/install.sh`](./scripts/install.sh) |
| **자동화 스크립트 테스트 스위트** | [`tests/test_planning_scripts.py`](./tests/test_planning_scripts.py) |
