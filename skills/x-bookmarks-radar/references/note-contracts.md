# X Note Contracts

X 採 **topic-note 模式**：同主題的書籤寫進同一篇主題筆記，每則書籤在其中佔一個獨立段落；不另建單篇 atomic note。以下的「note」都指該主題筆記。

## 主題筆記與書籤段落

- 先以 `search_notes` 找同主題、`status: active` 的既有主題筆記；沒有合適的才用 `new_note(note_type="resource")` 建立，標題寫主題，不寫 status id。
- 成人或 NSFW 書籤只寫進成人向主題筆記，不混入一般主題筆記。
- 同一主題筆記內，每則書籤以 `append_to_note` 追加一個段落；canonical URL 已在該筆記出現時不重複追加。段落依序包含：

```markdown
## {posted_at 或未確認} — {12 至 30 字摘要}｜{status id}

- canonical_url: https://x.com/{username}/status/{id}
- author: @{username}
- posted_at: {可見日期或未確認}
- collected_at: {Asia/Taipei timestamp}
- priority: 高價值 | 待觀察 | 低優先
- evidence: {支持判斷的可見證據}
- limitations: {未確認資訊}

### 可重用內容

{可重用 prompt、參數、步驟或「無」}

### 原文與媒體

{完整可見主文、同串內容、quoted post 與媒體說明；不得補寫未顯示內容}
```

## Index row

索引每次執行追加一個 `## 增量更新 {YYYY-MM-DD}` 段落，內含一張表，每則一列：

```markdown
| 收錄時間 | 優先級 | 作者 | 類別 | 已整理內容 | 原貼 | 詳細筆記 |
|---|---|---|---|---|---|---|
| {collected_at} | {priority} | @{username} | {類別} | {一句摘要} | [X]({canonical_url}) | [[{主題筆記的 vault 相對路徑，不含 .md}]] |
```

連結一律寫 vault 相對路徑（例如 `30-resources/某主題筆記`），不寫筆記標題；標題式連結在 Obsidian 點不開。

## Sync-state record

只有書籤段落與 index row 都成功後才追加：

```markdown
- {canonical_url}
  - processed_at: {Asia/Taipei timestamp}
  - priority: {與書籤段落相同}
  - note: [[{主題筆記的 vault 相對路徑，不含 .md}]]
```

舊紀錄（2026-10-04「設定更新」段落之前）只有 URL，沒有 priority 與 note；不回填，讀取端以索引列定位筆記、priority 視為「未確認」。

## Run record（執行鎖與新鮮度）

每次執行在同步狀態追加兩行，夾住本次所有寫入：

```markdown
- run_started: {Asia/Taipei timestamp} | runner: {主機名或 automation id}
- run_finished: {Asia/Taipei timestamp} | runner: {同上} | new_count: {n} | bottom_reached: {true/false} | failures: {n} | pending_retry: {n}
```

- **開始前判斷鎖**：找同步狀態中最後一個 `run_started`。若它之後沒有 `run_finished`、且開始時間在 3 小時內，代表另一個執行還在跑：停止並回報，本次零寫入。若已超過 3 小時，先追加 `- run_abandoned: {該 run_started 的時間} | noted_at: {now}`，再繼續。
- **確認拿到鎖**：追加自己的 `run_started` 後重新讀取同步狀態；若自己這行之後已出現別的 `run_started`，停止並追加 `run_finished`（new_count: 0，failures: 0，註明 `yielded`），不寫任何書籤。
- 沒有新書籤時仍追加 `run_finished`（new_count: 0）；這行是週報判斷新鮮度的依據。
- 失敗中止時也要盡量追加 `run_finished`，在 failures 與 pending_retry 記下數量。
- 同步狀態中同名設定欄位出現多次時，以最後出現者為準。

重試既有 canonical URL 時不得新增第二個書籤段落、第二列 index 或第二筆 processed record。
