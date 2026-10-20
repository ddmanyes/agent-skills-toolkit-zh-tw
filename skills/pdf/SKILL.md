---
name: pdf
description: 當使用者要讀取、轉換、合併、分割、OCR 或填寫本機 PDF，或要從 PDF 提取文字與表格時使用；支援表單填寫、頁面渲染驗證。要把 PDF 歸檔進 Second Brain 或 lcdda vault 時，改用 lcdda 的 save_article。
---
# PDF 處理

先界定頁碼、資料與輸出格式，再判斷文字層、掃描件或混合內容。只讀所需範圍；OCR 結果需對照頁面，特別留意數字、表格與符號。

## 開工前檢查環境

在本 skill 目錄執行 `python3 scripts/check_env.py`，它會列出可用的命令列工具與 Python 套件。缺少的 Python 套件不要用系統 `pip` 安裝，改用 `uv run --with <套件> python3 <script>` 臨時帶入，例如：

```bash
uv run --with pypdf --with pdfplumber --with pdf2image --with pillow python3 scripts/check_fillable_fields.py form.pdf
```

缺少命令列工具（`qpdf`、`ocrmypdf`）時，改用下表的備援，或請使用者以 `brew install qpdf ocrmypdf` 安裝。

## 工具選擇

| 任務 | 首選 | 備援 |
|---|---|---|
| 純文字提取 | `pdftotext -layout` | pdfplumber、pypdfium2 |
| 表格提取 | pdfplumber `extract_tables` | `pdftotext -layout` 後人工整理 |
| 文字加座標 | pdfplumber `chars` | `pdftotext -bbox-layout`（輸出 XML） |
| 合併、分割、抽頁 | qpdf | pypdf `PdfWriter` |
| 轉成圖片檢查頁面 | `pdftoppm -png -r 150` | `scripts/convert_pdf_to_images.py` |
| 抽取內嵌圖片 | `pdfimages -all` | pypdfium2 渲染頁面後裁切 |
| 掃描件 OCR | `ocrmypdf`（輸出可搜尋 PDF） | `pdftoppm` 加 `tesseract` |
| 填表 | `scripts/` 內的填表腳本，見 [forms.md](forms.md) | 無；不要自行改座標 |
| 修復損壞檔案 | `qpdf --check`、`qpdf --replace-input` | 以 pdftoppm 重新渲染再重組 |
| 從零產生 PDF | reportlab | pdf-lib（JavaScript，見 [reference-js.md](reference-js.md)） |

## 讀哪份文件

- Python 與命令列範例、疑難排解讀 [reference.md](reference.md)。
- JavaScript（pdf-lib、pdfjs-dist）範例讀 [reference-js.md](reference-js.md)；只有任務明確要用 Node 或瀏覽器時才讀。
- 填表與欄位／座標驗證讀 [forms.md](forms.md)，重用其中腳本；不要把視覺註記當成真實表單欄位。

## 品質規則

- 表格提取核對標題、行列、單位、合併儲存格及抽樣數值；必要時提供 Markdown 預覽，避免把整個大型表格塞入回覆。
- 編輯、合併、分割或填表時保留原檔／可恢復副本，確認頁數、順序、文字與欄位值。修改可能影響數位簽章；不宣稱未具備工具驗證的簽章能力。
- 產生或修改 PDF 後渲染並檢查受影響頁面；文字提取則核對相關來源區域。欄位溢位、裁切、OCR 疑誤要修正或明確標記。
- 完成時提供實際產物、檢查結果及未能驗證的位置；保存到 findings.md 或外部系統只在任務需要時進行。

## 歸檔到 vault

本 skill 只處理檔案本身，不負責儲存到知識庫。使用者要把 PDF 存進 Second Brain 或 lcdda vault 時：

- 單篇本機 PDF 或網頁：呼叫 lcdda 的 `save_article`（學術論文用 `dest_folder="20-areas/research"`，檔名用 `YYYY_Author_ShortTitle`）。
- 依主題從 PubMed 收錄文獻：改用 `pubmed-lcdda-harvest` skill。
- 歸檔前若需要先合併、分割或 OCR，先在本 skill 完成，再把產物路徑交給 `save_article`。

以繁體中文回報；使用者指定其他語言時依其要求。
