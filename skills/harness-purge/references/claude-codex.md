# Claude／Codex 原生評測

## 使用與載入

本技能預設在目前客戶端做診斷；不需要 Gemma 或第三方 API。Claude Code 可用 `/harness-purge`，Codex 可用 `$harness-purge`。其他 Claude 介面若不提供本機檔案與終端，僅做文字審查，腳本由有本機能力的客戶端執行。

共享內容只使用標準 `name`、`description` 與相對資源路徑；`agents/openai.yaml` 是 Codex 介面資料，不當成 Claude 權限設定。不要新增 `allowed-tools`、自動執行 hook 或 `context: fork` 來完成比較。

Codex 官方本機使用者位置是 `~/.agents/skills/`，Claude Code 是 `~/.claude/skills/`。先確認目前會話實際列出的技能路徑；既有環境若已從其他路徑載入，優先更新該份，不建立另一個同名技能。看得到磁碟檔案、選單列出技能、實際載入正文與完成任務，是四種不同證據。

來源（2026-11-04 查核）：[OpenAI 技能文件](https://learn.chatgpt.com/docs/build-skills)、[Claude Code 技能文件](https://code.claude.com/docs/zh-CN/skills)。客戶端更新後，先查本機 `--version`／`--help`；文件不保證所有帳號與版本一致。

## 先審查，再決定是否 A/B

收集一個具體失敗樣本、任務預期與指定技能。審查觸發描述、必要資源、步驟完成條件、輸出契約與失敗處理；每項 finding 附檔案位置或回覆證據，區分已確認與待測假設。

修改授權已包含在「審查並改善」時，可修指定技能及必要資源；只有「review」時先交付問題。保存原文與差異，保留可用腳本與既有權限邊界。修正格式、依賴或靜態歧義後先跑對應本機檢查；只有行為效果仍不確定時才安排模型比較。

比較採用同一客戶端與明確模型；Claude 與 Codex 各自建立 run。保留 reasoning、工具權限、輸出契約、背景與檔案版本。每個任務使用獨立乾淨工作階段或隔離背景，baseline 不接觸 candidate 或標準答案。無法控制的設定記 `unknown`，無法隔離既有技能時列為混淆因素。不要將同一長會話先做 baseline、再提示正確答案後做 candidate，當成公平對照。

若用 CLI，先核對本機版本支援的選項。已核對本機 Codex 的 `exec --output-schema` 與 Claude 的非互動輸出選項，不表示本工具會自動啟動它們。啟動另一個代理、額外付費請求或傳送私人內容，沿用本次使用者授權與宿主規則；沒有授權時先完成本機部分。不使用略過權限的旗標。

## 準備與匯入

以下命令相對於安裝的技能目錄。`<...>` 都需換成任務確定的值；使用新輸出目錄。

```text
python scripts/session_eval.py prepare --client codex --model <exact-model> --profiles <profiles.json> --cases <cases.json> --conditions <conditions.json> --output <new-run>
python scripts/session_eval.py compare --run <run> --records <records.json> --output <new-comparison>
```

`--client claude` 為另一套獨立 run。省略 profiles 使用通用範例，不能稱為 QG 技能評測；測 QG 時要另行選取相同範圍的原版與修改版技能內容。省略 cases 使用六個合成案例，測證據、連續性、執行誠實與修稿驗收，不能代表完整小說或程式能力。

`conditions.json` 可含以下字串欄位：`client_version`、`reasoning`、`tools`、`output_contract`、`context_setup`、`workspace_snapshot`。未提供者記為 `unknown`。只記非機密的設定描述、檔案雜湊或版本識別；不填入設定全文、金鑰或環境變數值。

`prepare` 產生固定的 manifest、交替順序的 `prompts/001.txt` 等任務與 `records-template.json`。模型只收到對應 prompt；manifest 包含標準答案，評測端保管，勿送入待測會話。profile 文字在原生客戶端是任務內容，不會取得 API system message 的權威。

將模板另存為 `records.json`，選定的原始最終回覆存成 UTF-8 文字檔。只保存最終任務輸出與必要的已去除憑證證據，不整批複製會話或設定。`output_file` 相對於 records 檔所在目錄，不能越出該目錄。範例單筆紀錄：

```json
{
  "case": "cross-model-evidence",
  "profile": "baseline",
  "repeat": 0,
  "status": "completed",
  "output_file": "outputs/001.txt",
  "observed_model": "unknown",
  "seconds": null,
  "semantic_review": {
    "verdict": "not_reviewed",
    "evidence": ""
  }
}
```

狀態只能是 `completed`、`model_refusal`、`runtime_error`、`not_run`；由操作者依原始證據指定，腳本不以關鍵字推斷拒答。未匯入的任務保持 `not_run`；只有選單或規則檔證據時，模型填 `unknown`。原生 JSON wrapper、串流事件與最終任務輸出要分開：匯入檔是未改寫的最終內容，不是整包事件 JSON；抽取方式寫在報告。

人工 `semantic_review.verdict` 可為 `pass`、`fail` 或 `not_reviewed`。pass／fail 需對已完成回覆提供具體 evidence；匯入器只驗證紀錄結構，不代替人工判讀。語意檢查題目保留在評測端，不先把發現的錯誤答案告訴待測模型。

## 指標與修稿驗收

`summary.json` 將以下項目分開：執行狀態、原始 JSON 語法、確定性欄位／文字檢查、人工語意審核、未測項目。`json_fields` 只檢查指定欄位的遞迴型別與值，不是完整 JSON Schema 驗證。JSON 合法而答案錯誤時，格式可通過、內容檢查應失敗。Markdown 包裹、重複 key 與非標準 JSON 數值不自動修復。

只對雙方都有完成回覆的配對計算觀察差值；拒答、錯誤與漏測另外列出，不從總數中隱藏。`observed_model` 不符或未知、控制條件未知、人工審核未完成都保留警示。模型標籤與耗時是操作者提供的紀錄，不等於已由工具觀測。

修稿另開一次任務，保留原始 A/B。回饋表至少含：

| 缺陷 ID | 原稿證據 | 驗收條件 | 修稿證據 | 結果 |
| --- | --- | --- | --- | --- |
| continuity-01 | 鑰匙紙上／紙下矛盾 | 沒有移動事件就維持同一位置 | 對應段落或檔案位置 | 已修／未修 |

新增問題給新 ID，不因舊問題修好而標全部通過。若測試跨章情節，先從已確認設定建立時間、人物已知資訊與物件狀態表；模型新提出的設定另列建議，不覆蓋已確認 canon。只在這些資訊與任務相關時加入。

修稿率、人工修改段數、耗時與請求數分別統計。編輯直接重寫、程式修正與技能改版分開歸因。六個合成案例或同一作者自評只能支持局部觀察，不能證明文筆提升、跨模型可靠或通用破甲。報告需明確區分：靜態 review、本機腳本驗證、原生客戶端行為測試、實際任務驗收。

## 失敗與恢復

輸入錯誤先停止；不覆寫既有 run／comparison。讀取或寫入中斷可能留下部分本機檔案，保留作為失敗證據，下次用新目錄。比較失敗不重新呼叫模型。技能改版恢復只針對指定檔案，先檢查有無後續使用者修改，不整批回復專案。
