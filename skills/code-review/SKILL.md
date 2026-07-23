---
name: sp-code-review
description: 雙軸程式碼審查（Standards / Spec 並行）＋ Fowler code smell 基線，專為 Python 與生物資訊數據分析優化。
allowed-tools: Terminal, Read, Write, Edit, Glob, Grep, Task
---

# 超級能力：進階代碼審查 (Code Review)

你是資深技術審查員。審查一個固定點（commit / branch / tag / merge-base）到 `HEAD` 之間的 diff，沿**兩條互不干擾的軸**進行：

- **Standards（規範軸）**：這段 diff 是否符合本專案的成文規範（`CLAUDE.md`、`CONTEXT.md`、風格指南）以及通用的 code smell 基線？
- **Spec（規格軸）**：這段 diff 是否忠實實作了它源頭的需求（issue / PRD / 你們討論定案的規格）？

兩條軸各用一個 **平行 sub-agent** 跑，避免彼此污染 context，最後本 skill 把兩份報告**並排呈現、不合併排名**。

## 為什麼要兩條軸

一段改動可能過了一軸卻掛了另一軸：符合所有規範但做錯了東西（Standards pass, Spec fail）；或精準實作了 issue 卻違反專案慣例（Spec pass, Standards fail）。分開報告，才不會一軸的問題被另一軸蓋掉。

## 審查前自檢清單 (Pre-review Checklist)

1. **測試驗證**：確認新測試與回歸測試全部通過（Scanpy/uv 環境特別留意）。
2. **文件同步**：相關 README、API 文件、內部註解是否跟著改動更新。
3. **提交訊息**：git commit 訊息是否精準且符合規範。

## 審查流程 (Process)

### 1. 釘住固定點

使用者指定的就是固定點（SHA / branch / tag / `main` / `HEAD~5`）。沒指定就問。
先確認 ref 解析得出（`git rev-parse`）且 diff 非空——壞的 ref 或空 diff 要在這裡就失敗，別丟進兩個 sub-agent 才炸。
記下：`git diff <固定點>...HEAD`（三點，比對 merge-base）與 `git log <固定點>..HEAD --oneline`。

### 2. 找出規格來源（給 Spec 軸）

依序找：commit 訊息裡的 issue 引用 → 使用者指定的路徑 → `docs/`、`specs/`、`.scratch/` 下對應此分支/功能的 PRD。都找不到就問使用者；若確實沒有規格，Spec 軸略過並回報「無規格可比對」。

### 3. 找出規範來源（給 Standards 軸）

專案內任何定義「程式該怎麼寫」的文件：`CLAUDE.md`、`CONTEXT.md`、`CODING_STANDARDS.md` 等。

除了專案成文規範，Standards 軸**永遠**附帶 Fowler code smell 基線（12 條，含約束與逐條修法）——見 [SMELLS.md](SMELLS.md)。開 Standards sub-agent 時把它整份貼入該 sub-agent 的 prompt。

### 4. 平行開兩個 sub-agent

用**一則訊息**同時發兩個 `Task`（`general-purpose`）：

**Standards sub-agent** 帶：完整 diff 指令與 commit 清單、步驟 3 找到的規範檔清單、**以及 [SMELLS.md](SMELLS.md) 整份原文貼入**（sub-agent 沒別的管道拿到它）。
指示：「逐檔/逐 hunk 回報：(a) diff 違反成文規範的每一處，引用規範（檔名＋規則）；(b) 你看到的任何基線 smell，命名它並引用 hunk。區分硬性違規與判斷題——成文規範可為硬性，基線 smell 一律是判斷題，且專案成文規範蓋過基線。工具能抓的略過。400 字內，繁體中文。」

**Spec sub-agent** 帶：diff 指令與 commit 清單、規格路徑或內容。
指示：「回報：(a) 規格要求但缺失或只做一半的；(b) diff 裡沒被要求的行為（scope creep）；(c) 看似有實作但實作方式看起來錯的需求。每條引用規格的那一行。400 字內，繁體中文。」

若無規格，略過 Spec sub-agent 並在最終報告註明。

### 5. 彙整

在 `## Standards` 與 `## Spec` 兩個標題下並排呈現兩份報告，逐字或輕度整理即可。**不要合併或跨軸重排**——兩軸刻意分開。
結尾一行摘要：各軸的 finding 總數，以及**各軸內**最嚴重的問題。不要跨軸選單一贏家（那正是分軸要防的重排）。

## 輸出要求

- 全程使用「繁體中文」。
- 針對 Scanpy/uv/Python 生信環境特別優化檢查。
