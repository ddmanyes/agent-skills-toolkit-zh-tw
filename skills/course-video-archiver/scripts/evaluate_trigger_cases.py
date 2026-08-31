#!/usr/bin/env python3
"""Validate, emit, and score course-video-archiver trigger cases."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


EXPECTED_BY_KIND = {
    "positive": "trigger",
    "negative": "do_not_trigger",
    "guardrail": "trigger_then_stop",
}
ALLOWED_ACTUAL = set(EXPECTED_BY_KIND.values())
MINIMUM_COUNTS = {"positive": 5, "negative": 5, "guardrail": 3}
DEFAULT_SUITE = Path(__file__).resolve().parents[1] / "evals" / "trigger_cases.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate, emit, or score trigger evaluation cases."
    )
    parser.add_argument(
        "--suite",
        type=Path,
        default=DEFAULT_SUITE,
        help="Path to trigger_cases.json",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="Validate suite structure and balance")
    subparsers.add_parser("emit", help="Emit answer-free JSONL prompts to stdout")
    score = subparsers.add_parser("score", help="Score a complete result file")
    score.add_argument("results", help="Results JSON path, or '-' for stdin")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise ValueError(f"File does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc


def validate_suite(payload: Any) -> list[dict[str, str]]:
    if not isinstance(payload, dict):
        raise ValueError("Suite root must be an object")
    if payload.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    if payload.get("skill") != "course-video-archiver":
        raise ValueError("skill must be course-video-archiver")

    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases must be a non-empty array")

    required = {"id", "kind", "locale", "prompt", "expected", "reason"}
    ids: set[str] = set()
    counts: Counter[str] = Counter()
    normalized: list[dict[str, str]] = []
    for index, case in enumerate(cases, 1):
        if not isinstance(case, dict):
            raise ValueError(f"Case {index} must be an object")
        missing = sorted(required - case.keys())
        if missing:
            raise ValueError(f"Case {index} is missing: {', '.join(missing)}")
        if any(not isinstance(case[key], str) or not case[key].strip() for key in required):
            raise ValueError(f"Case {index} fields must be non-empty strings")

        case_id = case["id"]
        if case_id in ids:
            raise ValueError(f"Duplicate case id: {case_id}")
        ids.add(case_id)

        kind = case["kind"]
        if kind not in EXPECTED_BY_KIND:
            raise ValueError(f"Unknown kind for {case_id}: {kind}")
        if case["expected"] != EXPECTED_BY_KIND[kind]:
            raise ValueError(
                f"Expected label for {case_id} must be {EXPECTED_BY_KIND[kind]}"
            )
        counts[kind] += 1
        normalized.append({key: case[key].strip() for key in required})

    for kind, minimum in MINIMUM_COUNTS.items():
        if counts[kind] < minimum:
            raise ValueError(f"Suite needs at least {minimum} {kind} cases")
    if not any(case["locale"] == "en" for case in normalized):
        raise ValueError("Suite needs at least one English case")
    if not any(case["locale"] == "zh-TW" for case in normalized):
        raise ValueError("Suite needs at least one Traditional Chinese case")
    return normalized


def emit_cases(cases: list[dict[str, str]]) -> None:
    for case in cases:
        public_case = {
            key: case[key] for key in ("id", "kind", "locale", "prompt")
        }
        print(json.dumps(public_case, ensure_ascii=False))


def load_results(location: str) -> Any:
    if location == "-":
        try:
            return json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on stdin: {exc}") from exc
    return load_json(Path(location).resolve())


def divide(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def score_results(cases: list[dict[str, str]], payload: Any) -> int:
    if not isinstance(payload, dict):
        raise ValueError("Results root must be an object")
    if payload.get("skill") != "course-video-archiver":
        raise ValueError("Results skill must be course-video-archiver")
    results = payload.get("results")
    if not isinstance(results, list):
        raise ValueError("results must be an array")

    expected_by_id = {case["id"]: case["expected"] for case in cases}
    actual_by_id: dict[str, str] = {}
    for index, result in enumerate(results, 1):
        if not isinstance(result, dict):
            raise ValueError(f"Result {index} must be an object")
        case_id = result.get("id")
        actual = result.get("actual")
        if not isinstance(case_id, str) or case_id not in expected_by_id:
            raise ValueError(f"Unknown result id at row {index}: {case_id}")
        if case_id in actual_by_id:
            raise ValueError(f"Duplicate result id: {case_id}")
        if actual not in ALLOWED_ACTUAL:
            raise ValueError(f"Invalid actual label for {case_id}: {actual}")
        actual_by_id[case_id] = actual

    missing = sorted(set(expected_by_id) - set(actual_by_id))
    if missing:
        raise ValueError("Missing result ids: " + ", ".join(missing))

    mismatches = []
    true_positive = false_positive = false_negative = 0
    guardrail_total = guardrail_passed = 0
    for case_id, expected in expected_by_id.items():
        actual = actual_by_id[case_id]
        expected_trigger = expected != "do_not_trigger"
        actual_trigger = actual != "do_not_trigger"
        if expected_trigger and actual_trigger:
            true_positive += 1
        elif not expected_trigger and actual_trigger:
            false_positive += 1
        elif expected_trigger and not actual_trigger:
            false_negative += 1
        if expected == "trigger_then_stop":
            guardrail_total += 1
            guardrail_passed += int(actual == expected)
        if actual != expected:
            mismatches.append((case_id, expected, actual))

    total = len(cases)
    exact = total - len(mismatches)
    summary = {
        "cases": total,
        "exact_accuracy": divide(exact, total),
        "trigger_precision": divide(true_positive, true_positive + false_positive),
        "trigger_recall": divide(true_positive, true_positive + false_negative),
        "guardrail_accuracy": divide(guardrail_passed, guardrail_total),
        "mismatches": len(mismatches),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    for case_id, expected, actual in mismatches:
        print(f"MISMATCH {case_id}: expected={expected}, actual={actual}")
    return 0 if not mismatches else 1


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    args = parse_args()
    try:
        cases = validate_suite(load_json(args.suite.resolve()))
        if args.command == "validate":
            counts = Counter(case["kind"] for case in cases)
            print(
                f"PASS: {len(cases)} cases "
                f"(positive={counts['positive']}, negative={counts['negative']}, "
                f"guardrail={counts['guardrail']})"
            )
            return 0
        if args.command == "emit":
            emit_cases(cases)
            return 0
        return score_results(cases, load_results(args.results))
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
