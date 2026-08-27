"""Normalize a Threads post URL into the ledger identity used by the Skill."""

from __future__ import annotations

import argparse
import re
from urllib.parse import urlsplit


POST_PATH = re.compile(r"^/@([A-Za-z0-9._]+)/post/([A-Za-z0-9_-]+)/*$")
ALLOWED_HOSTS = {"threads.com", "www.threads.com", "threads.net", "www.threads.net"}
ERROR_MESSAGE = "Expected a Threads post URL: https://www.threads.com/@user/post/shortcode"


def normalize_url(raw_url: str) -> str:
    parsed = urlsplit(raw_url.strip())
    host = (parsed.hostname or "").lower()
    match = POST_PATH.fullmatch(parsed.path)
    if parsed.scheme not in {"http", "https"} or host not in ALLOWED_HOSTS or match is None:
        raise ValueError(ERROR_MESSAGE)
    username, shortcode = match.groups()
    return f"https://www.threads.com/@{username}/post/{shortcode}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Threads post URL to normalize")
    args = parser.parse_args()
    try:
        print(normalize_url(args.url))
    except ValueError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
