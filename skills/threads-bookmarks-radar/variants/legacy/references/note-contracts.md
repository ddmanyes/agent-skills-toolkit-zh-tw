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

每則一列：`- {collected_at} | {priority} | [[atomic note title]] | {canonical_url} | {一句摘要}`。

## Sync-state record

只有 atomic note 與 index 都成功後才追加：

```markdown
- {canonical_url}
  - processed_at: {Asia/Taipei timestamp}
  - note: [[atomic note title]]
```

每次執行可再追加一個 run summary，包含 `new_count`、`bottom_reached`、`failures` 與 `pending_retry`。重試既有 canonical URL 時不得建立第二篇 atomic note或第二列 index。
