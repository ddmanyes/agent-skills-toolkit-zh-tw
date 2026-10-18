# REA skills 發布驗證（2026-10-18）

新增兩個Active skills（43→45）：

- reverse-engineer-anything：npm rea-agents@6.5.0內附SKILL.md與六個references原樣保留，七檔SHA逐一核對；新增MIT原文及upstream.json。npm gitHead未提供，commit不推定。
- ep-tool-investigation：本機EP外部工具研究流程；改用當前使用者本機目錄，新增可攜安裝依賴指引，保留原始碼優先／REA條件使用／EP部署與執行分層／科學品質及SB讀回界線。

附REA跨機安裝指南、Python3.11+ Codex stdio握手檢查工具及CI測試。MCP runtime需另外安裝／為單一client註冊；不把另一台config、token或本機路徑帶入倉庫。

## 已驗證

- Skill QA：EP PASS，REA無FAIL／三WARN；quick_validate兩者通過。REA警告為trigger字串啟發式、metadata可攜性及未附agents/openai.yaml；為保留上游原版不改寫。
- checker 6個測試PASS：分頁、重複cursor、timeout、JSON-RPC錯誤遮蔽、非JSON、設定失敗不洩漏命令值。
- POSIX同步12個測試PASS；mirror ownership 7個測試PASS（合計25）。
- 指定兩skill在全新隔離home同步，14個檔案逐檔一致。
- 完整隔離home同步45個Active：41個內容比對通過，4個既有transitional副本僅查可讀；README數量45相符。
- 既有本機Codex註冊真實stdio initialize/tools-list PASS：REA6.5.0、207工具、1頁；沒有呼叫目標分析工具，也沒有更動客戶端設定。
- diff whitespace及新增範圍個人路徑檢查通過。

## 保留的首敗／界線

系統Python缺PyYAML，改用任務venv裝PyYAML6.0.3完成QA，未修改全域。首次直接執行consistency checker時預設檢查現行本機mirror，因此報新skill尚未部署及新增license/provenance缺席；改為明確隔離mirror驗證發布內容通過，沒有為了清除訊息覆蓋現行客製skill。

Windows/PowerShell MCP啟動、另一台真實安裝、native providers與跨模型觸發/效果未實跑。checker PASS不等於當前聊天已重新連接，須在目標客戶端新session確認工具。GitHub CI結果以commit對應Actions為準；本文件不預先宣稱遠端CI成功。
