"""Exercise sync scripts only in disposable repositories and homes.

Run: python scripts/tests/test_sync_local_skills.py
PowerShell and Bash/rsync cases skip explicitly when their runtime is unavailable.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
PWSH = shutil.which("pwsh") or shutil.which("powershell")
GIT_BASH = Path("C:/Program Files/Git/bin/bash.exe")
BASH = str(GIT_BASH) if GIT_BASH.is_file() else shutil.which("bash")


def bash_has_rsync() -> bool:
    if not BASH or os.name == "nt":
        return False
    return subprocess.run([BASH, "-lc", "command -v rsync"], capture_output=True).returncode == 0


HAS_RSYNC = bash_has_rsync()


def posix_path(path: Path) -> str:
    value = path.resolve().as_posix()
    if os.name == "nt" and len(value) > 2 and value[1] == ":":
        return "/" + value[0].lower() + value[2:]
    return value


class SyncCases:
    runner: str

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="skills-sync-test-")
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.home = self.root / "home"
        self.target = self.home / ".agents" / "skills"
        (self.repo / "scripts").mkdir(parents=True)
        (self.repo / "skills").mkdir()
        (self.repo / "disabled_skills").mkdir()
        self.target.mkdir(parents=True)
        for filename in ("sync-local-skills.ps1", "sync-local-skills.sh", "transitional-skills.txt"):
            shutil.copy2(SCRIPTS / filename, self.repo / "scripts" / filename)
        self.make_skill("alpha", b"new alpha\n")
        self.make_skill("writing-for-agents", b"new writing guide\n")
        self.make_skill("canvas-design", b"new canvas\n", disabled=True)
        self.put(self.target / "alpha" / "SKILL.md", b"old alpha\n")
        self.put(self.target / "alpha" / "local-only.txt", b"local knowledge\n")
        self.put(self.target / "writing-great-skills" / "SKILL.md", b"legacy knowledge\n")

    def tearDown(self) -> None:
        # Verify the recursive cleanup target is this test's allocated temporary root.
        self.assertEqual(self.root.resolve().parent, Path(tempfile.gettempdir()).resolve())
        self.assertTrue(self.root.name.startswith("skills-sync-test-"))
        self.temp.cleanup()

    @staticmethod
    def put(path: Path, data: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def make_skill(self, name: str, text: bytes, disabled: bool = False) -> Path:
        directory = self.repo / ("disabled_skills" if disabled else "skills") / name
        self.put(directory / "SKILL.md", text)
        return directory

    def run_sync(self, names: tuple[str, ...] = (), disabled: bool = False,
                 archive: bool = False, whatif: bool = False, transitional: bool = False) -> subprocess.CompletedProcess:
        if self.runner == "powershell":
            script = self.repo / "scripts" / "sync-local-skills.ps1"
            # A small invocation file preserves true PowerShell string-array arguments.
            invocation = self.root / "invoke.ps1"
            quote = lambda value: "'" + str(value).replace("'", "''") + "'"
            command = "& " + quote(script) + " -Agents -SkillsHome " + quote(self.home)
            if names:
                command += " -SkillNames @(" + ",".join(quote(n) for n in names) + ")"
            if disabled:
                command += " -IncludeDisabled"
            if transitional:
                command += " -IncludeTransitional"
            if archive:
                command += " -ArchiveLegacy"
            if whatif:
                command += " -WhatIf"
            invocation.write_text("$ErrorActionPreference = 'Stop'\n" + command + "\n", encoding="utf-8")
            args = [PWSH, "-NoProfile", "-NonInteractive", "-File", str(invocation)]
        else:
            args = [BASH, posix_path(self.repo / "scripts" / "sync-local-skills.sh"),
                    "--agents", "--skills-home", posix_path(self.home)]
            for name in names:
                args += ["--skill", name]
            if disabled:
                args += ["--include-disabled"]
            if transitional:
                args += ["--include-transitional"]
            if archive:
                args += ["--archive-legacy"]
        return subprocess.run(args, cwd=self.repo, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=40)

    def backup_files(self) -> list[Path]:
        return sorted((self.home / ".agents" / "skills-backups").glob("**/SKILL.md"))

    def assert_success(self, result: subprocess.CompletedProcess) -> None:
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_changed_backup_restore_noop_and_extra_file(self) -> None:
        result = self.run_sync(("alpha",))
        self.assert_success(result)
        self.assertEqual((self.target / "alpha" / "SKILL.md").read_bytes(), b"new alpha\n")
        self.assertEqual((self.target / "alpha" / "local-only.txt").read_bytes(), b"local knowledge\n")
        self.assertFalse((self.target / "writing-for-agents").exists())
        self.assertTrue((self.target / "writing-great-skills" / "SKILL.md").is_file())
        originals = self.backup_files()
        self.assertEqual(len(originals), 1)
        self.assertEqual(originals[0].read_bytes(), b"old alpha\n")
        self.assert_success(self.run_sync(("alpha",)))
        self.assertEqual(self.backup_files(), originals, "Unchanged rerun must not add overwritten-file backups")
        shutil.copy2(originals[0], self.target / "alpha" / "SKILL.md")
        restored = (self.target / "alpha" / "SKILL.md").read_bytes()
        self.assertEqual(hashlib.sha256(restored).digest(), hashlib.sha256(b"old alpha\n").digest())

    def test_new_files_added_without_deleting_local_files(self) -> None:
        self.put(self.repo / "skills" / "alpha" / "references" / "guide.md", b"new reference\n")
        self.assert_success(self.run_sync(("alpha",)))
        self.assertEqual((self.target / "alpha" / "references" / "guide.md").read_bytes(), b"new reference\n")
        self.assertEqual((self.target / "alpha" / "local-only.txt").read_bytes(), b"local knowledge\n")

    def test_disabled_requires_selection_and_existing_install(self) -> None:
        self.assertNotEqual(self.run_sync(disabled=True).returncode, 0)
        self.assertNotEqual(self.run_sync(("canvas-design",), disabled=True).returncode, 0)
        self.assertFalse((self.target / "canvas-design").exists())
        self.put(self.target / "canvas-design" / "SKILL.md", b"old canvas\n")
        self.assertNotEqual(self.run_sync(("canvas-design",)).returncode, 0)
        self.assert_success(self.run_sync(("canvas-design",), disabled=True))
        self.assertEqual((self.target / "canvas-design" / "SKILL.md").read_bytes(), b"new canvas\n")
        self.assertEqual(self.backup_files()[0].read_bytes(), b"old canvas\n")
        self.assertEqual((self.target / "alpha" / "SKILL.md").read_bytes(), b"old alpha\n")

    def test_transitional_default_preserves_existing_and_installs_missing(self) -> None:
        self.make_skill("content-radar", b"public weekly fallback\n")
        self.make_skill("github-stars-radar", b"public collector fallback\n")
        self.put(self.target / "content-radar" / "SKILL.md", b"externally managed weekly\n")
        result = self.run_sync()
        self.assert_success(result)
        self.assertIn("SKIP transitional/external", result.stdout)
        self.assertEqual((self.target / "content-radar" / "SKILL.md").read_bytes(), b"externally managed weekly\n")
        self.assertEqual((self.target / "github-stars-radar" / "SKILL.md").read_bytes(), b"public collector fallback\n")
        self.assertFalse(any(path.parent.name == "content-radar" for path in self.backup_files()))

    def test_transitional_overwrite_requires_flag_and_explicit_selection(self) -> None:
        self.make_skill("content-radar", b"public weekly fallback\n")
        self.put(self.target / "content-radar" / "SKILL.md", b"externally managed weekly\n")
        self.assertNotEqual(self.run_sync(transitional=True).returncode, 0)
        self.assertNotEqual(self.run_sync(("alpha", "content-radar")).returncode, 0)
        self.assertEqual((self.target / "alpha" / "SKILL.md").read_bytes(), b"old alpha\n")
        self.assertFalse(self.backup_files())
        self.assert_success(self.run_sync(("content-radar",), transitional=True))
        self.assertEqual((self.target / "content-radar" / "SKILL.md").read_bytes(), b"public weekly fallback\n")
        self.assertEqual(self.backup_files()[0].read_bytes(), b"externally managed weekly\n")

    def test_transitional_override_stays_within_explicit_selection(self) -> None:
        for name in ("content-radar", "github-stars-radar"):
            self.make_skill(name, b"public fallback\n")
            self.put(self.target / name / "SKILL.md", b"externally managed\n")
        self.assert_success(self.run_sync(("content-radar",), transitional=True))
        self.assertEqual((self.target / "content-radar" / "SKILL.md").read_bytes(), b"public fallback\n")
        self.assertEqual((self.target / "github-stars-radar" / "SKILL.md").read_bytes(), b"externally managed\n")

    def test_missing_transitional_policy_fails_before_copy(self) -> None:
        (self.repo / "scripts" / "transitional-skills.txt").unlink()
        self.assertNotEqual(self.run_sync(("alpha",)).returncode, 0)
        self.assertEqual((self.target / "alpha" / "SKILL.md").read_bytes(), b"old alpha\n")
        self.assertFalse(self.backup_files())

    def test_legacy_archive_is_opt_in_and_scoped(self) -> None:
        self.assert_success(self.run_sync(("writing-for-agents",)))
        self.assertTrue((self.target / "writing-great-skills" / "SKILL.md").is_file())
        self.assert_success(self.run_sync(("alpha",), archive=True))
        self.assertTrue((self.target / "writing-great-skills" / "SKILL.md").is_file())
        self.assert_success(self.run_sync(("writing-for-agents",), archive=True))
        self.assertFalse((self.target / "writing-great-skills").exists())
        archived = list((self.home / ".agents" / "skills-archive").glob("writing-great-skills-*/SKILL.md"))
        self.assertEqual(len(archived), 1)
        self.assertEqual(archived[0].read_bytes(), b"legacy knowledge\n")

    def test_invalid_name_and_type_conflict_fail_before_copy(self) -> None:
        self.assertNotEqual(self.run_sync(("../outside",)).returncode, 0)
        self.put(self.repo / "skills" / "alpha" / "blocked" / "new.txt", b"new nested file\n")
        self.put(self.target / "alpha" / "blocked", b"keep local file\n")
        self.assertNotEqual(self.run_sync(("alpha",)).returncode, 0)
        self.assertEqual((self.target / "alpha" / "SKILL.md").read_bytes(), b"old alpha\n")
        self.assertFalse(self.backup_files())

    def link_directory(self, link: Path, destination: Path) -> None:
        try:
            link.symlink_to(destination, target_is_directory=True)
            return
        except OSError:
            if os.name != "nt" or not PWSH:
                self.skipTest("Directory symlinks cannot be created by this test environment")
        # Windows directory junctions exercise reparse protection without admin privileges.
        script = self.root / "junction.ps1"
        script.write_text("param([string]$Link, [string]$Destination)\nNew-Item -ItemType Junction -Path $Link -Target $Destination | Out-Null\n", encoding="utf-8")
        result = subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-File", str(script),
                                 "-Link", str(link), "-Destination", str(destination)], capture_output=True)
        if result.returncode:
            self.skipTest("Directory symlinks or junctions cannot be created by this test environment")

    def test_destination_link_is_rejected(self) -> None:
        external = self.root / "outside"
        external.mkdir()
        self.put(external / "SKILL.md", b"outside untouched\n")
        linked = self.target / "linked-skill"
        self.make_skill("linked-skill", b"new linked content\n")
        self.link_directory(linked, external)
        try:
            self.assertNotEqual(self.run_sync(("linked-skill",)).returncode, 0)
            self.assertEqual((external / "SKILL.md").read_bytes(), b"outside untouched\n")
        finally:
            linked.unlink() if linked.is_symlink() else linked.rmdir()

    def test_nested_source_link_is_rejected(self) -> None:
        external = self.root / "outside"
        external.mkdir()
        self.put(external / "private.txt", b"unrelated source\n")
        linked = self.repo / "skills" / "alpha" / "linked"
        self.link_directory(linked, external)
        try:
            self.assertNotEqual(self.run_sync(("alpha",)).returncode, 0)
            self.assertEqual((self.target / "alpha" / "SKILL.md").read_bytes(), b"old alpha\n")
            self.assertFalse((self.target / "alpha" / "linked").exists())
        finally:
            linked.unlink() if linked.is_symlink() else linked.rmdir()

    def test_backup_link_is_rejected_before_copy(self) -> None:
        external = self.root / "outside"
        external.mkdir()
        linked = self.home / ".agents" / "skills-backups"
        self.link_directory(linked, external)
        try:
            self.assertNotEqual(self.run_sync(("alpha",)).returncode, 0)
            self.assertEqual((self.target / "alpha" / "SKILL.md").read_bytes(), b"old alpha\n")
            self.assertFalse(list(external.iterdir()))
        finally:
            linked.unlink() if linked.is_symlink() else linked.rmdir()


@unittest.skipUnless(PWSH, "PowerShell runtime is not installed")
class PowerShellSyncTests(SyncCases, unittest.TestCase):
    runner = "powershell"

    def test_whatif_does_not_write_or_archive(self) -> None:
        self.assert_success(self.run_sync(("alpha", "writing-for-agents"), archive=True, whatif=True))
        self.assertEqual((self.target / "alpha" / "SKILL.md").read_bytes(), b"old alpha\n")
        self.assertFalse((self.target / "writing-for-agents").exists())
        self.assertFalse(self.backup_files())
        self.assertTrue((self.target / "writing-great-skills" / "SKILL.md").is_file())


@unittest.skipUnless(BASH and HAS_RSYNC, "Bash and rsync are required for these integration cases")
class BashSyncTests(SyncCases, unittest.TestCase):
    runner = "bash"


if __name__ == "__main__":
    unittest.main(verbosity=2)
