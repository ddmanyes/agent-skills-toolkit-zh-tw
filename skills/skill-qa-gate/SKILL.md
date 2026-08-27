---
name: skill-qa-gate
description: Validate and improve Agent Skills with deterministic structure checks, safety-contract review, controlled-language ambiguity checks, and semantic-preservation review. Use whenever Codex creates, edits, reviews, audits, validates, commits, pushes, or publishes a Skill, including changes to SKILL.md, agents/openai.yaml, scripts, or references. Do not use merely because another Skill is being executed normally.
---

# Skill QA Gate

Treat QA as a mixed gate. Block objective structure and safety failures. Report language ambiguity as warnings unless the user explicitly requests warnings as errors.

## Workflow

1. Identify each changed Skill directory. Do not inspect unrelated Skills unless the user requests a repository-wide audit.
2. Run the deterministic validator:

   ```bash
   python3 "$SKILL_QA_DIR/scripts/lint_skill.py" <path/to/skill>
   ```

   Set `SKILL_QA_DIR` to this Skill's directory. Add `--warnings-as-errors` only for an explicitly strict gate.
3. Fix every `FAIL` finding when the user authorized edits. If the request is review-only, report findings without modifying files.
4. Read [quality-rules.md](references/quality-rules.md) when the validator reports ambiguity or when prose changed.
5. Read [safety-contracts.md](references/safety-contracts.md) when the Skill can write, delete, publish, execute external instructions, use credentials, or change remote state.
6. Compare the revised instructions with the source. Preserve actors, actions, objects, numbers, paths, negation, modality, conditions, scope, failure behavior, and recovery behavior.
7. Run the Skill's own tests. Run `quick_validate.py` when it is available.
8. Report the final result as `PASS`, `WARN`, or `FAIL`. List unresolved warnings and the commands that were run.

## Severity Contract

- `FAIL`: Invalid identity or frontmatter, missing referenced files, unsafe broad destructive commands, or another objective defect. Do not publish.
- `WARN`: Ambiguous wording, non-portable metadata, missing recommended UI metadata, long instructions, or safety language that needs human review.
- `PASS`: All deterministic checks passed. This does not prove that the Skill is effective; run realistic forward tests for complex workflows.

Do not claim formal ASD-STE100 compliance. Apply its structural clarity principles only. Treat lexical compliance as unverified without the official controlled dictionary.

## Trigger Behavior

Rely on implicit triggering during Skill creation, modification, review, validation, commit, push, and publication.
Allow users to invoke `$skill-qa-gate` explicitly for an audit or strict run.
Do not add this QA pass to ordinary execution of unrelated Skills.
