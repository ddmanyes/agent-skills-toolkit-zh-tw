# 技能目錄

[回到專案首頁](../README.md) · [安裝、更新與驗證](installation.md)

Active 是 repository 的分發分類，不代表每個客戶端已安裝或會自動觸發全部技能。

### 核心開發 (Active)

- **SP 系列**：按未解決決策啟用的設計討論、按複雜度規劃、自動執行、子代理調度、測試除錯等。
- **架構工具**：專案建築師 v3.0、循環開發 (Ralph)、檔案計畫管理 (Manus 風格)。
- **代碼品質**：`sp-code-review`（Standards/Spec 雙軸 + Fowler code smell 基線）、代碼簡化專家。
- **Skill QA Gate**：建立、修改或發布 Skill 時，檢查結構、安全邊界、指令歧義與語義保留；一般 Skill 執行不會觸發。

### 設計方法論 (Active，源自 mattpocock/skills)

- **domain-modeling**：建立與磨利專案的領域模型——`CONTEXT.md` 術語表 + ADR 決策紀錄（三條件才寫）。
- **improve-architecture（去蕪存菁）**：掃描程式碼庫找出深化模組的機會，用 deletion test 判斷哪些抽象在白佔位。
- **writing-for-agents**：新版 Agent 文件寫作規範，取代 `writing-great-skills`；涵蓋 Skill、`AGENTS.md`、`CLAUDE.md`、規格與其他 Agent 會讀取的文件。
- **wait-what**：當上一段解釋沒有講清楚時，以補足背景、白話與專案詞彙重新說明。
- **research**：只從高信任的一手來源研究，留下具引用、可追溯的 Markdown 結果。
- **teach**：建立跨多次對話的教學工作區，保存任務、來源、HTML 課程與學習紀錄。
- **tdd**：以 red–green–refactor 與垂直切片推進功能或修復。
- **to-questionnaire**：把只有特定利害關係人能回答的未知事項整理成可交付問卷。
- **ask-matt**：依目前環境實際可用的 Skill，推薦最小工作路徑與替代方案。

### 跨來源內容雷達（過渡相容副本）

以下四個目錄仍可由本 repository 的同步腳本安裝，但不再是後續更新的正式來源。同步這些副本不會安裝新的 Codex Plugin，也不會建立或轉移排程。切換到新版後，同一時間只能保留一台 scheduler owner，避免重複收集與重複寫入。

- **github-stars-radar**：每日增量整理 GitHub Stars、repository 專用評分與高價值深度分析。
- **x-bookmarks-radar**：透過已登入瀏覽器增量整理 X 書籤，維護獨立同步狀態與重試契約。
- **threads-bookmarks-radar**：透過已登入瀏覽器增量整理 Threads saved posts，維護獨立同步狀態與重試契約。
- **content-radar**：從 Second Brain 唯讀彙整三個來源，產生冪等的每週跨來源雷達。

建議讓三個 collector 分開執行，再由 `content-radar` 統一產生週報；單一來源登入失效時，不會拖垮其他來源。

| 工作 | Skill | 建議排程 | 執行位置／前提 |
| --- | --- | --- | --- |
| GitHub Stars 增量收集 | `github-stars-radar` | 每日 12:00 | 可存取 GitHub 與中央 Second Brain 的電腦 |
| Threads saved posts 增量收集 | `threads-bookmarks-radar` | 每日 12:30 | 保有 Threads 登入狀態的瀏覽器電腦 |
| X 書籤增量收集 | `x-bookmarks-radar` | 每日，沿用該機既有時段 | 保有 X 登入狀態的瀏覽器電腦 |
| 三來源週報 | `content-radar` | 每週一 13:00 | 可讀取中央 Second Brain 的電腦 |

`content-radar` 只彙整已成功寫入 Second Brain 的內容，不會代替每日 collector 重新抓取來源。舊版 GitHub-only 週報可保留作手動相容用途，但不應與跨來源週報重複排程。

### 快速視覺解說 (Active)

- **eli5**：針對單一主題產生一頁、離線、自包含的視覺 HTML；與長期學習用途的 `teach` 分工。

### 影音課程封存 (Active)

- **course-video-archiver**：下載使用者有權存取且無 DRM 的課程影片，驗證影音、產生逐字稿／SRT／JSON、用投影片校正時間軸重點，並可選擇寫入 Second Brain。

### 生醫文獻收錄 (Active)

- **pubmed-lcdda-harvest**：用關鍵字搜尋 PubMed／NCBI 生醫文獻，列候選清單交由使用者挑選，再透過 lcdda-harvest 抓全文並依歸檔規則存進研究資料庫。刻意保留「人工挑選」這道關卡，避免關鍵字雜訊灌爆資料庫；AI／CS 類主題不適用，應改走 alphaXiv 流程。

### 數據與檔案 (Active)

- **Office 專家**：Word (XML 級別編輯)、Excel (數據分析)、PPT (專業設計師版)、PDF (高精準提取)。

### 圖表與知識視覺化 (Active)

- **diagram-design**：將文字、Mermaid 或 draw.io 重繪為專業、可存取的 SVG／單檔 HTML；支援架構圖、流程圖、資料流、時間軸與 Dots／signal-flow，並可把產物索引寫回 Second Brain。

### 視覺與藝術 (Disabled by default)

- **設計專家**：UI-UX Pro Max、玻璃擬態、前端設計、自動化測試。
- **創意工具**：生成式藝術、Slack GIF 製作。
