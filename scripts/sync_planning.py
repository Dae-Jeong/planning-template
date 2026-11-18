#!/usr/bin/env python3
"""Synchronize planning/30-work.md AUTO tables, batch-accept WPs, and distill reusable insights."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    WpRecord,
    apply_auto_blocks,
    escape_cell,
    is_none_value,
    is_owner_gate_label,
    load_all_wps,
    render_auto_blocks,
)


def promote_wp_text_to_done(markdown: str) -> str:
    """Update `- Status: ...` to `done` and check off owner Release Gate items."""
    updated = re.sub(
        r"(?m)^(-\s*Status:\s*)(.+?)\s*$",
        r"\g<1>done",
        markdown,
        count=1,
    )

    lines = updated.splitlines(keepends=True)
    in_gate = False
    out: list[str] = []
    for line in lines:
        if line.startswith("## "):
            in_gate = line[3:].strip() == "Release Gate"
            out.append(line)
            continue
        if in_gate:
            m = re.match(r"^(\s*-\s*)\[\s\](\s+.+?)(\r?\n?)$", line)
            if m and is_owner_gate_label(m.group(2)):
                out.append(f"{m.group(1)}[x]{m.group(2)}{m.group(3)}")
                continue
        out.append(line)
    return "".join(out)


def match_requested_wps(wps: list[WpRecord], raw_targets: list[str]) -> tuple[list[WpRecord], list[str]]:
    """Resolve full WP IDs (SHOP-WP-002) or short suffixes (WP-002) against loaded WpRecords."""
    matched: list[WpRecord] = []
    missing: list[str] = []
    seen: set[str] = set()
    for token in raw_targets:
        norm = token.strip().upper()
        if not norm:
            continue
        found = next(
            (w for w in wps if w.wp_id.upper() == norm or w.wp_id.upper().endswith(f"-{norm}")),
            None,
        )
        if found is None:
            missing.append(token.strip())
        elif found.rel_path not in seen:
            seen.add(found.rel_path)
            matched.append(found)
    return matched, missing


def run_distill(planning_dir: Path, as_json: bool) -> int:
    """Extract all non-empty `Reusable Insight` entries from 30-work/work-*.md."""
    wps = load_all_wps(planning_dir)
    insights = [
        {
            "wp_id": w.wp_id,
            "title": w.title,
            "status": w.status or "unknown",
            "covers_spec": list(w.covers_spec),
            "insight": w.reusable_insight,
            "file": f"planning/{w.rel_path}",
        }
        for w in wps
        if not is_none_value(w.reusable_insight)
    ]

    if as_json:
        print(json.dumps({"ok": True, "count": len(insights), "insights": insights}, ensure_ascii=False, indent=2))
        return 0

    if not insights:
        print("추출할 Reusable Insight 항목이 없습니다 (모든 WP가 'none').")
        return 0

    print("| WP | 제목 | Status | Reusable Insight | 파일 |")
    print("| --- | --- | --- | --- | --- |")
    for item in insights:
        print(
            f"| {escape_cell(item['wp_id'])} | {escape_cell(item['title'])} | {escape_cell(item['status'])} "
            f"| {escape_cell(item['insight'])} | `{item['file']}` |"
        )
    return 0


def sync_work_board_file(planning_dir: Path, dry_run: bool = False) -> tuple[bool, list[str]]:
    """Re-render AUTO blocks in planning/30-work.md and return (changed, changed_blocks)."""
    work_path = planning_dir / "30-work.md"
    if not work_path.is_file():
        raise FileNotFoundError(f"Missing work board: {work_path}")

    original = work_path.read_text(encoding="utf-8")
    blocks = render_auto_blocks(planning_dir)
    updated, changed_blocks = apply_auto_blocks(original, blocks)

    if changed_blocks:
        today_str = date.today().isoformat()
        updated = re.sub(
            r"(?m)^(최종 수정:\s*)\d{4}-\d{2}-\d{2}\s*$",
            rf"\g<1>{today_str}",
            updated,
            count=1,
        )

    changed = updated != original
    if changed and not dry_run:
        work_path.write_text(updated, encoding="utf-8")
    return changed, changed_blocks


def build_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser for sync_planning.py."""
    parser = argparse.ArgumentParser(
        description="Sync planning/30-work.md AUTO tables, accept verified/human-checked WPs, or distill insights."
    )
    parser.add_argument("--target", required=True, help="Target repository root directory")
    parser.add_argument(
        "--accept",
        default="",
        help="Comma-separated WP IDs (e.g. SHOP-WP-002,WP-003) to promote to 'done' after human check",
    )
    parser.add_argument(
        "--accept-verified",
        action="store_true",
        help="Batch-promote all WPs currently in 'agent_verified' status to 'done'",
    )
    parser.add_argument(
        "--distill",
        action="store_true",
        help="Read-only: extract non-empty 'Reusable Insight' items across all WPs",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON summary")
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for syncing and operating the planning board."""
    args = build_parser().parse_args(argv)
    target_root = Path(args.target).expanduser().resolve()
    planning_dir = target_root / "planning"
    if not planning_dir.is_dir():
        print(f"Error: planning directory not found at {planning_dir}", file=sys.stderr)
        return 2

    if args.distill:
        return run_distill(planning_dir, args.json)

    wps = load_all_wps(planning_dir)
    to_accept: list[WpRecord] = []

    if args.accept.strip():
        tokens = [t for t in args.accept.split(",") if t.strip()]
        matched, missing = match_requested_wps(wps, tokens)
        if missing:
            err = f"Unknown WP ID(s): {', '.join(missing)}"
            print(json.dumps({"ok": False, "error": err}) if args.json else f"Error: {err}", file=sys.stderr)
            return 1
        to_accept.extend(matched)

    if args.accept_verified:
        existing = {w.rel_path for w in to_accept}
        for w in wps:
            if w.status == "agent_verified" and w.rel_path not in existing:
                to_accept.append(w)

    # Safety check: never accept a WP whose technical Release Gate items remain unchecked
    blocked_gates = [
        (w.wp_id, list(w.unchecked_tech_gates))
        for w in to_accept
        if w.unchecked_tech_gates
    ]
    if blocked_gates:
        details = "; ".join(f"{wid} ({len(g)} unchecked tech gate(s))" for wid, g in blocked_gates)
        err = f"Cannot promote to 'done' before technical Release Gate items are checked: {details}"
        print(json.dumps({"ok": False, "error": err}) if args.json else f"Error: {err}", file=sys.stderr)
        return 1

    accepted_ids: list[str] = []
    for w in to_accept:
        wp_path = planning_dir / w.rel_path
        before = wp_path.read_text(encoding="utf-8")
        after = promote_wp_text_to_done(before)
        accepted_ids.append(w.wp_id)
        if not args.dry_run and after != before:
            wp_path.write_text(after, encoding="utf-8")

    # If dry_run with promotions, compute board preview against in-memory state if no disk writes occurred
    changed, changed_blocks = sync_work_board_file(planning_dir, dry_run=args.dry_run)

    result = {
        "ok": True,
        "dry_run": args.dry_run,
        "target": str(target_root),
        "accepted_wps": accepted_ids,
        "board_updated": changed,
        "changed_blocks": changed_blocks,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if accepted_ids:
            prefix = "[DRY-RUN] Would accept" if args.dry_run else "Accepted"
            print(f"{prefix} {len(accepted_ids)} WP(s) -> done: {', '.join(accepted_ids)}")
        if changed:
            prefix = "[DRY-RUN] Would sync" if args.dry_run else "Synced"
            print(f"{prefix} planning/30-work.md blocks: {', '.join(changed_blocks)}")
        elif not accepted_ids:
            print("planning/30-work.md is already in sync.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
