---
name: image-to-prompt
description: 用本機 llama-server 視覺模型將使用者提供的圖片轉成描述或 FLUX／manga prompt；當使用者明確要求此本機圖片轉 prompt 流程時使用。
---

# 本機圖片轉 Prompt

`SKILL_DIR` 是此已安裝 Skill 的目錄。重用 [generate_prompt.py](generate_prompt.py)，不依賴固定使用者路徑或不存在的模型切換腳本。

1. 解析圖片路徑、模式和額外要求；相對圖片路徑依使用者的專案目錄解析成絕對路徑。確認檔案可讀且格式為 jpg/jpeg/png/webp/gif。
2. 模式預設 `manga`；`flux` 是英文出圖 prompt，`describe` 是中文描述，`fidelity` 限可見事實，`f2m` 先忠實觀察再轉雙語 manga。保留 ddwoman／awei 等既有 storyboard tokens 及 metadata schema。
3. 使用允許的 Python 環境，以參數陣列執行 `python <SKILL_DIR>/generate_prompt.py <absolute_image_path> <mode> [extra_prompt]`。只將指定圖片送到本機 `http://localhost:8080`，不得自行改用遠端服務。
4. `/health` 回傳成功只代表服務有回應，不能證明 Gemma 版本、vision 或 mmproj 能力。以實際圖片請求結果判斷能否使用；不要把服務名稱、空白答案或文字回應當成視覺能力已確認。
5. 查看輸出與輸入圖片是否相符；`manga`／`f2m` 檢查英文、中文、JSON metadata，明確區分 prompt 風格詞與圖片可見事實。JSON 未解析成功不得稱可直接匯入 storyboard。

腳本已有有限的請求重試與補全；不要在外部無限重跑。服務、模型或格式失敗時保留錯誤／不完整輸出並回報，必要時先讀 [故障與驗收](references/validation.md)。只有已查到實際啟動腳本，且啟動符合使用者授權時才執行；不得假造 switch-model.ps1 路徑或擅自切換使用者模型。

完成時交付實際輸出、使用模式和仍不確定的內容。未連線測試 vision 時明確說明，不宣稱特定模型或描述品質已驗證。
