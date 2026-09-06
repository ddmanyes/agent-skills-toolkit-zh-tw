---
name: source-command-docx-docx-js
description: Use when the user explicitly invokes the legacy docx-docx-js command; preserve that invocation through its maintained workflow.
---

# 舊命令 docx-docx-js

僅在使用者明確要求 `docx-docx-js` 或 `$source-command-docx-docx-js` 時使用；不自行攔截一般任務。

1. 讀取同一安裝根中的 [正本流程](../docx/SKILL.md)，以使用者本次需求決定範圍，套用其檢查、完成與失敗處理。
2. `SKILL_DIR` 是本檔所在的已安裝目錄；`CANONICAL_DIR` 是它的 `../docx`。正本中的 scripts／references 相對於 `CANONICAL_DIR`，不是此舊入口或使用者專案目錄。
3. 執行前確認相依檔案存在；找不到時列出缺失的完整路徑並停止依賴它的步驟。保留專案工作目錄；以腳本的絕對路徑執行，只有腳本明定需要時才暫時切換工作目錄。
4. 沿用使用者已給的授權和適用專案指示；此相容入口不增加工具、檔案、發布或憑證權限。回報正本要求的結果與未完成項目。

## 技術參考分支

使用 docx-js 產生 Word 文件時，讀取建置、段落、表格、圖片、頁首頁尾及本次用到的章節，保留其中格式限制。

讀取 [原技術參考](../docx/docx-js.md)；它保留詳細範例，沒有複製到舊入口。搭配正本入口的按工作分支讀取與驗證規則，不因舊教學開頭的「全文讀取」就強迫載入無關章節。
