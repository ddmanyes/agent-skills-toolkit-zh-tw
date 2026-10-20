# 技能目錄

[回到專案首頁](../README.md) · [安裝、更新與驗證](installation.md) · [完整來源與致謝](../ACKNOWLEDGEMENTS.md)

Active 是 repository 的分發分類，不代表每個客戶端已安裝或會自動觸發全部技能。共 45 個 Active Skills。

**來源類型說明**

| 類型 | 意義 |
| --- | --- |
| 改編 | 以上游內容為基礎，做繁體中文化、觸發條件與驗證調整，附上游授權 |
| 方法整合 | 吸收上游方法，併入本倉庫既有 skill，不是上游原版 |
| 原樣分發 | 上游內容原樣收錄 |
| 官方改編 | 取自 Anthropic 官方 skills／plugins，做在地化與客戶端適配 |
| 本機新增 | 本工具包自行新增 |

來源欄空白表示致謝文件沒有記載來源。

## 開發流程（SP 系列）

啟發來源：[obra/superpowers](https://github.com/obra/superpowers)。以下各項的個別來源以「來源」欄為準。

| Skill | 功用 | 來源 |
| --- | --- | --- |
| `sp-brainstorming` | 需求或設計有未決取捨時，釐清目標、限制與方案 | Matt 的 grilling 方法啟發升級 |
| `sp-writing-plans` | 將明確需求拆成有依賴與驗收條件的多步驟計畫 | 方法整合 Matt `to-tickets` |
| `sp-executing-plans` | 執行已批准的書面計畫，含驗證、失敗修復與進度紀錄 | 方法整合 Matt `implement-spec` |
| `sp-subagent-dev` | 使用者要求時，依模型能力把獨立工作派給 subagent，由主代理整合驗收 |  |
| `sp-fix-test` | 以四階段除錯法修復失敗測試或定位漏洞 | 方法整合 Matt `diagnosing-bugs` |
| `sp-git-worktrees` | 需要隔離並行功能、修復或審查時建立與管理 worktree |  |
| `sp-learn-codebase` | 為跨模組修改或架構問題探索陌生程式庫 |  |
| `sp-code-review` | 依專案規範（AGENTS.md 等）或規格做 Standards／Spec 雙軸審查，含 Fowler code smell 基線；找缺陷請用客戶端內建審查 | 方法整合 Matt `code-review` |
| `code-simplifier` | 保持行為不變下簡化程式碼，改善可讀性與維護性 | 官方改編（Anthropic）；本機補強可讀性與基準驗證，精確原始 commit 未確認 |
| `tdd` | red–green–refactor 與垂直切片，功能或修復先寫測試 | 改編 Matt Pocock |

## 自主執行與計畫管理

| Skill | 功用 | 來源 |
| --- | --- | --- |
| `autonomous-pilot` | 依已授權的計畫持續執行、驗證，並記錄可恢復檢查點 |  |
| `checkpoint-manager` | 使用者明確要求時，依 execution_trace.md 的 hash 恢復 Git 檢查點 |  |
| `ralph-loop` | 以既有 prd.json 與 Ralph runner 逐輪完成故事 | 參考 [snarktank/ralph](https://github.com/snarktank/ralph) |
| `planning-with-files` | 跨多輪任務以 Markdown 檔案持久保存計畫、發現與進度 | 參考 [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) |
| `project-architect` | 初始化 Python／uv 專案，配置 Ruff、目錄與 Agent 導航文件 |  |

## 設計方法論（源自 mattpocock/skills）

上游固定在 [`49dd158`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336)，改編項目附 `upstream.json` 與 `UPSTREAM-LICENSE.txt`。

| Skill | 功用 | 來源 |
| --- | --- | --- |
| `domain-modeling` | 建立專案領域模型：`GLOSSARY.md` 術語表（相容 `CONTEXT.md`）與 ADR 決策紀錄 | 改編 |
| `improve-architecture` | 掃描程式碼庫找出深化模組的機會，用 deletion test 判斷白佔位的抽象 | 改編 |
| `codebase-design` | 共用模組／介面／接縫詞彙與依賴測試原則 | 改編（本輪新增） |
| `handoff` | 明確要求時記錄可恢復的任務交接，不自動傳訊其他聊天 | 改編（本輪新增） |
| `retro` | 明確要求時回顧開發環境、檢查與規範，提出有證據的改善 | 改編（本輪新增） |
| `ask-matt` | 依目前環境實際可用的 Skill，推薦最小工作路徑與替代方案；僅明確呼叫時運作 | 改編（路由為本機設計） |
| `wait-what` | 上一段解釋沒講清楚時，補足背景與專案詞彙重新說明 | 改編 |
| `teach` | 建立跨多次對話的教學工作區，保存任務、來源、HTML 課程與學習紀錄 | 改編 |
| `research` | 只從高信任一手來源研究，留下具引用、可追溯的 Markdown 結果 | 上游對應內容＋本機適配 |
| `to-questionnaire` | 把只有特定利害關係人能回答的未知事項整理成問卷 | 上游對應內容＋本機適配 |
| `writing-for-agents` | 撰寫給 Agent 讀的文件規範（Skill、AGENTS.md、CLAUDE.md、規格）；取代 `writing-great-skills` | 上游對應內容＋本機適配 |

## Skill 維護與開發工具

| Skill | 功用 | 來源 |
| --- | --- | --- |
| `skill-qa-gate` | 建立、修改或發布 Skill 時，檢查結構、安全邊界、指令歧義與語義保留 |  |
| `skill-architect` | 從網頁或本機來源匯入、翻譯並部署 Agent Skill |  |
| `skill-creator` | 維護本工具包的跨客戶端 Skills、封裝腳本與相容設定 |  |
| `mcp-builder` | 設計、建立或修改 MCP 伺服器的工具、資源、Schema 與傳輸層 | 官方改編（Anthropic） |

## 文件與資料處理

| Skill | 功用 | 來源 |
| --- | --- | --- |
| `docx` | 建立、編輯、分析 Word 檔，含修訂與註釋 | 官方改編（Anthropic） |
| `xlsx` | 分析、建立或精確修改 XLSX／CSV／TSV，含公式與格式 | 官方改編（Anthropic） |
| `pptx` | 讀取、建立、編輯 PowerPoint | 官方改編（Anthropic） |
| `pdf` | 讀取、轉換、合併、分割、OCR、填表與提取文字／表格 | 官方改編（Anthropic） |
| `lecture-converter` | 將課程 PDF、投影片或 Markdown 改寫為完整自學講義 |  |
| `diagram-design` | 將文字、Mermaid 或 draw.io 重繪為可存取的 SVG／單檔 HTML 圖表 | 改編 [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design)（MIT）；新增 Dots／signal-flow 與 Second Brain 整合 |
| `eli5` | 針對單一主題產生一頁、離線、自包含的視覺 HTML；與長期學習的 `teach` 分工 | 改編 claude-plugins-community（原作者 Thariq Shihipar）；本倉庫加入離線資產、安全與來源查核規則 |

## 研究與內容收集

| Skill | 功用 | 來源 |
| --- | --- | --- |
| `pubmed-lcdda-harvest` | 搜尋 PubMed／NCBI，列候選清單交使用者挑選，再經 lcdda-harvest 抓全文歸檔；AI／CS 主題不適用 |  |
| `course-video-archiver` | 下載使用者有權存取且無 DRM 的課程影片，產生逐字稿、SRT、重點，可寫入 Second Brain |  |

### 跨來源內容雷達（過渡相容副本）

以下四個目錄仍可由本 repository 的同步腳本安裝，但不再是後續更新的正式來源。同步這些副本不會安裝新的 Codex Plugin，也不會建立或轉移排程。切換到新版後，同一時間只能保留一台 scheduler owner，避免重複收集與重複寫入。

| Skill | 功用 | 來源 |
| --- | --- | --- |
| `github-stars-radar` | 每日增量整理 GitHub Stars，repository 專用評分與高價值深度分析 |  |
| `x-bookmarks-radar` | 透過已登入瀏覽器增量整理 X 書籤，維護獨立同步狀態與重試契約 |  |
| `threads-bookmarks-radar` | 透過已登入瀏覽器增量整理 Threads saved posts，維護獨立同步狀態與重試契約 |  |
| `content-radar` | 從 Second Brain 唯讀彙整三個來源，產生冪等的每週跨來源雷達 |  |

建議讓三個 collector 分開執行，再由 `content-radar` 統一產生週報；單一來源登入失效時，不會拖垮其他來源。

| 工作 | Skill | 建議排程 | 執行位置／前提 |
| --- | --- | --- | --- |
| GitHub Stars 增量收集 | `github-stars-radar` | 每日 12:00 | 可存取 GitHub 與中央 Second Brain 的電腦 |
| Threads saved posts 增量收集 | `threads-bookmarks-radar` | 每日 12:30 | 保有 Threads 登入狀態的瀏覽器電腦 |
| X 書籤增量收集 | `x-bookmarks-radar` | 每日，沿用該機既有時段 | 保有 X 登入狀態的瀏覽器電腦 |
| 三來源週報 | `content-radar` | 每週一 13:00 | 可讀取中央 Second Brain 的電腦 |

`content-radar` 只彙整已成功寫入 Second Brain 的內容，不會代替每日 collector 重新抓取來源。舊版 GitHub-only 週報可保留作手動相容用途，但不應與跨來源週報重複排程。

## 外部工具與相容性研究

| Skill | 功用 | 來源 |
| --- | --- | --- |
| `reverse-engineer-anything` | REA 上游指引，涵蓋發行檔、JavaScript、原生及執行行為證據；完整原始碼架構研究不啟動 REA | 原樣分發 [morluto/rea](https://github.com/morluto/rea) `rea-agents@6.5.0` |
| `ep-tool-investigation` | 核對 EP 既有能力、外部工具差異、adapter／驗收契約及 SB 紀錄；需要發行檔證據時才轉 REA | 本機新增 |

Skill 同步不會安裝 runtime 或註冊 MCP。請完成 [REA 跨機安裝](rea-installation.md)。

## 視覺與藝術（Disabled by default）

- **設計專家**：UI-UX Pro Max、玻璃擬態、前端設計、自動化測試。來源：[nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)。
- **創意工具**：生成式藝術、Slack GIF 製作。
