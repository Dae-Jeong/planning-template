"""Shared constants, rendering helpers, and Markdown parsers for planning-template."""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "templates"

VALID_WP_STATUSES = frozenset({
    "draft",
    "in_dev",
    "ready_for_qa",
    "qa_blocked",
    "ready_for_release",
    "done",
    "cancelled",
    "superseded",
})

MODES = ("standalone", "multi-repo-central", "multi-repo-impl")

PLACEHOLDER_RE = re.compile(r"__[A-Z][A-Z0-9_]*__")
FENCE_RE = re.compile(r"(?ms)(^(?:```|~~~).*?^(?:```|~~~)[^\n]*$)")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
MD_LINK_RE = re.compile(r"!\[[^\]]*\]\([^)]+\)|\[([^\]]+)\]\((<[^>]+>|[^\s)]+)(?:\s+\"[^\"]*\")?\)")


def render_template(text: str, variables: dict[str, str], flags: dict[str, bool]) -> str:
    """Render conditional marker blocks and replace template placeholders cleanly."""
    rendered = text
    for flag_name, enabled in flags.items():
        # Handle line-standalone conditional blocks first so removed blocks leave no blank lines
        line_block_re = re.compile(
            rf"(?ms)^[ \t]*<!-- IF_{flag_name} -->[ \t]*\n(.*?)^[ \t]*<!-- END_IF_{flag_name} -->[ \t]*\n?"
        )
        if enabled:
            rendered = line_block_re.sub(lambda m: m.group(1), rendered)
        else:
            rendered = line_block_re.sub("", rendered)

        # Handle inline / mixed conditional markers
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
    """Remove fenced code blocks and inline code spans before scanning links or placeholders."""
    parts = FENCE_RE.split(markdown)
    for idx in range(0, len(parts), 2):
        parts[idx] = INLINE_CODE_RE.sub("", parts[idx])
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
    lines = [line.strip() for line in strip_code_spans(section_body).splitlines()]
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


def extract_status_from_wp(markdown: str) -> str | None:
    """Read `- Status: <value>` from a WP Markdown file outside code blocks."""
    cleaned = strip_code_spans(markdown)
    match = re.search(r"(?m)^-\s*Status:\s*([a-zA-Z0-9_-]+)\s*$", cleaned)
    return match.group(1).strip() if match else None
