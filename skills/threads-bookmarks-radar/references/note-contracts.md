# Threads Note Contracts

## Atomic resource note

標題使用 `Threads 書籤｜{12 至 30 字摘要}｜{shortcode}`。內容依序包含：

```markdown
## 來源

- platform: Threads
- author: @{username}
- posted_at: {可見日期或未確認}
- canonical_url: https://www.threads.com/@{username}/post/{shortcode}
- collected_at: {Asia/Taipei timestamp}

## 內容摘要

{短解釋}

## 可重用內容

{可重用 prompt、參數、步驟或「無」}

## 初步判斷

- priority: 高價值 | 待觀察 | 低優先
- evidence: {支持判斷的可見證據}
- limitations: {未確認資訊}

## 原文與媒體

{完整可見主文、同作者串文與媒體說明；不得補寫未顯示內容}
```

## Index row

每則一列：`- {collected_at} | {priority} | [[{atomic note 的 vault 相對路徑，不含 .md}]] | {canonical_url} | {一句摘要}`。

連結一律寫 vault 相對路徑（例如 `30-resources/threads-書籤-…`），從 `new_note` 結果或再次搜尋取得；不寫筆記標題，標題式連結在 Obsidian 點不開。

## Sync-state record

只有 atomic note 與 index 都成功後才追加：

```markdown
- {canonical_url}
  - processed_at: {Asia/Taipei timestamp}
  - note: [[{atomic note 的 vault 相對路徑，不含 .md}]]
```

重試既有 canonical URL 時不得建立第二篇 atomic note或第二列 index。

## Run record（執行鎖與新鮮度）

每次執行在同步狀態追加一個 `## 同步 {Asia/Taipei timestamp}` 段落，第一行與最後一行夾住本次所有寫入：

```markdown
- run_started: {Asia/Taipei timestamp} | runner: {主機名或 automation id}
- run_finished: {Asia/Taipei timestamp} | runner: {同上} | new_count: {n} | bottom_reached: {true/false} | failures: {n} | pending_retry: {n}
```

- **開始前判斷鎖**：找同步狀態中最後一個 `run_started`。若它之後沒有 `run_finished`、且開始時間在 3 小時內，代表另一個執行還在跑：停止並回報，本次零寫入。若已超過 3 小時，先追加 `- run_abandoned: {該 run_started 的時間} | noted_at: {now}`，再繼續。
- **確認拿到鎖**：追加自己的 `run_started` 後重新讀取同步狀態；若自己這行之後已出現別的 `run_started`，停止並追加 `run_finished`（new_count: 0，failures: 0，註明 `yielded`），不寫任何書籤。
- 沒有新書籤時仍追加 `run_finished`（new_count: 0）；這行是週報判斷新鮮度的依據。
- 失敗中止時也要盡量追加 `run_finished`，在 failures 與 pending_retry 記下數量。
