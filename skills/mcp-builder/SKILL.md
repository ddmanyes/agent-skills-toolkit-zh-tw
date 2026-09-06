---
name: mcp-builder
description: 設計、建立或修改 MCP 伺服器的工具、資源、Schema 與傳輸層；適用 Python FastMCP 或 TypeScript MCP SDK，不因一般 API 整合自動啟用。
---
# MCP 伺服器開發

採用專案既有語言、SDK 版本、傳輸與權限模型；新專案按部署需求選擇。查閱與目標版本相符的官方 MCP／SDK 文件，避免把舊範例當成現行 API。

## 按需要讀取

- 工具邊界、命名、輸入與錯誤設計：[mcp_best_practices.md](reference/mcp_best_practices.md)。
- Python：[python_mcp_server.md](reference/python_mcp_server.md)。
- TypeScript：[node_mcp_server.md](reference/node_mcp_server.md)。
- 使用者需要工具選擇品質評估、或新工具語意難以驗證時：[evaluation.md](reference/evaluation.md)，重用 [evaluation.py](scripts/evaluation.py) 和 [範例](scripts/example_evaluation.xml)。小修正不用先交 XML 評估計畫。

## 工作與完成

先明確目標工作流、資料界限與錯誤情況；需求不清時查資料或問必要問題，不自動擴大成完整 API 端點覆蓋。以 Zod／Pydantic 等定義輸入；名稱可辨識動作，回應包含必要資料與可行的錯誤下一步。

驗證身份、授權及輸入；destructiveHint、readOnlyHint 等註記是描述，不能代替伺服器的權限檢查。憑證從安全設定取得，不写進 Skill、輸出或測試資料。遠端寫入遵守使用者授權。

依改動執行 Schema／啟動檢查及相關工具成功、無效輸入、權限和外部失敗案例，可使用專案測試或官方 Inspector。修復問題並重測；無服務或憑證時用明確標示的模擬資料測可測部分，回報未測真實整合。交付程式、使用方式及實際驗證結果；不把尚未執行的 eval 當成品質提升證據。

以繁體中文回報；使用者指定其他語言時依其要求。
