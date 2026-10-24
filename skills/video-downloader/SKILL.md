---
name: video-downloader
description: 下載各類串流與網站影片（支援 YouTube、Bilibili、Hanime1 等，具備 Cloudflare 反爬指紋偽裝與最高畫質提取）。當使用者提供影片網址並要求下載、抓取影片檔或解析串流時使用。
---

# Video Downloader

提供跨平台、抗反爬防護的現代化串流影片下載流程。整合 `uvx`、`yt-dlp`、`curl-cffi` 指紋偽裝以及 `ffmpeg` 影音重混封裝，確保在 Windows、macOS 與 Linux 上皆能自動提取最高可用畫質並保留正確的檔名編碼。

## 適用場景與限制

- **適用來源**：YouTube、Bilibili、Hanime1、Twitter/X、Vimeo、成人影音站點及一般已公開之 HTML5 / HLS (`.m3u8`) / DASH (`.mpd`) 串流。
- **權限與邊界**：
  - 僅下載使用者指定或有權存取之公開內容；不規避 Widevine / FairPlay / PlayReady 等硬性 DRM 加密。
  - 遇登入驗證時使用 `--cookies-from-browser`，嚴禁外流憑證或將敏感 Token 寫入共享記錄。
  - 下載後自動校驗媒體串流完整性（至少包含一條視訊串流與一條音訊串流）。

## 核心工具鏈

1. **`uv` / `uvx`**：免全域安裝、免污染 Python 環境，即時掛載最新版 `yt-dlp` 與擴充套件。
2. **`curl-cffi`**：提供瀏覽器 TLS（JA3/JA4）與 HTTP/2 握手特徵模擬，用以順利通過 Cloudflare 等 Anti-bot 質詢。
3. **`ffmpeg` / `ffprobe`**：自動偵測系統環境中既有的編解碼器，負責音畫重混封裝（避免轉碼失真）與檔案有效性校驗。

## 標準作業流程

### 1. 來源分析與防護識別

- 評估網址來源特性：
  - 一般串流（YouTube、Bilibili 等）：原生 `yt-dlp` 即可解析。
  - 受 Cloudflare 防護或特徵檢驗站點（如 Hanime1、某些論壇或外嵌串流）：必須啟用 `--impersonate chrome`。
  - 需會員或成年驗證：使用 `--cookies-from-browser chrome`（或 edge / firefox）。

### 2. 格式探測（可選）

下載前若需確認可用解析度或檔案大小，可先探測格式清單：

```bash
uvx --with "yt-dlp[curl-cffi]" yt-dlp --impersonate chrome -F "<VIDEO_URL>"
```

### 3. 執行下載

預設下載最佳畫質（通常為 1080p 或以上）並指定輸出模板與 ffmpeg 路徑：

```bash
uvx --with "yt-dlp[curl-cffi]" yt-dlp \
  --impersonate chrome \
  --ffmpeg-location "<FFMPEG_PATH>" \
  -f "bestvideo*+bestaudio/best" \
  -o "<OUTPUT_DIR>/%(title)s.%(ext)s" \
  "<VIDEO_URL>"
```

Windows PowerShell 範例：
```powershell
uvx --with "yt-dlp[curl-cffi]" yt-dlp --impersonate chrome --ffmpeg-location "C:\Users\User\Downloads\ffmpeg\ffmpeg-2026-01-12-git-21a3e44fbe-full_build\bin" -f "best" -o "I:\downloads\%(title)s.%(ext)s" "<VIDEO_URL>"
```

### 4. 編碼與命名防護（Windows 規範）

在 Windows 環境下，若影片標題包含日文、特殊符號或繁體中文，終端預設 codepage（如 950）可能使終端顯示異常。
- 建議使用隨附腳本 `scripts/download_video.py`，該腳本會以原生 Python UTF-8 方式執行下載與重新命名，避免檔名編碼損壞。
- 或在 PowerShell 啟動前宣告：
  ```powershell
  $OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8
  ```

### 5. 串流校驗與驗收

下載完成後，必須調用 `ffprobe` 檢驗檔案可用性：

```bash
ffprobe -v error -show_entries format=duration,size:stream=codec_name,width,height -of default=noprint_wrappers=1 "<FILE_PATH>"
```

確認條件：
- 存在有效的視訊編碼（如 h264, hevc, av1）且解析度大於 0。
- 影片時長（duration）大於 0 且檔案大小正常。

## 疑難排解

詳細錯誤代碼（如 403 Forbidden、429 Too Many Requests、DRM 限制）請參閱 [references/troubleshooting.md](references/troubleshooting.md)。
