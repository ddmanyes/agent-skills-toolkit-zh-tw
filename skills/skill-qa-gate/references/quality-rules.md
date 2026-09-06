# Skill QA Quality Rules

## Deterministic gate

Fail a Skill when any of these conditions is true:

- `SKILL.md` is missing or its frontmatter is malformed.
- `name` or `description` is not a non-empty string.
- In the `repository` profile, `name` violates the lowercase hyphen-case convention or differs from its directory. The `runtime` profile reports naming portability warnings instead.
- `description` is missing.
- A local Markdown link outside a code example points to a missing file. Check links in `SKILL.md` and `references/` relative to the containing document.
- An instruction contains a broad destructive command such as `rm -rf /`, `rm -rf ~`, or `rm -rf $HOME`.

Parse YAML with PyYAML and reject malformed input or duplicate keys; a hand-written scalar parser is insufficient.
Keep angle-bracket destinations, escaped spaces, URL-encoded spaces, and balanced parentheses intact when checking Markdown links.
Review `REF002` script-literal warnings: establish whether a path names an installed dependency, an example, or an output before treating it as a confirmed missing resource.
Executable shell fences can contain script hints; generic code examples and variable-built paths are not evidence of required files.
Do not claim complete dependency coverage: inspect imports, scripts, runtime settings, and services separately when the edited workflow depends on them.

Treat product-specific frontmatter keys as portability warnings, not failures. Claude, Codex, and other runtimes do not accept exactly the same metadata.

## Controlled-language review

Use these ASD-STE100-inspired structural rules for English instructions:

- Name the actor when responsibility could be unclear.
- Put one action in each procedural sentence.
- Preserve `must`, `must not`, `may`, `only`, `unless`, and similar modality or scope markers.
- Replace vague conditions such as `when appropriate`, `as needed`, and `if necessary` with testable conditions.
- Prefer active voice for procedures.
- Split long instruction sentences when the split does not change meaning.
- Define project-specific terms once and use the same term consistently.

Do not enforce official controlled vocabulary. Do not claim ASD-STE100 compliance without the official dictionary and qualified review.

For Traditional Chinese instructions, apply the same contract principles without presenting them as STE compliance:

- 寫明執行者、動作、目標與完成條件。
- 把「適當時」、「視需要」、「相關內容」改成可驗證條件。
- 保留「可能」、「必須」、「僅限」、「除非」與否定詞。
- 把多個連續動作拆成有順序的步驟。

## Semantic-preservation review

Compare source and revision before accepting a rewrite. Reject unapproved or accidental semantic changes; a repair explicitly within the user-approved scope may intentionally change the affected rule. Review whether it:

- changes or removes a number, path, parameter, identifier, or quoted literal;
- removes a negative, exception, precondition, or authorization boundary;
- changes uncertainty into certainty or certainty into uncertainty;
- changes who performs an action;
- changes success, failure, retry, or recovery behavior;
- invents a cause, mechanism, frequency, guarantee, or recommendation;
- narrows or expands the original scope without authorization.

For shared Skills, preserve knowledge and guardrails needed by Astra, Sol, or Luna until tests justify a change. Do not infer cross-model effects from one model's static review.

Shorter text is not automatically better. Stop rewriting when the contract is unambiguous and complete.

## Result levels

- Use `FAIL` for objective defects and unsafe commands.
- Use `WARN` for ambiguity and portability concerns that require judgment.
- Use `PASS` only when deterministic checks succeed. State separately whether forward tests ran.
