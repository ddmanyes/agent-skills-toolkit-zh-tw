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

## 已安裝版本的功能分支
<!-- skill-routing-v1 -->
需要 PptxGenJS、原生圖表、`.potx`、投影片複製／清理或模板基準驗證 時，讀 [跨平台分支路由](../skill-toolkit/references/variant-routing.md)，以 `resolve --kind synced --skill pptx` 尋找該機已安裝版本，讀取完整流程及其附帶資源後再操作。原有本機實作繼續保留；不同版本的同名腳本參數不可混用。
此分支需同時安裝 skill-toolkit；缺少時可沿用上述本機功能，並回報外部分支不可用。外部流程中的預裝套件／沙箱假設須依目前環境核對；原檔保護、權限及驗證規則仍適用。來源不可用或有多個不同版本時，不停用那些版本，也不假稱該功能已完成。
