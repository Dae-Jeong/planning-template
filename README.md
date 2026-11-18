# planning-template

`mediness`의 Decision–SPEC–Work–QA 파이프라인, `lets_talk`의 실전 멀티 에이전트 운용 플레이북, `onjaewa`의 API Baseline · Policy QA 체계를 통합하고 **자동 보드 동기화(`sync_planning.py`) + 앞단 스펙 노후화 차단(`check_planning.py`)**을 더한 정본 템플릿 저장소입니다.

Python 3.11+ 표준 라이브러리만 사용하므로 **어떤 PC · 어떤 언어의 레포지토리에서도 패키지 설치 없이 즉시 실행**됩니다.

---

## 1. 다른 PC 이관 & 회사 프로젝트 단독(Solo) 즉시 적용 가이드

### Step 1. 새 PC에 `planning-template` 세팅 (10초)

```bash
git clone https://github.com/Dae-Jeong/planning-template.git
cd planning-template
bash scripts/install.sh   # ~/.agents/skills/ 및 ~/.claude/skills/ 에 스킬 등록
```

### Step 2. 기존 회사 프로젝트에 나 혼자 먼저 적용하기 (`--local-exclude`)

팀 전체 합의 전이라 회사 레포의 `git status`나 공유 `.gitignore`를 건드리지 않고 **로컬에서 혼자 에이전트와 바로 굴리고 싶을 때** `--local-exclude` 플래그를 붙입니다:

```bash
python3 /path/to/planning-template/scripts/init_planning.py \
  --target /path/to/company-repo \
  --code PROJ \
  --name "Company Service" \
  --local-exclude
```

- 회사 레포에 이미 `AGENTS.md`가 있으면 절대 덮어쓰지 않고 옆에 `AGENTS.planning.snippet.md`로 분리 생성합니다.
- `--local-exclude`가 `<company-repo>/.git/info/exclude`에 `/planning/`과 `/AGENTS.planning.snippet.md`를 자동 등록하므로 **팀원 PR에 섞이지 않으면서 로컬 에이전트는 100% 동일하게 `planning/` 체계를 읽고 작업**합니다.
- 나중에 팀 공유 문서로 정식 편입할 때는 `<company-repo>/.git/info/exclude`에서 `# planning-template local-only solo mode` 아래 항목만 지운 뒤 `git add planning/`으로 그대로 커밋하면 됩니다.

### Step 3. 세팅 직후 에이전트에 던질 첫 온보딩 프롬프트

기존 회사 레포에 `init_planning.py`를 실행한 직후, 에이전트 세션에 아래 한 줄을 던지면 빈 골격을 현재 코드베이스 기준으로 즉시 채울 수 있습니다:

```text
AGENTS.planning.snippet.md(또는 AGENTS.md)와 planning/README.md 규칙을 읽고,
현재 레포의 코드와 설정을 스캔해서 planning/10-decision.md(확정 DEC / 미결 OPEN),
planning/rules/policy-direction.md(서비스 전제 및 가드레일), planning/20-spec.md 초안을 채운 뒤
sync_planning.py와 check_planning.py까지 통과시켜줘.
```

---

## 2. 일상 운용 4줄 명령어

```bash
# 1) WP 파일(planning/30-work/work-*.md) 또는 10-decision.md 수정 후 30-work.md 표 자동 갱신
python3 /path/to/planning-template/scripts/sync_planning.py --target /path/to/repo

# 2) 사람 시각/실단말 확인(awaiting_human) 끝난 WP 일괄 done 승인
python3 /path/to/planning-template/scripts/sync_planning.py --target /path/to/repo --accept PROJ-WP-003,WP-004

# 3) 에이전트 검증 완료(agent_verified, Human Check: none) WP 일괄 done 승인
python3 /path/to/planning-template/scripts/sync_planning.py --target /path/to/repo --accept-verified

# 4) 무결성 검증 (깨진 링크, 보드 미동기화, 해소된 OPEN 잔존, 미체크 게이트, 5-WP 리뷰 주기 점검)
python3 /path/to/planning-template/scripts/check_planning.py --target /path/to/repo

# (선택) Phase 종료 시 재사용 교훈(Reusable Insight) 모아 보기
python3 /path/to/planning-template/scripts/sync_planning.py --target /path/to/repo --distill
```

---

## 3. 지원하는 3가지 토폴로지

| 모드 (`--mode`) | 구조 | 적합한 상황 |
| --- | --- | --- |
| **`standalone`** (기본) | 프로젝트 루트 `planning/` 1곳에 Decision·SPEC·WP·QA·Architecture·Log 완결 | 단일 서비스 레포, 회사 레포 단독 도입, 고객사 납품용 |
| **`multi-repo-central`** | 중앙 기획·정책 원장 전용 `planning/` + 하위 구현 레포 경계 규칙 | BE/FE/AI 레포가 분리되어 중앙 기획 정본이 필요한 경우 |
| **`multi-repo-impl`** | 구현 레포 내부에 얇은 `wiki/`(`_map.md`, `document-ownership.md`) + `tasks/` 배치 | 중앙 기획 레포를 참조하며 구현·검증 증거만 소유하는 레포 |

- **`--obsidian`**: Obsidian 중앙 Task와 함께 쓸 때 이중 정본(Dual-SSOT) 방지 브릿지를 활성화합니다.

---

## 4. 저장소 구조

```text
planning-template/
├── AGENTS.md                        # 정본 진입점 라우터
├── design/                          # 체계 설계 정본 (왜 · 경계 · 운용 규칙)
│   ├── README.md
│   ├── pipeline-architecture.md     # 00-baseline → 10-decision → 20-spec → 30-work → 40-architecture → log
│   ├── agent-operations.md          # Single Writer 자동동기화, 2트랙 게이트, Red Line, 5-WP 리뷰, QA Sweep
│   ├── quality-evidence-harness.md  # REQ-* 분해 → FE/DB/Log/Network 판정(PASS/FAIL/UNKNOWN)
│   └── obsidian-integration.md      # 단독 / 멀티레포 / Obsidian 연동 경계 및 지식 적재 원칙
├── templates/                       # 타겟 프로젝트 주입용 표준 템플릿 묶음
│   ├── standalone/                  # 단일 레포용 planning/ 풀셋 (AUTO 보드 마커 포함)
│   ├── multi-repo/                  # multi-repo-central & multi-repo-impl 오버레이
│   ├── obsidian-bridge/             # Obsidian 이중 정본 방지 브릿지 규칙
│   └── agent-snippets/              # 타겟 프로젝트 AGENTS.md 삽입용 규칙 블록
├── scripts/
│   ├── common.py                    # 공통 파서 · WP 메타 · AUTO 블록 렌더러
│   ├── init_planning.py             # 1커맨드 프로젝트 세팅 CLI (--local-exclude 지원)
│   ├── sync_planning.py             # 30-work.md 자동 동기화 · --accept · --accept-verified · --distill
│   ├── check_planning.py            # 읽기 전용 무결성/드리프트 검사기
│   └── install.sh                   # ~/.agents/skills/ 및 ~/.claude/skills/ 스킬 심볼릭 링크 설치
├── skills/
│   └── planning-bootstrap/SKILL.md  # AI 에이전트용 세팅 · 기획 · 동기화 · 운용 스킬
└── tests/
    └── test_planning_scripts.py     # 전 모드 · 동기화 · 승인 · 오류 탐지 통합 테스트 스위트
```

---

## 5. 자체 테스트 실행

```bash
python3 -m unittest discover -s tests -v
```
