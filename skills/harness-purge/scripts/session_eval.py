#!/usr/bin/env python3
"""Prepare Claude/Codex tasks and compare explicitly selected local outputs. No model calls."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

from purge_lab import (ASSETS, LabError, MAX_RESPONSE_BYTES, digest, judge, load_cases,
                       load_profiles, read_json, strict_json_loads, write_new_json)

CONDITIONS = ("client_version", "reasoning", "tools", "output_contract", "context_setup", "workspace_snapshot")
STATUSES = {"completed", "model_refusal", "runtime_error", "not_run"}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def snapshot_digest(manifest):
    keys = ("schema_version", "client", "model", "conditions", "profiles", "cases", "tasks")
    return digest(json.dumps({k: manifest[k] for k in keys}, sort_keys=True,
                             ensure_ascii=False, allow_nan=False).encode("utf-8"))


def make_tasks(cases, repeats):
    tasks = []
    for repeat in range(repeats):
        for index, case in enumerate(cases):
            order = ("baseline", "candidate") if (index + repeat) % 2 == 0 else ("candidate", "baseline")
            for profile in order:
                tasks.append({"case": case["id"], "profile": profile, "repeat": repeat})
    return tasks


def prepare(*, client, model, output, profiles_path, cases_path, repeats=1, conditions_path=None):
    if client not in {"claude", "codex"} or not nonempty(model):
        raise LabError("provide claude or codex and an explicit model")
    profiles, cases = load_profiles(profiles_path), load_cases(cases_path)
    if type(repeats) is not int or not 1 <= repeats <= 5 or len(cases) * 2 * repeats > 60:
        raise LabError("invalid repeats or experiment exceeds 60 tasks")
    conditions = {k: "unknown" for k in CONDITIONS}
    if conditions_path:
        supplied = read_json(conditions_path)
        if not isinstance(supplied, dict) or set(supplied) - set(CONDITIONS):
            raise LabError("conditions contain unsupported fields")
        if not all(nonempty(v) for v in supplied.values()):
            raise LabError("condition values must be nonempty strings")
        conditions.update(supplied)
    tasks = make_tasks(cases, repeats)
    manifest = {"schema_version": 1, "client": client, "model": model,
                "conditions": conditions, "profiles": profiles, "cases": cases, "tasks": tasks,
                "profiles_sha256": digest(Path(profiles_path).read_bytes()),
                "cases_sha256": digest(Path(cases_path).read_bytes()),
                "scope": "local preparation/import only; no client or model was launched"}
    manifest["snapshot_sha256"] = snapshot_digest(manifest)
    destination = Path(output).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    write_new_json(destination / "manifest.json", manifest)
    prompts = destination / "prompts"
    prompts.mkdir()
    cases_by_id = {case["id"]: case for case in cases}
    template = []
    for index, task in enumerate(tasks, 1):
        # Numeric filenames avoid treating user-supplied case IDs as paths.
        prompt = ("Task instructions:\n" + profiles[task["profile"]]["prompt"] +
                  "\n\nTask:\n" + cases_by_id[task["case"]]["prompt"] + "\n")
        with (prompts / f"{index:03d}.txt").open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(prompt)
        template.append({**task, "status": "not_run", "output_file": None,
                         "observed_model": "unknown", "seconds": None,
                         "semantic_review": {"verdict": "not_reviewed", "evidence": ""}})
    write_new_json(destination / "records-template.json", template)
    return {"client": client, "model": model, "planned_tasks": len(tasks),
            "directory": str(destination), "model_calls": 0}


def load_manifest(run):
    manifest = read_json(Path(run) / "manifest.json")
    try:
        valid = (manifest["schema_version"] == 1 and manifest["client"] in {"claude", "codex"}
                 and nonempty(manifest["model"]) and snapshot_digest(manifest) == manifest["snapshot_sha256"])
        if not valid:
            raise ValueError()
        tasks = manifest["tasks"]
        if not isinstance(tasks, list) or not 1 <= len(tasks) <= 60:
            raise ValueError()
        identities = [identity(task) for task in tasks]
        if len(set(identities)) != len(identities):
            raise ValueError()
        if set(manifest["conditions"]) != set(CONDITIONS):
            raise ValueError()
    except (KeyError, TypeError, ValueError):
        raise LabError("invalid or changed session manifest") from None
    return manifest


def identity(record):
    if not isinstance(record, dict):
        raise LabError("records and tasks must be objects")
    case, profile, repeat = (record.get(k) for k in ("case", "profile", "repeat"))
    if (not nonempty(case) or not isinstance(profile, str) or profile not in {"baseline", "candidate"}
            or type(repeat) is not int or repeat < 0):
        raise LabError("invalid case, profile or repeat")
    return case, profile, repeat


def load_output(base, filename):
    if not nonempty(filename) or Path(filename).is_absolute():
        raise LabError("output_file must be relative to the records file")
    path = (base / filename).resolve()
    if not path.is_relative_to(base):
        raise LabError("output_file escaped the records directory")
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise LabError("selected output exceeds size limit")
        return raw.decode("utf-8"), digest(raw)
    except (OSError, UnicodeError):
        raise LabError("selected output is missing or not UTF-8") from None


def inspect_output(content, check, completed):
    result = {"format": "not_checked", "check_passed": False, "criterion": "not_completed"}
    if not completed:
        return result
    passed, criterion = judge(content, check)
    result.update(check_passed=passed, criterion=criterion)
    if check["kind"] == "json_fields":
        try:
            strict_json_loads(content.strip())
            result["format"] = "valid_json"
        except ValueError:
            result["format"] = "invalid_json"
    else:
        result["format"] = "not_applicable"
    return result


def compare(*, run, records_path, output):
    manifest = load_manifest(run)
    records_file = Path(records_path).resolve()
    supplied = read_json(records_file)
    if not isinstance(supplied, list):
        raise LabError("records must be a JSON array")
    planned = {identity(t): t for t in manifest["tasks"]}
    indexed = {}
    allowed = {"case", "profile", "repeat", "status", "output_file", "observed_model", "seconds", "semantic_review"}
    for record in supplied:
        key = identity(record)
        if key not in planned or key in indexed or set(record) - allowed:
            raise LabError("duplicate, unknown or malformed record")
        indexed[key] = record
    cases = {c["id"]: c for c in manifest["cases"]}
    rows = []
    model_warnings = set()
    for key, task in planned.items():
        record = indexed.get(key, {})
        status = record.get("status", "not_run")
        if not isinstance(status, str) or status not in STATUSES:
            raise LabError("unsupported execution status")
        review = record.get("semantic_review", {"verdict": "not_reviewed", "evidence": ""})
        if not isinstance(review, dict) or set(review) != {"verdict", "evidence"}:
            raise LabError("semantic_review requires verdict and evidence")
        verdict, evidence = review["verdict"], review["evidence"]
        if not isinstance(verdict, str) or verdict not in {"pass", "fail", "not_reviewed"} or not isinstance(evidence, str):
            raise LabError("invalid semantic review")
        if verdict != "not_reviewed" and (status != "completed" or not evidence.strip()):
            raise LabError("semantic verdict needs a completed response and evidence")
        seconds = record.get("seconds")
        if seconds is not None and (type(seconds) not in (int, float) or not math.isfinite(seconds) or seconds < 0):
            raise LabError("seconds must be a finite nonnegative number or null")
        observed_model = record.get("observed_model", "unknown")
        if not nonempty(observed_model):
            raise LabError("observed_model must be a nonempty string")
        if status != "not_run" and observed_model != manifest["model"]:
            model_warnings.add("model unknown or differs from the declared model")
        content, sha = None, None
        filename = record.get("output_file")
        if status in {"completed", "model_refusal"} and not filename:
            raise LabError("completed/refusal records require an output file")
        if status == "not_run" and filename is not None:
            raise LabError("not_run records cannot contain an output file")
        if filename is not None:
            content, sha = load_output(records_file.parent, filename)
        if status == "completed" and not content.strip():
            raise LabError("empty output cannot be classified as completed")
        rows.append({**task, "status": status, "output_file": filename, "response_sha256": sha,
                     "raw_response": content, "observed_model": observed_model, "seconds": seconds,
                     "semantic_review": review,
                     **inspect_output(content or "", cases[key[0]]["check"], status == "completed")})
    stats = {}
    for profile in ("baseline", "candidate"):
        subset = [r for r in rows if r["profile"] == profile]
        stats[profile] = {"planned": len(subset),
                          **{s: sum(r["status"] == s for r in subset) for s in sorted(STATUSES)},
                          "valid_json": sum(r["format"] == "valid_json" for r in subset),
                          "invalid_json": sum(r["format"] == "invalid_json" for r in subset),
                          "checks_passed": sum(r["check_passed"] for r in subset),
                          **{"semantic_" + s: sum(r["semantic_review"]["verdict"] == s for r in subset)
                             for s in ("pass", "fail", "not_reviewed")}}
    keyed = {identity(row): row for row in rows}
    pairs = []
    for row in rows:
        if row["profile"] != "baseline":
            continue
        other = keyed[(row["case"], "candidate", row["repeat"])]
        if row["status"] == other["status"] == "completed":
            pairs.append({"case": row["case"], "repeat": row["repeat"],
                          "baseline_check": row["check_passed"], "candidate_check": other["check_passed"]})
    unknown = [k for k, v in manifest["conditions"].items() if v.strip().lower() == "unknown"]
    summary = {"scope": "selected local outputs; execution labels and reviews are supplied by the operator",
               "client": manifest["client"], "declared_model": manifest["model"],
               "execution_complete": all(r["status"] in {"completed", "model_refusal"} for r in rows),
               "profiles": stats, "completed_pairs": pairs,
               "paired_check_delta": sum(int(p["candidate_check"]) - int(p["baseline_check"]) for p in pairs),
               "unknown_conditions": unknown, "model_warnings": sorted(model_warnings),
               "causal_improvement_established": False,
               "limitations": ["No model was called and no client loading was observed by this script.",
                               "Recorded conditions are not independent proof of equal runtime contexts.",
                               "JSON and deterministic checks do not establish semantic correctness.",
                               "Semantic verdicts need primary review; imported labels are not verified here.",
                               "Paired deltas are descriptive and exclude incomplete pairs.",
                               "No automatic retry, profile activation or host changes occurred."]}
    destination = Path(output).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    write_new_json(destination / "manifest.json", manifest)
    write_new_json(destination / "results.json", rows)
    write_new_json(destination / "summary.json", summary)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("prepare", help="write paired prompts without answers or model calls")
    init.add_argument("--client", choices=("claude", "codex"), required=True)
    init.add_argument("--model", required=True)
    init.add_argument("--profiles", default=str(ASSETS / "profiles.json"))
    init.add_argument("--cases", default=str(ASSETS / "agent-cases.json"))
    init.add_argument("--conditions")
    init.add_argument("--repeats", type=int, default=1)
    init.add_argument("--output", required=True)
    check = commands.add_parser("compare", help="import selected local outputs and separate check/review results")
    check.add_argument("--run", required=True)
    check.add_argument("--records", required=True)
    check.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            result = prepare(client=args.client, model=args.model, output=args.output,
                             profiles_path=args.profiles, cases_path=args.cases,
                             repeats=args.repeats, conditions_path=args.conditions)
        else:
            result = compare(run=args.run, records_path=args.records, output=args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("execution_complete", True) else 2
    except (LabError, OSError) as exc:
        message = str(exc) if isinstance(exc, LabError) else type(exc).__name__
        print(json.dumps({"error": message}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
