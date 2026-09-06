---
name: source-command-project-architect
description: Use when the user explicitly invokes the legacy project-architect command; preserve that invocation through its maintained workflow.
---

# 舊命令 project-architect

僅在使用者明確要求 `project-architect` 或 `$source-command-project-architect` 時使用；不自行攔截一般任務。

1. 讀取同一安裝根中的 [正本流程](../project-architect/SKILL.md)，以使用者本次需求決定範圍，套用其檢查、完成與失敗處理。
2. `SKILL_DIR` 是本檔所在的已安裝目錄；`CANONICAL_DIR` 是它的 `../project-architect`。正本中的 scripts／references 相對於 `CANONICAL_DIR`，不是此舊入口或使用者專案目錄。
3. 執行前確認相依檔案存在；找不到時列出缺失的完整路徑並停止依賴它的步驟。保留專案工作目錄；以腳本的絕對路徑執行，只有腳本明定需要時才暫時切換工作目錄。
4. 沿用使用者已給的授權和適用專案指示；此相容入口不增加工具、檔案、發布或憑證權限。回報正本要求的結果與未完成項目。

此舊命令預設為 Codex 新專案建立 `AGENTS.md`；已存在 `CLAUDE.md` 或其他客戶端規範時遵循正本的沿用策略，不將它們機械重新命名。
