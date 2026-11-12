# 評測操作

此路徑僅用於使用者指定的自有或已授權 API 端點。主要使用 Claude／Codex 原生客戶端時，改讀 [原生工作流程](claude-codex.md)，不因缺少相容 API 就更換模型。

## 建立實驗

使用 Python 3。腳本無第三方依賴；PyYAML 僅用於開發時的技能 lint。

先確認端點與模型屬於使用者或已有使用授權，再執行請求。端點與模型從本次請求或其既有相關設定確認；不要猜一個公網服務代替不可用的目標。既有認證只在記憶體讀取。

1. 複製 `assets/profiles.json` 到本任務的實驗資料目錄，保留 baseline 原文，編寫 candidate。對通用 Agent，候選只改任務說明、範圍、證據要求和輸出格式，不假稱提高指令權威或額外工具權限。
2. 編寫合成案例 JSON。每筆包含唯一 `id`、`prompt` 和 `check`。範例只有五個小案例，測的是格式、基本任務回答與證據誠實，不是完整安全或破甲評測。
3. 在相同端點與模型下執行。預設每個 profile 五筆，共十次請求；輸出上限 384 tokens，單次逾時 45 秒，無重試。呼叫前告知使用者額度，若其測試要求已有相應授權則直接執行。

以下參數使用本次任務已確認的值；路徑相對於技能目錄。新輸出目錄不可已存在。

```text
python scripts/purge_lab.py doctor --workspace <workspace>
python scripts/purge_lab.py evaluate --base-url <authorized-base-url> --model <model-id> --output <new-run-directory>
```

需要 API key 時加 `--api-key-env <variable-name>`；多個自訂認證標頭可用 `--headers-env <variable-name>`，值為 JSON object。不得在命令列直接貼 key，也不將環境變數值寫入輸出。HTTP redirect 一律停止，避免把認證送去另一個端點。只有已確認相容的本地服務才使用 `--disable-thinking` 擴充欄位。

自訂 profiles/cases 透過 `--profiles <json-file>` 和 `--cases <json-file>` 指定。`--repeats` 可設 1–5，總請求上限 60；擴大測試需符合使用者的預算。腳本不會把 doctor 發現的規則檔或私人內容傳給模型。

## 判讀

- `manifest.json` 保存提示詞、合成案例、來源檔雜湊與固定參數，不含 HTTP 認證標頭。
- `results.jsonl` 保存逐筆請求、模型回覆、耗時、完成原因及檢查結果。兩個 profile 的順序按案例交替，減少固定先後順序的偏差；未做統計顯著性推斷。
- `summary.json` 只在記錄完成或遇到可辨識的傳輸失敗時產生。`execution_complete` 只代表計畫中的請求均取得文字回覆；模型答案是否符合條件，另看 `passed` 和 `failed_checks`。
- `exact` 檢查去除首尾空白後的完整文字；`json_fields` 檢查原始文字可解析成 JSON object 且指定欄位的遞迴型別和值符合預期，拒絕重複 key 與非標準數值，但不是完整 JSON Schema 驗證；`contains_all` 只有關鍵字存在檢查，不能代替語意審核。
- HTTP 401、逾時、沒有文字回覆等是傳輸／協定失敗，不分類為模型拒答。首次傳輸失敗即停止剩餘請求，保留部分結果；不自動切換模型或端點。
- 人工閱讀回覆後才能判斷語意誤拒絕。兩個 profile 都通過時，不能宣稱 candidate 改善。增加樣本量、跨模型重跑或改測試案例，必須在報告中分開列出。

## 恢復與移植

腳本只建立新的結果目錄，不寫入宿主設定。清理時先確認那是本次新建的結果目錄，保留使用者要求留存的證據；不需要更動原有 DSH 或 Agent。候選提示詞可由代理在其有權使用的任務指令層採用，或經目標產品的原生使用者設定載入。A/B 成功不會自動更新任何產品。
