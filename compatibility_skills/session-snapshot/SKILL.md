---
name: session-snapshot
description: 當使用者要求保存目前工作進度、交接或下次續作快照時，整理可驗證的狀態與復原資訊到 SESSION_RESUME.md。
---

# 工作進度快照

1. 讀取現有 IMPLEMENTATION_PLAN.md／task_plan.md、execution_trace.md／progress.md 與本次工作上下文。缺少某份文件時使用可取得的證據，不為小任務補建整套規劃文件。
2. 在專案目錄記錄目前分支、`git rev-parse HEAD` 及 `git status --short`。此 hash 是已提交基線，不能代表未提交內容。非 Git 專案改記錄可恢復副本及位置。
3. 寫入前保留原 SESSION_RESUME.md。更新已確認的完成狀態，生成 [交接格式](references/handoff.md)，包含目的、已完成／待辦、準確中斷位置、檢查結果、下一步及實際觀察到的環境。
4. 使用者已要求提交或目前計畫已授權檢查點提交時，才檢查並暫存本次快照及明確屬於本任務的檔案。先讀 staged diff；若存在其他任務／使用者預先暫存內容，保留它們並避免併入本次提交。用逐檔或逐 hunk 的範圍，不使用 git add .。
5. 提交成功後，於交付回覆記錄新 commit hash；不要把含未提交內容的文件標成該 hash 已完整保存，也不為把 commit 自己的 hash 寫進自己而無限重提。提交失敗時保留快照，標記「尚未建立 commit」，列出原因及復原副本。
6. 重讀快照，確認基線 hash 可解析、所列未提交檔案與工作狀態一致、檔案路徑存在、下一步可執行。快照任務不自動 push、reset、checkout 或清除工作樹。

完成代表 SESSION_RESUME.md 已保存並能區分已提交基線與未提交工作，每項未完成內容與恢復方式清楚；不要求所有原工作完成才可交接。以繁體中文交付快照路徑、已驗證 hash／副本及下一步。
