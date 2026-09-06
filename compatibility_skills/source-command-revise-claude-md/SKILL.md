---
name: source-command-revise-claude-md
description: Use when the user explicitly invokes revise-claude-md or asks to record verified lessons from this session in project instructions.
---

# 將本次會話心得寫回專案指示

僅在使用者明確呼叫 `revise-claude-md` 或本 Skill，或明確要求把本次工作心得寫回專案指示時使用。

1. 從本次實際發現選出可重用的指令、測試方法、風格、環境限制與陷阱；每项附來源或驗證結果，不把未驗證推測寫成專案規則。
2. 用 `rg --files --hidden -g AGENTS.md -g CLAUDE.md -g .Codex.local.md` 找相關指示，讀取檔案層級與既有內容。沿用目前客戶端實際使用的文件；不因舊命令名稱就建立 CLAUDE.md。
3. 團隊共用知識放入正確範圍的 AGENTS.md／CLAUDE.md；個人設定只放實際受支援且已確認 gitignored 的本機文件，不寫入秘密或憑證。只有本次有新知識的檔案需要修改。
4. 比對重複、矛盾及適用條件，提出具體 diff。使用者要求先審查時等待；已批准寫回範圍時直接套用，不重複索取同一批准。替換前保留可恢復版本。
5. 檢查新增指令與路徑有效、作用範圍正確、保留原有安全／權限限制，並重讀完整 diff。未確認的內容留在報告，不當成事實寫入規範。

完成時以繁體中文列出修改檔案、新知識的理由、檢查結果及未採納項目；沒有可重用的新知識時說明無需變更。這是會話心得寫回流程，不自動啟動整庫稽核。
