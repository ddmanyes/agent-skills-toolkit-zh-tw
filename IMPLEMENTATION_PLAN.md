# GitHub Stars Radar Skill 實作計畫

## 目標摘要

建立 `github-stars-radar` Skill，以每日增量模式擷取 `ddmanyes` 新增的公開 GitHub Stars，產生可解釋的候選卡並依固定量表評分；75 分以上自動做深度分析。每週模式彙整固定工具雷達。所有 Second Brain 寫入必須透過中央 MCP，且排程不得安裝或執行第三方 repository。

目標目錄目前不是 Git repository，因此本次無法執行原子 commit；改以逐步驗證輸出與最終檔案清單保留可稽核紀錄，不初始化新的 repository 以免擴張使用者授權範圍。

## 文件架構圖

```text
antigravity-skills-zht/
├── IMPLEMENTATION_PLAN.md
└── skills/
    └── github-stars-radar/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        ├── references/
        │   ├── evaluation-rubric.md
        │   └── note-contracts.md
        └── scripts/
            ├── fetch_new_stars.py
            └── test_fetch_new_stars.py
```

## 任務列表

### 任務 1：建立 Skill 骨架

- [x] 使用系統 `init_skill.py` 建立 `github-stars-radar`，只建立 `scripts/` 與 `references/`。
- 預期行為：產生合法 `SKILL.md` 與 `agents/openai.yaml`。
- 驗證指令：`quick_validate.py skills/github-stars-radar`
- 相關檔案：`skills/github-stars-radar/SKILL.md`、`skills/github-stars-radar/agents/openai.yaml`

### 任務 2：以測試定義增量擷取契約（Red）

- [x] 建立標準函式庫 `unittest`，涵蓋 star API envelope、ledger 去重、時間排序、批次上限與錯誤 payload。
- 預期行為：在尚未建立實作前測試失敗。
- 驗證指令：`python3 skills/github-stars-radar/scripts/test_fetch_new_stars.py`
- 相關檔案：`skills/github-stars-radar/scripts/test_fetch_new_stars.py`

### 任務 3：實作增量擷取器（Green）

- [x] 實作 GitHub 公開 API 抓取、`repo_id + starred_at` 鍵值、ledger 解析與 JSON 輸出。
- [x] 支援 `--username`、`--ledger-file`、`--limit`、`--input-json`，並保持唯讀、不寫 Vault。
- 預期行為：相同項目不重複輸出；輸出由新到舊排序；錯誤以非零狀態結束。
- 驗證指令：`python3 skills/github-stars-radar/scripts/test_fetch_new_stars.py`
- 相關檔案：`skills/github-stars-radar/scripts/fetch_new_stars.py`

### 任務 4：重構與固定分析規格（Refactor）

- [x] 將評分量表、候選卡、深度分析、ledger 與週報格式拆至 references。
- [x] 在 `SKILL.md` 固定 daily/weekly 流程、MCP 寫入順序、成功後 checkpoint 與通知規則。
- 預期行為：agent 能在不自行發明格式的前提下安全重跑，且不自動安裝第三方程式。
- 驗證指令：`quick_validate.py skills/github-stars-radar`
- 相關檔案：`SKILL.md`、`references/evaluation-rubric.md`、`references/note-contracts.md`

### 任務 5：本機與網路 dry-run 驗證

- [x] 以 fixture 驗證零新增、單筆新增、重複項目與上限。
- [x] 讀取 `ddmanyes` 公開 Stars，確認能取得 `starred_at` 且不寫入 SB。
- 預期行為：測試全通過；live dry-run 輸出合法 JSON。
- 驗證指令：`python3 .../test_fetch_new_stars.py`、`python3 .../fetch_new_stars.py --username ddmanyes --limit 5`
- 相關檔案：`scripts/fetch_new_stars.py`、`scripts/test_fetch_new_stars.py`

### 任務 6：安裝 Skill 與建立排程

- [x] 將驗證完成的 Skill 安裝至個人 Skill 目錄。
- [x] 建立每日 12:00 daily automation；無新增時靜默。
- [x] 建立每週一 12:10 weekly automation；只通知高分項目或失敗。
- 預期行為：兩個排程啟用並明確呼叫 `$github-stars-radar`。
- 驗證方式：檢視 automation 設定與已安裝 Skill 檔案。
- 相關項目：個人 Skill 目錄、Codex automations。

### 任務 7：Second Brain 實作紀錄

- [x] 經 MCP 建立或追加實作紀錄，包含架構、排程、驗證結果與限制。
- 預期行為：中央 SB 可搜尋到本次實作，不產生直接檔案寫入衝突。
- 驗證方式：`search_notes("github-stars-radar")` 後讀取命中筆記。
- 相關筆記：Second Brain coding/project note。
