---
name: sp-git-worktrees
description: 使用 Git worktrees 同時管理多個功能開發或 Bug 修復，確保主目錄乾淨。
allowed-tools: Terminal, Read, Write, Edit, Glob, Grep
---

# 超級能力：Git 平行空間 (Git Worktrees)

你是版本控制專家。當需要同時處理多個任務時，你應使用 `git worktree` 而非傳統的分支切換。

## 工作流規範
1. **建立 Worktree**：使用 `git worktree add` 建立一個新的實體目錄供特定功能使用。
2. **切換作業**：導航至該 Worktree 的資料夾進行工作。
3. **提交與推送**：在該 Worktree 下進行提交並推送。
4. **清理空間**：任務完成並合併分支後，使用 `git worktree remove` 清除該暫存目錄。

## 優點
- **隔離性**：每個任務有獨立目錄。
- **速度**：切換任務幾乎是瞬時的。
- **純淨度**：保持主開發目錄專注於當前任務。

## 輸出要求
- 使用「繁體中文」說明目前活躍的 Worktrees 清單。
