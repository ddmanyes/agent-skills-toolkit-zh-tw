#!/usr/bin/env python3
"""Fetch public GitHub Stars and emit only unprocessed records as JSON.

This collector is intentionally read-only. It never writes the Second Brain vault or
the ledger; the calling agent must write candidate notes through the central MCP and
append a ledger marker only after that write succeeds.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


API_VERSION = "2026-03-10"
LEDGER_PATTERN = re.compile(r"<!--\s*github-star-key:\s*([^\s]+)\s*-->")
CURSOR_PATTERN = re.compile(r"<!--\s*github-stars-cursor:\s*([^\s]+)\s*-->")


def normalize_star(item: dict[str, Any]) -> dict[str, Any]:
    """Normalize GitHub's star envelope to the stable fields used by the skill."""
    starred_at = item.get("starred_at")
    repo = item.get("repo")
    if not isinstance(starred_at, str) or not starred_at:
        raise ValueError("GitHub star item is missing starred_at; request star+json media type")
    if not isinstance(repo, dict):
        raise ValueError("GitHub star item is missing repo envelope")

    repo_id = repo.get("id")
    full_name = repo.get("full_name")
    if not isinstance(repo_id, int) or not isinstance(full_name, str) or "/" not in full_name:
        raise ValueError("GitHub repository is missing a valid id or full_name")

    license_data = repo.get("license")
    license_id = license_data.get("spdx_id") if isinstance(license_data, dict) else None
    topics = repo.get("topics")
    if not isinstance(topics, list):
        topics = []

    return {
        "key": f"{repo_id}@{starred_at}",
        "repo_id": repo_id,
        "starred_at": starred_at,
        "full_name": full_name,
        "html_url": repo.get("html_url") or f"https://github.com/{full_name}",
        "description": repo.get("description"),
        "language": repo.get("language"),
        "license": license_id,
        "stargazers_count": repo.get("stargazers_count"),
        "forks_count": repo.get("forks_count"),
        "open_issues_count": repo.get("open_issues_count"),
        "topics": [str(topic) for topic in topics],
        "archived": bool(repo.get("archived", False)),
        "pushed_at": repo.get("pushed_at"),
        "default_branch": repo.get("default_branch"),
    }


def parse_ledger(content: str) -> set[str]:
    """Return stable keys from canonical HTML markers in an append-only ledger."""
    return set(LEDGER_PATTERN.findall(content))


def parse_cursor(content: str) -> str | None:
    """Return the newest ISO-8601 high-watermark cursor from a ledger."""
    cursors = CURSOR_PATTERN.findall(content)
    return max(cursors) if cursors else None


def read_ledger(path: Path | None) -> set[str]:
    """Read a local, read-only mirror of the MCP-managed ledger."""
    if path is None or not path.is_file():
        return set()
    return parse_ledger(path.read_text(encoding="utf-8"))


def read_cursor(path: Path | None) -> str | None:
    if path is None or not path.is_file():
        return None
    return parse_cursor(path.read_text(encoding="utf-8"))


def fetch_starred(username: str, pages: int = 1) -> list[dict[str, Any]]:
    """Fetch newest public stars using GitHub's timestamped star media type."""
    if pages < 1:
        raise ValueError("pages must be at least 1")

    safe_username = urllib.parse.quote(username, safe="")
    records: list[dict[str, Any]] = []
    for page in range(1, pages + 1):
        url = (
            f"https://api.github.com/users/{safe_username}/starred"
            f"?sort=created&direction=desc&per_page=100&page={page}"
        )
        try:
            completed = subprocess.run(
                [
                    "curl",
                    "--fail-with-body",
                    "--silent",
                    "--show-error",
                    "--location",
                    "--max-time",
                    "30",
                    "--header",
                    "Accept: application/vnd.github.star+json",
                    "--header",
                    f"X-GitHub-Api-Version: {API_VERSION}",
                    "--header",
                    "User-Agent: github-stars-radar/1.0",
                    url,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            raise RuntimeError("curl is required but was not found") from exc
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or exc.stdout or "unknown curl error").strip()
            raise RuntimeError(f"GitHub API request failed: {detail}") from exc

        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise ValueError("GitHub API response is not valid JSON") from exc

        if not isinstance(payload, list):
            raise ValueError("GitHub API response must be a list")
        records.extend(payload)
        if len(payload) < 100:
            break
    return records


def select_new(
    payload: list[dict[str, Any]],
    processed: set[str],
    limit: int,
    cursor: str | None,
) -> dict[str, Any]:
    """Normalize, de-duplicate, sort, and bound unprocessed star records."""
    if limit < 1:
        raise ValueError("limit must be at least 1")

    unique: dict[str, dict[str, Any]] = {}
    for raw in payload:
        if not isinstance(raw, dict):
            raise ValueError("GitHub API list contains a non-object item")
        record = normalize_star(raw)
        unique[record["key"]] = record

    unprocessed = [
        record
        for key, record in unique.items()
        if key not in processed and (cursor is None or record["starred_at"] > cursor)
    ]
    unprocessed.sort(key=lambda record: record["starred_at"], reverse=True)
    selected = unprocessed[:limit]
    return {
        "fetched_count": len(unique),
        "processed_key_count": len(processed),
        "new_count_total": len(unprocessed),
        "selected_count": len(selected),
        "truncated": len(unprocessed) > len(selected),
        "items": selected,
    }


def run(
    *,
    username: str,
    ledger_file: Path | None,
    limit: int,
    input_json: Path | None,
    pages: int,
    processed_keys: set[str] | None = None,
    cursor: str | None = None,
) -> dict[str, Any]:
    """Execute a collector run and return its versioned JSON contract."""
    if input_json is None:
        payload = fetch_starred(username, pages=pages)
        source = "github-api"
    else:
        payload = json.loads(input_json.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("input JSON must contain a list")
        source = str(input_json)

    processed = read_ledger(ledger_file)
    processed.update(processed_keys or set())
    ledger_cursor = read_cursor(ledger_file)
    cursor_candidates = [value for value in (ledger_cursor, cursor) if value is not None]
    effective_cursor = max(cursor_candidates) if cursor_candidates else None
    selection = select_new(payload, processed, limit, effective_cursor)
    return {
        "schema_version": 1,
        "username": username,
        "fetched_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": source,
        "cursor": effective_cursor,
        **selection,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", default="ddmanyes")
    parser.add_argument("--ledger-file", type=Path)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--input-json", type=Path, help="Use a fixture instead of the network")
    parser.add_argument(
        "--processed-key",
        action="append",
        default=[],
        help="Mark one repo_id@starred_at key as processed; repeat as needed",
    )
    parser.add_argument(
        "--cursor",
        help="Ignore Stars at or before this ISO-8601 starred_at high-watermark",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = run(
            username=args.username,
            ledger_file=args.ledger_file,
            limit=args.limit,
            input_json=args.input_json,
            pages=args.pages,
            processed_keys=set(args.processed_key),
            cursor=args.cursor,
        )
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
