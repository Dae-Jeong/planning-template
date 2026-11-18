#!/usr/bin/env python3
"""Deterministic integrity validator for planning/ and multi-repo wiki/ harnesses."""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    MODES,
    PLACEHOLDER_RE,
    VALID_WP_STATUSES,
    extract_status_from_wp,
    iter_relative_links,
    parse_markdown_sections,
    parse_table_rows,
    strip_code_spans,
)

ID_TOKEN_RE = re.compile(r"\b([A-Z0-9_-]+-(?:DEC|OPEN|SPEC|WP)-\d+)\b")


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


def check_standalone_contracts(target_root: Path) -> tuple[list[dict[str, str]], dict]:
    """Validate ID uniqueness, SPEC/WP board sync, status values, and Done gate compliance."""
    issues: list[dict[str, str]] = []
    planning_dir = target_root / "planning"
    stats: dict = {
        "specs_indexed": 0,
        "spec_files": 0,
        "wps_listed": 0,
        "wp_files": 0,
        "wp_status_counts": {},
        "open_decisions": 0,
    }

    # 1. Check 10-decision.md for duplicate DEC / OPEN IDs
    dec_path = planning_dir / "10-decision.md"
    if dec_path.is_file():
        sections = parse_markdown_sections(dec_path.read_text(encoding="utf-8"))
        for heading, body in sections.items():
            seen_ids: set[str] = set()
            is_open_sec = "남은 결정" in heading or "OPEN" in heading
            rows = parse_table_rows(body)
            if is_open_sec:
                stats["open_decisions"] += len(rows)
            for row in rows:
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

    # 2. Check 20-spec.md <-> 20-spec/spec-*.md bidirectional consistency
    spec_index_path = planning_dir / "20-spec.md"
    spec_dir = planning_dir / "20-spec"
    disk_specs = {
        p.relative_to(planning_dir).as_posix()
        for p in (sorted(spec_dir.glob("spec-*.md")) if spec_dir.is_dir() else [])
    }
    stats["spec_files"] = len(disk_specs)
    linked_specs: set[str] = set()
    if spec_index_path.is_file():
        spec_text = spec_index_path.read_text(encoding="utf-8")
        spec_sections = parse_markdown_sections(spec_text)
        seen_spec_ids: set[str] = set()
        for heading, body in spec_sections.items():
            if "SPEC List" not in heading:
                continue
            rows = parse_table_rows(body)
            stats["specs_indexed"] = len(rows)
            for row in rows:
                sid = row.get("ID", "").strip()
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

    # 3. Check 30-work.md tables <-> 30-work/work-*.md consistency + status + Done gate
    work_index_path = planning_dir / "30-work.md"
    work_dir = planning_dir / "30-work"
    disk_wps = {
        p.relative_to(planning_dir).as_posix()
        for p in (sorted(work_dir.glob("work-*.md")) if work_dir.is_dir() else [])
    }
    stats["wp_files"] = len(disk_wps)
    linked_wps: set[str] = set()
    board_statuses: dict[str, str] = {}
    status_counter: Counter[str] = Counter()

    if work_index_path.is_file():
        work_text = work_index_path.read_text(encoding="utf-8")
        work_sections = parse_markdown_sections(work_text)

        for heading, body in work_sections.items():
            if heading not in ("Status Board", "WP List"):
                continue
            seen_in_table: set[str] = set()
            for row in parse_table_rows(body):
                raw_id = row.get("ID") or row.get("WP") or ""
                wp_ids = ID_TOKEN_RE.findall(raw_id)
                wp_id = wp_ids[0] if wp_ids else raw_id.strip()
                if wp_id and wp_id in seen_in_table:
                    issues.append({
                        "severity": "error",
                        "code": "duplicate-wp-id",
                        "path": "planning/30-work.md",
                        "message": f"Duplicate WP '{wp_id}' inside section '## {heading}'",
                    })
                if wp_id:
                    seen_in_table.add(wp_id)

                status = row.get("Status", "").strip().strip("`")
                if status and status not in VALID_WP_STATUSES:
                    issues.append({
                        "severity": "error",
                        "code": "invalid-wp-status",
                        "path": "planning/30-work.md",
                        "message": f"Invalid Status '{status}' for '{wp_id}' in '## {heading}'",
                    })

                if heading == "WP List":
                    stats["wps_listed"] += 1
                    if status:
                        status_counter[status] += 1
                    file_links = iter_relative_links(row.get("파일", ""))
                    for fl in file_links:
                        linked_wps.add(fl)
                        if status:
                            board_statuses[fl] = status

        for link in iter_relative_links(work_text):
            if link.startswith("30-work/work-"):
                linked_wps.add(link)

    for orphan_wp in sorted(disk_wps - linked_wps):
        issues.append({
            "severity": "error",
            "code": "unindexed-wp",
            "path": f"planning/{orphan_wp}",
            "message": "WP file exists under planning/30-work/ but is not linked in planning/30-work.md",
        })

    for rel_wp in sorted(disk_wps):
        wp_path = planning_dir / rel_wp
        wp_text = wp_path.read_text(encoding="utf-8")
        wp_status = extract_status_from_wp(wp_text)
        full_rel = f"planning/{rel_wp}"

        if wp_status is None:
            issues.append({
                "severity": "error",
                "code": "missing-wp-status",
                "path": full_rel,
                "message": "Missing '- Status: <status>' line in WP file",
            })
        elif wp_status not in VALID_WP_STATUSES:
            issues.append({
                "severity": "error",
                "code": "invalid-wp-status",
                "path": full_rel,
                "message": f"Invalid '- Status: {wp_status}' in WP file",
            })
        elif rel_wp in board_statuses and board_statuses[rel_wp] != wp_status:
            issues.append({
                "severity": "error",
                "code": "status-mismatch",
                "path": full_rel,
                "message": f"WP Status '{wp_status}' mismatches 30-work.md WP List status '{board_statuses[rel_wp]}'",
            })

        if wp_status == "done":
            wp_sections = parse_markdown_sections(wp_text)
            gate_body = wp_sections.get("Release Gate", "")
            unchecked = re.findall(r"(?m)^-\s*\[\s\]\s+(.+)$", strip_code_spans(gate_body))
            if unchecked:
                issues.append({
                    "severity": "error",
                    "code": "done-with-unchecked-gate",
                    "path": full_rel,
                    "message": f"WP marked 'done' still has {len(unchecked)} unchecked Release Gate item(s)",
                })

    # Advisory warning if many WPs stacked in ready_for_qa or done since review
    ready_for_qa_count = status_counter.get("ready_for_qa", 0)
    if ready_for_qa_count >= 5:
        issues.append({
            "severity": "warning",
            "code": "qa-sweep-recommended",
            "path": "planning/30-work.md",
            "message": f"{ready_for_qa_count} WPs are waiting in 'ready_for_qa'; consider running a 3-Stage QA Sweep WP",
        })

    stats["wp_status_counts"] = dict(sorted(status_counter.items()))
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
        stats = {"wiki_files": len(list((target_root / "wiki").rglob("*.md"))) if (target_root / "wiki").is_dir() else 0}

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
