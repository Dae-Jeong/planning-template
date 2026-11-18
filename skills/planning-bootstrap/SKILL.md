---
name: planning-bootstrap
description: Bootstrap, synchronize, validate, and operate the canonical planning/ harness (Decision -> SPEC -> WP -> Auto-Synced Board -> 2-Track Verification -> Log) across standalone, solo company-repo (--local-exclude), multi-repo, and Obsidian-orchestrated projects. Use when initializing planning documents, syncing 30-work.md, accepting WPs, distilling insights, or checking planning drift.
---

# Planning Bootstrap & Operations

Use this skill to install and operate the canonical `planning-template` harness.

Always resolve symlinked `SKILL.md` paths to the real filesystem path first (`<planning-template-root>` = two levels up from the resolved `SKILL.md`).

---

## 1. Choose Topology & Mode

| Scenario | Flags | Notes |
| --- | --- | --- |
| Shared single-repo project | `--mode standalone` | Commits `planning/` into the repository |
| **Solo adoption inside a team/company repo** | `--mode standalone --local-exclude` | Adds `/planning/` & snippet to `.git/info/exclude` so git status stays clean for teammates |
| Obsidian-coordinated repo | `--mode standalone --obsidian` | Prevents Dual-SSOT between `Obsidian Task` and `30-work.md` |
| Multi-repo product (central vs impl) | `--mode multi-repo-central` / `--mode multi-repo-impl --central-ref <path>` | Separates product policy SoT from code/task repos |

---

## 2. Core CLI Commands

```bash
# 1. Bootstrap a project
python3 <planning-template-root>/scripts/init_planning.py \
  --target /abs/path/to/project \
  --code PROJ \
  --name "Project Name"

# 2. Auto-render 30-work.md AUTO tables after editing any work-*.md, 20-spec.md, or 10-decision.md
python3 <planning-template-root>/scripts/sync_planning.py --target /abs/path/to/project

# 3. Human acceptance (promote awaiting_human or agent_verified WPs to done)
python3 <planning-template-root>/scripts/sync_planning.py --target /abs/path/to/project --accept PROJ-WP-002
python3 <planning-template-root>/scripts/sync_planning.py --target /abs/path/to/project --accept-verified

# 4. Extract reusable engineering insights at Phase/Release cut
python3 <planning-template-root>/scripts/sync_planning.py --target /abs/path/to/project --distill

# 5. Read-only validation (broken links, out-of-sync board, stale OPEN-*, invalid WP metadata, 5-WP review due)
python3 <planning-template-root>/scripts/check_planning.py --target /abs/path/to/project
```

---

## 3. Mandatory Operating Rules

1. **Single Writer for WP State**: Edit WP status/metadata ONLY inside `planning/30-work/work-NNN-*.md`, then run `sync_planning.py`. Never hand-edit `<!-- AUTO:... -->` blocks in `30-work.md`.
2. **JIT Anti-Bloat**: Keep unstarted WPs as 1-line rows in `30-work.md` (`신규 기능 로드맵`). When starting `work-NNN-*.md`, delete its row from the roadmap table immediately.
3. **2-Track Stop Rule (Never Self-Promote to `done`)**:
   - If `Human Check: none` and all technical Release Gate items have primary `Tool` evidence (`Log + DB + FE`), set `Status: agent_verified`.
   - If visual/device/human judgment is needed, write a concrete 1-line summary in `Human Check:` and set `Status: awaiting_human`.
   - Leave `done` promotion to the human via `--accept` / `--accept-verified`.
4. **Resolve `OPEN-*` Cleanly**: When an `OPEN-NNN` in `10-decision.md` becomes a `DEC`, remove it from `남은 결정 (OPEN)` and update any `OPEN-NNN` mentions in `20-spec/` or `30-work/` (`check_planning.py` blocks stale `OPEN-*` references).
5. **5-WP Pattern Review**: When `check_planning.py` warns `pattern-review-due`, inspect `git diff` since the last anchor, register accepted refactors as WPs, and advance `리뷰 기준 WP: PROJ-WP-NNN` in `planning/log.md`.
