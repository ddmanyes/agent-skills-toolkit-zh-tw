# 相容入口比較與驗證

來源是本次更新前既有的本機 Skills；`manifest.json` 記錄各來源 SKILL.md 的 SHA-256，可與更新前備份核對。比較先移除遷移外層標題及 BOM，再檢查正文與原正本；不以名稱相似當作用途相同的證據。

| 相容名稱 | 判定與來源證據 | 修正版路由／保留用途 |
| --- | --- | --- |
| `source-command-autonomous-pilot` | 同一正文：移除外層遷移標題及 BOM 後，正文與已安裝正本完全相同。 | `autonomous-pilot` |
| `source-command-checkpoint-manager` | 同一正文：移除外層遷移標題及 BOM 後，正文與已安裝正本完全相同。 | `checkpoint-manager` |
| `source-command-code-review` | 保留不同工作分支：舊命令是提交前自檢和回應審查意見，正本是 Standards/Spec findings；保留舊工作分支而非宣稱完全同用途。 | `sp-code-review` |
| `source-command-code-simplifier` | 同一正文：移除外層遷移標題及 BOM 後，正文與已安裝正本完全相同。 | `code-simplifier` |
| `source-command-docx-docx-js` | 同一技術參考：原正文完整複製 docx/docx-js.md；改成有條件讀取同一參考與正本驗收。 | `docx` |
| `source-command-docx-ooxml` | 修訂作者適配：技術參考差異為 Claude→Codex 修訂作者與說明；保留明確作者參數，重用已修正驗證器。 | `docx` |
| `source-command-docx-skill` | 同一正文：移除外層遷移標題及 BOM 後，正文與已安裝正本完全相同。 | `docx` |
| `source-command-pdf-forms` | 同一技術參考：原正文完整複製 pdf/forms.md；改成有條件讀取同一參考與正本驗收。 | `pdf` |
| `source-command-pdf-skill` | 同一正文：移除外層遷移標題及 BOM 後，正文與已安裝正本完全相同。 | `pdf` |
| `source-command-planning-with-files` | 同一正文：移除外層遷移標題及 BOM 後，正文與已安裝正本完全相同。 | `planning-with-files` |
| `source-command-pptx-ooxml` | 同一技術參考：原正文完整複製 pptx/ooxml.md；改成有條件讀取同一參考與正本驗收。 | `pptx` |
| `source-command-pptx-skill` | 稱呼適配：已安裝版本的實質差異只有 Claude/Codex 稱呼；共用能力與流程。 | `pptx` |
| `source-command-project-architect` | 客戶端適配：相同初始化流程，舊命令指定 AGENTS.md；保留 Codex 新專案預設，既有客戶端不強制搬移。 | `project-architect` |
| `source-command-ralph-loop` | 同用途流程演進：舊命令將 AGENTS.md 重複列兩次且保留失效 fence；工作目的同為 prd.json 逐輪執行，導向已修正正本。 | `ralph-loop` |
| `source-command-revise-claude-md` | 保留獨立用途：revise-claude-md 從本次會話萃取心得寫回 AGENTS.md；不同於整庫指示稽核，不強行合併。 | `獨立會話心得寫回流程` |
| `source-command-skill-architect` | 同一正文：移除外層遷移標題及 BOM 後，正文與已安裝正本完全相同。 | `skill-architect` |
| `source-command-skill-creator` | 稱呼適配：已安裝版本的實質差異只有 Claude/Codex 稱呼；共用能力與流程。 | `skill-creator` |
| `source-command-sp-brainstorming` | 同用途流程演進：舊命令是較早設計訪談版，正本增加事實自行查證與邊界情境；同一設計釐清用途，保留按需求選擇 1–2 個方案而不固定訪談輪數。 | `sp-brainstorming` |
| `source-command-sp-executing-plans` | 同一正文：移除外層遷移標題及 BOM 後，正文與已安裝正本完全相同。 | `sp-executing-plans` |
| `source-command-sp-fix-test` | 同一正文：移除外層遷移標題及 BOM 後，正文與已安裝正本完全相同。 | `sp-fix-test` |
| `source-command-sp-git-worktrees` | 同一正文：移除外層遷移標題及 BOM 後，正文與已安裝正本完全相同。 | `sp-git-worktrees` |
| `source-command-sp-learn-codebase` | 專案指示適配：舊命令把 CLAUDE.md 改成 AGENTS.md；保留依目前專案實際指示選擇的規則。 | `sp-learn-codebase` |
| `source-command-sp-subagent-dev` | 同一正文：移除外層遷移標題及 BOM 後，正文與已安裝正本完全相同。 | `sp-subagent-dev` |
| `source-command-sp-writing-plans` | 專案指示適配：舊命令把 CLAUDE.md 改成 AGENTS.md；保留依目前專案實際指示選擇的規則。 | `sp-writing-plans` |
| `source-command-xlsx` | 同一正文：移除外層遷移標題及 BOM 後，正文與已安裝正本完全相同。 | `xlsx` |
| `image-to-prompt` | 原入口指向不存在的 .Codex 路徑與 switch-model.ps1；原 generate_prompt.py 只以 /health 判斷 vision，且包含入口未列出的 fidelity/f2m 模式。 | 重用 generate_prompt.py，補輸入、健康檢查界線、錯誤與部分輸出判斷；保留所有模式、tokens、翻譯與Comfy欄位。 |
| `notebooklm` | 原入口的 Smart Add 與先詢問 metadata 互相矛盾；原 config.py:9–15 實際使用 SKILL_DIR/data，入口寫成固定 .Codex 路徑；追問沒有次數／無新證據的出口。 | 文件 overlay；保留現有 runtime，明記相依與資料位置；一次內容探索、最多兩個來源追問與有界失敗處理。 |
| `session-snapshot` | 原入口第 30 行使用 git add .，先 commit 才寫快照，未區分 HEAD 與未提交內容，也缺 commit 失敗狀態。 | 獨立快照流程；保留繁體中文交接、進度／中斷資訊，新增範圍化暫存、復原基線與保存後讀回。 |

## 已執行檢查

- 28 個 overlays 在臨時共同安裝根完成 deterministic QA：PASS，0 FAIL、0 WARN。所有 `../canonical` 及其明確技術參考都存在。
- 25 個舊命令的 `agents/openai.yaml` 皆設定 `policy.allow_implicit_invocation: false`；3 個原 workflow 保持可依精確需求啟用。
- image-to-prompt：8 個 regression tests 通過，以 tempfile 與 mock 網路／模型邊界驗證，沒有傳送真實圖片。
- NotebookLM：唯讀確認9個必要既有檔案存在及其中 Python 語法；沒有執行 wrapper、登入、查詢、cleanup 或讀取個人資料。
- 所有 overlay Python 語法及 manifest 目錄／啟用政策一致性已檢查；套件內未加入 data、.venv、browser_state、模型或憑證。

## 仍需實際環境驗證

本機模型身分、vision/投影器支援、NotebookLM 登入與目前 DOM、Codex 重新載入後的手動觸發，以及 Astra／Sol／Luna 的實際流程效果尚未測試。沒有宣稱速度或模型效果改善。相容層必須與相依正本一起安裝；本 repo 的 overlays 原始位置不是直接執行環境。
