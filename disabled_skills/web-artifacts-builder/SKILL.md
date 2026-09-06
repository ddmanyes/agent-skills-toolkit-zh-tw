---
name: web-artifacts-builder
description: Build complex browser artifacts with React, TypeScript, Tailwind, and shadcn/ui, then bundle them as HTML. Use for multi-component artifacts needing application state or routing; simple single-file HTML can be built directly.
license: Complete terms in LICENSE.txt
---

# Web Artifacts Builder

Build the requested interactive artifact within the user's project and runtime constraints.
Use existing source and a configured build pipeline when present.
Read [build-and-bundle.md](references/build-and-bundle.md) when scaffolding a new artifact or using the bundled scripts.

## Workflow

1. Resolve the authorized project/output directory. Preserve user files and any existing generated output that must be recoverable.
2. For a new project, use the existing initialization helper after its prerequisites are available. For an existing project, implement the change using its stack and conventions.
3. Run the project's required checks and bundle the artifact with the existing helper when single-file HTML is requested.
4. Open the delivered build or bundle in a browser. Check rendering, relevant console errors, narrow/wide layout, and the primary interactions such as input, navigation, and state changes.
5. Fix observed failures and rerun affected checks, then share the result and report what was verified.

## Design

Use a visual direction grounded in the content and audience.
Preserve an existing brand, typography, accessibility constraints, and framework.
Centered layouts, gradients, rounded corners, or Inter are valid when they fit the project; avoid using them as an automatic template for every artifact.

## Completion and failure

A successful bundle command alone does not establish a working artifact.
Complete the requested build, render check, and main interaction check before describing the result as verified.
Focused verification is enough for a low-risk change; create new automated tests only when they cover meaningful behavior or a repository requirement.

If build, browser, or dependency setup remains blocked, preserve the source, report the failing command or missing capability, and identify unverified behavior.
Delivering a local file does not authorize deployment, external publication, or sending it to other people.
Do not claim an offline bundle until external dependencies have been checked.
