"""Validate overlay packages in their intended shared install-root layout.

No user data or installed Skill is modified. NotebookLM remains an external
runtime dependency; --existing-root only checks required files and Python syntax.
"""
from __future__ import annotations
import argparse
import ast
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import shutil
import sys
import tempfile

REPO = Path(__file__).resolve().parents[2]
OVERLAYS = REPO / "compatibility_skills"
sys.path.insert(0, str(REPO / "skills" / "skill-qa-gate" / "scripts"))
from lint_skill import validate_skill
import yaml


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--existing-root", type=Path)
    args = parser.parse_args()
    manifest = json.loads((OVERLAYS / "manifest.json").read_text(encoding="utf-8"))
    entries = manifest["entries"]
    failures = []
    warnings = []
    names = [entry["name"] for entry in entries]
    if len(names) != len(set(names)):
        failures.append("Duplicate names in overlay manifest")
    packaged = {p.parent.name for p in OVERLAYS.glob("*/SKILL.md")}
    if packaged != set(names):
        failures.append("Manifest and overlay directories disagree")
    allowed_modes = {"overlay", "self-contained-script-overlay", "requires-existing-install", "documentation-overlay"}
    for entry in entries:
        if entry.get("mode") not in allowed_modes:
            failures.append(f"Unknown overlay mode: {entry['name']}")
        if entry.get("mode") == "requires-existing-install":
            required = entry.get("required_existing_files")
            if not isinstance(required, list) or not required or any(not isinstance(item, str) for item in required):
                failures.append(f"External runtime dependency declaration is missing or invalid: {entry['name']}")
                continue
            if len(required) != len(set(required)):
                failures.append(f"Duplicate external runtime dependencies: {entry['name']}")
            for relative in required:
                posix = PurePosixPath(relative)
                windows = PureWindowsPath(relative)
                if not relative or posix.is_absolute() or windows.is_absolute() or windows.drive or ".." in posix.parts or ".." in windows.parts:
                    failures.append(f"External dependency must be a relative path inside its Skill: {entry['name']}/{relative}")
    forbidden_parts = {"data", ".venv", "node_modules", "browser_state", "models"}
    forbidden_names = {".env", "cookies.json", "auth_info.json", "state.json", "library.json"}
    for name in names:
        directory = OVERLAYS / name
        for path in directory.rglob("*"):
            relative = path.relative_to(directory)
            if forbidden_parts.intersection(relative.parts) or path.name in forbidden_names:
                failures.append(f"Private/runtime file in overlay: {name}/{relative}")
            if path.is_file() and path.suffix == ".py":
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        agent = yaml.safe_load((directory / "agents" / "openai.yaml").read_text(encoding="utf-8"))
        expected = not next(e for e in entries if e["name"] == name)["manual_only"]
        if agent.get("policy", {}).get("allow_implicit_invocation") is not expected:
            failures.append(f"Invocation policy mismatch: {name}")
        if name.startswith("source-command-") and expected:
            failures.append(f"Legacy command is not manual-only: {name}")

    with tempfile.TemporaryDirectory(prefix="skill-overlay-validation-") as temp:
        stage = Path(temp)
        for canonical in (REPO / "skills").iterdir():
            if canonical.is_dir():
                shutil.copytree(canonical, stage / canonical.name,
                                ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", "node_modules", "data", "models"))
        for entry in entries:
            name = entry["name"]
            shutil.copytree(OVERLAYS / name, stage / name, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("__pycache__"))
            target = entry.get("canonical")
            if target and not (stage / target / "SKILL.md").is_file():
                failures.append(f"Missing canonical dependency: {name} -> {target}")
        for entry in entries:
            report = validate_skill(stage / entry["name"])
            for finding in report.findings:
                message = f'{entry["name"]}: {finding.code}: {finding.message}'
                (failures if finding.severity == "FAIL" else warnings).append(message)

    external = []
    for entry in entries:
        if entry.get("required_existing_files"):
            if args.existing_root:
                for relative in entry["required_existing_files"]:
                    path = args.existing_root / entry["name"] / relative
                    if not path.is_file():
                        failures.append(f"Required existing runtime file missing: {entry['name']}/{relative}")
                    elif path.suffix == ".py":
                        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
                external.append(f'{entry["name"]}: existing file presence/syntax checked; no login/query executed')
            else:
                external.append(f'{entry["name"]}: {len(entry["required_existing_files"])} required files declared with valid relative paths; existing runtime files not checked')
    print(json.dumps({"overlays":len(entries), "legacy_commands":sum(e["manual_only"] for e in entries),
                      "result":"FAIL" if failures else "WARN" if warnings else "PASS",
                      "failures":failures, "warnings":warnings, "external_runtime":external},
                     ensure_ascii=False, indent=2))
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
