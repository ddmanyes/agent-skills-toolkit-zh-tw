# Agent Skills Toolkit — 繁體中文優化版 🚀

歡迎使用！本專案目前收錄 40 個 Active Skills（其中 4 個 Radar Skills 為過渡相容副本），可同步到 **Claude／Claude Code、Codex／通用 Agent 與 Antigravity**。

這些 Skills 經繁體中文優化，並針對資訊分析、Agent 工作流、自動化開發與內容整理強化；每個 Skill 的 scripts、references 與其他支援資源也會一起同步。

> [!IMPORTANT]
> `github-stars-radar`、`x-bookmarks-radar`、`threads-bookmarks-radar` 與 `content-radar` 的正式開發與更新來源已移至獨立的 Private 維運專案。本 repository 暫時保留四個相容副本，供既有安裝遷移與回復使用；兩邊不做雙向同步。Private 專案的存取與安裝資訊只提供給已獲授權的使用者。

---

## ⚡️ 快速安裝

建議 clone 完整 repository，再使用同步腳本；不要只複製 `SKILL.md`，否則可能漏掉 Skill 需要的 scripts、references、templates 或其他資源。

macOS／Linux：

```bash
git clone https://github.com/ddmanyes/agent-skills-toolkit-zh-tw.git
cd agent-skills-toolkit-zh-tw
./scripts/sync-local-skills.sh --all
```

Windows PowerShell：

```powershell
git clone https://github.com/ddmanyes/agent-skills-toolkit-zh-tw.git
cd agent-skills-toolkit-zh-tw
.\scripts\sync-local-skills.ps1 -All
```

同步後可以驗證有沒有漏：

```bash
python3 scripts/check-skill-consistency.py --mirror ~/.agents/skills
```

它比對 README 宣稱的 skill 數量與實際樹狀結構，檢查鏡像是否有可用入口，並比對一般技能內容。四個過渡 Radar 副本預設只檢查入口可讀，另列為未比對內容；指向其他來源的 symlink 只檢查有沒有斷。若要唯讀比對過渡副本與本倉庫的內容，可加 `--include-transitional`。多份鏡像用重複的 `--mirror`，或設 `SKILLS_MIRRORS`（以作業系統路徑分隔符分隔）。必要入口缺失或已選內容比對失敗時回傳非零，未比對的項目不會被宣稱為一致。

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

同步採增量覆蓋：只更新已選技能，覆寫前先把原檔存入各環境的 `skills-backups`，並保留其他本機檔案。指定 `--skill NAME`／`-SkillNames NAME` 可縮小範圍。舊技能目錄預設保留；只有明確加 `--archive-legacy`／`-ArchiveLegacy` 才歸檔已選替代技能的舊入口。

四個過渡 Radar 名稱由 [transitional-skills.txt](scripts/transitional-skills.txt) 共用管理。每個同步目標各自判斷：尚無該目錄時安裝本倉庫的相容副本，讓新安裝仍可使用；已有目錄時預設保留並顯示 `SKIP transitional/external`，避免覆蓋另一來源管理的版本。指定名稱但未授權覆寫已安裝的過渡副本時，會在寫入前停止。

只有要明確恢復本倉庫的過渡副本時，才同時指定名稱與覆寫選項，例如只恢復 `content-radar`：

```bash
./scripts/sync-local-skills.sh --agents --skill content-radar --include-transitional
```

```powershell
.\scripts\sync-local-skills.ps1 -Agents -SkillNames content-radar -IncludeTransitional
```

`--include-transitional`／`-IncludeTransitional` 必須搭配明確的技能名稱，不能只對全部技能開啟。上述覆寫仍先備份；未選中的技能及其他來源的排程不會因此變更。

---

## 本次稽核與相容入口

[2026-09-06 修復紀錄](docs/skills-audit-2026-09-06.md) 說明實際證據、保留內容與未測限制。觸發與完成條件按任务需要調整；未宣稱 Astra／Sol／Luna 的速度或模型效果已提升。

[compatibility_skills](compatibility_skills/README.md) 維護 25 個舊命令及 3 個既有本機流程的 overlay，另有逐名比較與來源 hash。這些不是新增 Active Skills；只向既有同名安裝逐檔合併，先備份、檢查相依並保留原環境與使用者資料。常規同步腳本不會自動新增這些相容入口。

## 📂 技能包內容清單

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

---

## 📜 聲明與致謝

本專案為開源社群作品，核心邏輯之版權歸屬原創作者。詳細致謝清單請參閱 [ACKNOWLEDGEMENTS.md](./ACKNOWLEDGEMENTS.md)。
