# Antigravity Skills ZHT (繁體中文優化版) 🚀

歡迎使用！本專案目前收錄 39 個 Active Skills，可同步到 **Claude／Claude Code、Codex／通用 Agent 與 Antigravity**。

這些 Skills 經繁體中文優化，並針對資訊分析、Agent 工作流、自動化開發與內容整理強化；每個 Skill 的 scripts、references 與其他支援資源也會一起同步。

---

## ⚡️ 快速安裝

建議 clone 完整 repository，再使用同步腳本；不要只複製 `SKILL.md`，否則可能漏掉 Skill 需要的 scripts、references、templates 或其他資源。

macOS／Linux：

```bash
git clone https://github.com/ddmanyes/antigravity-skills-zht.git
cd antigravity-skills-zht
./scripts/sync-local-skills.sh --all
```

Windows PowerShell：

```powershell
git clone https://github.com/ddmanyes/antigravity-skills-zht.git
cd antigravity-skills-zht
.\scripts\sync-local-skills.ps1 -All
```

`--all`／`-All` 會同步到：

- Claude／Claude Code：`~/.claude/skills`
- Codex／通用 Agent：`~/.agents/skills`
- Antigravity：`~/.gemini/config/skills`

同步完成後，請重啟 Agent 應用程式或開啟新 session，讓 Skill discovery 重新載入。

---

## 🗺️ 新專案怎麼串起來用

不知道從哪個 skill 開始？看 **[新專案工作流.md](./新專案工作流.md)**——一張流程圖 + 對照表，說明開新專案時各階段該呼叫哪個 skill。

---

## 🔄 更新本機技能

macOS／Linux 在已 clone 的倉庫中執行：

```bash
git pull --ff-only
./scripts/sync-local-skills.sh --all
```

Windows PowerShell：

```powershell
git pull --ff-only
.\scripts\sync-local-skills.ps1 -All
```

同步目標：

- Claude／Claude Code：`~/.claude/skills`
- Codex／通用 Agent：`~/.agents/skills`
- Antigravity：`~/.gemini/config/skills`

同步採增量覆蓋：更新本倉庫管理的同名技能，但保留其他本機技能。已淘汰的 `writing-great-skills` 會在新版 `writing-for-agents` 寫入成功後移到各環境的 `skills-archive`，可隨時復原。

---

## 📂 技能包內容清單

### 核心開發 (Active)

- **SP 系列**：腦力激盪（已升級為 grilling 決策樹拷問）、極細計畫、自動執行、子代理調度、測試除錯等。
- **架構工具**：專案建築師 v3.0、循環開發 (Ralph)、檔案計畫管理 (Manus 風格)。
- **代碼品質**：`sp-code-review`（雙軸 Standards/Spec 並行 + Fowler code smell 基線）、代碼簡化專家。
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

### 跨來源內容雷達 (Active)

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

### 數據與檔案 (Active)

- **Office 專家**：Word (XML 級別編輯)、Excel (數據分析)、PPT (專業設計師版)、PDF (高精準提取)。

### 圖表與知識視覺化 (Active)

- **diagram-design**：將文字、Mermaid 或 draw.io 重繪為專業、可存取的 SVG／單檔 HTML；支援架構圖、流程圖、資料流、時間軸與 Dots／signal-flow，並可把產物索引寫回 Second Brain。

### 視覺與藝術 (Disabled by default)

- **設計專家**：UI-UX Pro Max、玻璃擬態、前端設計、自動化測試。
- **創意工具**：生成式藝術、Slack GIF 製作。

---

## 📜 聲明與致謝

本專案為開源社群作品，核心邏輯之版權歸屬原創作者。詳細致謝清單請參閱 [ACKNOWLEDGEMENTS.md](./ACKNOWLEDGEMENTS.md)。
