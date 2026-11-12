---
name: skill-toolkit
description: 維護跨客戶端技能工具包、封裝相容資源，或對技能做 eval、benchmark、盲測及描述觸發優化；一般 Codex 技能初建使用系統 skill-creator。
---
# 技能工具包與評測

- 跨客戶端維護、init/package/quick_validate：先讀 [工具包原流程](../skill-creator/SKILL.md)，腳本相對於該流程目錄。
- eval、baseline、benchmark、盲測、review viewer 或描述優化：先讀 [分支路由](references/variant-routing.md)，尋找並讀取已安裝的評測版本；腳本相對於解析出的入口目錄。
- 一般 Codex 新技能使用系統 skill-creator；其他客戶端沒有系統入口時使用上述工具包流程。

外部技能保持原地，不重新分發或複製。必要資源缺失或版本不唯一時停止相應分支，列明缺件；其餘可獨立執行的本機分支仍可使用。以 skill-qa-gate 驗證變更；實際模型、服務或客戶端未測時明確列出，不以靜態檢查代替效果證據。

整理 Codex 重複入口時使用路由文件中的 dry-run／apply 流程，只修改已核對的設定區段，保留來源及備份；不替其他客戶端停用技能。

<!-- skill-routing-v1 -->
