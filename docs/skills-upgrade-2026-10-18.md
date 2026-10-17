# 2026-10-18 Skills 升級與上游對照

上游：[mattpocock/skills](https://github.com/mattpocock/skills)，固定 commit `49dd158d1076134a641b33efb035946536778336`。

本輪更新 11 個、新增 3 個，Active 總數為 43。沒有整套安裝上游插件。能力對應不等同歷史來源證明。

## 完整對照

| 上游 | 分類 | 本機對應 | 本輪處置 | 原因 |
| --- | --- | --- | --- | --- |
| ask-matt | engineering | ask-matt | 更新 | 路由保留本機已安裝技能，補上設計／交接／回顧 |
| code-review | engineering | sp-code-review | 整合更新 | 凍結比較基準，保留雙軸與工作樹審查能力 |
| codebase-design | engineering | codebase-design | 新增 | 集中模組設計詞彙；原先分散在架構與 TDD 參考 |
| diagnosing-bugs | engineering | sp-fix-test | 整合更新 | 補精確症狀、最小重現、可反證假設、效能基準與清理 |
| domain-modeling | engineering | domain-modeling | 更新 | 新增 GLOSSARY 命名，保留舊 CONTEXT 權威位置 |
| grill-with-docs | engineering | sp-brainstorming + domain-modeling | 已有組合 | 不重複安裝訪談入口 |
| implement | engineering | sp-executing-plans + tdd | 整合更新 | 驗證／整合既有執行流程，不強制 commit |
| implement-spec | engineering | sp-executing-plans + sp-subagent-dev | 部分覆蓋 | 補依賴 frontier 與整合驗證；未導入自動 PR／關 issue／worktree 編排 |
| improve-codebase-architecture | engineering | improve-architecture | 更新 | 保留舊名稱，加入共用設計參考、候選 HTML、風險與交接 |
| pr | engineering | 既有開發者 PR 寫作規則 | 未裝專用技能 | 已有描述與驗證要求；無必要新增相同入口 |
| prototype | engineering | visualize／sites／sp-brainstorming | 部分覆蓋、延後 | 現有工具能做原型；專用邏輯／UI 分支與原型歸檔流程未導入 |
| research | engineering | research | 保留 | SKILL.md 與上游相同；僅 UI metadata 差異 |
| retro | engineering | retro | 新增 | 依工作紀錄改善導覽、檢查與規範，先建議後依授權修改 |
| setup-matt-pocock-skills | engineering | project-architect（僅部分） | 缺少、延後 | 沒有完整 tracker／triage 設定流程；本輪不引入 tracker 整套依賴 |
| tdd | engineering | tdd | 更新 | 詞彙表相容及共用介面參考；保留 red-green-refactor 與既有授權 |
| to-spec | engineering | sp-brainstorming + sp-writing-plans | 部分覆蓋 | 規格可產出；未引入自動發布 issue |
| to-tickets | engineering | sp-writing-plans | 整合更新 | 垂直切片、blocking edges、expand-migrate-contract；未自動建立遠端 tickets |
| triage | engineering | 無專用對應 | 缺少、延後 | issue／外部 PR 狀態機屬另一項遠端流程，未安裝 |
| wayfinder | engineering | planning-with-files + sp-writing-plans | 部分覆蓋、延後 | 有跨輪計畫，沒有完整 decision-ticket map／claim／tracker 工作流 |
| wizard | engineering | 無專用對應 | 缺少、延後 | 互動式 bash 設定／憑證精靈需獨立腳本審查，未安裝 |
| chief-of-staff | in-progress | 未納入正式技能升級 | 實驗／特定用途、延後 | 上游 in-progress 區，不因整批升級啟用 |
| claude-handoff | in-progress | 未納入正式技能升級 | 實驗／特定用途、延後 | 上游 in-progress 區，不因整批升級啟用 |
| loop-me | in-progress | 未納入正式技能升級 | 實驗／特定用途、延後 | 上游 in-progress 區，不因整批升級啟用 |
| setup-ts-deep-modules | in-progress | 未納入正式技能升級 | 實驗／特定用途、延後 | 上游 in-progress 區，不因整批升級啟用 |
| writing-beats | in-progress | 未納入正式技能升級 | 實驗／特定用途、延後 | 上游 in-progress 區，不因整批升級啟用 |
| writing-fragments | in-progress | 未納入正式技能升級 | 實驗／特定用途、延後 | 上游 in-progress 區，不因整批升級啟用 |
| writing-shape | in-progress | 未納入正式技能升級 | 實驗／特定用途、延後 | 上游 in-progress 區，不因整批升級啟用 |
| git-guardrails-claude-code | misc | 未納入正式技能升級 | 實驗／特定用途、延後 | 上游 misc 區，不因整批升級啟用 |
| migrate-to-shoehorn | misc | 未納入正式技能升級 | 實驗／特定用途、延後 | 上游 misc 區，不因整批升級啟用 |
| scaffold-exercises | misc | 未納入正式技能升級 | 實驗／特定用途、延後 | 上游 misc 區，不因整批升級啟用 |
| setup-pre-commit | misc | 未納入正式技能升級 | 實驗／特定用途、延後 | 上游 misc 區，不因整批升級啟用 |
| grill-me | productivity | sp-brainstorming | 已有相近能力 | 保留只問重要未決問題的本機策略 |
| grilling | productivity | sp-brainstorming | 已有相近能力 | 不引入無限制訪談或重複批准 |
| handoff | productivity | handoff | 新增 | 任務交接與可恢復狀態；不自動傳訊其他聊天 |
| teach | productivity | teach | 更新 | 補工作區相對路徑與正確答案位置變化 |
| to-questionnaire | productivity | to-questionnaire | 保留 | 差異在描述／UI，本機觸發更明確 |
| wait-what | productivity | wait-what | 更新 | 新舊 glossary 相容，保留原觸發與顯式政策 |
| writing-for-agents | productivity | writing-for-agents | 保留 | 本機已有 Codex metadata 與安全界線適配；不採用未驗證的刪除否定指令主張 |

## 保留的本機差異

- 沿用已批准的測試接縫；保留 red-green-refactor。
- 舊 CONTEXT.md 不強制遷移，新專案預設 GLOSSARY.md。
- 架構 HTML 使用內嵌 CSS/SVG；不載入 CDN。
- 舊測試有獨特覆蓋就保留；不因模組深化直接刪除。
- Commit、push、issue 發布、正式資料變更依使用者授權。
- 每個客戶端保留其觸發 metadata，不把不同 runtime 當成相同。

## 驗證界線

變更技能需通過 skill-qa-gate 結構檢查。quick_validate 對 Claude 的 disable-model-invocation／argument-hint 欄位會回傳非零；依本倉庫 QA 規則列相容性 WARN，不刪除其語意。
本輪有 8 個主代理靜態情境檢查；未做跨模型任務實跑，不宣稱可靠性、準確率或效能提升。客戶端檔案一致不等於已驗證新 session 的載入。

## 更新與回復

依 [安裝指南](installation.md#跨電腦更新與共用目錄) 執行。同步先備份原檔，保留其他 skills 與過渡 Radar。回復時先比較後續修改，再依備份路徑還原；不要用全目錄 reset 或刪除。

## 發布前實際驗證（macOS）

- 14 個變更 skills：skill-qa-gate 無 FAIL；WARN 為中文 trigger 啟發式、跨客戶端 metadata、既有英文長句。
- POSIX sync 12、mirror consistency 7、validator 14、image-to-prompt 8、DOCX redlining 12：共 53 個測試通過。
- 28 個 compatibility overlays 驗證通過；外部 NotebookLM runtime 未測。
- Windows PowerShell 未在本機執行；未修改 PowerShell 同步器。
- 新 session discovery 與跨模型任務效果未實跑，不等同檔案同步驗證。
