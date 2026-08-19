#!/usr/bin/env python3

from __future__ import annotations

import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from lint_skill import main, validate_skill


class SkillQaTests(unittest.TestCase):
    def make_skill(
        self,
        root: Path,
        name: str = "sample-skill",
        body: str = "# Sample\n\nFollow the exact procedure.",
        description: str = "Validate a sample. Use when a sample Skill changes.",
        with_agents: bool = True,
    ) -> Path:
        skill = root / name
        skill.mkdir()
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {description}\n---\n\n{body}\n",
            encoding="utf-8",
        )
        if with_agents:
            agents = skill / "agents"
            agents.mkdir()
            (agents / "openai.yaml").write_text(
                "interface:\n"
                f'  default_prompt: "Use ${name} to validate this sample."\n',
                encoding="utf-8",
            )
        return skill

    def test_valid_skill_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            report = validate_skill(self.make_skill(Path(temp)))
            self.assertEqual("PASS", report.result)

    def test_missing_reference_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = self.make_skill(
                Path(temp), body="# Sample\n\nRead [rules](references/missing.md)."
            )
            report = validate_skill(skill)
            self.assertEqual("FAIL", report.result)
            self.assertIn("REF001", {item.code for item in report.findings})

    def test_directory_name_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = self.make_skill(Path(temp))
            text = (skill / "SKILL.md").read_text(encoding="utf-8")
            (skill / "SKILL.md").write_text(
                text.replace("name: sample-skill", "name: different-skill"),
                encoding="utf-8",
            )
            report = validate_skill(skill)
            self.assertIn("META004", {item.code for item in report.findings})

    def test_vague_condition_warns_but_does_not_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = self.make_skill(
                Path(temp), body="# Sample\n\nUpdate the file when appropriate."
            )
            report = validate_skill(skill)
            self.assertEqual("WARN", report.result)
            self.assertIn("LANG001", {item.code for item in report.findings})
            with redirect_stdout(StringIO()):
                self.assertEqual(0, main([str(skill)]))
                self.assertEqual(1, main([str(skill), "--warnings-as-errors"]))

    def test_broad_destructive_command_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = self.make_skill(
                Path(temp), body="# Sample\n\nRun `rm -rf $HOME` to reset the environment."
            )
            report = validate_skill(skill)
            self.assertIn("SAFE001", {item.code for item in report.findings})
            self.assertEqual("FAIL", report.result)


if __name__ == "__main__":
    unittest.main()
