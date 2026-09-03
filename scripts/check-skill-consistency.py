#!/usr/bin/env python3
"""Report drift between this repository, the README index, and each skill mirror.

`sync-local-skills.sh` pushes skills outward. Nothing checked afterwards whether
the copies still agreed, so a skill could ship without a README entry and a
mirror could sit two skills behind for days without anyone noticing.

Checks:
  1. the README's active-skill count matches the tree
  2. skills not named verbatim in the README are listed as a note
  3. every mirror holds every skill, with matching content

Mirrors default to ~/.agents/skills. Add more with --mirror, repeatable, or set
SKILLS_MIRRORS to an os.pathsep-separated list. Mirror paths are deliberately
not hardcoded: they differ per machine and some live in private cloud folders.

Exit status is 0 when everything agrees and 1 otherwise, so this can guard a
commit or run straight after a sync.
"""

from __future__ import annotations

import argparse
import filecmp
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
README = REPO_ROOT / "README.md"

IGNORED_NAMES = {".DS_Store", ".Rhistory", "__pycache__"}
IGNORED_SUFFIXES = (".pyc", ".pyo")
COUNT_PATTERN = re.compile(r"收錄 (\d+) 個 Active Skills")


def is_noise(path: Path) -> bool:
    name = path.name
    return (
        name in IGNORED_NAMES
        or name.startswith("._")
        or name.endswith(IGNORED_SUFFIXES)
    )


def skill_names(root: Path) -> set[str]:
    if not root.is_dir():
        return set()
    return {
        entry.name
        for entry in root.iterdir()
        if entry.is_dir() and (entry / "SKILL.md").is_file() and not is_noise(entry)
    }


def relative_files(root: Path) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and not any(is_noise(part) for part in path.parents)
        and not is_noise(path)
    }


def compare_trees(left: Path, right: Path) -> tuple[set[str], set[str]]:
    """Return (missing in right, differing content)."""
    left_files = relative_files(left)
    right_files = relative_files(right)
    missing = left_files - right_files
    differing = {
        name
        for name in left_files & right_files
        if not filecmp.cmp(left / name, right / name, shallow=False)
    }
    return missing, differing


def check_readme(problems: list[str]) -> None:
    if not README.is_file():
        problems.append(f"README not found at {README}")
        return
    text = README.read_text(encoding="utf-8")
    tree = skill_names(SKILLS_DIR)

    match = COUNT_PATTERN.search(text)
    if match is None:
        problems.append("README does not state an active-skill count")
    elif int(match.group(1)) != len(tree):
        problems.append(
            f"README claims {match.group(1)} active skills, the tree holds {len(tree)}"
        )

    # Not a failure: the index groups related skills under one heading (the
    # Office family, the sp-* workflow set), so a name can be covered without
    # appearing verbatim. The count above is the check that actually binds.
    unlisted = sorted(name for name in tree if name not in text)
    if unlisted:
        print(f"note  {len(unlisted)} skill(s) not named verbatim in the README: "
              + ", ".join(unlisted))


def check_mirror(mirror: Path, problems: list[str]) -> None:
    if not mirror.is_dir():
        problems.append(f"mirror does not exist: {mirror}")
        return

    tree = skill_names(SKILLS_DIR)
    for name in sorted(tree):
        source = SKILLS_DIR / name
        target = mirror / name

        if target.is_symlink():
            # The canonical copy lives elsewhere on purpose; only prove it resolves.
            if not (target / "SKILL.md").is_file():
                problems.append(f"{mirror}: broken symlink for {name} -> {os.readlink(target)}")
            continue

        if not target.is_dir():
            problems.append(f"{mirror}: missing skill {name}")
            continue

        missing, differing = compare_trees(source, target)
        for entry in sorted(missing):
            problems.append(f"{mirror}: {name} is missing {entry}")
        for entry in sorted(differing):
            problems.append(f"{mirror}: {name}/{entry} differs from the repository")

    extra = sorted(skill_names(mirror) - tree)
    if extra:
        print(f"note  {mirror}: holds skills this repository does not track: {', '.join(extra)}")


def resolve_mirrors(arguments: argparse.Namespace) -> list[Path]:
    if arguments.mirror:
        return [Path(item).expanduser() for item in arguments.mirror]
    configured = os.environ.get("SKILLS_MIRRORS", "").strip()
    if configured:
        return [Path(item).expanduser() for item in configured.split(os.pathsep) if item.strip()]
    return [Path.home() / ".agents" / "skills"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--mirror",
        action="append",
        default=[],
        help="skill directory to compare against; repeatable",
    )
    parser.add_argument(
        "--skip-readme", action="store_true", help="only compare mirrors"
    )
    arguments = parser.parse_args()

    problems: list[str] = []
    if not arguments.skip_readme:
        check_readme(problems)
    for mirror in resolve_mirrors(arguments):
        check_mirror(mirror, problems)

    if problems:
        print(f"FAIL  {len(problems)} problem(s) found\n", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    print(f"OK    {len(skill_names(SKILLS_DIR))} skills consistent across README and mirrors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
