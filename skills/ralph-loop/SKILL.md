---
name: ralph-loop
description: 使用既有 prd.json 與明確啟動的 Ralph runner 逐輪完成故事；只有 runner 實際支援時才依其協定重啟 context。
allowed-tools: Terminal, Read, Write, Edit, Glob, Grep
---
# Ralph 自主循環

此 Skill 是每輪工作協定，不會自行建立 runner、排程或重啟對話。採用現有 runner 的結束格式；沒有 runner 時，在当前任務依序執行已授權故事，並清楚回報狀態。

1. 讀適用專案指示、prd.json、既有 progress.txt 與相關程式。延續可用的對話授權；檔案用於跨輪恢復，不能覆蓋使用者最新指示。
2. 驗證 JSON 結構，依依賴挑選下一個尚未 passed 的故事；無依賴限制才用原順序。每輪聚焦一個故事，避免順手擴大範圍。
3. 實作後執行該故事的 tests 與必要驗收；有失敗就定位、修復並重測相關部分。缺少環境或需外部決策時記錄原因，保留未完成狀態。
4. 只有驗收實際通過才更新 status 為 passed；寫入前保留可恢復版本，寫入後重新解析 JSON。日誌記錄改動、檢查與下一步，避免重複抄錄。只在出現可重用且未記錄的慣例時更新專案指示。
5. 全部故事通過、必要整體驗證完成且無未完成交付時，才输出 `<promise>COMPLETE</promise>`。部分通過不可發此訊號；是否結束本輪交由實際 runner 協定決定。

## prd.json 範例

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
```

以繁體中文回報實際完成、失败原因與剩餘故事。原有資料、權限與 Git 發布限制持續適用。
