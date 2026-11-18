#!/usr/bin/env python3
"""Bootstrap the canonical planning/ or impl wiki/ harness into a target repository."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import MODES, TEMPLATES_DIR, render_template  # noqa: E402


def normalize_slug(value: str) -> str:
    """Normalize a project name or directory name into a lowercase kebab-case slug."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip()).strip("-").lower()
    return slug or "project"


def collect_plan(
    target_root: Path,
    mode: str,
    variables: dict[str, str],
    flags: dict[str, bool],
    inject_agents: str,
) -> list[tuple[Path, str]]:
    """Build deterministic list of (destination_path, rendered_content) pairs to write."""
    plan: list[tuple[Path, str]] = []

    if mode in ("standalone", "multi-repo-central"):
        src_base = TEMPLATES_DIR / "standalone"
        dest_base = target_root / "planning"
        for src_path in sorted(src_base.rglob("*")):
            if not src_path.is_file():
                continue
            rel = src_path.relative_to(src_base).as_posix()
            if not flags["API"] and (rel == "20-spec/api" or rel.startswith("20-spec/api/")):
                continue
            if not flags["QA"] and rel == "20-spec/qa-matrix.md":
                continue
            text = src_path.read_text(encoding="utf-8")
            rendered = render_template(text, variables, flags) if text else ""
            plan.append((dest_base / rel, rendered))

        if mode == "multi-repo-central":
            central_src = TEMPLATES_DIR / "multi-repo/central/multi-repo-boundaries.md"
            plan.append((
                dest_base / "rules/multi-repo-boundaries.md",
                render_template(central_src.read_text(encoding="utf-8"), variables, flags),
            ))

        if flags["OBSIDIAN"] and not (target_root / "tasks").exists():
            bridge_src = TEMPLATES_DIR / "obsidian-bridge/tasks-README-note.md"
            plan.append((
                target_root / "tasks/README.md",
                render_template(bridge_src.read_text(encoding="utf-8"), variables, flags),
            ))

    elif mode == "multi-repo-impl":
        src_base = TEMPLATES_DIR / "multi-repo/impl-repo"
        for src_path in sorted(src_base.rglob("*")):
            if not src_path.is_file():
                continue
            rel = src_path.relative_to(src_base)
            rendered = render_template(src_path.read_text(encoding="utf-8"), variables, flags)
            plan.append((target_root / rel, rendered))

    if inject_agents != "skip":
        snippet_name = (
            "multi-repo-impl-agents.md"
            if mode == "multi-repo-impl"
            else "agents-planning-section.md"
        )
        snippet_text = render_template(
            (TEMPLATES_DIR / "agent-snippets" / snippet_name).read_text(encoding="utf-8"),
            variables,
            flags,
        )
        agents_path = target_root / "AGENTS.md"
        if inject_agents == "snippet" or (inject_agents == "auto" and agents_path.exists()):
            plan.append((target_root / "AGENTS.planning.snippet.md", snippet_text))
        elif inject_agents == "auto":
            plan.append((agents_path, snippet_text))

    return plan


def build_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser for init_planning.py."""
    parser = argparse.ArgumentParser(
        description="Initialize canonical planning/ or multi-repo wiki/ harness in a target project."
    )
    parser.add_argument("--target", required=True, help="Target repository root directory")
    parser.add_argument("--code", required=True, help="Uppercase project ID prefix (e.g. SHOP, LETS)")
    parser.add_argument("--name", required=True, help="Human-readable project name")
    parser.add_argument("--slug", default="", help="Kebab-case project slug (defaults to target dir name)")
    parser.add_argument("--api-prefix", default="/api/v1", help="Default HTTP API prefix (default: /api/v1)")
    parser.add_argument("--mode", choices=MODES, default="standalone", help="Planning layout topology")
    parser.add_argument("--central-ref", default="../planning-repo", help="Central planning path/ref for multi-repo-impl")
    parser.add_argument("--obsidian", action="store_true", help="Enable Obsidian orchestration Dual-SSOT bridge")
    parser.add_argument("--no-api", action="store_true", help="Omit 20-spec/api/ contract baseline")
    parser.add_argument("--no-qa", action="store_true", help="Omit 20-spec/qa-matrix.md baseline")
    parser.add_argument(
        "--inject-agents",
        choices=("auto", "snippet", "skip"),
        default="auto",
        help="auto writes AGENTS.md if missing or AGENTS.planning.snippet.md if AGENTS.md exists",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files in destination")
    parser.add_argument("--dry-run", action="store_true", help="Show planned writes without modifying disk")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON summary")
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for initializing the planning harness."""
    args = build_parser().parse_args(argv)
    target_root = Path(args.target).expanduser().resolve()
    if not target_root.exists():
        target_root.mkdir(parents=True, exist_ok=True)

    code = re.sub(r"[^A-Za-z0-9_-]", "", args.code.strip().upper())
    if not code:
        print("Error: --code must contain alphanumeric characters.", file=sys.stderr)
        return 2

    slug = normalize_slug(args.slug or target_root.name)
    variables = {
        "PROJECT_CODE": code,
        "PROJECT_NAME": args.name.strip(),
        "PROJECT_SLUG": slug,
        "API_PREFIX": args.api_prefix.strip() or "/api/v1",
        "DATE": date.today().isoformat(),
        "CENTRAL_REF": args.central_ref.strip() or "../planning-repo",
    }
    flags = {
        "API": not args.no_api,
        "QA": not args.no_qa,
        "NO_QA": args.no_qa,
        "OBSIDIAN": args.obsidian,
        "NOT_OBSIDIAN": not args.obsidian,
    }

    plan = collect_plan(target_root, args.mode, variables, flags, args.inject_agents)
    conflicts = [str(dst) for dst, _ in plan if dst.exists() and not args.force]
    if conflicts:
        msg = {
            "ok": False,
            "error": "Existing destination files found (pass --force to overwrite)",
            "conflicts": conflicts,
        }
        print(json.dumps(msg, ensure_ascii=False, indent=2) if args.json else f"Conflicts found:\n  " + "\n  ".join(conflicts), file=sys.stderr)
        return 1

    if not args.dry_run:
        for dst, content in plan:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(content, encoding="utf-8")

    summary = {
        "ok": True,
        "dry_run": args.dry_run,
        "target": str(target_root),
        "mode": args.mode,
        "code": code,
        "slug": slug,
        "obsidian": args.obsidian,
        "files_count": len(plan),
        "files": [str(dst.relative_to(target_root)) for dst, _ in plan],
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        verb = "Would create" if args.dry_run else "Created"
        print(f"{verb} {len(plan)} files in {target_root} (mode={args.mode}, code={code}, obsidian={args.obsidian})")
        print(f"Next: python3 {Path(__file__).resolve().parent / 'check_planning.py'} --target {target_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
