# Skill QA Quality Rules

## Deterministic gate

Fail a Skill when any of these conditions is true:

- `SKILL.md` is missing or its frontmatter is malformed.
- `name` is missing, invalid, or different from the Skill directory name.
- `description` is missing.
- A local Markdown reference points to a missing file.
- An instruction contains a broad destructive command such as `rm -rf /`, `rm -rf ~`, or `rm -rf $HOME`.

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

Compare source and revision before accepting a rewrite. Reject the revision if it:

- changes or removes a number, path, parameter, identifier, or quoted literal;
- removes a negative, exception, precondition, or authorization boundary;
- changes uncertainty into certainty or certainty into uncertainty;
- changes who performs an action;
- changes success, failure, retry, or recovery behavior;
- invents a cause, mechanism, frequency, guarantee, or recommendation;
- narrows or expands the original scope without authorization.

Shorter text is not automatically better. Stop rewriting when the contract is unambiguous and complete.

## Result levels

- Use `FAIL` for objective defects and unsafe commands.
- Use `WARN` for ambiguity and portability concerns that require judgment.
- Use `PASS` only when deterministic checks succeed. State separately whether forward tests ran.
