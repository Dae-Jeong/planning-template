"""Unit and integration tests for planning-template init, sync, and check scripts."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import check_planning  # noqa: E402
import common  # noqa: E402
import init_planning  # noqa: E402
import sync_planning  # noqa: E402


def make_wp_markdown(
    wp_id: str,
    title: str,
    *,
    phase: str = "1",
    status: str = "draft",
    covers_spec: str = "ACME-SPEC-001",
    blocker: str = "-",
    human_check: str = "none",
    reusable_insight: str = "none",
    tech_checked: bool = True,
    owner_checked: bool = False,
) -> str:
    """Build a synthetic WP Markdown file for testing."""
    t_mark = "x" if tech_checked else " "
    o_mark = "x" if owner_checked else " "
    return (
        f"# {wp_id} {title}\n\n"
        f"## 메타\n\n"
        f"- Phase: {phase}\n"
        f"- Status: {status}\n"
        f"- Owner: agent\n"
        f"- Covers SPEC: {covers_spec}\n"
        f"- Related Decision: ACME-DEC-001\n"
        f"- Dependencies: -\n"
        f"- Blocker: {blocker}\n"
        f"- Human Check: {human_check}\n"
        f"- Reusable Insight: {reusable_insight}\n\n"
        f"## Release Gate\n\n"
        f"- [{t_mark}] 연결된 SPEC 최신화\n"
        f"- [{t_mark}] Log / DB / FE 1차 증거 확인\n"
        f"- [{o_mark}] Decision Owner / Human Check 최종 확인\n"
    )


class PlanningScriptsTests(unittest.TestCase):
    """Verify bootstrapping, auto-sync, 2-track acceptance, distill, and drift guards."""

    def test_render_template_conditional_blocks(self) -> None:
        raw = (
            "Top\n"
            "<!-- IF_API -->\nAPI block __PROJECT_CODE__\n<!-- END_IF_API -->\n"
            "<!-- IF_NO_QA -->No QA line<!-- END_IF_NO_QA -->\n"
            "Bottom\n"
        )
        rendered = common.render_template(
            raw,
            {"PROJECT_CODE": "DEMO"},
            {"API": True, "NO_QA": False},
        )
        self.assertEqual(rendered, "Top\nAPI block DEMO\nBottom\n")

    def test_init_and_check_standalone_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "acme-app"
            rc_init = init_planning.main([
                "--target", str(target),
                "--code", "ACME",
                "--name", "Acme App",
            ])
            self.assertEqual(rc_init, 0)
            self.assertTrue((target / "AGENTS.md").is_file())
            self.assertTrue((target / "planning/20-spec/api/README.md").is_file())
            self.assertTrue((target / "planning/20-spec/qa-matrix.md").is_file())
            self.assertEqual(check_planning.main(["--target", str(target), "--strict"]), 0)

    def test_init_with_local_exclude_in_git_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "company-repo"
            target.mkdir()
            subprocess.run(["git", "-C", str(target), "init", "-q"], check=True)
            (target / "AGENTS.md").write_text("# Team Agents\n", encoding="utf-8")

            rc_init = init_planning.main([
                "--target", str(target),
                "--code", "CMP",
                "--name", "Company Service",
                "--local-exclude",
            ])
            self.assertEqual(rc_init, 0)
            exclude_text = (target / ".git/info/exclude").read_text(encoding="utf-8")
            self.assertIn("/planning/", exclude_text)
            self.assertIn("/AGENTS.planning.snippet.md", exclude_text)

            # Verify git status remains clean in the company repo!
            status_out = subprocess.run(
                ["git", "-C", str(target), "status", "--porcelain", "--untracked-files=all"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.splitlines()
            self.assertEqual(status_out, ["?? AGENTS.md"])
            self.assertEqual(check_planning.main(["--target", str(target), "--strict"]), 0)

    def test_init_and_check_without_api_or_qa_and_with_obsidian(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "batch-worker"
            target.mkdir()
            (target / "AGENTS.md").write_text("# Existing Agents\n", encoding="utf-8")

            rc_init = init_planning.main([
                "--target", str(target),
                "--code", "BAT",
                "--name", "Batch Worker",
                "--obsidian",
                "--no-api",
                "--no-qa",
            ])
            self.assertEqual(rc_init, 0)
            self.assertEqual((target / "AGENTS.md").read_text(encoding="utf-8"), "# Existing Agents\n")
            self.assertTrue((target / "AGENTS.planning.snippet.md").is_file())
            self.assertFalse((target / "planning/20-spec/api").exists())
            self.assertFalse((target / "planning/20-spec/qa-matrix.md").exists())
            self.assertTrue((target / "tasks/README.md").is_file())
            self.assertEqual(check_planning.main(["--target", str(target), "--strict"]), 0)

    def test_init_and_check_multi_repo_modes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            central = Path(tmp) / "shop-planning"
            impl = Path(tmp) / "shop-backend"

            self.assertEqual(init_planning.main([
                "--target", str(central),
                "--code", "SHOP",
                "--name", "Shop Platform",
                "--mode", "multi-repo-central",
            ]), 0)
            self.assertTrue((central / "planning/rules/multi-repo-boundaries.md").is_file())
            self.assertEqual(check_planning.main(["--target", str(central), "--strict"]), 0)

            self.assertEqual(init_planning.main([
                "--target", str(impl),
                "--code", "SHOP",
                "--name", "Shop Platform",
                "--mode", "multi-repo-impl",
                "--central-ref", "../shop-planning",
            ]), 0)
            self.assertTrue((impl / "wiki/document-ownership.md").is_file())
            self.assertEqual(check_planning.main(["--target", str(impl), "--strict"]), 0)

    def test_sync_two_track_queue_accept_and_distill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "acme"
            self.assertEqual(init_planning.main(["--target", str(target), "--code", "ACME", "--name", "Acme"]), 0)

            # Remove WP-002 from pre-kickoff roadmap before starting work-002
            work_board = target / "planning/30-work.md"
            work_board.write_text(
                work_board.read_text(encoding="utf-8").replace("| ACME-WP-002 |", "| ACME-WP-010 |"),
                encoding="utf-8",
            )

            # Create WP-002 (agent_verified, Human Check: none, with insight) and WP-003 (awaiting_human)
            (target / "planning/30-work/work-002-db-lock.md").write_text(
                make_wp_markdown(
                    "ACME-WP-002",
                    "DB Advisory Lock",
                    status="agent_verified",
                    human_check="none",
                    reusable_insight="PostgreSQL 벌크 시드 경합은 pg_try_advisory_xact_lock으로 차단",
                ),
                encoding="utf-8",
            )
            (target / "planning/30-work/work-003-checkout-sheet.md").write_text(
                make_wp_markdown(
                    "ACME-WP-003",
                    "Checkout Sheet UI",
                    status="awaiting_human",
                    human_check="375px 모바일 뷰포트에서 하단 시트 버튼 가림 확인",
                ),
                encoding="utf-8",
            )

            # Before sync -> check_planning must fail with board-out-of-sync
            proc_unsynced = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "check_planning.py"), "--target", str(target), "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc_unsynced.returncode, 1)
            codes = {i["code"] for i in json.loads(proc_unsynced.stdout)["issues"]}
            self.assertIn("board-out-of-sync", codes)

            # Run sync_planning.py -> HUMAN_QUEUE should contain ONLY ACME-WP-003!
            self.assertEqual(sync_planning.main(["--target", str(target)]), 0)
            synced_text = work_board.read_text(encoding="utf-8")
            hq_section = synced_text.split("<!-- AUTO:HUMAN_QUEUE:START -->")[1].split("<!-- AUTO:HUMAN_QUEUE:END -->")[0]
            self.assertIn("ACME-WP-003", hq_section)
            self.assertNotIn("ACME-WP-002", hq_section)
            self.assertEqual(check_planning.main(["--target", str(target), "--strict"]), 0)

            # Test --distill extracts only WP-002's Reusable Insight
            distill_out = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "sync_planning.py"), "--target", str(target), "--distill", "--json"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout
            distill_data = json.loads(distill_out)
            self.assertEqual(distill_data["count"], 1)
            self.assertEqual(distill_data["insights"][0]["wp_id"], "ACME-WP-002")

            # Batch-accept agent_verified (--accept-verified) and human queue (--accept WP-003)
            self.assertEqual(sync_planning.main(["--target", str(target), "--accept-verified", "--accept", "WP-003"]), 0)
            self.assertEqual(check_planning.main(["--target", str(target), "--strict"]), 0)
            hq_after = work_board.read_text(encoding="utf-8").split("<!-- AUTO:HUMAN_QUEUE:START -->")[1].split("<!-- AUTO:HUMAN_QUEUE:END -->")[0]
            self.assertIn("현재 사람 확인 대기", hq_after)

    def test_accept_refuses_unchecked_technical_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "acme"
            self.assertEqual(init_planning.main(["--target", str(target), "--code", "ACME", "--name", "Acme"]), 0)
            (target / "planning/30-work/work-003-incomplete.md").write_text(
                make_wp_markdown("ACME-WP-003", "Incomplete Tech Gate", status="in_dev", tech_checked=False),
                encoding="utf-8",
            )
            self.assertEqual(sync_planning.main(["--target", str(target), "--accept", "ACME-WP-003"]), 1)

    def test_drift_guards_stale_open_roadmap_dup_metadata_and_pattern_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "drift"
            self.assertEqual(init_planning.main(["--target", str(target), "--code", "DFT", "--name", "Drift App"]), 0)

            # 1. Inject stale OPEN-999 in 20-spec.md
            spec_md = target / "planning/20-spec.md"
            spec_md.write_text(spec_md.read_text(encoding="utf-8") + "\n미결 항목 DFT-OPEN-999 참조\n", encoding="utf-8")

            # 2. Start DFT-WP-002 WITHOUT removing DFT-WP-002 from roadmap table, AND set invalid awaiting_human with Human Check: none
            (target / "planning/30-work/work-002-started.md").write_text(
                make_wp_markdown("DFT-WP-002", "Started WP", covers_spec="DFT-SPEC-001", status="awaiting_human", human_check="none"),
                encoding="utf-8",
            )
            # 3. Add 4 more agent_verified WPs (WP-003..006 -> 5 WPs beyond anchor WP-001 -> triggers pattern-review-due)
            for num in range(3, 7):
                (target / f"planning/30-work/work-00{num}-feat.md").write_text(
                    make_wp_markdown(f"DFT-WP-00{num}", f"Feat {num}", covers_spec="DFT-SPEC-001", status="agent_verified"),
                    encoding="utf-8",
                )
            sync_planning.main(["--target", str(target)])

            proc = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "check_planning.py"), "--target", str(target), "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 1)
            report = json.loads(proc.stdout)
            issue_codes = {item["code"] for item in report["issues"]}
            self.assertIn("stale-open-reference", issue_codes)
            self.assertIn("roadmap-already-started", issue_codes)
            self.assertIn("wp-metadata-invalid", issue_codes)
            self.assertIn("pattern-review-due", issue_codes)


if __name__ == "__main__":
    unittest.main()
