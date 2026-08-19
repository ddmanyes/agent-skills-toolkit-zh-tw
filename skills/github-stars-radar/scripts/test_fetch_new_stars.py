#!/usr/bin/env python3
"""Unit tests for the deterministic GitHub Stars collector."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import fetch_new_stars as subject


def star(repo_id: int, full_name: str, starred_at: str) -> dict:
    owner, name = full_name.split("/", 1)
    return {
        "starred_at": starred_at,
        "repo": {
            "id": repo_id,
            "full_name": full_name,
            "name": name,
            "owner": {"login": owner},
            "html_url": f"https://github.com/{full_name}",
            "description": f"Description for {name}",
            "language": "Python",
            "license": {"spdx_id": "MIT"},
            "stargazers_count": repo_id * 10,
            "forks_count": repo_id,
            "open_issues_count": 2,
            "topics": ["ai", "tools"],
            "archived": False,
            "pushed_at": "2026-08-18T00:00:00Z",
            "default_branch": "main",
        },
    }


class NormalizeTests(unittest.TestCase):
    def test_normalizes_star_envelope(self) -> None:
        record = subject.normalize_star(star(7, "acme/tool", "2026-08-19T00:00:00Z"))
        self.assertEqual(record["key"], "7@2026-08-19T00:00:00Z")
        self.assertEqual(record["full_name"], "acme/tool")
        self.assertEqual(record["license"], "MIT")

    def test_rejects_payload_without_star_timestamp(self) -> None:
        with self.assertRaisesRegex(ValueError, "starred_at"):
            subject.normalize_star({"id": 7, "full_name": "acme/tool"})


class LedgerTests(unittest.TestCase):
    def test_extracts_only_canonical_markers(self) -> None:
        content = """
        prose 1@not-a-marker
        <!-- github-star-key: 7@2026-08-19T00:00:00Z -->
        <!-- github-star-key: 8@2026-08-18T00:00:00Z -->
        """
        self.assertEqual(
            subject.parse_ledger(content),
            {
                "7@2026-08-19T00:00:00Z",
                "8@2026-08-18T00:00:00Z",
            },
        )

    def test_missing_ledger_file_is_empty(self) -> None:
        self.assertEqual(subject.read_ledger(Path("/definitely/missing.md")), set())

    def test_extracts_latest_cursor(self) -> None:
        content = """
        <!-- github-stars-cursor: 2026-08-14T00:00:00Z -->
        <!-- github-stars-cursor: 2026-08-19T00:00:00Z -->
        """
        self.assertEqual(subject.parse_cursor(content), "2026-08-19T00:00:00Z")


class SelectionTests(unittest.TestCase):
    def test_filters_processed_sorts_newest_and_applies_limit(self) -> None:
        payload = [
            star(1, "acme/old", "2026-08-17T00:00:00Z"),
            star(3, "acme/new", "2026-08-19T00:00:00Z"),
            star(2, "acme/middle", "2026-08-18T00:00:00Z"),
        ]
        result = subject.select_new(
            payload,
            processed={"2@2026-08-18T00:00:00Z"},
            limit=1,
            cursor=None,
        )
        self.assertEqual(result["new_count_total"], 2)
        self.assertTrue(result["truncated"])
        self.assertEqual([item["full_name"] for item in result["items"]], ["acme/new"])

    def test_cursor_excludes_unlisted_historical_stars(self) -> None:
        payload = [
            star(3, "acme/new", "2026-08-19T00:00:00Z"),
            star(1, "acme/historical", "2026-08-13T00:00:00Z"),
        ]
        result = subject.select_new(
            payload,
            processed=set(),
            limit=5,
            cursor="2026-08-14T00:00:00Z",
        )
        self.assertEqual([item["full_name"] for item in result["items"]], ["acme/new"])

    def test_cli_accepts_fixture_and_emits_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = Path(tmpdir) / "stars.json"
            fixture.write_text(
                json.dumps([star(9, "acme/fixture", "2026-08-19T01:00:00Z")]),
                encoding="utf-8",
            )
            result = subject.run(
                username="ddmanyes",
                ledger_file=None,
                limit=5,
                input_json=fixture,
                pages=1,
                processed_keys=set(),
                cursor=None,
            )
        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(result["username"], "ddmanyes")
        self.assertEqual(result["selected_count"], 1)

    def test_run_accepts_processed_keys_without_local_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = Path(tmpdir) / "stars.json"
            fixture.write_text(
                json.dumps([star(9, "acme/fixture", "2026-08-19T01:00:00Z")]),
                encoding="utf-8",
            )
            result = subject.run(
                username="ddmanyes",
                ledger_file=None,
                limit=5,
                input_json=fixture,
                pages=1,
                processed_keys={"9@2026-08-19T01:00:00Z"},
                cursor=None,
            )
        self.assertEqual(result["selected_count"], 0)


if __name__ == "__main__":
    unittest.main()
