---
name: sb-article-housekeeper
description: Audit Second Brain article and social-source records, then maintain the personal housekeeping report through the central MCP. Use for article housekeeping, source freshness review, or replay of an incomplete housekeeping run.
---

# Second Brain Article Housekeeper

Audit the central Second Brain before changing any housekeeping note. Treat the MCP result as the source of truth for this run.

Read [housekeeping-contract.md](references/housekeeping-contract.md) before using source-specific note titles or policies.

## Required entry sequence

1. Call Second Brain `get_agent_instructions()`.
2. Call `audit_article_records(scope="all", limit=100, stale_after_days=8)`.
3. Stop and report a retryable failure if either call fails. Do not write a report from partial or cached audit data.

Do not call another Second Brain tool before the two required calls succeed. Keep all returned paths vault-relative. Never read or write the vault filesystem directly.
