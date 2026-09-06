# Agent Skills Toolkit — 繁體中文優化版

本專案收錄 40 個 Active Skills，可同步到 Claude Code、Codex／通用 Agent 與 Antigravity，涵蓋開發工作流、文件與資料處理、研究及內容整理。詳細流程與技術資源隨技能一起分發。

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

本專案整理開源社群作品，保留原作者的版權及各技能授權。詳見 [來源與致謝](ACKNOWLEDGEMENTS.md)。
