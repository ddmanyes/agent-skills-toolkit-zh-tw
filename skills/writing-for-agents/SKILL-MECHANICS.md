# Skill mechanics

This is the Skill-specific branch of [writing-for-agents](SKILL.md): discovery metadata, explicit invocation and routing. Apply the target client's actual configuration; names shared by two clients do not guarantee identical behavior.

## Invocation

A discoverable Skill needs a concise description saying when and why to use it. State the capability and distinguishing triggers, not every downstream step. Preserve details needed to distinguish near-miss requests.

In Codex, explicit-only intent is configured with `policy.allow_implicit_invocation: false` in `agents/openai.yaml`. A legacy `disable-model-invocation: true` frontmatter field may be retained for a client that supports it, but is not evidence of the Codex policy. Verify installed runtime discovery after changing settings.

Explicit invocation changes automatic discovery; it does not make reference files unreadable by authorized filesystem access. Avoid claims that no other Skill can ever consult such content or that a setting guarantees zero token cost.

## Splitting and routers

Split a separate Skill only when the behavior needs its own invocation trigger. Otherwise keep shared detailed knowledge in linked reference files with clear read conditions. Dependencies outside a bundle require a declared installation prerequisite and a missing-dependency fallback.

A router identifies the appropriate capability or reference without starting unrelated workflows. Compatibility aliases preserve the old invocation and distinct semantics, point to the maintained implementation, resolve paths relative to the installed Skill directory and stop clearly if the target is unavailable.

## Verify across clients and models

Check frontmatter, target runtime metadata, links and bundled scripts first. Then test positive and near-miss triggers plus completion/failure cases when selection behavior matters. Preserve useful operational detail for Astra, Sol and Luna until evidence shows it is unnecessary for each supported model. Report untested runtime or model behavior explicitly.
