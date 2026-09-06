#!/usr/bin/env python3
"""Deterministic structural and safety checks for Agent Skills."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote

import yaml


VALID_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
BROAD_DESTRUCTIVE = re.compile(
    r"\brm\s+(?:-[A-Za-z]*r[A-Za-z]*f[A-Za-z]*|-[A-Za-z]*f[A-Za-z]*r[A-Za-z]*)\s+"
    r"(?:/|~(?:/|\s|$)|\$\{?HOME\}?\b)",
    re.IGNORECASE,
)
VAGUE_PATTERNS = (
    (re.compile(r"\bwhen appropriate\b", re.IGNORECASE), "when appropriate"),
    (re.compile(r"\bas needed\b", re.IGNORECASE), "as needed"),
    (re.compile(r"\bif necessary\b", re.IGNORECASE), "if necessary"),
    (re.compile(r"\bwhere relevant\b", re.IGNORECASE), "where relevant"),
    (re.compile(r"適當時"), "適當時"),
    (re.compile(r"視需要"), "視需要"),
    (re.compile(r"如有必要"), "如有必要"),
    (re.compile(r"相關內容"), "相關內容"),
)
DESTRUCTIVE_INSTRUCTION = re.compile(
    r"^(?:\d+\.\s+|[-*]\s+)?(?:the agent\s+|agent\s+|you\s+)?"
    r"(?:delete|overwrite|force[- ]push|drop|destroy|reset|刪除|覆寫|強制推送|重置)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    file: str
    line: int | None = None


@dataclass
class Report:
    skill: str
    path: str
    findings: list[Finding] = field(default_factory=list)
    passed: list[str] = field(default_factory=list)

    @property
    def result(self) -> str:
        if any(item.severity == "FAIL" for item in self.findings):
            return "FAIL"
        if any(item.severity == "WARN" for item in self.findings):
            return "WARN"
        return "PASS"

    def add(
        self,
        severity: str,
        code: str,
        message: str,
        file: Path,
        line: int | None = None,
    ) -> None:
        self.findings.append(Finding(severity, code, message, str(file), line))


class _UniqueKeyLoader(yaml.SafeLoader):
    """Reject duplicate mapping keys instead of silently replacing metadata."""


def _unique_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise yaml.constructor.ConstructorError(
                None, None, "metadata keys must be strings", key_node.start_mark
            )
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                None, None, f"duplicate key: {key}", key_node.start_mark
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping
)


def _skill_dir(target: Path) -> Path:
    return target.parent if target.name == "SKILL.md" else target


def _frontmatter(lines: list[str]) -> tuple[dict, int, str | None]:
    if not lines or lines[0].strip() != "---":
        return {}, 0, "SKILL.md must start with YAML frontmatter."
    closing = next(
        (i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---"), None
    )
    if closing is None:
        return {}, 0, "YAML frontmatter has no closing delimiter."
    try:
        metadata = yaml.load("\n".join(lines[1:closing]), Loader=_UniqueKeyLoader)
    except yaml.YAMLError as exc:
        return {}, closing, f"Invalid YAML frontmatter: {exc}"
    if not isinstance(metadata, dict):
        return {}, closing, "YAML frontmatter must be a mapping."
    return metadata, closing, None


def _markdown_regions(body: str) -> Iterable[tuple[str, bool]]:
    """Return prose and executable fences; generic example fences are excluded."""
    fence = None
    executable = False
    shell_languages = {"bash", "sh", "shell", "zsh", "powershell", "ps1", "cmd", "bat"}
    for line in body.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})([^`~]*)$", line)
        if marker:
            chars, info = marker.groups()
            if fence is None:
                fence = chars
                executable = info.strip().lower() in shell_languages
            elif chars[0] == fence[0] and len(chars) >= len(fence) and not info.strip():
                fence = None
                executable = False
            yield "", False
        elif fence is None:
            yield line, False
        elif executable:
            yield line, True
        else:
            yield "", False


def _link_destinations(text: str) -> Iterable[str]:
    """Read inline link destinations, including balanced parentheses and titles."""
    for match in re.finditer(r"\[[^]\n]+\]\(", text):
        start = match.end()
        depth = 1
        escaped = False
        for index in range(start, len(text)):
            char = text[index]
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    destination = text[start:index].strip()
                    if destination.startswith("<"):
                        end = destination.find(">")
                        if end != -1:
                            yield destination[1:end]
                    else:
                        # A quoted trailing title is not part of the path.
                        destination = re.sub(r"\s+[\"'].*[\"']$", "", destination)
                        yield destination
                    break


def _local_references(body: str) -> Iterable[str]:
    for line, executable in _markdown_regions(body):
        if executable:
            continue
        # Inline code is an example or literal, never a Markdown link.
        prose = re.sub(r"(`+).*?\1", "", line)
        for destination in _link_destinations(prose):
            destination = unquote(destination.split("#", 1)[0])
            if not destination or re.match(r"^[a-z][a-z0-9+.-]*:", destination, re.I):
                continue
            if destination.startswith(("/", "$", "~")):
                continue
            yield re.sub(r"\\([() ])", r"\1", destination)


def _literal_script_references(body: str) -> Iterable[str]:
    """Conservative hints: exact bundled script literals, not dynamic paths."""
    pattern = re.compile(r"(?<![\w/\\$}])scripts/[A-Za-z0-9_./-]+\.(?:py|js|mjs|sh|ps1)\b")
    for line, executable in _markdown_regions(body):
        parts = [line] if executable else re.findall(r"`([^`]+)`", line)
        for part in parts:
            for match in pattern.finditer(part):
                candidate = match.group()
                # These are templates/globs or variable-built paths, not dependencies.
                if ".." in candidate or any(c in part for c in "<>{}*"):
                    continue
                if candidate.endswith(("/example.py", "/your_script.py")):
                    continue
                yield candidate


def validate_skill(target: Path, max_body_lines: int = 500, profile: str = "repository") -> Report:
    directory = _skill_dir(target.resolve())
    skill_file = directory / "SKILL.md"
    report = Report(skill=directory.name, path=str(directory))

    if not skill_file.is_file():
        report.add("FAIL", "STRUCT001", "SKILL.md is missing.", skill_file)
        return report

    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    metadata, closing, error = _frontmatter(lines)
    if error:
        report.add("FAIL", "META001", error, skill_file, 1)
        return report

    name = metadata.get("name", "")
    description = metadata.get("description", "")
    if not name:
        report.add("FAIL", "META002", "Frontmatter name is missing.", skill_file, 2)
    elif not isinstance(name, str):
        report.add("FAIL", "META002", "Frontmatter name must be a string.", skill_file, 2)
        name = ""
    elif not VALID_NAME.fullmatch(name):
        report.add("FAIL" if profile == "repository" else "WARN", "META003",
                   "Repository naming requires lowercase hyphen-case; runtime acceptance varies.", skill_file, 2)
    elif name != directory.name:
        report.add(
            "FAIL" if profile == "repository" else "WARN",
            "META004",
            f"Skill name '{name}' does not match directory '{directory.name}'.",
            skill_file,
            2,
        )

    if not isinstance(description, str) or not description.strip():
        report.add("FAIL", "META005", "Frontmatter description must be a non-empty string.", skill_file, 3)
    elif not re.search(
        r"\buse (?:when|whenever|for)\b|當|用於|適用",
        description,
        re.IGNORECASE,
    ):
        report.add(
            "WARN",
            "META006",
            "Description should state specific trigger conditions.",
            skill_file,
            3,
        )

    extra_keys = sorted(set(metadata) - {"name", "description"})
    if extra_keys:
        report.add(
            "WARN",
            "META007",
            "Non-portable frontmatter keys: " + ", ".join(extra_keys),
            skill_file,
            2,
        )

    if not any(item.code.startswith("META") and item.severity == "FAIL" for item in report.findings):
        report.passed.append("Frontmatter identity and required fields are valid.")

    body_lines = lines[closing + 1 :]
    body = "\n".join(body_lines)
    if len(body_lines) > max_body_lines:
        report.add(
            "WARN",
            "STRUCT002",
            f"Skill body has {len(body_lines)} lines; keep it at or below {max_body_lines}.",
            skill_file,
        )
    else:
        report.passed.append(f"Skill body is within the {max_body_lines}-line limit.")

    missing_refs: list[str] = []
    # Referenced Markdown can contain dependencies omitted from the entry point.
    markdown_files = [skill_file, *sorted(directory.glob("references/**/*.md"))]
    for document in markdown_files:
        document_body = body if document == skill_file else document.read_text(encoding="utf-8")
        for reference in sorted(set(_local_references(document_body))):
            if not (document.parent / reference).exists():
                missing_refs.append(reference)
                report.add("FAIL", "REF001", f"Referenced local path does not exist: {reference}", document)
        for reference in sorted(set(_literal_script_references(document_body))):
            if not (directory / reference).is_file():
                report.add(
                    "WARN", "REF002",
                    f"Script literal is missing: {reference}. Confirm whether it is a bundled dependency or an example/output.",
                    document,
                )
    if not missing_refs:
        report.passed.append("All checked local Markdown references exist (code examples excluded).")

    destructive_match = BROAD_DESTRUCTIVE.search(text)
    if destructive_match:
        line = text[: destructive_match.start()].count("\n") + 1
        report.add(
            "FAIL",
            "SAFE001",
            "Broad destructive command targets a home or filesystem root.",
            skill_file,
            line,
        )
    else:
        report.passed.append("No broad destructive shell command was found.")

    for line_number, line_text in enumerate(body_lines, start=closing + 2):
        stripped = line_text.strip()
        if not stripped or stripped.startswith("```"):
            continue
        for pattern, label in VAGUE_PATTERNS:
            if pattern.search(stripped):
                report.add(
                    "WARN",
                    "LANG001",
                    f"Replace vague condition '{label}' with a testable condition.",
                    skill_file,
                    line_number,
                )
                break
        english_words = re.findall(r"\b[A-Za-z][A-Za-z'-]*\b", stripped)
        if len(english_words) > 35 and not stripped.startswith("|"):
            report.add(
                "WARN",
                "LANG002",
                f"Instruction line contains {len(english_words)} English words; review for multiple actions.",
                skill_file,
                line_number,
            )
        if DESTRUCTIVE_INSTRUCTION.search(stripped) and not stripped.lower().startswith(("do not ", "never ")):
            report.add(
                "WARN",
                "SAFE002",
                "Destructive wording requires an exact target, authority boundary, and failure behavior.",
                skill_file,
                line_number,
            )

    agents_file = directory / "agents" / "openai.yaml"
    if not agents_file.is_file():
        report.add(
            "WARN",
            "UI001",
            "agents/openai.yaml is recommended for UI metadata and implicit invocation policy.",
            agents_file,
        )
    else:
        agents_text = agents_file.read_text(encoding="utf-8")
        if name and f"${name}" not in agents_text:
            report.add(
                "WARN",
                "UI002",
                f"agents/openai.yaml default_prompt should mention '${name}'.",
                agents_file,
            )
        else:
            report.passed.append("Agent UI metadata refers to the Skill explicitly.")

    return report


def _render_text(report: Report) -> str:
    output = [f"Skill: {report.skill}", f"Result: {report.result}"]
    for severity in ("FAIL", "WARN"):
        items = [item for item in report.findings if item.severity == severity]
        output.extend(["", severity])
        if not items:
            output.append("- None")
            continue
        for item in items:
            location = item.file + (f":{item.line}" if item.line else "")
            output.append(f"- [{item.code}] {item.message} ({location})")
    output.extend(["", "PASS"])
    output.extend(f"- {message}" for message in report.passed)
    return "\n".join(output)


def _render_json(reports: list[Report]) -> str:
    payload = []
    for report in reports:
        payload.append(
            {
                "skill": report.skill,
                "path": report.path,
                "result": report.result,
                "findings": [asdict(item) for item in report.findings],
                "passed": report.passed,
            }
        )
    return json.dumps(payload, ensure_ascii=False, indent=2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("targets", nargs="+", type=Path, help="Skill directories or SKILL.md files")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--warnings-as-errors", action="store_true")
    parser.add_argument("--max-body-lines", type=int, default=500)
    parser.add_argument("--profile", choices=("repository", "runtime"), default="repository",
                        help="repository enforces local naming; runtime reports naming portability warnings")
    args = parser.parse_args(argv)

    reports = [validate_skill(target, args.max_body_lines, args.profile) for target in args.targets]
    if args.format == "json":
        print(_render_json(reports))
    else:
        print("\n\n".join(_render_text(report) for report in reports))

    has_failure = any(report.result == "FAIL" for report in reports)
    has_warning = any(report.result == "WARN" for report in reports)
    return int(has_failure or (args.warnings_as_errors and has_warning))


if __name__ == "__main__":
    sys.exit(main())
