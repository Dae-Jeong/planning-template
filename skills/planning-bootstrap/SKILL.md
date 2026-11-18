---
name: planning-bootstrap
description: Bootstrap, validate, and operate the canonical planning/ harness (Decision -> SPEC -> WP -> Quality Evidence -> Log) across standalone, multi-repo, and Obsidian-orchestrated projects. Use when initializing planning documents in a repository, translating requirements into 10-decision / 20-spec / 30-work, running a 5-WP design pattern review or 3-stage QA sweep, or validating planning integrity with check_planning.py.
---

# Planning Bootstrap & Operations

Use this skill to install and operate the canonical `mediness` + `lets_talk` + `onjaewa` planning harness from the `planning-template` repository.

Always resolve symlinked `SKILL.md` paths to the real filesystem path first (`<planning-template-root>` = two levels up from the resolved `SKILL.md`), so all `scripts/` and `design/` paths resolve cleanly on any machine.

---

## 1. Choose the Right Topology Before Writing

| Target Repo Shape | CLI Flags | Primary Execution Board |
| --- | --- | --- |
| Single-repo project (independent / client handoff) | `--mode standalone` | `planning/30-work.md` |
| Single-repo coordinated by Obsidian harness | `--mode standalone --obsidian` | `Obsidian/wiki/projects/<slug>/tasks/` (`30-work.md` = WP catalog/coverage) |
| Multi-repo product — Central planning repo | `--mode multi-repo-central` (+ optional `--obsidian`) | Central `planning/30-work.md` (or Obsidian) |
| Multi-repo product — Implementation repo (`be`/`fe`/`ai`) | `--mode multi-repo-impl --central-ref <path-or-url>` | `tasks/README.md` + `wiki/document-ownership.md` |

Optional toggles:
- `--no-api`: omit `20-spec/api/` (e.g., CLI/batch-only project without HTTP endpoints)
- `--no-qa`: omit `20-spec/qa-matrix.md`
- `--inject-agents {auto,snippet,skip}`: `auto` creates `AGENTS.md` if absent or writes `AGENTS.planning.snippet.md` alongside an existing `AGENTS.md` without overwriting project instructions.

---

## 2. Bootstrap Command

Run `init_planning.py` first (`--dry-run` if inspecting conflicts in a dirty repo):

```bash
python3 <planning-template-root>/scripts/init_planning.py \
  --target /abs/path/to/project \
  --code PROJ \
  --name "Project Name" \
  --mode standalone
```

Never overwrite custom existing planning files blindly (`--force` only when resetting deliberately).

---

## 3. Fill Project-Specific Roots (Do Not Leave Generic Skeletons Untouched)

After scaffolding:
1. Update `planning/README.md` (In/Out Scope for v1) and `planning/10-decision.md` (`DEC-*` confirmed choices and `OPEN-*` unresolved architectural questions).
2. Customize `planning/rules/policy-direction.md`: define the user scale/context, reference system convention, and confirm the 6 Red Lines stay reserved for the human Decision Owner.
3. Convert initial features into `planning/20-spec/spec-NNN-*.md` (use `planning/templates/spec-screen.md` for UI screens so technical notes stay at §10 and QA rules stay readable from the top).
4. Register upcoming features ONLY as 1-line rows in the `planning/30-work.md` roadmap table — create `planning/30-work/work-NNN-*.md` **JIT when starting work**.

---

## 4. Operating Cadence During Delivery

Follow the operational rules in `<planning-template-root>/design/agent-operations.md`:
- **2-Commit WP Cycle**: `plan: WP-NNN` (fix `Scope`, `Domain/Contract`, `REQ-*` in `work-NNN-*.md`) → implement with tests → update `work-NNN-*.md`, `30-work.md`, and `planning/log.md` in `WP-NNN ...`.
- **Stop at `ready_for_qa`**: Never jump straight to `done` if GUI/runtime/human verification remains. Check off `Release Gate` boxes only when real primary evidence (**Log + DB consistency + FE/Network behavior**) is observed (`Tool` evidence, not assumption).
- **Periodic Design Pattern Review**: Every Phase completion OR every **5 implemented WPs**, review `git diff <last-review-commit>...HEAD` for DDD/layer drift, filter speculative refactors, log accepted WPs, and record the new review anchor hash in `planning/log.md`.
- **3-Stage QA Sweep**: When a batch of WPs accumulates in `ready_for_qa`, open a Sweep WP using `planning/templates/qa-sweep.md` (Per-Feature → Cross-Feature E2E → Adversarial attack surface) and bundle real defects into a Fix WP.

---

## 5. Validate Before Reporting Completion

Always run the deterministic validator after edits to `planning/` or `wiki/`:

```bash
python3 <planning-template-root>/scripts/check_planning.py --target /abs/path/to/project
```

Report any remaining errors or `ready_for_qa` / `UNKNOWN` limits honestly.
