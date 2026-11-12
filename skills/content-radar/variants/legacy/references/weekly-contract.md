# Weekly Radar Contract

## 完整週次區段

```markdown
## {YYYY-Www}

### 資料新鮮度

| 來源 | 最後可驗證同步 | 狀態 |
|---|---:|---|
| GitHub | {timestamp 或 unknown} | fresh / stale / unknown |
| X | {timestamp 或 unknown} | fresh / stale / unknown |
| Threads | {timestamp 或 unknown} | fresh / stale / unknown |

### 本週摘要

- GitHub Stars：{count}
- X 書籤：{count}
- Threads 書籤：{count}
- 跨來源重複訊號：{count}

### GitHub 工具候選

| 分數 | Repository | 判斷 | Source ID |
|---:|---|---|---|
| {score 或未確認} | [[note]] | {摘要} | `github:{repo_id}@{starred_at}` |

### 社群內容

| 優先級 | 來源 | 內容 | 判斷 | Source ID |
|---|---|---|---|---|
| 高價值／待觀察／低優先 | X／Threads | [[note]] | {摘要} | `x:{id}` |

### 跨來源訊號

{只列有明確共同 repository URL、external URL 或可驗證同一工具的群組。每組保留原 source id。}

### 建議行動

{具體但不自動執行的下一步；沒有時寫「本週無」。}
```

沒有某類項目時保留計數，但可省略該來源的明細表。不得為了填滿版面加入時窗外內容。

## 補充區段

同一 ISO week 出現尚未列入的 source id 時追加：

```markdown
### 補充 {Asia/Taipei timestamp}

- 新增來源數：GitHub {n}、X {n}、Threads {n}
- {priority 或 score} | [[note]] | `{source id}` | {一句判斷}
```

## 完成條件

- 每個列出的 source id 在該週只出現一次。
- 每個 wikilink 都能回到已存在的 atomic note。
- 來源讀取失敗時沒有新增完整或補充區段。
- 報告只追加，不覆寫既有週次。
