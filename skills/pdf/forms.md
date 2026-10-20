# PDF 填表流程

**重要：必須依序完成以下步驟，不可跳過去直接寫程式。**

所有 `python3 scripts/...` 指令都從本檔所在目錄（`skills/pdf`）執行。缺少 `pypdf`、`pdf2image`、`pillow` 時，用 `uv run --with pypdf --with pdf2image --with pillow python3 scripts/<script>.py ...` 執行；`pdf2image` 另需系統安裝 poppler。環境檢查見 `python3 scripts/check_env.py`。

填表前先確認 PDF 是否有可填欄位：

`python3 scripts/check_fillable_fields.py <file.pdf>`

依結果進入「可填欄位」或「不可填欄位」流程。

# 可填欄位

PDF 有可填表單欄位時：

- 執行 `python3 scripts/extract_form_field_info.py <input.pdf> <field_info.json>`，會產生欄位清單 JSON，格式如下：
```
[
  {
    "field_id": (欄位唯一 ID),
    "page": (頁碼，從 1 起算),
    "rect": ([left, bottom, right, top] PDF 座標的邊界框，y=0 在頁面底部),
    "type": ("text"、"checkbox"、"radio_group" 或 "choice"),
  },
  // 核取方塊有 "checked_value" 與 "unchecked_value"：
  {
    "field_id": (欄位唯一 ID),
    "page": (頁碼，從 1 起算),
    "type": "checkbox",
    "checked_value": (設為此值即勾選),
    "unchecked_value": (設為此值即取消勾選),
  },
  // 選項按鈕群組有 "radio_options" 清單：
  {
    "field_id": (欄位唯一 ID),
    "page": (頁碼，從 1 起算),
    "type": "radio_group",
    "radio_options": [
      {
        "value": (設為此值即選取該選項),
        "rect": (該選項按鈕的邊界框)
      },
      // 其他選項
    ]
  },
  // 選擇欄位有 "choice_options" 清單：
  {
    "field_id": (欄位唯一 ID),
    "page": (頁碼，從 1 起算),
    "type": "choice",
    "choice_options": [
      {
        "value": (設為此值即選取該選項),
        "text": (選項顯示文字)
      },
      // 其他選項
    ],
  }
]
```
- 將 PDF 轉成逐頁 PNG：
  `python3 scripts/convert_pdf_to_images.py <file.pdf> <output_directory>`
  接著檢視圖片，判斷每個欄位的用途（要把邊界框的 PDF 座標換算成圖片座標）。
- 建立 `field_values.json`，內容是要填入各欄位的值：
```
[
  {
    "field_id": "last_name", // 必須與 extract_form_field_info.py 輸出的 field_id 相同
    "description": "使用者的姓氏",
    "page": 1, // 必須與 field_info.json 的 "page" 相同
    "value": "Simpson"
  },
  {
    "field_id": "Checkbox12",
    "description": "年滿 18 歲時勾選的核取方塊",
    "page": 1,
    "value": "/On" // 核取方塊用它的 checked_value；選項按鈕群組用 radio_options 其中一個 value
  },
  // 更多欄位
]
```
- 執行 `fill_fillable_fields.py` 產生填好的 PDF：
  `python3 scripts/fill_fillable_fields.py <input pdf> <field_values.json> <output pdf>`
  腳本會驗證你給的 field_id 與值；若印出錯誤訊息，修正對應欄位後重跑。

# 不可填欄位

PDF 沒有可填欄位時，必須以視覺判斷該填的位置，再建立文字註記。以下步驟要完整照做，才能確保填得準確：

- 將 PDF 轉成 PNG 圖片，判斷欄位邊界框。
- 建立含欄位資訊的 JSON 檔，並產生標示邊界框的驗證圖片。
- 驗證邊界框。
- 用邊界框填表。

## 步驟 1：視覺分析（必做）

- 將 PDF 轉成 PNG 圖片：
  `python3 scripts/convert_pdf_to_images.py <file.pdf> <output_directory>`
  腳本會為每一頁產生一張 PNG。
- 逐張檢視圖片，找出所有需要填寫的欄位。對每個文字欄位，分別判斷「欄位標籤」與「填寫區域」的邊界框。標籤框與填寫框**不可相交**；填寫框只含實際要填字的區域，通常緊鄰標籤的右側、上方或下方。填寫框必須夠高夠寬，容得下要填的文字。

常見的欄位結構：

*標籤在框內*
```
┌────────────────────────┐
│ Name:                  │
└────────────────────────┘
```
填寫區在 "Name" 標籤右側，一直延伸到框的邊緣。

*標籤在底線前*
```
Email: _______________________
```
填寫區在底線上方，涵蓋整條底線的寬度。

*標籤在底線下*
```
_________________________
Name
```
填寫區在底線上方，涵蓋整條底線的寬度。簽名與日期欄位常見這種結構。

*標籤在底線上*
```
Please enter any special requests:
________________________________________________
```
填寫區從標籤下緣延伸到底線，涵蓋整條底線的寬度。

*核取方塊*
```
Are you a US citizen? Yes □  No □
```
核取方塊的處理：
- 找小方塊（□），那才是實際要鎖定的核取方塊，可能在標籤的左邊或右邊。
- 區分標籤文字（"Yes"、"No"）與可點選的方塊。
- 填寫框只涵蓋小方塊，不含文字標籤。

## 步驟 2：建立 fields.json 與驗證圖片（必做）

- 建立名為 `fields.json` 的檔案，記錄欄位資訊與邊界框，格式如下：
```
{
  "pages": [
    {
      "page_number": 1,
      "image_width": (第一頁圖片寬度，像素),
      "image_height": (第一頁圖片高度，像素),
    },
    {
      "page_number": 2,
      "image_width": (第二頁圖片寬度，像素),
      "image_height": (第二頁圖片高度，像素),
    }
    // 其他頁
  ],
  "form_fields": [
    // 文字欄位範例。
    {
      "page_number": 1,
      "description": "此處填入使用者的姓氏",
      // 邊界框格式為 [left, top, right, bottom]。標籤框與填寫框不可重疊。
      "field_label": "Last name",
      "label_bounding_box": [30, 125, 95, 142],
      "entry_bounding_box": [100, 125, 280, 142],
      "entry_text": {
        "text": "Johnson", // 這段文字會以註記方式加在 entry_bounding_box 的位置
        "font_size": 14, // 選填，預設 14
        "font_color": "000000", // 選填，RRGGBB 格式，預設 000000（黑色）
      }
    },
    // 核取方塊範例。填寫框要鎖定方塊本身，不是文字
    {
      "page_number": 2,
      "description": "年滿 18 歲時要勾選的核取方塊",
      "entry_bounding_box": [140, 525, 155, 540],  // 只框住方塊
      "field_label": "Yes",
      "label_bounding_box": [100, 525, 132, 540],  // 框住 "Yes" 文字
      // 用 "X" 表示勾選。
      "entry_text": {
        "text": "X",
      }
    }
    // 其他欄位
  ]
}
```

對每一頁執行下列指令產生驗證圖片：
`python3 scripts/create_validation_image.py <page_number> <path_to_fields.json> <input_image_path> <output_image_path>`

驗證圖片中，紅色矩形是要填字的位置，藍色矩形蓋住標籤文字。

## 步驟 3：驗證邊界框（必做）

### 自動相交檢查
- 用 `check_bounding_boxes.py` 檢查 fields.json，確認沒有邊界框相交，且填寫框夠高：
  `python3 scripts/check_bounding_boxes.py <JSON file>`

有錯誤時，重新分析相關欄位、調整邊界框，反覆到沒有錯誤為止。切記：標籤（藍色）框要包含文字標籤，填寫（紅色）框不可包含文字。

### 人工檢視圖片
**重要：沒有目視檢查驗證圖片之前，不可進入下一步。**
- 紅色矩形只能蓋住輸入區域。
- 紅色矩形內不可有任何文字。
- 藍色矩形要包含標籤文字。
- 核取方塊：
  - 紅色矩形必須置中於方塊。
  - 藍色矩形要蓋住該方塊的文字標籤。

- 任何矩形看起來不對，就修正 fields.json、重新產生驗證圖片並再次檢查，直到邊界框完全準確。

## 步驟 4：把註記加進 PDF

依 fields.json 的資訊產生填好的 PDF：
`python3 scripts/fill_pdf_form_with_annotations.py <input_pdf_path> <path_to_fields.json> <output_pdf_path>`

完成後用 `pdftoppm -png -r 150` 渲染輸出頁面，目視確認文字沒有溢位或被裁切。
