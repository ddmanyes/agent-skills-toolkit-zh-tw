# HTML／SVG 輸出規格

## 必要條件

- 輸出為 UTF-8 單檔 HTML，主要圖表使用 inline SVG。
- SVG 必須包含 `role="img"` 與 `aria-labelledby`。
- SVG 第一個子元素必須是帶唯一 ID 的 `<title>`，接著是帶唯一 ID 的 `<desc>`。
- 使用 `viewBox`，讓圖表能等比例縮放。
- 外部資源只允許 Google Fonts `/css2` stylesheet；不得使用 iframe、object、embed 或遠端腳本。
- 不得加入 inline event handler，例如 `onclick`。
- 不得使用可執行 URL，例如 `javascript:`。

## 建議畫布

| 用途 | viewBox |
|---|---|
| 簡報／橫向 | `0 0 1280 720` |
| 文件／一般圖表 | `0 0 1000 600` |
| 縱向流程 | `0 0 800 1200` |

## SVG 結構

```html
<svg viewBox="0 0 1280 720" role="img"
     aria-labelledby="example-title example-desc">
  <title id="example-title">圖表標題</title>
  <desc id="example-desc">一句話說明圖表內容。</desc>
  <defs>...</defs>
  <!-- 背景與群組 -->
  <!-- 連線 -->
  <!-- 節點 -->
  <!-- 圖例 -->
</svg>
```

所有 ID 必須以圖表 slug 為前綴，避免多張 SVG 合併時衝突。

## 驗證命令

```bash
python3 scripts/self_check.py diagram.html
```

只有出現 `OK <path>` 才算通過結構與安全檢查。
