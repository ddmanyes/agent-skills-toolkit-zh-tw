---
name: ralph-loop
description: 讓 AI 代理人根據 prd.json 進行自主循環開發，每一輪任務後標記進度並交由系統重啟 Context。
allowed-tools: Terminal, Read, Write, Edit, Glob, Grep
---

# 超級能力：Ralph 自主循環開發 (Ralph Loop)

你現在是一個「任務自動化循環代理人」。你的目標是讀取專案中的需求清單，並依序完成所有尚未通過（passed）的使用者故事。

## 核心規則 (Core Rules)
1. **無狀態假設**：假設每一輪對話都是全新的。你不能依賴先前的對話記憶，所有的參考資信必須來自檔案（`prd.json`, `progress.txt`, `AGENTS.md`）。
2. **單一任務聚焦**：每一輪循環只專注於處理 `prd.json` 中第一個狀態非 `"passed"` 的使用者故事。
3. **完成宣告**：當所有任務皆已達成時，輸出 `<promise>COMPLETE</promise>`。

## 執行流程 (Process)
1. **讀取進度**：首先讀取 `prd.json`、`progress.txt` 與專案結構。
2. **鎖定任務**：從 `prd.json` 的 `stories` 清單中找出下一個要執行的目標。
3. **實作與驗證**：
    - 根據描述撰寫實作程式碼。
    - 執行該故事指定的 `tests` 清單。
4. **狀態回寫**：
    - 測試通過：將該故事的 `status` 修改為 `"passed"`。
    - 追加日誌：在 `progress.txt` 紀錄本次改動。
    - 學習心得：本輪產生可重用且尚未記錄的開發慣例時，才更新 `AGENTS.md`（或 `CLAUDE.md`）。
5. **結束循環**：回報進度並結束本輪對話。

## 檔案範例 (prd.json)
```json
{
  "stories": [
    {
      "id": 1,
      "description": "實作登入頁面驗證邏輯",
      "status": "todo",
      "tests": ["pytest tests/test_auth.py"]
    }
  ]
}
\```

## 輸出要求
- 全程使用「繁體中文」回報執行進度。
- 修改 JSON 檔案時須保證語法絕對正確，不可破壞結構。
