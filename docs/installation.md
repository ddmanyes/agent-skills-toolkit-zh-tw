# 安裝、更新與驗證

[回到專案首頁](../README.md)

除 clone 與切換目錄的指令外，以下命令都從 repository 根目錄執行。請選擇自己的客戶端與安裝範圍。

> [!IMPORTANT]
> `github-stars-radar`、`x-bookmarks-radar`、`threads-bookmarks-radar` 與 `content-radar` 的正式開發與更新來源已移至獨立的 Private 維運專案。本 repository 暫時保留四個相容副本，供既有安裝遷移與回復使用；兩邊不做雙向同步。Private 專案的存取與安裝資訊只提供給已獲授權的使用者。

## ⚡️ 快速安裝

建議 clone 完整 repository，再使用同步腳本；不要只複製 `SKILL.md`，否則可能漏掉 Skill 需要的 scripts、references、templates 或其他資源。

macOS／Linux：

```bash
git clone https://github.com/ddmanyes/agent-skills-toolkit-zh-tw.git
cd agent-skills-toolkit-zh-tw
./scripts/sync-local-skills.sh --all
```

Windows PowerShell：

```powershell
git clone https://github.com/ddmanyes/agent-skills-toolkit-zh-tw.git
cd agent-skills-toolkit-zh-tw
.\scripts\sync-local-skills.ps1 -All
```

同步後可以驗證有沒有漏：

```bash
python3 scripts/check-skill-consistency.py --mirror ~/.agents/skills
```

它比對 README 宣稱的 skill 數量與實際樹狀結構，檢查鏡像是否有可用入口，並比對一般技能內容。四個過渡 Radar 副本預設只檢查入口可讀，另列為未比對內容；指向其他來源的 symlink 只檢查有沒有斷。若要唯讀比對過渡副本與本倉庫的內容，可加 `--include-transitional`。多份鏡像用重複的 `--mirror`，或設 `SKILLS_MIRRORS`（以作業系統路徑分隔符分隔）。必要入口缺失或已選內容比對失敗時回傳非零，未比對的項目不會被宣稱為一致。

`--all`／`-All` 會同步到：

- Claude／Claude Code：`~/.claude/skills`
- Codex／通用 Agent：`~/.agents/skills`
- Antigravity：`~/.gemini/config/skills`

同步完成後，請重啟 Agent 應用程式或開啟新 session，讓 Skill discovery 重新載入。

## 🔄 更新本機技能

macOS／Linux 在已 clone 的倉庫中執行：

```bash
git pull --ff-only
./scripts/sync-local-skills.sh --all
```

Windows PowerShell：

```powershell
git pull --ff-only
.\scripts\sync-local-skills.ps1 -All
```

同步目標：

- Claude／Claude Code：`~/.claude/skills`
- Codex／通用 Agent：`~/.agents/skills`
- Antigravity：`~/.gemini/config/skills`

### 只更新指定客戶端

以下指令會同步該客戶端的 Active Skills；不會自動啟用 Disabled Skills 或安裝相容 overlay。先在 repository 根目錄執行 `git pull --ff-only`。

| 客戶端 | Windows PowerShell | macOS／Linux |
| --- | --- | --- |
| Claude Code | `.\scripts\sync-local-skills.ps1 -Claude` | `./scripts/sync-local-skills.sh --claude` |
| Antigravity | `.\scripts\sync-local-skills.ps1 -Antigravity` | `./scripts/sync-local-skills.sh --antigravity` |

只更新一個技能，例如 Claude Code 的 `docx`：

```powershell
.\scripts\sync-local-skills.ps1 -Claude -SkillNames docx
```

```bash
./scripts/sync-local-skills.sh --claude --skill docx
```

安裝到其他位置時，先確認實際目錄與連結目標。若舊路徑連到上述標準目錄，只同步實際目錄一次；不要刪掉連結或再複製一份。

### 驗證兩個客戶端

在 repository 根目錄執行；使用有 Python 3 的環境，macOS／Linux 可把 `python` 換成 `python3`：

```powershell
python scripts/check-skill-consistency.py --mirror "$HOME/.claude/skills"
python scripts/check-skill-consistency.py --mirror "$HOME/.gemini/config/skills"
```

這是對照 repository **全部 Active Skills** 的檢查。如果你刻意只安裝部分技能，未安裝的項目仍會列為缺失，不能把它誤認為本次指定技能更新失敗；單一技能可用檔案比對及 `skill-qa-gate` 檢查。過渡 Radar 內容預設不比對，應在其維護正本驗證。

### 備份與更新範圍

同步採增量覆蓋：只更新已選技能，覆寫前先把原檔存入各環境的 `skills-backups`，並保留其他本機檔案。指定 `--skill NAME`／`-SkillNames NAME` 可縮小範圍。舊技能目錄預設保留；只有明確加 `--archive-legacy`／`-ArchiveLegacy` 才歸檔已選替代技能的舊入口。

### 更新已安裝的 Disabled Skills

例如該客戶端已安裝 `frontend-design`，可明確更新：

```powershell
.\scripts\sync-local-skills.ps1 -Claude -SkillNames frontend-design -IncludeDisabled
```

```bash
./scripts/sync-local-skills.sh --claude --skill frontend-design --include-disabled
```

Antigravity 使用對應的 `-Antigravity`／`--antigravity` 開關。此方式要求每個選定目標已存在同名技能；`-IncludeDisabled`／`--include-disabled` 必須搭配明確名稱。Active 與 Disabled 的更新建議分開執行；若兩區都有同名來源，腳本會拒絕含糊選擇。這些選項不會批次啟用所有 Disabled Skills。

### 過渡 Radar 的來源保護

四個過渡 Radar 名稱由 [transitional-skills.txt](../scripts/transitional-skills.txt) 共用管理。每個同步目標各自判斷：尚無該目錄時安裝本倉庫的相容副本，讓新安裝仍可使用；已有目錄時預設保留並顯示 `SKIP transitional/external`，避免覆蓋另一來源管理的版本。指定名稱但未授權覆寫已安裝的過渡副本時，會在寫入前停止。

只有要明確恢復本倉庫的過渡副本時，才同時指定名稱與覆寫選項，例如只恢復 `content-radar`：

```bash
./scripts/sync-local-skills.sh --agents --skill content-radar --include-transitional
```

```powershell
.\scripts\sync-local-skills.ps1 -Agents -SkillNames content-radar -IncludeTransitional
```

`--include-transitional`／`-IncludeTransitional` 必須搭配明確的技能名稱，不能只對全部技能開啟。上述覆寫仍先備份；未選中的技能及其他來源的排程不會因此變更。
