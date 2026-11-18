#!/usr/bin/env python3
"""Deterministic read-only validator for planning/ and multi-repo wiki/ harnesses."""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    AUTO_BLOCKS,
    ID_TOKEN_RE,
    LEGACY_WP_STATUSES,
    MODES,
    OPEN_ID_RE,
    PLACEHOLDER_RE,
    SPEC_ID_RE,
    VALID_WP_STATUSES,
    WP_ID_RE,
    apply_auto_blocks,
    is_none_value,
    iter_relative_links,
    load_active_open_decisions,
    load_all_wps,
    parse_markdown_sections,
    parse_table_rows,
    render_auto_blocks,
    strip_fences_only,
)


def detect_mode(target_root: Path, requested_mode: str | None) -> str:
    """Resolve mode explicitly or from directory structure on disk."""
    if requested_mode:
        return requested_mode
    if (target_root / "planning/rules/multi-repo-boundaries.md").exists():
        return "multi-repo-central"
    if (target_root / "planning").is_dir():
        return "standalone"
    if (target_root / "wiki/document-ownership.md").exists():
        return "multi-repo-impl"
    return "standalone"


def check_required_files(target_root: Path, mode: str) -> list[dict[str, str]]:
    """Verify baseline canonical files exist for the selected topology."""
    issues: list[dict[str, str]] = []
    if mode in ("standalone", "multi-repo-central"):
        required = [
            "planning/README.md",
            "planning/10-decision.md",
            "planning/20-spec.md",
            "planning/30-work.md",
            "planning/log.md",
            "planning/rules/document-pipeline.md",
            "planning/rules/policy-direction.md",
            "planning/rules/policy-qa-checklist.md",
            "planning/rules/quality-evidence-harness.md",
        ]
        if mode == "multi-repo-central":
            required.append("planning/rules/multi-repo-boundaries.md")
    else:
        required = [
            "wiki/README.md",
            "wiki/_map.md",
            "wiki/_log.md",
            "wiki/document-ownership.md",
            "wiki/rules/document-pipeline.md",
            "tasks/README.md",
        ]

    for rel in required:
        if not (target_root / rel).is_file():
            issues.append({
                "severity": "error",
                "code": "missing-required-file",
                "path": rel,
                "message": f"Required canonical file missing for mode '{mode}'",
            })
    return issues


def check_links_and_placeholders(target_root: Path, scope_dirs: list[Path]) -> list[dict[str, str]]:
    """Scan Markdown files under scope_dirs for unreplaced placeholders and broken links."""
    issues: list[dict[str, str]] = []
    for base in scope_dirs:
        if not base.exists():
            continue
        for md_path in sorted(base.rglob("*.md")):
            rel = md_path.relative_to(target_root).as_posix()
            text = md_path.read_text(encoding="utf-8")

            unreplaced = sorted(set(PLACEHOLDER_RE.findall(text)))
            if unreplaced:
                issues.append({
                    "severity": "error",
                    "code": "unreplaced-placeholder",
                    "path": rel,
                    "message": f"Unreplaced template placeholder(s): {', '.join(unreplaced)}",
                })

            for link in iter_relative_links(text):
                resolved = (md_path.parent / link).resolve()
                if not resolved.exists():
                    issues.append({
                        "severity": "error",
                        "code": "broken-link",
                        "path": rel,
                        "message": f"Broken relative link target: {link}",
                    })
    return issues


def check_stale_open_references(planning_dir: Path, target_root: Path, active_opens: set[str]) -> list[dict[str, str]]:
    """Ensure resolved/absent OPEN-NNN IDs do not linger in README, 20-spec*, or 30-work*."""
    issues: list[dict[str, str]] = []
    candidates: list[Path] = []
    for rel in ("README.md", "20-spec.md", "30-work.md"):
        p = planning_dir / rel
        if p.is_file():
            candidates.append(p)
    for sub in ("20-spec", "30-work"):
        d = planning_dir / sub
        if d.is_dir():
            candidates.extend(sorted(d.rglob("*.md")))

    for md_path in candidates:
        text = strip_fences_only(md_path.read_text(encoding="utf-8"))
        found_opens = sorted(set(OPEN_ID_RE.findall(text)) - active_opens)
        if found_opens:
            rel = md_path.relative_to(target_root).as_posix()
            issues.append({
                "severity": "error",
                "code": "stale-open-reference",
                "path": rel,
                "message": (
                    f"Resolved or unknown OPEN decision(s) referenced outside 10-decision.md/log.md: "
                    f"{', '.join(found_opens)}"
                ),
            })
    return issues


def check_standalone_contracts(target_root: Path) -> tuple[list[dict[str, str]], dict]:
    """Validate IDs, WP metadata, AUTO board sync, stale OPENs, roadmap duplicates, and review cadence."""
    issues: list[dict[str, str]] = []
    planning_dir = target_root / "planning"

    # 1. Check 10-decision.md duplicate IDs and gather active OPEN set
    active_opens: set[str] = set()
    dec_path = planning_dir / "10-decision.md"
    if dec_path.is_file():
        sections = parse_markdown_sections(dec_path.read_text(encoding="utf-8"))
        for heading, body in sections.items():
            seen_ids: set[str] = set()
            is_open_sec = "남은 결정" in heading or "OPEN" in heading
            for row in parse_table_rows(body):
                cell = row.get("ID", "")
                for match in ID_TOKEN_RE.findall(cell):
                    if match in seen_ids:
                        issues.append({
                            "severity": "error",
                            "code": "duplicate-id",
                            "path": "planning/10-decision.md",
                            "message": f"Duplicate ID '{match}' in section '{heading}'",
                        })
                    seen_ids.add(match)
                    if is_open_sec and "-OPEN-" in match:
                        active_opens.add(match)

    # 2. Check 20-spec.md <-> 20-spec/spec-*.md bidirectional consistency
    spec_index_path = planning_dir / "20-spec.md"
    spec_dir = planning_dir / "20-spec"
    disk_specs = {
        p.relative_to(planning_dir).as_posix()
        for p in (sorted(spec_dir.glob("spec-*.md")) if spec_dir.is_dir() else [])
    }
    specs_indexed = 0
    linked_specs: set[str] = set()
    if spec_index_path.is_file():
        spec_text = spec_index_path.read_text(encoding="utf-8")
        spec_sections = parse_markdown_sections(spec_text)
        seen_spec_ids: set[str] = set()
        for heading, body in spec_sections.items():
            if "SPEC List" not in heading:
                continue
            rows = parse_table_rows(body)
            specs_indexed = len(rows)
            for row in rows:
                sid_matches = SPEC_ID_RE.findall(row.get("ID", ""))
                sid = sid_matches[0] if sid_matches else row.get("ID", "").strip()
                if sid in seen_spec_ids:
                    issues.append({
                        "severity": "error",
                        "code": "duplicate-spec-id",
                        "path": "planning/20-spec.md",
                        "message": f"Duplicate SPEC ID '{sid}' in SPEC List",
                    })
                if sid:
                    seen_spec_ids.add(sid)
        for link in iter_relative_links(spec_text):
            if link.startswith("20-spec/spec-"):
                linked_specs.add(link)

    for orphan_spec in sorted(disk_specs - linked_specs):
        issues.append({
            "severity": "error",
            "code": "unindexed-spec",
            "path": f"planning/{orphan_spec}",
            "message": "SPEC file exists under planning/20-spec/ but is not linked in planning/20-spec.md",
        })

    # 3. Validate all 30-work/work-*.md records
    wps = load_all_wps(planning_dir)
    status_counter: Counter[str] = Counter()
    seen_wp_ids: dict[str, str] = {}

    for w in wps:
        full_rel = f"planning/{w.rel_path}"
        if w.wp_id in seen_wp_ids:
            issues.append({
                "severity": "error",
                "code": "duplicate-wp-id",
                "path": full_rel,
                "message": f"Duplicate WP ID '{w.wp_id}' already declared in '{seen_wp_ids[w.wp_id]}'",
            })
        else:
            seen_wp_ids[w.wp_id] = full_rel

        if w.status is None:
            issues.append({
                "severity": "error",
                "code": "missing-wp-status",
                "path": full_rel,
                "message": "Missing '- Status: <status>' under '## 메타'",
            })
            continue

        if w.status in LEGACY_WP_STATUSES:
            issues.append({
                "severity": "error",
                "code": "legacy-wp-status",
                "path": full_rel,
                "message": (
                    f"Legacy Status '{w.status}' is deprecated; use 'agent_verified' (Human Check: none) "
                    f"or 'awaiting_human' (Human Check specified)"
                ),
            })
            continue

        if w.status not in VALID_WP_STATUSES:
            issues.append({
                "severity": "error",
                "code": "invalid-wp-status",
                "path": full_rel,
                "message": f"Invalid Status '{w.status}' in WP file",
            })
            continue

        status_counter[w.status] += 1

        if w.status == "agent_verified":
            if not is_none_value(w.human_check):
                issues.append({
                    "severity": "error",
                    "code": "wp-metadata-invalid",
                    "path": full_rel,
                    "message": "Status 'agent_verified' requires 'Human Check: none'; use 'awaiting_human' instead",
                })
            if w.unchecked_tech_gates:
                issues.append({
                    "severity": "error",
                    "code": "wp-metadata-invalid",
                    "path": full_rel,
                    "message": f"Status 'agent_verified' still has {len(w.unchecked_tech_gates)} unchecked technical Release Gate item(s)",
                })
        elif w.status == "awaiting_human":
            if is_none_value(w.human_check):
                issues.append({
                    "severity": "error",
                    "code": "wp-metadata-invalid",
                    "path": full_rel,
                    "message": "Status 'awaiting_human' requires a concrete 1-line description in 'Human Check:'",
                })
            if w.unchecked_tech_gates:
                issues.append({
                    "severity": "error",
                    "code": "wp-metadata-invalid",
                    "path": full_rel,
                    "message": f"Status 'awaiting_human' still has {len(w.unchecked_tech_gates)} unchecked technical Release Gate item(s)",
                })
        elif w.status == "qa_blocked" and is_none_value(w.blocker):
            issues.append({
                "severity": "error",
                "code": "wp-metadata-invalid",
                "path": full_rel,
                "message": "Status 'qa_blocked' requires a concrete unblock condition in 'Blocker:'",
            })
        elif w.status == "done":
            unchecked_total = len(w.unchecked_tech_gates) + len(w.unchecked_owner_gates)
            if unchecked_total > 0:
                issues.append({
                    "severity": "error",
                    "code": "done-with-unchecked-gate",
                    "path": full_rel,
                    "message": f"WP marked 'done' still has {unchecked_total} unchecked Release Gate item(s)",
                })

    # 4. Validate 30-work.md AUTO markers, sync state, and Backlog/Roadmap duplicates
    work_index_path = planning_dir / "30-work.md"
    if work_index_path.is_file():
        work_text = work_index_path.read_text(encoding="utf-8")
        missing_markers = [
            name
            for name in AUTO_BLOCKS
            if f"<!-- AUTO:{name}:START -->" not in work_text or f"<!-- AUTO:{name}:END -->" not in work_text
        ]
        if missing_markers:
            issues.append({
                "severity": "error",
                "code": "missing-auto-marker",
                "path": "planning/30-work.md",
                "message": f"Missing AUTO block marker(s) in 30-work.md: {', '.join(missing_markers)}",
            })
        else:
            expected_blocks = render_auto_blocks(planning_dir)
            _, changed_blocks = apply_auto_blocks(work_text, expected_blocks)
            if changed_blocks:
                issues.append({
                    "severity": "error",
                    "code": "board-out-of-sync",
                    "path": "planning/30-work.md",
                    "message": (
                        f"AUTO section(s) out of sync ({', '.join(changed_blocks)}); "
                        f"run sync_planning.py --target {target_root}"
                    ),
                })

        work_sections = parse_markdown_sections(work_text)
        started_wp_ids = {w.wp_id for w in wps}
        for heading, body in work_sections.items():
            if not any(kw in heading.lower() for kw in ("로드맵", "backlog", "roadmap")):
                continue
            for row in parse_table_rows(body):
                raw_cell = row.get("WP") or row.get("ID") or ""
                for wid, _ in WP_ID_RE.findall(raw_cell):
                    if wid in started_wp_ids:
                        issues.append({
                            "severity": "error",
                            "code": "roadmap-already-started",
                            "path": "planning/30-work.md",
                            "message": (
                                f"WP '{wid}' already has a file in 30-work/; remove it from the pre-kickoff '{heading}' table"
                            ),
                        })

    # 5. Stale OPEN-* check across active spec/work documents
    issues.extend(check_stale_open_references(planning_dir, target_root, active_opens))

    # 6. Cadence advisories: 5-WP Design Pattern Review & Human Sign-off backlog
    anchor_wp_num = 0
    log_path = planning_dir / "log.md"
    if log_path.is_file():
        log_text = strip_fences_only(log_path.read_text(encoding="utf-8"))
        anchors = [int(m.group(2)) for m in re.finditer(r"리뷰 기준 WP:\s*([A-Z][A-Z0-9_-]*-WP-(\d+))", log_text)]
        if anchors:
            anchor_wp_num = max(anchors)

    unreviewed_completed = [
        w.wp_id
        for w in wps
        if w.wp_num > anchor_wp_num and w.status in ("agent_verified", "awaiting_human", "done")
    ]
    if len(unreviewed_completed) >= 5:
        issues.append({
            "severity": "warning",
            "code": "pattern-review-due",
            "path": "planning/log.md",
            "message": (
                f"{len(unreviewed_completed)} WPs verified/completed since last review anchor (WP-{anchor_wp_num:03d}); "
                f"run a 5-WP Design Pattern Review and update '리뷰 기준 WP:' in log.md"
            ),
        })

    awaiting_human_count = status_counter.get("awaiting_human", 0)
    if awaiting_human_count >= 5:
        issues.append({
            "severity": "warning",
            "code": "human-signoff-backlog",
            "path": "planning/30-work.md",
            "message": (
                f"{awaiting_human_count} WPs waiting in Human Sign-off Queue; "
                f"check items and run sync_planning.py --accept <WP-IDs>"
            ),
        })

    stats = {
        "specs_indexed": specs_indexed,
        "spec_files": len(disk_specs),
        "wp_files": len(wps),
        "wp_status_counts": dict(sorted(status_counter.items())),
        "open_decisions": len(active_opens),
        "review_anchor_wp_num": anchor_wp_num,
        "wps_since_review": len(unreviewed_completed),
    }
    return issues, stats


def build_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser for check_planning.py."""
    parser = argparse.ArgumentParser(
        description="Validate structural integrity of a planning/ or multi-repo wiki/ harness."
    )
    parser.add_argument("--target", required=True, help="Target repository root directory")
    parser.add_argument("--mode", choices=MODES, default=None, help="Override auto-detected topology mode")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON output")
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for validating a target repository planning harness."""
    args = build_parser().parse_args(argv)
    target_root = Path(args.target).expanduser().resolve()
    if not target_root.is_dir():
        print(f"Error: target directory does not exist: {target_root}", file=sys.stderr)
        return 2

    mode = detect_mode(target_root, args.mode)
    issues = check_required_files(target_root, mode)

    if mode in ("standalone", "multi-repo-central"):
        scope_dirs = [target_root / "planning"]
        issues.extend(check_links_and_placeholders(target_root, scope_dirs))
        contract_issues, stats = check_standalone_contracts(target_root)
        issues.extend(contract_issues)
    else:
        scope_dirs = [target_root / "wiki", target_root / "tasks"]
        issues.extend(check_links_and_placeholders(target_root, scope_dirs))
        stats = {
            "wiki_files": len(list((target_root / "wiki").rglob("*.md"))) if (target_root / "wiki").is_dir() else 0
        }

    errors = [item for item in issues if item["severity"] == "error"]
    warnings = [item for item in issues if item["severity"] == "warning"]
    ok = len(errors) == 0 and (not args.strict or len(warnings) == 0)

    report = {
        "ok": ok,
        "target": str(target_root),
        "mode": mode,
        "errors": len(errors),
        "warnings": len(warnings),
        "stats": stats,
        "issues": issues,
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        status_label = "PASS" if ok else "FAIL"
        print(f"[{status_label}] target={target_root} mode={mode} errors={len(errors)} warnings={len(warnings)}")
        for item in issues:
            print(f"  - [{item['severity'].upper()}] {item['code']} ({item['path']}): {item['message']}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
