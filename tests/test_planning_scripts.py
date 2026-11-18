"""Unit and integration tests for planning-template init and check scripts."""
from __future__ import annotations

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


class PlanningScriptsTests(unittest.TestCase):
    """Verify bootstrapping, validation, flag variants, and failure detection."""

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

            rc_check = check_planning.main(["--target", str(target), "--strict"])
            self.assertEqual(rc_check, 0)

    def test_init_and_check_without_api_or_qa_and_with_obsidian(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "batch-worker"
            (target / "AGENTS.md").parent.mkdir(parents=True, exist_ok=True)
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
            # Existing AGENTS.md must stay untouched while snippet is generated alongside
            self.assertEqual((target / "AGENTS.md").read_text(encoding="utf-8"), "# Existing Agents\n")
            self.assertTrue((target / "AGENTS.planning.snippet.md").is_file())
            self.assertFalse((target / "planning/20-spec/api").exists())
            self.assertFalse((target / "planning/20-spec/qa-matrix.md").exists())
            self.assertTrue((target / "tasks/README.md").is_file())

            rc_check = check_planning.main(["--target", str(target), "--strict"])
            self.assertEqual(rc_check, 0)

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

    def test_init_refuses_overwrite_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "demo"
            self.assertEqual(init_planning.main(["--target", str(target), "--code", "DM", "--name", "Demo"]), 0)
            self.assertEqual(init_planning.main(["--target", str(target), "--code", "DM", "--name", "Demo"]), 1)
            self.assertEqual(init_planning.main(["--target", str(target), "--code", "DM", "--name", "Demo", "--force"]), 0)

    def test_check_detects_broken_link_orphan_wp_unreplaced_placeholder_and_unchecked_done_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "broken-app"
            self.assertEqual(init_planning.main(["--target", str(target), "--code", "BRK", "--name", "Broken App"]), 0)

            # 1. Inject orphan WP marked done with an unchecked Release Gate
            orphan_wp = target / "planning/30-work/work-099-orphan.md"
            orphan_wp.write_text(
                "# BRK-WP-099 Orphan\n\n## 메타\n\n- Status: done\n\n## Release Gate\n\n- [ ] 미완료 항목\n",
                encoding="utf-8",
            )
            # 2. Inject broken link and unreplaced placeholder
            readme = target / "planning/README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8") + "\n[Dead](does-not-exist.md)\n__LEFT_OVER__\n",
                encoding="utf-8",
            )

            proc = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "check_planning.py"), "--target", str(target)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 1)
            self.assertIn("unindexed-wp", proc.stdout)
            self.assertIn("done-with-unchecked-gate", proc.stdout)
            self.assertIn("broken-link", proc.stdout)
            self.assertIn("unreplaced-placeholder", proc.stdout)


if __name__ == "__main__":
    unittest.main()
