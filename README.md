# Agent Skills Toolkit — 繁體中文優化版

本專案收錄 43 個 Active Skills，可同步到 Claude Code、Codex／通用 Agent 與 Antigravity，涵蓋開發工作流、文件與資料處理、研究及內容整理。詳細流程與技術資源隨技能一起分發。

## 快速開始

Clone 完整 repository，再執行同步；不要只複製 `SKILL.md`，以免缺少 scripts、references 或 templates。

**Windows PowerShell**

```powershell
git clone https://github.com/ddmanyes/agent-skills-toolkit-zh-tw.git
cd agent-skills-toolkit-zh-tw
.\scripts\sync-local-skills.ps1 -All
```

**macOS／Linux**

```bash
git clone https://github.com/ddmanyes/agent-skills-toolkit-zh-tw.git
cd agent-skills-toolkit-zh-tw
./scripts/sync-local-skills.sh --all
```

**已使用共用 symlink 的機器**：若 `~/.claude/skills` 指向 `~/.agents/skills`，請用 `./scripts/sync-local-skills.sh --agents --antigravity`；不要對連結執行 `--all`。詳見[跨電腦更新](docs/installation.md#跨電腦更新與共用目錄)。

`-All`／`--all` 同步到 `~/.claude/skills`、`~/.agents/skills` 和 `~/.gemini/config/skills`。只需一個客戶端、更新既有安裝或驗證結果時，請看 [安裝指南](docs/installation.md)。完成後重啟客戶端或開新 session。

同步會先備份被覆寫的檔案，保留其他本機內容。Disabled Skills 與相容 overlay 不會自動啟用或新增；四個 Radar Skills 是過渡副本，正式更新由獨立維護來源管理，既有安裝預設不被覆蓋。操作範圍與復原方式見安裝指南。

## 文件導覽

| 想做甚麼 | 文件 |
| --- | --- |
| 安裝、指定客戶端更新、備份與驗證 | [安裝指南](docs/installation.md) |
| 查看技能分類、用途與 Radar 工作流 | [技能目錄](docs/skill-catalog.md) |
| 為專案選擇合適的技能組合 | [新專案工作流](新專案工作流.md) |
| 更新舊命令入口與既有本機流程 | [相容入口指南](compatibility_skills/README.md) |
| 查看修復證據、驗證與未測限制 | [2026-09-06 稽核紀錄](docs/skills-audit-2026-09-06.md) |

本機安裝數量依客戶端與選擇範圍而異，不等於 Active Skills 總數。Astra／Sol／Luna 的實際效果與速度尚未實測。

## 來源與致謝

本專案是社群技能的繁體中文改編與跨客戶端整合工具包；不是下列作者的官方發行版，也不代表作者背書。

| 參考來源 | 本機技能／範圍 | 本專案的改編 |
| --- | --- | --- |
| [Matt Pocock / skills](https://github.com/mattpocock/skills) | `tdd`、`domain-modeling`、`improve-architecture`、`codebase-design`、`handoff`、`retro`、`teach` 等 | 保留舊名稱、調整觸發與授權、相容舊詞彙表、補驗證；部分方法整合入 SP 系列 |
| [Jesse Vincent / superpowers](https://github.com/obra/superpowers) | `sp-` 開發流程系列 | 依任務規模規劃、沿用既有批准與專案規範 |
| [Anthropic / skills](https://github.com/anthropics/skills) 與 [官方 plugins](https://github.com/anthropics/claude-plugins-official) | 文件工具、`mcp-builder`、`code-simplifier` 等 | 在地化與客戶端適配；各目錄的授權保留 |
| [完整來源清單](ACKNOWLEDGEMENTS.md) | Ralph、檔案規劃、圖表與其他技能 | 逐項說明參考關係，不將所有內容宣稱為原創 |

**本輪上游基準**：Matt Pocock [`49dd158`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336)（2026-10-18 查核）。新增／更新的改編技能附 `upstream.json` 與 `UPSTREAM-LICENSE.txt`，保留來源路徑、commit 與 MIT 原文。舊項目若未能確認原始 commit，會標示未確認，不倒填來源。

來源關係區分「改編」、「方法參考」與「本機新增」；授權依各技能與第三方資源原檔，不以一份總授權覆蓋全部作品。參見[本輪升級與完整對照](docs/skills-upgrade-2026-10-18.md)。
