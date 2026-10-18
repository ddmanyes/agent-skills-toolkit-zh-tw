# 致謝 (Acknowledgements)

本專案的技能邏輯深受以下開源專案與作者的啟發。我們在此表達最深切的感謝，並鼓勵使用者前往他們的原專案給予 Star 支持：

### 1. 核心工作流與超級能力
- **[obra/superpowers](https://github.com/obra/superpowers)** (Author: Jesse Vincent / @obra)
  - 提供了 `sp-` 系列的核心哲學，包含腦力激盪、計畫撰寫與測試驅動開發。
- **[snarktank/ralph](https://github.com/snarktank/ralph)**
  - 提供了自主循環開發 (Autonomous Loop) 的概念。
- **[OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files)**
  - 提供了以 Markdown 檔案為核心的計畫追蹤系統。

### 1b. 工程方法論與設計詞彙
- **[mattpocock/skills](https://github.com/mattpocock/skills)** (Author: Matt Pocock / @mattpocock)
  - 提供了 `domain-modeling`、`improve-architecture`、`writing-for-agents`、`wait-what`、`research`、`teach`、`tdd`、`to-questionnaire` 與 `ask-matt` 路由概念，並啟發了 `sp-brainstorming`（grilling）與 `sp-code-review`（雙軸 + Fowler code smell）的升級。

### 2. 官方插件與專業工具
- **[anthropics/skills](https://github.com/anthropics/skills)**
  - 提供了 `docx`, `xlsx`, `pdf`, `pptx`, `mcp-builder`, `webapp-testing` 等權威技能。
- **[anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)**
  - 提供了 `code-simplifier` 等代碼優化工具。
- **[anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community)**（`eli5` 原作者：Thariq Shihipar）
  - 提供 `eli5` 的單頁視覺解說概念；本倉庫版本加入 Codex metadata、離線資產、安全、可存取性與來源查核規則。

### 3. UI/UX 視覺強化
- **[nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)**
  - 提供了極致的前端設計風格與優先等級規範。

### 4. 圖表設計與語意重繪
- **[cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design)** (Author: Cathryn Lavery)
  - 提供 `diagram-design` 的 SVG／HTML 圖表工作流、Mermaid 與 draw.io 結構抽取器，以及安全與可存取性自檢腳本。本倉庫收錄依 MIT License 改編的繁體中文精簡版，並新增 Dots／signal-flow 與 Second Brain 整合指引。

---
*本倉庫為繁體中文在地化優化版，旨在服務台灣開發者。所有原始邏輯之版權歸屬原作者及其對應之開源協議。*

## 2026-10-18 來源追溯補強

Matt Pocock 上游固定在 [`49dd158d1076134a641b33efb035946536778336`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336)。本輪保留此版本 MIT 授權與 copyright 原文於每個受影響目錄的 `UPSTREAM-LICENSE.txt`。

- **改編**：`improve-architecture`、`domain-modeling`、`tdd`、`ask-matt`、`teach`、`wait-what`；新增 `codebase-design`、`handoff`、`retro`。
- **方法整合**：`diagnosing-bugs` → `sp-fix-test`、`code-review` → `sp-code-review`、`to-tickets` → `sp-writing-plans`、`implement-spec` → `sp-executing-plans`。SP 系列仍保留原有其他來源與本機規則，不改稱 Matt 的完整原版。
- **本機補強**：`code-simplifier` 加入可讀性與基準驗證；既有致謝來源為 Anthropic，精確原始 commit 未確認。本輪未把它歸給 Matt。
- `research`、`to-questionnaire`、`writing-for-agents` 已有對應內容或本機適配，本輪保留。

改編不是官方發行或作者背書。未完整查核的其他來源授權不在此重新宣告；原有 LICENSE／NOTICE 應隨資源保留。完整能力對照見 [升級紀錄](docs/skills-upgrade-2026-10-18.md)。

## REA（2026-10-18）

`reverse-engineer-anything` 及 references 原樣取自 [morluto/rea](https://github.com/morluto/rea) 的 `rea-agents@6.5.0` npm 發行包；MIT 原文與 copyright 保存在技能內的 UPSTREAM-LICENSE.txt，完整性與逐檔hash見 upstream.json。npm metadata未提供gitHead，未推定commit。這是上游指引的分發，不是我們自製的逆向引擎，也不代表上游背書。

`ep-tool-investigation` 為本工具包新增的 EP 候選研究／驗收流程，選擇性使用 REA。REA 的授權不授予被研究軟體、資料或模型再散布權。
