---
name: webapp-testing
description: 使用 Playwright 與本地網頁應用程式互動及測試的工具集。支援驗證前端功能、除錯 UI 行為、擷取螢幕截圖及查看瀏覽器日誌。
---

# 網頁應用程式測試 (Web Application Testing)

要測試本地網頁應用程式，請編寫原生的 Python Playwright 腳本。

**可用輔助腳本**：
- `scripts/with_server.py` - 管理伺服器生命週期（支援多個伺服器同時啟動）。

**首要原則**：
執行腳本前**務必先加上 `--help` 參數**查看用法。除非有絕對必要，否則不要閱讀腳本源碼，這些腳本通常很大，會污染你的對話空間。它們應被視為「黑盒工具」直接調用。

## 決策樹：選擇執行方式

使用者任務
→ 是否為靜態 HTML？
  ├─ 是 → 直接讀取 HTML 檔案以識別選擇器 (Selectors)
  │  ├─ 成功 → 使用該選擇器編寫 Playwright 腳本
  │  └─ 失敗/不完整 → 視為動態網頁 (見下方)
  │
  └─ 否 (動態網頁應用) → 伺服器是否已啟動？
     ├─ 否 → 執行：python scripts/with_server.py --help
     │  接著使用輔助工具並編寫簡化的 Playwright 腳本
     │
     └─ 是 → 採用「偵查後行動」策略：
        1. 導航至頁面並等待 `networkidle`。
        2. 截圖或檢查 DOM 結構。
        3. 從渲染後的狀態識別選擇器。
        4. 使用找到的選擇器執行操作。

## 範例：使用 with_server.py

**單一伺服器：**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**多個伺服器 (例如：後端 + 前端)：**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

## 最佳實踐
- **黑盒使用輔助腳本**：使用 `--help` 查看用法，然後直接調用。
- **等待 JS 載入**：對於動態應用，務必使用 `page.wait_for_load_state('networkidle')`。
- **無頭模式 (Headless)**：在自動化環境中，務必以無頭模式啟動 Chromium。