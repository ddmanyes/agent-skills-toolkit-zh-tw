#!/usr/bin/env python3
"""Bounded, reproducible prompt experiments. No host patches or tool execution."""
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import math
import os
from pathlib import Path
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ASSETS = Path(__file__).resolve().parent.parent / "assets"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024


class LabError(Exception):
    """An error safe to display without leaking provider responses or headers."""


def strict_json_loads(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError("nonfinite JSON number")

    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("JSON number exceeds finite float range")
        return number

    return json.loads(text, object_pairs_hook=unique, parse_constant=invalid_constant, parse_float=finite_float)


def same_json(actual, expected):
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(same_json(actual[k], v) for k, v in expected.items())
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(same_json(a, b) for a, b in zip(actual, expected))
    return actual == expected


def read_json(path):
    try:
        return strict_json_loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise LabError(f"invalid JSON file: {Path(path).name}") from exc


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_new_json(path, data):
    payload = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)


def load_profiles(path):
    profiles = read_json(path)
    if not isinstance(profiles, dict) or set(profiles) != {"baseline", "candidate"}:
        raise LabError("profiles must contain baseline and candidate only")
    for value in profiles.values():
        if not isinstance(value, dict) or set(value) != {"name", "prompt"}:
            raise LabError("each profile requires name and prompt only")
        if not all(isinstance(value[k], str) and value[k].strip() for k in value):
            raise LabError("profile name and prompt must be nonempty strings")
        if len(value["prompt"].encode("utf-8")) > 32768:
            raise LabError("profile prompt exceeds 32768 bytes")
    return profiles


def load_cases(path):
    cases = read_json(path)
    if not isinstance(cases, list) or not 1 <= len(cases) <= 20:
        raise LabError("provide 1 to 20 cases")
    ids = set()
    for case in cases:
        if not isinstance(case, dict) or set(case) != {"id", "prompt", "check"}:
            raise LabError("each case requires id, prompt and check only")
        if not all(isinstance(case[k], str) and case[k].strip() for k in ("id", "prompt")):
            raise LabError("case id and prompt must be nonempty strings")
        if case["id"] in ids:
            raise LabError("duplicate case id")
        ids.add(case["id"])
        if len(case["prompt"].encode("utf-8")) > 32768:
            raise LabError("case prompt exceeds 32768 bytes")
        check = case["check"]
        if not isinstance(check, dict):
            raise LabError("check must be an object")
        kind = check.get("kind")
        if kind == "exact":
            good = isinstance(check.get("value"), str) and bool(check["value"])
        elif kind == "contains_all":
            values = check.get("values")
            good = isinstance(values, list) and bool(values) and all(isinstance(v, str) and v for v in values)
        elif kind == "json_fields":
            good = isinstance(check.get("expected"), dict) and bool(check["expected"])
        else:
            good = False
        if not good:
            raise LabError("unsupported or invalid check")
    return cases


def judge(content, check):
    text = content.strip()
    if not text:
        return False, "empty-answer"
    if check["kind"] == "exact":
        return text == check["value"], "exact-match"
    if check["kind"] == "contains_all":
        return all(v in text for v in check["values"]), "keyword-presence-only"
    if check["kind"] == "json_fields":
        try:
            value = strict_json_loads(text)
        except ValueError:
            return False, "invalid-json"
        if not isinstance(value, dict):
            return False, "json-not-object"
        matches = all(k in value and same_json(value[k], v)
                      for k, v in check["expected"].items())
        return matches, "expected-json-fields"
    raise LabError("unsupported check")


def validate_base_url(raw):
    parsed = urllib.parse.urlsplit(raw)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise LabError("endpoint must be an explicit HTTP(S) base URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise LabError("endpoint must not contain credentials, query or fragment")
    try:
        _ = parsed.port
    except ValueError as exc:
        raise LabError("invalid endpoint port") from exc
    return raw.rstrip("/")


def credential_headers(api_key_env=None, headers_env=None):
    headers = {}
    if headers_env:
        raw = os.environ.get(headers_env)
        if not raw:
            raise LabError("requested headers environment variable is unset")
        try:
            headers = json.loads(raw)
        except ValueError as exc:
            raise LabError("headers environment variable is not JSON") from exc
        if not isinstance(headers, dict):
            raise LabError("headers must be an object")
        for key, value in headers.items():
            if not isinstance(key, str) or not isinstance(value, str) or any(c in key + value for c in "\r\n"):
                raise LabError("invalid header")
            if key.lower() in {"host", "content-length", "content-type"}:
                raise LabError("transport header override is not allowed")
    if api_key_env:
        key = os.environ.get(api_key_env)
        if not key or "\r" in key or "\n" in key:
            raise LabError("requested API key environment variable is unset or invalid")
        headers["Authorization"] = "Bearer " + key
    return headers


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise LabError("redirect refused; verify endpoint explicitly")


def http_json(url, body, headers, timeout):
    request_headers = dict(headers)
    request_headers["Content-Type"] = "application/json"
    payload = None if body is None else json.dumps(body, ensure_ascii=False, allow_nan=False).encode("utf-8")
    request = urllib.request.Request(url, data=payload, headers=request_headers,
                                     method="GET" if body is None else "POST")
    opener = urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise LabError("response exceeds size limit")
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise LabError("provider response is not an object")
        return data
    except urllib.error.HTTPError as exc:
        code = exc.code
        exc.close()
        raise LabError(f"provider HTTP {code}; response body omitted") from None
    except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException):
        raise LabError("network or timeout error; no automatic retry") from None
    except (ValueError, UnicodeError):
        raise LabError("provider returned invalid JSON") from None


def doctor(workspace, dsh_package=None):
    root = Path(workspace).resolve(strict=True)
    if not root.is_dir():
        raise LabError("workspace must be a directory")
    rules = []
    for name in ("AGENTS.md", "CLAUDE.md", "AGENTS.local.md", "CLAUDE.local.md"):
        path = root / name
        if not path.exists():
            continue
        if path.is_symlink() or not path.is_file():
            rules.append({"name": name, "status": "not-read", "reason": "symlink-or-nonfile"})
            continue
        with path.open("rb") as stream:
            raw = stream.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            rules.append({"name": name, "status": "not-read", "reason": "size-limit"})
            continue
        rules.append({"name": name, "bytes": len(raw), "sha256": digest(raw)})
    package = None
    if dsh_package:
        value = read_json(dsh_package)
        if not isinstance(value, dict) or value.get("name") != "@deepseek-ai/dsh":
            raise LabError("dsh-package is not the DSH manifest")
        version = value.get("version")
        package = {"name": value["name"], "version": version,
                   "matches_studied_upstream_targets": version in ("0.2.1-rc.2", "0.2.1-rc.5")}
    return {"workspace": str(root), "rule_candidates_only": rules, "dsh": package,
            "tools": {name: shutil.which(name) for name in ("python", "node", "git", "claude", "codex")},
            "limitations": ["Only direct workspace files were inventoried; host loading was not observed.",
                            "Tool presence does not prove runtime readiness or permission.",
                            "Version match is a declaration match, not a patch compatibility test."]}


def make_request(profile, case, model, max_tokens, disable_thinking=False):
    request = {"model": model, "messages": [{"role": "system", "content": profile["prompt"]},
                                           {"role": "user", "content": case["prompt"]}],
               "temperature": 0, "max_tokens": max_tokens, "stream": False}
    if disable_thinking:
        request["chat_template_kwargs"] = {"enable_thinking": False}
    return request


def redact_record(record, headers):
    secrets = set(headers.values())
    secrets.update(value[7:] for key, value in headers.items()
                   if key.lower() == "authorization" and value.lower().startswith("bearer "))
    secrets.discard("")
    def scrub(value):
        if isinstance(value, str):
            for secret in sorted(secrets, key=len, reverse=True):
                value = value.replace(secret, "[REDACTED]")
            return value
        if isinstance(value, dict):
            return {key: scrub(item) for key, item in value.items()}
        if isinstance(value, list):
            return [scrub(item) for item in value]
        return value
    return scrub(record)


def evaluate(*, base_url, model, profiles_path, cases_path, output, headers=None,
             max_tokens=384, timeout=45, repeats=1, disable_thinking=False, transport=http_json):
    base_url = validate_base_url(base_url)
    profiles, cases = load_profiles(profiles_path), load_cases(cases_path)
    if not isinstance(model, str) or not model.strip():
        raise LabError("model must be explicit")
    if not (1 <= repeats <= 5 and 1 <= max_tokens <= 4096 and 0 < timeout <= 120):
        raise LabError("invalid repeats, token limit or timeout")
    total = len(cases) * 2 * repeats
    if total > 60:
        raise LabError("experiment exceeds 60 requests")
    destination = Path(output).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    manifest = {"schema_version": 1, "endpoint": base_url, "model": model,
                "profiles": profiles, "cases": cases, "temperature": 0,
                "max_tokens": max_tokens, "timeout_seconds": timeout, "repeats": repeats,
                "disable_thinking": disable_thinking, "planned_requests": total,
                "profiles_sha256": digest(Path(profiles_path).read_bytes()),
                "cases_sha256": digest(Path(cases_path).read_bytes()),
                "scope": "synthetic text-only requests; no tools or host patches"}
    write_new_json(destination / "manifest.json", manifest)
    records = []
    with (destination / "results.jsonl").open("x", encoding="utf-8", newline="\n") as log:
        for repeat in range(repeats):
            for index, case in enumerate(cases):
                order = ("baseline", "candidate") if (index + repeat) % 2 == 0 else ("candidate", "baseline")
                for label in order:
                    body = make_request(profiles[label], case, model, max_tokens, disable_thinking)
                    start = time.monotonic()
                    record = {"case": case["id"], "profile": label, "repeat": repeat,
                              "request": body}
                    try:
                        response = transport(base_url + "/chat/completions", body, headers or {}, timeout)
                        choices = response.get("choices")
                        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
                            raise LabError("provider response has no choices")
                        message = choices[0].get("message")
                        if not isinstance(message, dict) or not isinstance(message.get("content"), str):
                            raise LabError("provider response has no text content")
                        content = message["content"]
                        if not content.strip():
                            raise LabError("provider returned empty text content")
                        passed, criterion = judge(content, case["check"])
                        record.update(status="completed", response=content, passed=passed,
                                      criterion=criterion, finish_reason=choices[0].get("finish_reason"),
                                      returned_model=response.get("model"))
                    except LabError as exc:
                        record.update(status="transport-error", passed=False, error=str(exc))
                    record["seconds"] = round(time.monotonic() - start, 3)
                    record = redact_record(record, headers or {})
                    log.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
                    log.flush()
                    records.append(record)
                    print(json.dumps({k: record[k] for k in ("case", "profile", "status", "passed", "seconds")}), flush=True)
                    if record["status"] == "transport-error":
                        summary = summarize(records, total)
                        write_new_json(destination / "summary.json", summary)
                        return summary
    summary = summarize(records, total)
    write_new_json(destination / "summary.json", summary)
    return summary


def summarize(records, planned):
    stats = {}
    for label in ("baseline", "candidate"):
        rows = [r for r in records if r["profile"] == label]
        stats[label] = {"attempted": len(rows), "completed": sum(r["status"] == "completed" for r in rows),
                        "passed": sum(r["passed"] for r in rows),
                        "failed_checks": sum(r["status"] == "completed" and not r["passed"] for r in rows),
                        "transport_errors": sum(r["status"] != "completed" for r in rows)}
    complete = len(records) == planned and all(r["status"] == "completed" for r in records)
    return {"execution_complete": complete, "planned_requests": planned, "attempted_requests": len(records),
            "profiles": stats, "limitations": ["Exact/JSON/keyword checks are proxies, not semantic safety or jailbreak evaluation.",
                "No host tools, approval, sandbox or persistent profile were changed.",
                "A small single-model sample cannot establish general effectiveness."]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("doctor", help="read-only direct workspace inventory")
    check.add_argument("--workspace", required=True)
    check.add_argument("--dsh-package")
    run = commands.add_parser("evaluate", help="compare synthetic cases at an explicitly authorized endpoint")
    run.add_argument("--base-url", required=True)
    run.add_argument("--model", required=True)
    run.add_argument("--profiles", default=str(ASSETS / "profiles.json"))
    run.add_argument("--cases", default=str(ASSETS / "cases.json"))
    run.add_argument("--output", required=True)
    run.add_argument("--api-key-env")
    run.add_argument("--headers-env")
    run.add_argument("--max-tokens", type=int, default=384)
    run.add_argument("--timeout", type=float, default=45)
    run.add_argument("--repeats", type=int, default=1)
    run.add_argument("--disable-thinking", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            result = doctor(args.workspace, args.dsh_package)
        else:
            headers = credential_headers(args.api_key_env, args.headers_env)
            result = evaluate(base_url=args.base_url, model=args.model, profiles_path=args.profiles,
                              cases_path=args.cases, output=args.output, headers=headers,
                              max_tokens=args.max_tokens, timeout=args.timeout,
                              repeats=args.repeats, disable_thinking=args.disable_thinking)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("execution_complete", True) else 2
    except (LabError, OSError) as exc:
        # Do not echo exception objects from arbitrary transports or request bodies.
        message = str(exc) if isinstance(exc, LabError) else type(exc).__name__
        print(json.dumps({"error": message}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
