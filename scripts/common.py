"""Shared constants, rendering helpers, WP parsers, and board builders for planning-template."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "templates"

VALID_WP_STATUSES = frozenset({
    "draft",
    "in_dev",
    "qa_blocked",
    "agent_verified",
    "awaiting_human",
    "done",
    "cancelled",
    "superseded",
})

LEGACY_WP_STATUSES = frozenset({
    "ready_for_qa",
    "ready_for_release",
})

MODES = ("standalone", "multi-repo-central", "multi-repo-impl")

PLACEHOLDER_RE = re.compile(r"__[A-Z][A-Z0-9_]*__")
FENCE_RE = re.compile(r"(?ms)(^(?:```|~~~).*?^(?:```|~~~)[^\n]*$)")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
MD_LINK_RE = re.compile(r"!\[[^\]]*\]\([^)]+\)|\[([^\]]+)\]\((<[^>]+>|[^\s)]+)(?:\s+\"[^\"]*\")?\)")
ID_TOKEN_RE = re.compile(r"\b([A-Z][A-Z0-9_-]*-(?:DEC|OPEN|SPEC|WP)-\d+)\b")
SPEC_ID_RE = re.compile(r"\b([A-Z][A-Z0-9_-]*-SPEC-\d+)\b")
OPEN_ID_RE = re.compile(r"\b([A-Z][A-Z0-9_-]*-OPEN-\d+)\b")
WP_ID_RE = re.compile(r"\b([A-Z][A-Z0-9_-]*-WP-(\d+))\b")
OWNER_GATE_KEYWORDS = ("decision owner", "human check", "최종 승인", "최종 확인")

AUTO_BLOCKS = ("HUMAN_QUEUE", "WP_BOARD", "SPEC_COVERAGE", "OPEN_MIRROR")


@dataclass(frozen=True)
class WpRecord:
    """Parsed representation of a single 30-work/work-NNN-*.md file."""

    rel_path: str
    wp_id: str
    wp_num: int
    title: str
    phase: str
    status: str | None
    owner: str
    covers_spec: tuple[str, ...]
    covers_spec_raw: str
    related_decision: str
    dependencies: str
    blocker: str
    human_check: str
    reusable_insight: str
    unchecked_tech_gates: tuple[str, ...]
    unchecked_owner_gates: tuple[str, ...]
    checked_gates: tuple[str, ...]


def render_template(text: str, variables: dict[str, str], flags: dict[str, bool]) -> str:
    """Render conditional marker blocks and replace template placeholders cleanly."""
    rendered = text
    for flag_name, enabled in flags.items():
        line_block_re = re.compile(
            rf"(?ms)^[ \t]*<!-- IF_{flag_name} -->[ \t]*\n(.*?)^[ \t]*<!-- END_IF_{flag_name} -->[ \t]*\n?"
        )
        rendered = line_block_re.sub((lambda m: m.group(1)) if enabled else "", rendered)

        inline_re = re.compile(
            rf"(?s)[ \t]*<!-- IF_{flag_name} -->(.*?)<!-- END_IF_{flag_name} -->[ \t]*\n?"
        )
        if enabled:
            rendered = inline_re.sub(
                lambda m: m.group(1) + ("\n" if m.group(0).endswith("\n") and not m.group(1).endswith("\n") else ""),
                rendered,
            )
        else:
            rendered = inline_re.sub("", rendered)

    for key, value in variables.items():
        rendered = rendered.replace(f"__{key}__", value)
    return rendered


def strip_code_spans(markdown: str) -> str:
    """Remove fenced code blocks and inline code spans before scanning links or tokens."""
    parts = FENCE_RE.split(markdown)
    for idx in range(0, len(parts), 2):
        parts[idx] = INLINE_CODE_RE.sub("", parts[idx])
    return "".join(parts[idx] if idx % 2 == 0 else "" for idx in range(len(parts)))


def strip_fences_only(markdown: str) -> str:
    """Remove fenced code blocks while preserving inline code content."""
    parts = FENCE_RE.split(markdown)
    return "".join(parts[idx] if idx % 2 == 0 else "" for idx in range(len(parts)))


def iter_relative_links(markdown: str) -> list[str]:
    """Extract non-external Markdown link targets outside code fences and inline code."""
    cleaned = strip_code_spans(markdown)
    targets: list[str] = []
    for match in MD_LINK_RE.finditer(cleaned):
        raw_target = match.group(2)
        if not raw_target:
            continue
        target = raw_target.strip("<>").split("#", 1)[0].split("?", 1)[0].strip()
        if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            continue
        targets.append(target)
    return targets


def parse_markdown_sections(markdown: str) -> dict[str, str]:
    """Split a Markdown document into top-level H2 section names and bodies."""
    sections: dict[str, str] = {}
    current_heading = ""
    buf: list[str] = []
    for line in markdown.splitlines():
        if line.startswith("## "):
            sections[current_heading] = "\n".join(buf)
            current_heading = line[3:].strip()
            buf = []
        else:
            buf.append(line)
    sections[current_heading] = "\n".join(buf)
    return sections


def parse_table_rows(section_body: str) -> list[dict[str, str]]:
    """Parse standard GitHub-flavored Markdown tables in a section into column-keyed dicts."""
    rows: list[dict[str, str]] = []
    lines = [line.strip() for line in strip_fences_only(section_body).splitlines()]
    idx = 0
    while idx < len(lines):
        if lines[idx].startswith("|") and idx + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[idx + 1]):
            headers = [cell.strip() for cell in lines[idx].strip("|").split("|")]
            idx += 2
            while idx < len(lines) and lines[idx].startswith("|"):
                cells = [cell.strip() for cell in lines[idx].strip("|").split("|")]
                row = {
                    headers[c]: (cells[c] if c < len(cells) else "")
                    for c in range(len(headers))
                }
                rows.append(row)
                idx += 1
            continue
        idx += 1
    return rows


def is_owner_gate_label(label: str) -> bool:
    """Return True if a Release Gate checkbox line represents final human/owner acceptance."""
    lowered = label.lower()
    return any(keyword in lowered for keyword in OWNER_GATE_KEYWORDS)


def is_none_value(value: str) -> bool:
    """Return True if a metadata value represents an explicit empty/none marker."""
    cleaned = value.strip().strip("`").lower()
    return cleaned in ("", "-", "none", "n/a", "없음")


def escape_cell(value: str) -> str:
    """Escape pipe characters and normalize whitespace for Markdown table cells."""
    return " ".join(value.replace("|", "\\|").split())


def parse_wp_file(planning_dir: Path, wp_path: Path) -> WpRecord:
    """Parse H1, metadata bullets, and Release Gate checkboxes from a WP file."""
    rel_path = wp_path.relative_to(planning_dir).as_posix()
    text = wp_path.read_text(encoding="utf-8")
    no_fences = strip_fences_only(text)

    wp_id = wp_path.stem.upper()
    wp_num = 999999
    title = wp_path.stem
    h1_match = re.search(r"(?m)^#\s+(.+?)\s*$", no_fences)
    if h1_match:
        h1_raw = h1_match.group(1).strip()
        id_match = WP_ID_RE.search(h1_raw)
        if id_match:
            wp_id = id_match.group(1)
            wp_num = int(id_match.group(2))
            remainder = h1_raw[id_match.end():].strip(" -—:")
            title = remainder or wp_id
        else:
            title = h1_raw
    else:
        stem_num = re.search(r"work-(\d+)", wp_path.stem)
        if stem_num:
            wp_num = int(stem_num.group(1))

    sections = parse_markdown_sections(text)
    meta_body = strip_fences_only(sections.get("메타", ""))
    meta: dict[str, str] = {}
    for line in meta_body.splitlines():
        m = re.match(r"^-\s*([^:]+):\s*(.*?)\s*$", line.strip())
        if m:
            meta[m.group(1).strip().lower()] = m.group(2).strip()

    raw_status = meta.get("status", "").strip().strip("`") or None
    covers_raw = meta.get("covers spec", "-") or "-"
    spec_ids = tuple(dict.fromkeys(SPEC_ID_RE.findall(covers_raw)))

    gate_body = strip_fences_only(sections.get("Release Gate", ""))
    unchecked_tech: list[str] = []
    unchecked_owner: list[str] = []
    checked: list[str] = []
    for m in re.finditer(r"(?m)^-\s*\[([ xX])\]\s+(.+?)\s*$", gate_body):
        mark, label = m.group(1), m.group(2).strip()
        if mark in ("x", "X"):
            checked.append(label)
        elif is_owner_gate_label(label):
            unchecked_owner.append(label)
        else:
            unchecked_tech.append(label)

    return WpRecord(
        rel_path=rel_path,
        wp_id=wp_id,
        wp_num=wp_num,
        title=title,
        phase=meta.get("phase", "0") or "0",
        status=raw_status,
        owner=meta.get("owner", "-") or "-",
        covers_spec=spec_ids,
        covers_spec_raw=covers_raw,
        related_decision=meta.get("related decision", "-") or "-",
        dependencies=meta.get("dependencies", "-") or "-",
        blocker=meta.get("blocker", "-") or "-",
        human_check=meta.get("human check", "none") or "none",
        reusable_insight=meta.get("reusable insight", "none") or "none",
        unchecked_tech_gates=tuple(unchecked_tech),
        unchecked_owner_gates=tuple(unchecked_owner),
        checked_gates=tuple(checked),
    )


def load_all_wps(planning_dir: Path) -> list[WpRecord]:
    """Load and deterministically sort all work-*.md records under planning/30-work/."""
    work_dir = planning_dir / "30-work"
    if not work_dir.is_dir():
        return []
    records = [parse_wp_file(planning_dir, p) for p in sorted(work_dir.glob("work-*.md"))]
    return sorted(records, key=lambda r: (r.wp_num, r.rel_path))


def load_active_open_decisions(planning_dir: Path) -> list[dict[str, str]]:
    """Return rows from 10-decision.md '남은 결정 (OPEN)' section."""
    dec_path = planning_dir / "10-decision.md"
    if not dec_path.is_file():
        return []
    sections = parse_markdown_sections(dec_path.read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    for heading, body in sections.items():
        if "남은 결정" in heading or "OPEN" in heading:
            rows.extend(parse_table_rows(body))
    return rows


def render_auto_blocks(planning_dir: Path) -> dict[str, str]:
    """Generate the 4 deterministic AUTO block payloads for planning/30-work.md."""
    wps = load_all_wps(planning_dir)

    # 1. HUMAN_QUEUE
    human_wps = [w for w in wps if w.status == "awaiting_human"]
    if human_wps:
        hq_lines = [
            "| WP | 제목 | Covers SPEC | Human Check 항목 | 파일 |",
            "| --- | --- | --- | --- | --- |",
        ]
        for w in human_wps:
            fname = Path(w.rel_path).name
            hq_lines.append(
                f"| {escape_cell(w.wp_id)} | {escape_cell(w.title)} | {escape_cell(w.covers_spec_raw)} "
                f"| {escape_cell(w.human_check)} | [{fname}]({w.rel_path}) |"
            )
        human_queue_md = "\n".join(hq_lines)
    else:
        human_queue_md = "_현재 사람 확인 대기(`awaiting_human`) 항목이 없습니다._"

    # 2. WP_BOARD
    if wps:
        wb_lines = [
            "| Phase | ID | 제목 | Covers SPEC | Status | Owner | Blocker | Human Check | 파일 |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for w in wps:
            fname = Path(w.rel_path).name
            st = w.status or "unknown"
            hc = "none" if is_none_value(w.human_check) else w.human_check
            wb_lines.append(
                f"| {escape_cell(w.phase)} | {escape_cell(w.wp_id)} | {escape_cell(w.title)} "
                f"| {escape_cell(w.covers_spec_raw)} | {escape_cell(st)} | {escape_cell(w.owner)} "
                f"| {escape_cell(w.blocker)} | {escape_cell(hc)} | [{fname}]({w.rel_path}) |"
            )
        wp_board_md = "\n".join(wb_lines)
    else:
        wp_board_md = "_등록된 실행 WP 파일(`30-work/work-*.md`)이 없습니다._"

    # 3. SPEC_COVERAGE
    spec_path = planning_dir / "20-spec.md"
    spec_rows: list[dict[str, str]] = []
    if spec_path.is_file():
        spec_sections = parse_markdown_sections(spec_path.read_text(encoding="utf-8"))
        for heading, body in spec_sections.items():
            if "SPEC List" in heading:
                spec_rows.extend(parse_table_rows(body))

    if spec_rows:
        sc_lines = [
            "| Spec ID | 제목 | Spec Status | Covering WPs | 진행 요약 |",
            "| --- | --- | --- | --- | --- |",
        ]
        for row in spec_rows:
            sid_raw = row.get("ID", "").strip()
            sids = SPEC_ID_RE.findall(sid_raw)
            sid = sids[0] if sids else sid_raw
            stitle = row.get("제목", "").strip()
            sstatus = row.get("Status", "").strip()
            covering = [w for w in wps if sid in w.covers_spec]
            if covering:
                wp_ids_str = ", ".join(w.wp_id for w in covering)
                counts = Counter((w.status or "unknown") for w in covering)
                summary_str = ", ".join(f"{k}: {counts[k]}" for k in sorted(counts))
            else:
                wp_ids_str = "-"
                summary_str = "미커버 (0 WPs)"
            sc_lines.append(
                f"| {escape_cell(sid)} | {escape_cell(stitle)} | {escape_cell(sstatus)} "
                f"| {escape_cell(wp_ids_str)} | {escape_cell(summary_str)} |"
            )
        spec_cov_md = "\n".join(sc_lines)
    else:
        spec_cov_md = "_`20-spec.md`에 등록된 SPEC 항목이 없습니다._"

    # 4. OPEN_MIRROR
    open_rows = load_active_open_decisions(planning_dir)
    active_open_rows = [r for r in open_rows if OPEN_ID_RE.search(r.get("ID", ""))]
    if active_open_rows:
        om_lines = [
            "| ID | 결정 필요 항목 | Owner | Source |",
            "| --- | --- | --- | --- |",
        ]
        for r in active_open_rows:
            oid = r.get("ID", "").strip()
            item = r.get("결정 필요 항목", "").strip()
            owner = r.get("Owner", "-").strip() or "-"
            om_lines.append(
                f"| {escape_cell(oid)} | {escape_cell(item)} | {escape_cell(owner)} | [10-decision.md](10-decision.md) |"
            )
        open_mirror_md = "\n".join(om_lines)
    else:
        open_mirror_md = "_현재 미결(`OPEN`) 항목이 없습니다._"

    return {
        "HUMAN_QUEUE": human_queue_md,
        "WP_BOARD": wp_board_md,
        "SPEC_COVERAGE": spec_cov_md,
        "OPEN_MIRROR": open_mirror_md,
    }


def apply_auto_blocks(work_markdown: str, blocks: dict[str, str]) -> tuple[str, list[str]]:
    """Replace <!-- AUTO:<NAME>:START -->...<!-- AUTO:<NAME>:END --> blocks and report changed block names."""
    updated = work_markdown
    changed_blocks: list[str] = []
    for name in AUTO_BLOCKS:
        pattern = re.compile(
            rf"(?s)(<!-- AUTO:{name}:START -->)\n?(.*?)\n?(<!-- AUTO:{name}:END -->)"
        )
        match = pattern.search(updated)
        if not match:
            continue
        current_inner = match.group(2).strip()
        desired_inner = blocks[name].strip()
        if current_inner != desired_inner:
            changed_blocks.append(name)
        replacement = f"{match.group(1)}\n{desired_inner}\n{match.group(3)}"
        updated = pattern.sub(lambda _, rep=replacement: rep, updated, count=1)
    return updated, changed_blocks
