---
name: mcp-builder
description: 建立高品質 MCP (Model Context Protocol) 伺服器的指南，使 LLM 能透過設計良好的工具與外部服務互動。當你需要整合外部 API 或服務時（支援 Python 的 FastMCP 或 Node/TypeScript 的 MCP SDK），請使用此技能。
---

# MCP 伺服器開發大腦 (MCP Builder)

建立高品質的 MCP 伺服器，使 LLM 能透過設計良好的工具與資源與外部服務互動。

## 1. 設計哲學 (Design Philosophy)
- **工具 vs. 覆蓋率**：優先建立能完成特定「工作流」的工具。如果使用者需求不明確，則追求完整的 API 端點覆蓋。
- **命名規範**：使用 `命名空間_動作` 格式（例：`github_create_issue`）。
- **錯誤引導**：錯誤訊息必須具備「行動建議」，告訴 AI 下一步該怎麼修復。

## 2. 推定技術棧 (Recommended Stack)
- **TypeScript (推薦)**：最成熟的 SDK 與類別支持。
- **Python (FastMCP)**：適合快速原型與數據科學工具。
- **傳輸協議**：本地開發用 `stdio`；遠端部署用 `Streamable HTTP`。

## 3. 實作檢查清單
- [ ] **輸入驗證**：使用 Zod 或 Pydantic 定義明確的 Schema 與範例。
- [ ] **上下文控制**：確保回傳的數據精簡且相關，避免 Token 浪費。
- [ ] **註解標記**：標註 `destructiveHint`（具破壞性操作）或 `readOnlyHint`。

## 4. 執行流程
1. **研究與規劃**：查看 `https://modelcontextprotocol.io` 獲取最新規範。
2. **開發與除錯**：使用 `npx @modelcontextprotocol/inspector <command>` 進行熱重載測試。
3. **評估 (Eval)**：建立 QA 配對以測試 AI 是否能正確選擇工具。

## 輸出要求
- 全程使用「繁體中文」回饋。
- 寫代碼前必須先產出 XML 格式的評估配對 (Evaluation pairs) 給使用者審查。
