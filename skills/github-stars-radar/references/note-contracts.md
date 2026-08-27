# Second Brain 筆記契約

## 候選筆記

使用 `new_note(note_type="tool")` 建立，並保留工具產生的 frontmatter。內容至少包含：

```markdown
## 候選卡

> 100–250 字繁體中文：說明這是什麼、解決什麼問題、核心做法，以及為何可能與現有系統相關。

| 欄位 | 值 |
|---|---|
| GitHub | <URL> |
| github_repo_id | <numeric id> |
| starred_at | <UTC timestamp> |
| retrieved_at | <UTC timestamp> |
| language | <value or 未確認> |
| license | <SPDX or 未確認> |
| stars_snapshot | <integer or 未確認> |
| last_push | <timestamp or 未確認> |
| decision | deep-review / watch / record-only |
| score | <0–100> |

## 評分

- 現有系統契合度：<n>/30 — <evidence>
- 實際問題價值：<n>/20 — <evidence>
- 成熟度與維護：<n>/15 — <evidence>
- 差異化：<n>/10 — <evidence>
- 文件與可採用性：<n>/10 — <evidence>
- 授權與安全：<n>/15 — <evidence>

## 初步風險

- <verified risk or 未確認>

## 建議

<one concrete next action>

## Sources

- [Repository](<URL>)
- [README](<direct URL when read>)
- [License](<direct URL when read>)
```

同 repository 再次 Star 時，追加：

```markdown
## Star event — <Asia/Taipei date>

- starred_at: <UTC timestamp>
- 變更：<metadata or evaluation delta>
```

## Ledger

Ledger 使用 append-only 記錄。每個成功處理的事件追加：

```markdown
- <starred_at> | `<owner/repo>` | score=<0–100> | decision=<tier> | note=`<vault-relative-path>`
  <!-- github-star-key: <repo_id>@<starred_at> -->
```

HTML marker 是擷取器的正本鍵，不得改寫格式。不得在候選筆記成功前追加 marker。

當一批候選全部成功且擷取結果 `truncated=false` 時，再追加 high-watermark：

```markdown
<!-- github-stars-cursor: <newest successfully processed starred_at> -->
```

部分失敗或尚有截斷 backlog 時不得前移 cursor；已成功項目依 event marker 去重，失敗項目會在下次重試。第一次啟用可用已人工完成分析的最新一批 Stars 建立 baseline cursor，避免誤匯入全部歷史收藏。

## 固定週報

每週追加一個 ISO week 區段：

```markdown
## YYYY-Www

### 一頁結論

<本週整體判斷>

| Repository | 分數 | 分級 | 一句話價值 | 建議 |
|---|---:|---|---|---|
| [owner/repo](URL) | 00 | watch | ... | ... |

### 高分項目

<只放 75 分以上的深度結論；沒有則寫「本週無高分項目」。>

### 待觀察與行動

- <具體後續>
```
