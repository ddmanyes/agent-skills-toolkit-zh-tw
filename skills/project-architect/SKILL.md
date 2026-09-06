---
name: project-architect
description: 初始化使用者要求的 Python／uv 專案，配置 Ruff、必要目錄及 Agent 導航文件。
allowed-tools: Terminal, Read, Write, Edit, Glob, Grep
---
# Project Architect
從需求推定專案是數據分析／生資或一般應用，沿用已指定的 Python 版本與依賴。只有資訊會改變初始化結果且無法推定時才詢問。

1. 確認目標目錄及既有檔案，初始化前保留會被替換的內容；既有專案只補本次要求的缺項。
2. 依指定版本執行 uv init。未指定版本时以環境相容的可用版本為準並記錄，不把 3.12 與 latest 混作同一承諾。
3. 以 uv add --dry-run 檢查所需依賴；有衝突先定位並嘗試符合原需求的解法，必須改變版本承諾或範圍時回報。預檢成功後執行 uv add 寫入已選依賴與鎖檔，並以 uv sync 同步環境；Ruff 依專案慣例列為開發依賴。
4. 配置適合專案的 Ruff 規則與 .gitignore。依實作、測試、文件、設定與持久日誌是否真的存在建立 src、tests、docs、config、logs 對應目錄；分析專案才加入 data/raw、data/processed、notebooks、results。scanpy、anndata、pandas、polars、seaborn、matplotlib 是分析用途候選，不是固定安裝清單。
5. 沿用專案的 Agent 指示文件。新 Codex／通用專案使用 AGENTS.md；Claude 專案使用 CLAUDE.md；兩者共用時維持單一規則來源與必要導引，不機械複製規則。導航內容保留實際 build／test／run 指令、專案編碼慣例與無法由設定看出的 gotchas。
6. 多階段實作才建立或更新 IMPLEMENTATION_PLAN.md 與 execution_trace.md；記錄可重用的初始化選擇、依賴變更與驗證，避免加入普遍的逐步日誌義務。

完成條件：環境與必要依賴可解析、初始化內容可執行、Ruff／最小啟動檢查有結果、未完成條件已說明。繁體中文交付目錄與指令；已授權後續實作時接續，不強制轉進另一 Skill。
