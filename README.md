# planning-template

`mediness`의 Decision–SPEC–Work–QA 파이프라인, `lets_talk`의 실전 멀티 에이전트 운용 플레이북, `onjaewa`의 API Baseline · Policy QA 체계를 하나로 통합한 **기획·의사결정·실행 추적·품질 검증 정본 템플릿 저장소**입니다.

[`backend-template`](https://github.com/Dae-Jeong/BackendTemplate) · [`frontend-template`](https://github.com/Dae-Jeong/frontend-template) · [`fde-skills`](https://github.com/Dae-Jeong/fde-skills)와 함께 새 프로젝트에 즉시 이식할 수 있도록 표준 템플릿, 1커맨드 부트스트랩 CLI, 무결성 검사기, 에이전트 스킬을 제공합니다.

---

## 1. 지원하는 3가지 토폴로지

| 모드 (`--mode`) | 구조 | 적합한 상황 |
| --- | --- | --- |
| **`standalone`** (기본) | 프로젝트 루트 `planning/` 1곳에 Decision·SPEC·WP·QA·Architecture·Log 완결 | 1개 레포로 운영하는 서비스, 클라이언트 납품용 프로젝트 |
| **`multi-repo-central`** | 중앙 기획·정책 원장 전용 `planning/` (`products/<slug>/` 또는 루트) + 하위 구현 레포 연동 규칙 | BE/FE/AI 레포가 분리되어 중앙 기획 정본이 필요한 경우 |
| **`multi-repo-impl`** | 구현 레포 내부에 얇은 `wiki/`(`_map.md`, `document-ownership.md`, `rules/document-pipeline.md`) + `tasks/` 배치 | 중앙 기획 레포를 참조하며 구현·운영·검증 증거만 소유하는 레포 |

- **Obsidian 오케스트레이션 연동 (`--obsidian`)**: [`Obsidian`](https://github.com/Dae-Jeong/Obsidian) 코디네이터/하네스와 함께 쓸 때, `30-work.md`와 Obsidian 중앙 Task가 **실행 진행 상태의 이중 정본**이 되지 않도록 역할을 분리하는 브릿지 규칙을 자동 주입합니다.

---

## 2. 저장소 구조

```text
planning-template/
├── AGENTS.md                        # 정본 진입점 라우터
├── design/                          # 체계 설계 정본 (왜 · 경계 · 운용 규칙)
│   ├── README.md
│   ├── pipeline-architecture.md     # 00-baseline → 10-decision → 20-spec → 30-work → 40-architecture → log
│   ├── agent-operations.md          # 2커밋 JIT, 역할 분리, Red Line 위임, 3종 증거, 5-WP 리뷰, QA Sweep
│   ├── quality-evidence-harness.md  # REQ-* 분해 → FE/DB/Log/Network 판정(PASS/FAIL/UNKNOWN)
│   └── obsidian-integration.md      # 단독 / 멀티레포 / Obsidian 연동 경계 및 knowledge/ 확장 가이드
├── templates/                       # 타겟 프로젝트 주입용 표준 템플릿 묶음
│   ├── standalone/                  # 단일 레포용 planning/ 풀셋 (templates/, rules/, api/, qa-matrix 포함)
│   ├── multi-repo/                  # multi-repo-central & multi-repo-impl 오버레이
│   ├── obsidian-bridge/             # Obsidian 이중 정본 방지 브릿지 규칙
│   └── agent-snippets/              # 타겟 프로젝트 AGENTS.md 삽입용 규칙 블록
├── scripts/
│   ├── common.py                    # 공통 파서 · 플레이스홀더 · 링크 검증 유틸
│   ├── init_planning.py             # 1커맨드 프로젝트 세팅 CLI (Python 표준 라이브러리 전용)
│   ├── check_planning.py            # 결정론적 무결성 검사기 (링크, ID 중복, WP 고아, Done 게이트 검증)
│   └── install.sh                   # ~/.agents/skills/ 및 ~/.claude/skills/ 스킬 심볼릭 링크 설치
├── skills/
│   └── planning-bootstrap/SKILL.md  # AI 에이전트용 세팅 · 기획 · 운용 스킬
└── tests/
    └── test_planning_scripts.py     # init / check 전 모드 · 오류 탐지 테스트 스위트
```

---

## 3. 빠른 시작 (Python 3.11+ 표준 라이브러리 전용, 별도 설치 없음)

### 새 프로젝트에 세팅하기

```bash
# 1. 단일 레포 풀셋 세팅 (API Baseline + QA Matrix + Quality Harness 포함)
python3 scripts/init_planning.py \
  --target /path/to/your-project \
  --code SHOP \
  --name "Shop Admin"

# 2. Obsidian 오케스트레이션 연동 프로젝트로 세팅
python3 scripts/init_planning.py \
  --target /path/to/your-project \
  --code SHOP \
  --name "Shop Admin" \
  --obsidian

# 3. 멀티 레포 분리형 — 구현 레포에 얇은 wiki/ 라우터 세팅
python3 scripts/init_planning.py \
  --target /path/to/your-service-repo \
  --code SHOP \
  --name "Shop Service" \
  --mode multi-repo-impl \
  --central-ref "../shop-planning"
```

### 무결성 검사 실행하기

```bash
# 타겟 프로젝트의 planning/ (또는 wiki/) 구조 · 링크 · ID 중복 · Done 게이트 점검
python3 scripts/check_planning.py --target /path/to/your-project
```

### 에이전트 스킬 전역 설치하기

```bash
bash scripts/install.sh
```

설치 후 Claude Code, Codex CLI, Antigravity(`agy`) 등 `SKILL.md`를 읽는 에이전트가 `planning-bootstrap` 스킬을 통해 새 프로젝트의 `planning/` 초기화부터 WP 운용·QA Sweep까지 자동으로 수행할 수 있습니다.

---

## 4. 이 저장소 자체 테스트

```bash
python3 -m unittest discover -s tests -v
```
