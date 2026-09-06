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

    def test_malformed_yaml_and_duplicate_keys_fail(self):
        for description in ("[broken", "valid\nname: overwritten", "[one, two]", "null"):
            with self.subTest(description=description), tempfile.TemporaryDirectory() as temp:
                report = validate_skill(self.make_skill(Path(temp), description=description))
                self.assertEqual("FAIL", report.result)

    def test_folded_yaml_description_is_supported(self):
        with tempfile.TemporaryDirectory() as temp:
            skill = self.make_skill(Path(temp), description=">\n  Validate a sample.\n  Use when a sample changes.")
            self.assertEqual("PASS", validate_skill(skill).result)

    def test_link_spaces_parentheses_titles_and_escapes(self):
        with tempfile.TemporaryDirectory() as temp:
            skill = self.make_skill(Path(temp), body="""# Sample

Read [one](<references/a b.md>).
Read [two](references/a%20b.md "Title").
Read [three](references/a (b).md).
Read [four](references/a b.md).
Read [five](references/a\\ \\(b\\).md).
""")
            refs = skill / "references"
            refs.mkdir()
            (refs / "a b.md").write_text("Known reference.", encoding="utf-8")
            (refs / "a (b).md").write_text("Known reference.", encoding="utf-8")
            self.assertEqual("PASS", validate_skill(skill).result)

    def test_example_links_inside_fences_and_inline_code_are_not_dependencies(self):
        with tempfile.TemporaryDirectory() as temp:
            skill = self.make_skill(Path(temp), body="""# Sample

```markdown
[example](references/nonexistent.md)
```
~~~md
[example](references/nonexistent2.md)
~~~
Use the syntax `[example](references/nonexistent3.md)`.
""")
            self.assertEqual("PASS", validate_skill(skill).result)

    def test_reference_documents_are_checked_relative_to_their_location(self):
        with tempfile.TemporaryDirectory() as temp:
            skill = self.make_skill(Path(temp), body="Read [rules](references/rules.md).")
            refs = skill / "references"
            refs.mkdir()
            (refs / "rules.md").write_text("Read [details](missing.md).", encoding="utf-8")
            failures = [f for f in validate_skill(skill).findings if f.severity == "FAIL"]
            self.assertEqual(1, len(failures))
            self.assertEqual("rules.md", Path(failures[0].file).name)

    def test_missing_literal_script_is_a_review_hint_not_false_structural_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            skill = self.make_skill(Path(temp), body="""Run `scripts/verify.py`.

```bash
python scripts/missing.py
```
```python
example = "scripts/sample.py"
```
Use `scripts/<name>.py`, `$TOOL_DIR/scripts/unknown.py`, or `scripts/{name}.py`.
""")
            findings = [f for f in validate_skill(skill).findings if f.code == "REF002"]
            self.assertEqual(2, len(findings))
            self.assertTrue(all(f.severity == "WARN" for f in findings))

    def test_runtime_name_profile_warns_for_vendor_names(self):
        with tempfile.TemporaryDirectory() as temp:
            skill = self.make_skill(Path(temp), name="Vendor-Skill")
            self.assertEqual("FAIL", validate_skill(skill).result)
            runtime = validate_skill(skill, profile="runtime")
            self.assertEqual("WARN", runtime.result)
            self.assertIn("META003", {f.code for f in runtime.findings})

    def test_product_specific_metadata_warns(self):
        with tempfile.TemporaryDirectory() as temp:
            skill = self.make_skill(Path(temp))
            entry = skill / "SKILL.md"
            entry.write_text(entry.read_text(encoding="utf-8").replace("name: sample-skill", "name: sample-skill\nargument-hint: file\ndisable-model-invocation: true"), encoding="utf-8")
            self.assertEqual("WARN", validate_skill(skill).result)

    def test_quick_validator_treats_runtime_metadata_as_warning(self):
        import importlib.util
        path = Path(__file__).resolve().parents[2] / "skill-creator" / "scripts" / "quick_validate.py"
        spec = importlib.util.spec_from_file_location("quick_validate", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temp:
            skill = self.make_skill(Path(temp))
            entry = skill / "SKILL.md"
            entry.write_text(entry.read_text(encoding="utf-8").replace("name: sample-skill", "name: sample-skill\nargument-hint: file\ndisable-model-invocation: true"), encoding="utf-8")
            valid, message = module.validate_skill(skill)
            self.assertTrue(valid)
            self.assertIn("WARN:", message)
            entry.write_text("---\nname: ''\ndescription: ''\n---\n", encoding="utf-8")
            self.assertFalse(module.validate_skill(skill)[0])


if __name__ == "__main__":
    unittest.main()
