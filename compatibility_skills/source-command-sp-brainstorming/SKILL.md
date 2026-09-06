---
name: source-command-sp-brainstorming
description: Use when the user explicitly invokes the legacy sp-brainstorming command; preserve that invocation through its maintained workflow.
---

# 舊命令 sp-brainstorming

僅在使用者明確要求 `sp-brainstorming` 或 `$source-command-sp-brainstorming` 時使用；不自行攔截一般任務。

1. 讀取同一安裝根中的 [正本流程](../sp-brainstorming/SKILL.md)，以使用者本次需求決定範圍，套用其檢查、完成與失敗處理。
2. `SKILL_DIR` 是本檔所在的已安裝目錄；`CANONICAL_DIR` 是它的 `../sp-brainstorming`。正本中的 scripts／references 相對於 `CANONICAL_DIR`，不是此舊入口或使用者專案目錄。
3. 執行前確認相依檔案存在；找不到時列出缺失的完整路徑並停止依賴它的步驟。保留專案工作目錄；以腳本的絕對路徑執行，只有腳本明定需要時才暫時切換工作目錄。
4. 沿用使用者已給的授權和適用專案指示；此相容入口不增加工具、檔案、發布或憑證權限。回報正本要求的結果與未完成項目。

釐清設計時可先提出 1–2 個有取捨的候選方案；先確認專案背景、動機及最終使用者，已知事實自行查證。
