---
name: skill-qa-gate
description: Validate and improve Agent Skills with deterministic structure checks, safety-contract review, controlled-language ambiguity checks, and semantic-preservation review. Use whenever Codex creates, edits, reviews, audits, validates, commits, pushes, or publishes a Skill, including changes to SKILL.md, agents/openai.yaml, scripts, or references. Do not use merely because another Skill is being executed normally.
---

# Skill QA Gate

Treat QA as a mixed gate. Block objective structure and safety failures. Report language ambiguity as warnings unless the user explicitly requests warnings as errors.

## Workflow

1. Identify each changed Skill directory. Do not inspect unrelated Skills unless the user requests a repository-wide audit.
2. Use Python 3 with PyYAML installed (`python3 -m pip install "PyYAML>=6,<7"` in the task environment), then run the deterministic validator:

   ```bash
   python3 "$SKILL_QA_DIR/scripts/lint_skill.py" <path/to/skill>
   ```

   Set `SKILL_QA_DIR` to this Skill's directory. The default `--profile repository` enforces this repository's lowercase names and directory matching.
   Use `--profile runtime` to audit externally supplied Skills without treating vendor naming conventions as runtime failures.
   Add `--warnings-as-errors` only for an explicitly strict gate.
3. Fix every `FAIL` finding when the user authorized edits. If the request is review-only, report findings without modifying files.
4. Read [quality-rules.md](references/quality-rules.md) when the validator reports ambiguity or when prose changed.
5. Read [safety-contracts.md](references/safety-contracts.md) when the Skill can write, delete, publish, execute external instructions, use credentials, or change remote state.
6. Compare the revised instructions with the source. Preserve actors, actions, objects, numbers, paths, negation, modality, conditions, scope, failure behavior, and recovery behavior.
7. Run tests for changed executable behavior; preserve and reuse working scripts. Run `quick_validate.py` when it is available, interpreting product-specific metadata as warnings.
   For changes to this validator, run `python3 "$SKILL_QA_DIR/scripts/test_lint_skill.py"`.
8. Rerun affected checks after fixes. Within an approved editing scope, investigate and correct failures before reporting; stop dependent publication if a failure remains.
9. Report `PASS`, `WARN`, or `FAIL`, unresolved warnings, commands run, and checks that could not run. Distinguish confirmed defects from hypotheses requiring model or service access.

## Severity Contract

- `FAIL`: Invalid identity or frontmatter, missing referenced files, unsafe broad destructive commands, or another objective defect. Do not publish.
- `WARN`: Ambiguous wording, non-portable metadata, missing recommended UI metadata, long instructions, or safety language that needs human review.
- `PASS`: All deterministic checks passed. This does not prove that the Skill is effective; run realistic forward tests for complex workflows.

## Coverage and completion

The gate parses YAML, checks local Markdown links in the entry and `references/`, and reports concrete missing `scripts/...` literals as `REF002` warnings for review.
Markdown examples in fenced code blocks are not links to required resources. Dynamic paths, imports, tool availability, remote links, and full workflow execution require targeted checks.
A missing script literal becomes a confirmed failure only after its role as a required bundled resource is established; placeholders and generated outputs are not missing dependencies.

Completion requires no unresolved deterministic failures, successful tests for changed behavior, preserved useful knowledge and authority boundaries, and an honest account of untested behavior.
For substantial trigger or workflow changes shared by Astra, Sol, and Luna, use representative cases across the available target models before claiming reliability or speed improvements.
Static repairs alone do not establish model effects. Preserve rules whose value for another target model remains untested.

Do not claim formal ASD-STE100 compliance. Apply its structural clarity principles only. Treat lexical compliance as unverified without the official controlled dictionary.

## Trigger Behavior

Rely on implicit triggering during Skill creation, modification, review, validation, commit, push, and publication.
Allow users to invoke `$skill-qa-gate` explicitly for an audit or strict run.
Do not add this QA pass to ordinary execution of unrelated Skills.
