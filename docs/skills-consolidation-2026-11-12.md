# Skills 整併與跨電腦更新｜2026-11-12

本版新增 harness-purge 與 skill-toolkit（Active 47 → 49），修復 Claude/Codex 引用，保留文件版本與 Radar 的獨有流程。原有 PowerShell／Bash 同步工具的備份、symlink 防護及過渡技能保護保持不變。

## 發布內容與來源

- harness-purge：本機原創診斷／評測工具，原生工作階段與授權 API 兩條路徑完整保留；references/claude-codex.md 為正確引用。沒有引入 dsh-purge 宿主補丁或上游提示詞。
- docx/pdf/pptx/xlsx：保留工具包原實作，新增已安裝來源解析分支；同步版的 Word 註解、PptxGenJS、PDF 額外操作、XLSX 外部連結與重算等功能可從原供應來源使用。
- skill-toolkit：跨客戶端維護路由到原 skill-creator；評測／benchmark／盲測路由到各機已安裝的評測版本。系統 skill-creator 保留一般建立功能。
- Radar：本機強化流程成為公開 fallback，保留執行鎖、topic-note、週報補發；repository 先前發布的 atomic-note 等流程原樣保存在 variants/legacy，入口命名 WORKFLOW.md，避免多一個技能被載入。
- 本次沒有把受限的 synced 文件技能、插件 cache、私人 config、憑證或模型 runtime 上傳。完整本機快照仍留在原電腦；其他電腦從原供應來源取得外部技能。

## 更新前

在每台電腦自己的完整 checkout 執行：

```text
git status --short
git remote -v
git pull --ff-only
```

origin 應為 https://github.com/ddmanyes/agent-skills-toolkit-zh-tw.git 。先保留未提交修改；分歧時不要 reset/force，另建 checkout 比對。遠端 IDE/container 的 home 與本機不同，須各自部署。

Python 至少 3.11；QA 使用 PyYAML 6，建議在 venv 安裝。同步腳本仍用原有 runtime：Windows PowerShell；macOS/Linux Bash + rsync。

## Windows PowerShell

```powershell
$updatedSkills = @('harness-purge','skill-toolkit','skill-creator','docx','pdf','pptx','xlsx')
.\scripts\sync-local-skills.ps1 -All -SkillNames $updatedSkills -WhatIf
.\scripts\sync-local-skills.ps1 -All -SkillNames $updatedSkills
```

只用 Codex 時將 -All 換成 -Agents。若目錄為 junction/symlink，先核對真實目標；不要刪連結來繞過同步防護，只同步一次實體來源。

## macOS／Linux

```bash
bash scripts/sync-local-skills.sh --all \
  --skill harness-purge --skill skill-toolkit --skill skill-creator \
  --skill docx --skill pdf --skill pptx --skill xlsx
```

若 ~/.claude/skills 已連到 ~/.agents/skills，將 --all 換成 --agents --antigravity；只需 Codex 則 --agents。這一輪不會自動改 symlink 或建立其他客戶端設定。

## Radar：先比對，再明確更新

四個 Radar 仍是 transitional，正常同步保留既有副本。比對本機 SKILL.md、references 與 scripts，合併額外客製後才執行下列指定更新；同步會備份被覆寫檔案，不刪額外檔案。

```powershell
.\scripts\sync-local-skills.ps1 -Agents -IncludeTransitional -SkillNames content-radar,github-stars-radar,threads-bookmarks-radar,x-bookmarks-radar
```

```bash
bash scripts/sync-local-skills.sh --agents --include-transitional \
  --skill content-radar --skill github-stars-radar \
  --skill threads-bookmarks-radar --skill x-bookmarks-radar
```

需要其他實體客戶端目錄時明確加選，不對共用連結重複寫入。topic-note 是 X 預設；每則一篇需明確指定 atomic 模式。週報統一48小時門檻需明確指定相容模式；預設保留 X 8天／其他48小時及補發功能。不變更既有排程。

## Codex 去重（其他客戶端不套用此設定）

Windows：

```powershell
python "$HOME/.agents/skills/skill-toolkit/scripts/skill_routes.py" resolve --kind synced --skill docx
python "$HOME/.agents/skills/skill-toolkit/scripts/skill_routes.py" configure
python "$HOME/.agents/skills/skill-toolkit/scripts/skill_routes.py" configure --apply
```

macOS/Linux 使用同樣參數，將 python 換成 python3。

先檢視 configure 的 planned/skipped。只停用已由可用主入口保留功能的確定副本；缺來源、多個不同版本、不同客製資源或未知插件版本會保留。設定使用實際絕對path，不寫死帳號、bucket或插件版本。原檔不刪除；不修改其他Codex設定。來源升版後重新 dry-run，再確認是否套用。

此處採 Codex 的 [[skills.config]] path + enabled=false，依據 [官方技能設定](https://learn.chatgpt.com/docs/build-skills)。Claude/Antigravity 保留原名稱與入口，不複製 Codex 設定。

## 驗證與回復

```text
python scripts/tests/test_skill_routes.py
python scripts/tests/test_sync_local_skills.py
python scripts/check-skill-consistency.py --mirror <實體技能目錄>
```

只做選擇性安裝時，完整 mirror checker 可能回報其他未安裝技能；這不代表本輪複製失敗。完整同步後再使用全目錄比較；過渡項預設只驗入口可讀，加 --include-transitional 才比較內容。明確區分 runtime SKIP 與 PASS。

重啟客戶端；Codex 以 skills/list 或技能清單確認啟用來源，實測一個所需分支。檔案一致不等於模型效果或外部服務已驗證。

同步備份在各客戶端 skills-backups；去重設定備份在 ~/.codex/skills-backups/config-routing-*.toml。還原前比對後續修改，逐檔恢復；config只移除本工具 BEGIN/END toolkit-skill-routing-v1 區段，不整份覆寫。若原先有20261112本機整併區段，仍由其原備份紀錄管理，這個工具不自行刪除。

CI 以 Linux、macOS、Windows 測試路由，並測各可用的原生同步工具；模型比較、真實文件渲染、社群收錄及其他電腦安裝效果需分別驗證。
