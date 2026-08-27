"""Normalize an X status URL into the ledger identity used by the Skill."""

from __future__ import annotations

import argparse
import re
from urllib.parse import urlsplit


STATUS_PATH = re.compile(
    r"^/([A-Za-z0-9_]+)/status/([0-9]+)(?:/(?:photo|video)/[0-9]+)?/*$"
)
ALLOWED_HOSTS = {"x.com", "www.x.com", "twitter.com", "www.twitter.com"}
ERROR_MESSAGE = "Expected an X status URL: https://x.com/user/status/id"


def normalize_url(raw_url: str) -> str:
    parsed = urlsplit(raw_url.strip())
    host = (parsed.hostname or "").lower()
    match = STATUS_PATH.fullmatch(parsed.path)
    if parsed.scheme not in {"http", "https"} or host not in ALLOWED_HOSTS or match is None:
        raise ValueError(ERROR_MESSAGE)
    username, status_id = match.groups()
    return f"https://x.com/{username}/status/{status_id}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="X status URL to normalize")
    args = parser.parse_args()
    try:
        print(normalize_url(args.url))
    except ValueError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
