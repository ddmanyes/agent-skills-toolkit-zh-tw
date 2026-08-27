# 跨來源內容雷達實作計畫

## 目標摘要

保留 `github-stars-radar` 的 repository 專用分析，新增 X 與 Threads 的獨立書籤擷取 Skill，再由 `content-radar` 每週唯讀彙整 Second Brain 中已成功寫入的三個來源。每日擷取失敗彼此隔離；任何來源都必須先完成 atomic note 與索引寫入，才能前移自己的同步狀態。

## 文件架構圖

```text
antigravity-skills-zht/
├── IMPLEMENTATION_PLAN.md
├── README.md
├── skills/
│   ├── ask-matt/
│   │   └── SKILL.md
│   ├── github-stars-radar/
│   │   └── SKILL.md
│   ├── threads-bookmarks-radar/
│   │   ├── SKILL.md
│   │   ├── agents/openai.yaml
│   │   ├── references/note-contracts.md
│   │   └── scripts/
│   │       ├── normalize_url.py
│   │       └── test_normalize_url.py
│   ├── x-bookmarks-radar/
│   │   ├── SKILL.md
│   │   ├── agents/openai.yaml
│   │   ├── references/note-contracts.md
│   │   └── scripts/
│   │       ├── normalize_url.py
│   │       └── test_normalize_url.py
│   └── content-radar/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       └── references/weekly-contract.md
└── SKILL_AUDIT_2026-08-27.md
```

## 任務列表

### 任務 1：固定來源 URL 契約（Red → Green → Refactor）

- [x] 先為 X 與 Threads 撰寫正常 URL、媒體尾碼、query、錯誤 host 與錯誤 path 測試。
- [x] 執行測試並確認在實作缺席時失敗。
- [x] 建立各來源 `normalize_url.py`，只輸出可作為 ledger key 的 canonical URL。
- [x] 重構共同的錯誤訊息與 CLI 輸出，重新執行測試。
- 預期行為：合法貼文 URL 產生穩定 key；非貼文 URL 以非零狀態失敗。
- 驗證指令：`python3 skills/*-bookmarks-radar/scripts/test_normalize_url.py`
- 相關檔案：兩個 `scripts/` 目錄。

### 任務 2：建立來源專用書籤 Skills

- [x] 建立 `threads-bookmarks-radar` 的 browser、去重、寫入順序、NSFW 與失敗恢復契約。
- [x] 建立 `x-bookmarks-radar`，沿用 Second Brain 現有 X 同步狀態與來源頁設定。
- [x] 為兩個 Skill 建立 Codex UI metadata 與 atomic note 格式。
- 預期行為：兩個來源各自維護 ledger；任何部分失敗都不會提前標記已處理。
- 驗證指令：`lint_skill.py`、來源 URL 單元測試。
- 相關檔案：`skills/threads-bookmarks-radar/`、`skills/x-bookmarks-radar/`。

### 任務 3：建立跨來源週報 Skill

- [ ] 建立 `content-radar` weekly workflow 與固定週報契約。
- [ ] 使用 ISO week heading 做冪等；只讀來源狀態與 atomic notes。
- [ ] 保留 GitHub 數字分數；社群內容使用可解釋優先級，不跨量表比較。
- [ ] 在來源超過 48 小時未同步時標示資料新鮮度警告。
- 預期行為：無新增時靜默；非空週報或讀寫失敗時才通知。
- 驗證指令：`lint_skill.py skills/content-radar` 與情境測試審查。
- 相關檔案：`skills/content-radar/`。

### 任務 4：更新路由與文件

- [ ] 更新 `ask-matt` 的 GitHub、X、Threads 與跨來源週報分流。
- [ ] 將 `github-stars-radar weekly` 標為手動相容模式，預設週報改由 `content-radar`。
- [ ] 更新 README 與操作說明。
- 預期行為：路由只建議目前實際安裝的 Skill；既有 GitHub daily 不受影響。
- 驗證指令：`git diff --check`、Skill QA。
- 相關檔案：`skills/ask-matt/SKILL.md`、`skills/github-stars-radar/SKILL.md`、`README.md`。

### 任務 5：全庫 Skill QA 與改善稽核

- [ ] 對所有 active Skills 執行 deterministic validator。
- [ ] 修正本次變更中的所有 FAIL；不以大規模改寫掩蓋上游 WARN。
- [ ] 將全庫問題依阻斷、可攜性、觸發準確度與文件負擔分級。
- [ ] 建立可追蹤的改善報告。
- 預期行為：本次新增／修改 Skill 為零 FAIL；全庫風險有清楚優先序。
- 驗證指令：`python3 skills/skill-qa-gate/scripts/lint_skill.py skills/*`
- 相關檔案：`SKILL_AUDIT_2026-08-27.md`。

### 任務 6：部署、排程遷移與紀錄

- [ ] 同步 Claude、Codex／通用 Agent、Antigravity 本機 Skill 目錄。
- [ ] 更新 Threads 排程，使其明確呼叫新 Skill。
- [ ] 停用 GitHub 單獨週報，新增每週一 13:00 的跨來源週報。
- [ ] 不在本機建立 X 排程；將另一台電腦的更新步驟寫入 Second Brain。
- [ ] 推送 GitHub 並同步 Google Drive repository 副本。
- 預期行為：不建立重複排程；GitHub daily 與 Threads daily 保持啟用。
- 驗證方式：回讀 automation、GitHub remote commit、三個本機 Skill 路徑與 SB 筆記。
- 相關項目：Codex automations、GitHub repository、Second Brain。
