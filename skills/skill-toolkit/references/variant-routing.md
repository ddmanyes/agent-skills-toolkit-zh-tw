# 跨平台分支路由

## 解析已安裝來源

令 TOOLKIT_DIR 為 skill-toolkit 的實際目錄。在 Windows 使用 python，macOS/Linux 使用 python3，Python 至少 3.11。

```text
python <TOOLKIT_DIR>/scripts/skill_routes.py resolve --kind synced --skill docx
python <TOOLKIT_DIR>/scripts/skill_routes.py resolve --kind synced --skill skill-creator
```

可用技能為 docx、pdf、pptx、xlsx、skill-creator。讀取回傳 entry 的完整內容，後續相對資源以其父目錄為準。若回傳 unavailable 或 ambiguous，停止該分支，列出缺件／候選；不要猜選最新版，不自動下載或上傳內容。各機從原供應來源安裝後可再解析。

工具以目前使用者 home 查 .agents/skills/synced；也辨識上輪本機保留的 variants 快照（只在 synced 未提供版本時備援）。--home 只用於指定另一安裝根或隔離測試。相同入口但附帶資源不同視為不同版本。工具只讀來源，不執行來源腳本。

來源宣稱的預裝套件、沙箱及應用相容性需在目前環境重新驗證。先保留使用者原檔；同名腳本不可混用參數。套件缺少時用隔離環境；原流程的失敗、權限與驗證條件繼續適用。

## Codex 重複入口

```text
python <TOOLKIT_DIR>/scripts/skill_routes.py configure
python <TOOLKIT_DIR>/scripts/skill_routes.py configure --apply
```

預設 dry-run 只列 planned/skipped，不寫入。先確認所有 planned 的保留入口與可達功能。--apply 重新檢查來源雜湊，備份既有設定到 .codex/skills-backups，再更新本工具專屬標記區段；不刪任何來源或改其他設定。

只在主入口已具本版路由且外部來源完整可解析時停用對應 synced 入口；harness-purge/local-dual-model 必須全資源一致（harness 可辨識已知誤替換）才停用 .codex 副本。有額外客製內容則 skipped。Radar 插件只有與已保留的本機或舊分支全文資源一致才停用；未知升版保留啟用供比對。

此設定只影響 Codex，不影響 Claude／Antigravity。重啟 Codex 後用 skills/list 或技能清單確認。無資料、重複版本或設定有後續修改時應回報 skipped/錯誤，不宣稱全部去重。

回復：先比對備份與目前設定，只移除 BEGIN/END toolkit-skill-routing-v1 區段；不要用整份備份覆蓋後續設定。其他舊整併區段由原紀錄管理。副本、LICENSE 與原腳本一直保留。
