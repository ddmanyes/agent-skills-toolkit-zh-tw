# Skills 檢查與修復紀錄 — 2026-09-06

## 範圍與原則

使用者先要求只讀稽核，再批准修復及更新 GitHub。本次以更新前的本機安裝與 repository main 比對，保留有用知識、權限、安全限制、既有腳本與相容名称；沒有直接修改第三方供應商的版本快取。

參考文章：[Rethinking skills and prompts for GPT-6 Astra](https://x.com/pvncher/status/2095991462416490862)。採用精確觸發、按需讀取與可檢查的完成條件，但不把 Astra 的假設套用到所有模型，也不以文件較短作為成功指標。

## 已修復的問題與保留內容

| 問題／實際證據 | 處理與影響 | 保留 |
| --- | --- | --- |
| autonomous-pilot 與 session-snapshot 使用整個工作樹暫存，及虛擬 recovery URI | 限定已授權路徑、檢查 staged diff、區分 commit 與未提交狀態；URI 需實際 handler | 計畫、uv、可恢復檢查點與繁中交接 |
| brainstorm／plans／exploration 對小任務也強迫訪談、計畫或日誌 | 以未解決決策、跨階段相依及恢復需要為觸發；沿用已有授權 | 設計取捨、必要問題、驗收、失敗修復與複雜任務指引 |
| worktree 與初始化缺少完整可執行步驟 | 明列 worktree add 與註冊核對；uv 預檢後真正 add／sync | 路徑、分支、依賴衝突、Ruff、分析目錄與 Agent 導航 |
| review 固定使用三點 diff 且強迫兩個子代理 | 區分版本、分支、工作樹範圍；按需要委派 | Standards／Spec 分軸及 12 條 Fowler smell 基線 |
| TDD 指向不存在的 codebase-design、每個 seam 重複批准、禁止 refactor | 自含測試介面詞彙；沿用已批准介面；支援 red-green-refactor | 反對同義測試、實作耦合與一次大量猜測測試 |
| ralph-loop fence 錯誤及假設自動重啟 context | 修正 JSON fence，明記需真實 runner；全部驗收後才 COMPLETE | 單故事聚焦、進度、原權限與跨輪恢復 |
| DOCX validator 固定辨識 Claude，無該作者時直接通過 | 明確作者參數；無匹配作者仍比對原稿；保護其他作者修訂 | 既有 Document、OOXML schema 與原有作者相容 |
| QA parser 對無效 YAML、特殊字元路徑及程式範例判斷不完整 | 正式 YAML／重複鍵檢查、連結解析、範例排除與實際腳本路徑提示 | 確定性檢查、警告人工判斷與 repository/runtime 區別 |
| 本機 creator 缺可執行 eval viewer；repo 缺現有初始化／封裝工具 | 移除不存在的必經工具，從既有安裝復原有效腳本及參考 | 跨模型評估需求、原封裝能力與實際測試證據 |
| 25 個舊 source-command 入口重複或失聯 | 逐一比較後設相容入口及明確手動政策；相對正本目錄解析腳本 | 舊名稱、不同作者、客戶端、提交前檢查與會話心得用途 |
| Office 入口沒有連到詳細操作、完成與失敗條件不足 | 建立工作類型路由、內容／結構／視覺驗收及未測聲明 | Word 修訂、PDF 表單、XLSX 重算與既有工具 |
| PPTX 大量整份必讀／逐次修改驗證 | 詳細流程拆成五個模式參考，按相關批次驗證 | 配色、排版、OOXML 與「replace.py 遺漏 shape 會清空文字」限制 |
| lecture-converter 重複 Layer／題數矛盾、直接覆寫原稿 | 統一七層與題數預設；先備份或另存；來源與補充分開 | 所有定義、公式、跨語言範例、案例、雷區與教學格式 |
| 十個設計／內容 Skills 過度強迫風格、流程、確認 | 按任務啟用詳細參考；尊重既有品牌／模板；補交付驗證 | 字型、範本、seed、GIF 核心、helper 與可存取性知識 |
| webapp-testing 將 networkidle 當普遍就緒條件 | 改成可觀察頁面／元素狀態，保留現有伺服器 helper | 偵查、主互動驗证、log 與瀏覽器關閉 |
| diagram-design 的 self_check 引用缺少 motion 模板 | 原樣復原上游固定 commit 模板並自檢 | 原控制器、安全白名單、靜態後備及 reduced-motion |
| image-to-prompt 路徑／啟動器不存在，health 不等於 vision | 使用安裝相對路徑；重用腳本並處理無效／部分輸出 | 全部模式、storyboard tokens、metadata 與本機 endpoint |
| NotebookLM 的資料路徑錯誤、Smart Add 與追問規則矛盾 | 文件 overlay；以實際 SKILL_DIR/data 為準，有限追問與來源不足出口 | 既有環境、登入資料與 runtime；未打包個資 |
| runtime 的 manual metadata 與文件內容矛盾 | Codex 用 openai.yaml 的 allow_implicit_invocation；舊客戶端欄位保留 | 明確手動意圖、安全禁令及可讀的共享參考 |
| MCP builder 對普通 API 工作也啟用、每次先審 XML eval | 限 MCP 伺服器工作；按新工具語意需要啟用 eval | Schema、錯誤處理、權限、版本查核與原評估腳本 |
| course-video 局部工作被推向完整封存 | 依下载／字幕／筆記／SB 的已要求成品選分支 | DRM／憑證／大小授權、片長與影音驗收及原取得順序 |
| 同步直接覆寫且可能把正式 Radar 降回過渡副本 | 覆寫前 hash 備份、指定名稱、既有 disabled 更新與過渡來源保護 | 額外本機檔案、復原能力及不同維護正本 |

舊名稱逐項比較與來源 SHA-256 見 [相容層稽核](../compatibility_skills/AUDIT.md)；這些是既有安裝 overlay，並非新增到 Active 清單的 28 份獨立依賴完整套件。

## 驗證方法與限制

實際執行：

- QA regression：14 個案例。
- DOCX tracked-edit regression：12 個案例，包括自訂作者、其他作者保護、損壞 XML／ZIP 及真正 CLI 串接。
- 28 個相容 overlay 在臨時共同安裝根的結構、引用與啟用政策檢查；本機 NotebookLM 的 9 個既有必要檔案存在／語法檢查。
- image-to-prompt：8 個網路隔離案例；沒有傳送真實圖片。
- 已修改 Skill 的 deterministic QA 與 quick validator；修復所有 FAIL。
- creator 初始化與封裝的臨時 fixture，確認 references/scripts 留在產物。
- diagram 靜態／motion 模板自檢及拒絕非原版 script 的負例。
- 同步工具的隔離備份、重跑、範圍、額外檔、路徑／junction 與恢復內容檢查；POSIX 分支另由 GitHub CI 驗證。

已檢視的非阻擋 WARN 主要是：原 license／allowed-tools 等跨客戶端 metadata、可選 UI metadata、較長但有實質判準的參考段落，以及用關鍵詞判斷的中文 description 提示。沒有為了清空警告而刪除授權條款或把一句正常描述改成不自然的觸發口號。精確執行數與 CI 狀態以本次提交的 Actions 結果及本機部署回執為準。

未測：Astra／Sol／Luna 的實際觸發率、完成品質或速度；Word／PowerPoint／PDF 的真實成品渲染；NotebookLM 登入與 DOM；本機 vision 模型；媒體下載、MCP／Second Brain 寫入與排程。這些部分沒有宣稱效果已提升。

供應商維護的 system／bundled／remote 插件入口（例如 Google Docs）留待其維護來源更新；本次未修改其版本快取。私人 Radar 在獨立正本修復並驗證分發，公開過渡內容不接收私人維運資訊。

## 復原與後續維護

修改前保留 repository 快照與已安裝檔案 hash 清單；每次實際覆寫再保留對應原文。同步工具的 skills-backups 與相容層部署回執存於本機，不發布憑證、模型或使用者資料。Git 歷史可還原 repository 內容，安裝备份可還原本機差異。

後續真實模型評估至少涵蓋：一行文字修正、已批准多檔案工作、局部 PPTX 修改、DOCX 不同作者修訂、需要登入／缺工具的失敗、明確手動別名與相近負例。每個支援模型分別記錄成功、誤觸發、遗漏與成本，再決定能否進一步删減規則。

## 本次發布驗收

修復分支的 [GitHub Actions 驗證](https://github.com/ddmanyes/agent-skills-toolkit-zh-tw/actions/runs/34028866310) 已成功：12 個 POSIX 同步、12 個 DOCX、7 個維護來源比對、14 個 QA parser、8 個影像腳本案例，共 53 個測試，另含相容 overlay 與變更 Skill 檢查。

本機 39 個主要 Skill 與 28 個相容入口共 67 個目錄、412 份受管檔案已逐檔 hash 核對，沒有不一致或 QA FAIL；未納入範圍的原有 Skill 檔案未改。從安裝位置重跑 DOCX 12、QA 14、影像 8 個測試全部通過。原始檔案備份與部署回執保留在本機。

仍保留 104 項非阻擋 QA WARN：27 項原有跨客戶端 metadata、31 項可選 UI metadata、18 項 description 關鍵詞提示、28 項較長敘述。這些已人工檢視，不等同實際模型失敗，也不是以刪除有用內容處理的項目。
