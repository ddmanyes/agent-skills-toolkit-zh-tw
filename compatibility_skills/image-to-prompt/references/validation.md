# 圖片轉 Prompt：故障與验收

- 輸入失敗：回報解析後的絕對路徑與格式，先修正輸入，不呼叫模型。
- 服務無回應：回報 localhost:8080 的連線結果；只依已讀到的服務設定或真實啟動檔處理。health 成功仍需實際圖像请求驗證。
- HTTP 錯誤／缺少 choices／空白內容：回報服務回傳格式或狀態，不斷言是 mmproj 未載入。純文字模型不能替代讀圖。
- manga/f2m 輸出：英文與中文都存在，JSON 是 object，核對 shot、framing、angle、mood、lighting、orientation、has_character、character_count、appearance、clothing、background、style_tags。欄位缺漏或不符使用者 schema 時保留部分結果，不能宣稱已可匯入。
- `fidelity` 把看不清楚列為未知；`manga`/`flux` 可帶生成風格詞，但不能把生成用詞冒充從圖片證實的年代、人物身分或地点。
- Comfy Safe Prompt 與 Negative Prompt 是另列的出圖欄位，不把 JSON 鍵名貼進 positive prompt，避免生成不需要的字樣。
- 本 Skill 的單元測試以 mock 回應檢查輸入、健康檢查界線和錯誤處理；它們不證明本機模型可用或效果提升。
