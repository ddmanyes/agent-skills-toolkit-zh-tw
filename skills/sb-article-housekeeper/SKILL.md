---
name: sb-article-housekeeper
description: Audit Second Brain article and social-source records, then maintain the personal housekeeping report through the central MCP. Use for article housekeeping, source freshness review, or replay of an incomplete housekeeping run.
---

# Second Brain Article Housekeeper

Audit the central Second Brain before changing any housekeeping note. Treat the MCP result as the source of truth for this run.

Read [housekeeping-contract.md](references/housekeeping-contract.md) before resolving report targets, formatting report content, or applying source-specific policy.

## Authority

Invocation authorizes writes only to the managed article index and housekeeping audit log named in the contract.

The Skill may create a missing managed report. It may snapshot an existing article index. It may replace the managed block and append one audit entry.

The Skill must keep collector notes, source ledgers, sync states, and article notes unchanged.

## Workflow

1. Call Second Brain `get_agent_instructions()`.
2. Call `audit_article_records(scope="all", limit=100, stale_after_days=8)`.
3. Validate the structured result against the required fields in the contract.
4. Stop before all writes if either required call fails or the result is incomplete.
5. Build the Asia/Taipei weekly run key `article-housekeeping:{YYYY-Www}`.
6. Sort and deduplicate candidate rows by issue type, match key, and vault-relative path.
7. Resolve the managed article index through `search_notes`.
8. Create the index only when no matching note exists. Stop without guessing when more than one note matches.
9. Read the complete index. Build the managed block from this audit. Preserve all text outside the two managed markers.
10. If an existing managed block changed, call `snapshot_note_tool(note_path, tier="base")`.
11. After the snapshot succeeds, call `update_note` with the complete preserved note.
12. For a new index, call `new_note` with the complete managed block instead.
13. Treat a confirmed no-change comparison as a successful index step.
14. Resolve the audit log only after the index step succeeds.
15. Append one entry when the run-key marker is absent. Create the log with that first entry when the log does not exist.
16. Re-read a target after an uncertain response before retrying its write.
17. Stop after the first confirmed failure. Report the completed step, target path, run key, and safe retry point.
18. Report issue totals, source freshness, and candidate-only actions. Report whether the index changed. Report whether the audit entry was appended or already present.

Do not call another Second Brain tool before Steps 1 and 2 succeed. Keep all paths vault-relative. Use only central MCP tools; the vault filesystem is not a write target.

## Recommendation boundary

- When `index_gap != 0`, add a `sync_index` recommendation to the report. Leave execution to a separately authorized workflow.
- Keep merge, archive, delete, `vault_sleep`, `consolidate_tool`, and `prune_archive_tool` as candidate report items. This Skill never executes them.
- When a source is stale, missing, or pending, recommend its owning collector. Keep source state unchanged.
