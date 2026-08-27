# Repository Agent Instructions

Whenever you create, edit, review, validate, commit, push, or publish a Skill under `skills/` or `disabled_skills/`, use `skills/skill-qa-gate/SKILL.md`.

Run the deterministic validator on each changed Skill. Fix every `FAIL` before publication. Report unresolved `WARN` findings. Do not run this gate merely because you execute an unrelated Skill normally.
