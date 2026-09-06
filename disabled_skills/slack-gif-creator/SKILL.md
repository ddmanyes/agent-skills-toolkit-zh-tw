---
name: slack-gif-creator
description: Create and validate animated GIFs intended for Slack messages or emoji. Use when the requested output is a Slack GIF; general images and unrelated animations use their own workflow.
license: Complete terms in LICENSE.txt
---

# Slack GIF Creator

Use the bundled GIF builder, validators, easing functions, and frame helpers. Preserve the user's subject, assets, requested motion, and output constraints.

## Workflow

1. Identify whether the output is an emoji or a message GIF. Reuse a type already stated; choose a reasonable default when the difference does not block the task.
2.
  Read the matching sections of [animation.md](references/animation.md) for frame generation, user-image handling, utility APIs, motion concepts, or optimization.
  Reuse the existing [GIF builder](core/gif_builder.py) and [validators](core/validators.py) rather than rewriting them.
3. Create frames, encode the GIF, and preview the animation. Read [requirements.txt](requirements.txt) for dependencies if imports fail; use the project's environment rather than assuming packages exist.
4. Run validate_gif with the selected emoji/message mode. Check dimensions, duration, file size, loop continuity, visible motion, and clipping against the request. If a constraint fails, reduce the least important frames, colors, or dimensions and recheck.

## Starting settings

The bundled guidance uses 128×128 for emoji and 480×480 for message GIFs, 10–30 FPS, and 48–128 colors.
Keep emoji animation under 3 seconds.
These are starting settings; check the user's requested limit and the actual validator result rather than calling them universal current Slack limits.

Preserve image provenance and the user's intended direct-use or reference-use role.
Do not assume emoji fonts or prepackaged artwork exist.
Where the runtime requires a particular image-generation or editing tool, follow that tool contract and use this Skill for GIF assembly and validation.

## Completion and failure

Deliver the GIF with its size, dimensions, and performed checks.
Fix visible or validator failures before calling it ready.
If an import, encoder, or preview tool remains unavailable, keep usable source frames and report exactly which check is blocked.
A passed file validator alone does not prove visible animation quality or successful Slack upload.

Write only to the authorized output directory and preserve existing user assets. Uploading to Slack or sending it to others requires user authorization.
