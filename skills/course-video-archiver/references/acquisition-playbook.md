# Remote Video Acquisition Playbook

只在來源是遠端 URL 或需登入的網頁時讀取本文件。

## 來源選擇順序

1. 先查是否有供應者官方下載、匯出或 API。
2. 已登入頁面需要互動時，使用目前 host 的瀏覽器控制能力。
3. 只有頁面已合法揭露未加密媒體時，才使用 `ffmpeg`／`ffprobe`。

若 host 有「先查 connector/API 再用 browser」的規則，先完成該查詢。專用 connector 能完成工作時使用 connector；需要登入畫面或播放器狀態時才使用 browser。

## 瀏覽器檢查

- 先讀該 host 的 browser skill 或操作文件。
- 確認頁面標題、課程名稱、標示片長與登入狀態。
- 檢查 `video`、`source`、`iframe`、官方 player metadata，以及可用的 page-assets inventory。
- 在 iframe 播放器中讀取可見 DOM 與頁面內嵌設定；不得讀 cookies、local storage 或瀏覽器 profile。
- 官方播放器若提供直接下載，使用下載事件或 media-download capability。
- 不為了取得資源而猜測大量 URL、枚舉 ID 或切換帳號。

## 無 DRM 串流

常見可處理來源：

- 直接 MP4／WebM。
- 未加密 HLS (`.m3u8`)。
- 未加密 DASH (`.mpd`)。

先以 `ffprobe` 列出所有 streams／programs，再選擇明確的 video 與 audio index。不要假設第一條 stream 是最佳畫質。

```text
ffprobe -v error -show_entries \
  stream=index,codec_type,codec_name,width,height,bit_rate \
  -of json <authorized-media-url>
```

下載時優先 stream copy：

```text
ffmpeg -i <authorized-media-url> \
  -map <video-index> -map <audio-index> \
  -c copy -movflags +faststart <output.mp4>
```

實際指令應使用目前 shell 的安全 quoting。媒體 URL 只存在於短期執行狀態；輸出與回覆必須移除 query token、signature 與授權標頭。

## DRM 停止訊號

出現任一訊號就停止取得影片：

- Widevine、FairPlay、PlayReady。
- Encrypted Media Extensions／`encrypted` event。
- license server、content key、key exchange。
- 需要破解、解密或繞過供應者限制的步驟。

停止後可提供兩個安全選項：使用供應者正式下載，或請使用者提供其合法取得的本機影片。

## 下載驗證

用 `ffprobe` 取得 duration、resolution、video codec、audio codec、sample rate 與 channels。抽取 0%、50%、95% 三個位置的畫面。完成必須同時滿足：

- 影音軌存在。
- duration 容差符合 `SKILL.md`。
- 三個抽查點都是同一堂完整影片，而非預告、廣告或錯誤頁面。
- 容器可從頭 seek 到接近結尾。
