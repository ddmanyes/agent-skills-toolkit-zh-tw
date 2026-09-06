---
name: pptx
description: Read, create or edit local PowerPoint files using this toolkit's HTML conversion, OOXML and template scripts; select the workflow needed for the requested PPTX work.
license: Proprietary. LICENSE.txt has complete terms
---
# PowerPoint files

Determine the requested slides, content, design and output first. Preserve the original or a recoverable copy before replacing it. For native Google Slides or a configured presentation service, use its corresponding tools and required checks.

| Task | Read when needed |
| --- | --- |
| Extract text, inspect themes, notes or XML | [Reading](references/reading.md) |
| Create slides with html2pptx | [Creation](references/create.md), then relevant converter rules |
| Edit existing OOXML | [Editing](references/edit.md), then relevant schema rules |
| Build from a template using rearrange/inventory/replace | [Template workflow](references/template.md) |
| Thumbnail grids, rendered inspection or dependencies | [Rendering](references/rendering.md) |

Run scripts relative to this installed Skill's directory or use absolute paths; input and output paths refer to the user's files.

**Data-loss boundary:** `scripts/replace.py` clears every inventoried text shape omitted from its replacement JSON. Before using it, account for all shapes in the working deck and preserve paragraph formatting. For a small text edit, prefer a targeted edit; never treat a partial replacement JSON as a partial-update API.

For visual work, respect the user's brand, template, content and chosen runtime. Preserve slide order, notes, relationships, media and existing styles unless the change requires otherwise.

Complete the requested content, run relevant structure checks, render the result and inspect affected slides for clipping, overlap, contrast and misplaced elements. Inspect the full deck after a template rebuild or changes to shared layouts. Fix problems and repeat affected checks before delivery. If rendering or a dependency is unavailable, report precisely what was checked and what remains unverified; XML validity alone does not prove appearance.
