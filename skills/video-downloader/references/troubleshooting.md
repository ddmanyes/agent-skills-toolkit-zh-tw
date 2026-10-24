# 影片下載疑難排解與常規指引 (Troubleshooting)

## 1. HTTP 403 Forbidden / Cloudflare 質詢攔截

### 徵兆
執行 `yt-dlp` 時出現：
`ERROR: [generic] Got HTTP Error 403 caused by Cloudflare anti-bot challenge`

### 解決方案
1. 確保掛載 `curl-cffi` 模組：
   `uvx --with "yt-dlp[curl-cffi]" yt-dlp ...`
2. 加入 impersonate 參數：
   `--impersonate chrome` 或 `--impersonate safari`、`--impersonate edge`
3. 檢查 User-Agent 與 Referer 標頭，必要時手動指定：
   `--add-header "Referer: <PAGE_URL>"`

## 2. 需會員登入或 18+ 質詢

### 徵兆
提示需要登入會員或 `Sign in to confirm you're not a bot`。

### 解決方案
使用當前本機瀏覽器會話：
`--cookies-from-browser chrome`
或使用 Firefox / Edge：
`--cookies-from-browser edge`

## 3. Windows 下檔案名稱亂碼 (ANSI Codepage 問題)

### 徵兆
下載下來的檔案名稱出現亂碼符號（如 `c ƹƱi...`）。

### 解決方案
1. 使用 `scripts/download_video.py` 輔助下載，該腳本直接調用 Windows Unicode API 保留檔名。
2. 或在執行前設定終端編碼：
   `$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8`

## 4. 畫質未達最高或僅下載到單獨影音軌

### 徵兆
只有 720p 甚至 480p，或影片沒有聲音。

### 解決方案
許多網站（如 YouTube、Bilibili）將 1080p 以上的視訊軌與音訊軌分開儲存（DASH 串流），需要 `ffmpeg` 進行自動合併。
- 必須指定 `--ffmpeg-location "<FFMPEG_BIN_DIR>"`。
- 格式選擇設定為 `-f "bestvideo*+bestaudio/best"`。
