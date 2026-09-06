"""Check public mirror policy in disposable repositories and mirror directories."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]


class ConsistencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="skills-consistency-test-")
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.mirror = self.root / "mirror"
        (self.repo / "scripts").mkdir(parents=True)
        self.mirror.mkdir()
        for name in ("check-skill-consistency.py", "transitional-skills.txt"):
            shutil.copy2(SCRIPTS / name, self.repo / "scripts" / name)
        (self.repo / "README.md").write_text("收錄 2 個 Active Skills: alpha, content-radar\n", encoding="utf-8")
        for root, name, content in [
            (self.repo / "skills", "alpha", "ordinary content"),
            (self.repo / "skills", "content-radar", "public fallback"),
            (self.mirror, "alpha", "ordinary content"),
            (self.mirror, "content-radar", "externally managed content"),
        ]:
            directory = root / name
            directory.mkdir(parents=True)
            (directory / "SKILL.md").write_text(content, encoding="utf-8")

    def tearDown(self) -> None:
        self.assertEqual(self.root.resolve().parent, Path(tempfile.gettempdir()).resolve())
        self.assertTrue(self.root.name.startswith("skills-consistency-test-"))
        self.temp.cleanup()

    def check(self, *options: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.repo / "scripts/check-skill-consistency.py"),
             "--mirror", str(self.mirror), *options],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=20,
        )

    def test_existing_transition_copy_is_readable_but_not_claimed_identical(self) -> None:
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("content not compared", result.stdout)
        self.assertIn("1 content comparison(s)", result.stdout)
        self.assertIn("1 transitional copy/copies", result.stdout)
        self.assertNotIn("skills consistent across README and mirrors", result.stdout)

    def test_explicit_transitional_comparison_reports_real_drift(self) -> None:
        result = self.check("--include-transitional")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("content-radar/SKILL.md differs", result.stderr)

    def test_explicit_transitional_comparison_accepts_matching_fallback(self) -> None:
        shutil.copy2(self.repo / "skills/content-radar/SKILL.md", self.mirror / "content-radar/SKILL.md")
        result = self.check("--include-transitional")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("2 content comparison(s)", result.stdout)
        self.assertIn("0 transitional copy/copies", result.stdout)

    def test_missing_transition_entry_point_still_fails(self) -> None:
        (self.mirror / "content-radar/SKILL.md").unlink()
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("transitional entry point is not readable", result.stderr)

    def test_missing_transition_directory_still_fails(self) -> None:
        (self.mirror / "content-radar/SKILL.md").unlink()
        (self.mirror / "content-radar").rmdir()
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing skill content-radar", result.stderr)

    def test_regular_skill_drift_is_not_exempt(self) -> None:
        (self.mirror / "alpha/SKILL.md").write_text("different", encoding="utf-8")
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("alpha/SKILL.md differs", result.stderr)

    def test_missing_shared_policy_fails_instead_of_overcomparing(self) -> None:
        (self.repo / "scripts/transitional-skills.txt").unlink()
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Cannot load transitional Skill policy", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
