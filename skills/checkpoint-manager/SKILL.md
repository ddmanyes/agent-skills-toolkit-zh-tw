---
name: checkpoint-manager
description: 解析 execution_trace.md 指令，利用 Git Hash 執行專案狀態回溯與進度重置。
allowed-tools: Terminal, Read, Write, Edit, Glob, Grep
---

# Checkpoint Manager

This skill is responsible for parsing recovery commands from `execution_trace.md` and restoring the project to a specific historical state using Git hashes.

## 1. Recovery Command Parsing (指令解析)
- **Action**: When a user clicks a recovery link or requests a rollback, identify the target Git Hash and Step Name from the input or `execution_trace.md`.
- **Extraction Logic**: Parse the JSON payload or text string (e.g., `{"hash":"abc1234", "step":"init"}`) provided in the request.

## 2. State Restoration (執行回溯)
- **Git Execution**: Run `git checkout [hash]` to restore the file system to the selected checkpoint.
- **Environment Safety**: Before checkout, ensure there are no uncommitted changes that might be lost, or prompt the user in Traditional Chinese to stash them.
- **uv Awareness**: If the project uses `uv`, ensure the current environment remains consistent with the restored code base.

## 3. Context Reset (上下文重置)
- **Implementation Sync**: Read the `IMPLEMENTATION_PLAN.md` from the restored state.
- **Alignment**: Re-align the active task pointers to the step immediately following the restored checkpoint.
- **Log Entry**: Record the restoration event in `execution_trace.md` using Traditional Chinese to maintain the history of rollbacks.

## 4. Output & Confirmation (輸出與確認)
- **Language**: All interaction and confirmation messages must be in Traditional Chinese for 王佳怡.
- **Summary**: Report the successful restoration, including the new active step and current Git head.
- **Next Step**: Ask the user: "專案已恢復至該階段。是否要重新啟動 `autonomous-pilot` 繼續執行計畫？"