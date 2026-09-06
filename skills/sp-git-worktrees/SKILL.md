---
name: sp-git-worktrees
description: 需要隔離並行功能、修復或審查的 Git 狀態時建立與管理 worktree。
allowed-tools: Terminal, Read, Write, Edit, Glob, Grep
---
# Git Worktrees
1. 確認 repository、目前分支、既有變更與工作目標；使用者指定的 base/ref 優先，否則依專案慣例選擇可解析的基線。
2. 先用 git worktree list --porcelain 檢查既有工作樹，避免重用忙碌分支或覆蓋目錄。用 git worktree add（需要新分支時加 -b 與已確定的名稱）從選定 ref 建立；再用 git worktree list --porcelain 核對目標絕對路徑、HEAD 與 branch，切換到該路徑開始工作。
3. 在該 worktree 完成範圍內實作及驗證。提交和推送僅在已授權範圍內進行，先檢查實際 diff。
4. 清理前確認工作已整合或有可恢復的提交／備份，工作樹沒有未保存內容，且目標確為本次建立的 worktree；再使用 git worktree remove。清理失敗保留資料並報告，不強制移除。

Windows 的目錄操作先解析絕對路徑並確認目標位於指定工作區。完成後以繁體中文列出 worktree 路徑、分支、驗證及保留／清理狀態。
