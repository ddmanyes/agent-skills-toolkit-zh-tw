---
name: source-command-code-review
description: Use when the user explicitly invokes the legacy code-review command; preserve that invocation through its maintained workflow.
---

# 舊命令 code-review

僅在使用者明確要求 `code-review` 或 `$source-command-code-review` 時使用；不自行攔截一般任務。

1. 讀取同一安裝根中的 [正本流程](../sp-code-review/SKILL.md)，以使用者本次需求決定範圍，套用其檢查、完成與失敗處理。
2. `SKILL_DIR` 是本檔所在的已安裝目錄；`CANONICAL_DIR` 是它的 `../sp-code-review`。正本中的 scripts／references 相對於 `CANONICAL_DIR`，不是此舊入口或使用者專案目錄。
3. 執行前確認相依檔案存在；找不到時列出缺失的完整路徑並停止依賴它的步驟。保留專案工作目錄；以腳本的絕對路徑執行，只有腳本明定需要時才暫時切換工作目錄。
4. 沿用使用者已給的授權和適用專案指示；此相容入口不增加工具、檔案、發布或憑證權限。回報正本要求的結果與未完成項目。

## 保留的提交前與回覆流程

使用者要求提交前檢查時，先彙整本次改動與目的，檢查相關測試結果、README/API/註解同步及已有 commit 訊息；不自行提交，也不要求不受影響的全部測試先通過才能審查。
收到審查意見時逐條回應：已授權修復的問題予以修復並重跑受影響檢查；不採納時說明證據。Python／Scanpy 專案沿用既有 uv 環境。
沿用正本兩軸發現格式，另交代複雜或重要改動的背景；完成代表每條意見已有處置或明確未完成原因。
