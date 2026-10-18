# REA 與 EP 研究 skill：另一台電腦的安裝

這份指南固定 `rea-agents@6.5.0`，不宣稱是最新版。Skill 是操作指引；REA runtime 提供 MCP 工具；Hopper／Ghidra／JADX 等是依目標另選的分析引擎。這三者分開安裝及驗證。

## 1. 更新兩個 skill

在既有工具包 checkout 先 `git status --short`，保存未提交內容，再 `git pull --ff-only`。若歷史分歧，保留原 checkout，另 clone，不使用 force/reset。

macOS／Linux，在工具包根目錄：

```bash
bash scripts/sync-local-skills.sh --agents --skill reverse-engineer-anything --skill ep-tool-investigation
```

Codex 使用 `~/.agents/skills`。若 Claude 的 `~/.claude/skills` 連到 agents，上式已涵蓋兩者。其他實體目錄可另用 `--claude` 或 `--antigravity`；不要對 symlink 執行同步，也不要拆掉原連結。

Windows PowerShell：

```powershell
.\scripts\sync-local-skills.ps1 -Agents -SkillNames reverse-engineer-anything,ep-tool-investigation
```

先核對 PowerShell 腳本的 `Get-Help`／參數；Windows MCP啟動尚未實機驗證。遠端IDE/container有自己的home，須在該環境操作。

若該機已有 `~/.codex/skills/ep-tool-investigation`，比較內容並保留備份，確認新版可讀後將重複舊目錄移到skills以外；不要同名兩份並存或盲目覆蓋客製內容。一般同步不會自動清理Codex額外目錄。

## 2. 固定 runtime，選擇單一客戶端

先確認 `node --version`、`npm --version`。6.5.0官方 engines 為 `^22.19.0 || ^24.11.0 || >=26.0.0`；已驗基準為Node24.18.0。不要為修MCP擅自更新全機Node。

macOS／Linux：

```bash
REA_RUNTIME="$HOME/LocalWork/Tools/rea-6.5.0"
mkdir -p "$REA_RUNTIME"
npm install --prefix "$REA_RUNTIME" --ignore-scripts --save-exact rea-agents@6.5.0
REA_CLI="$REA_RUNTIME/node_modules/rea-agents/scripts/rea.mjs"
node "$REA_CLI" setup --client codex --dry-run --json
```

Windows PowerShell對應：

```powershell
$ReaRuntime = Join-Path $env:USERPROFILE 'LocalWork\Tools\rea-6.5.0'
New-Item -ItemType Directory -Force $ReaRuntime | Out-Null
npm install --prefix $ReaRuntime --ignore-scripts --save-exact rea-agents@6.5.0
$ReaCli = Join-Path $ReaRuntime 'node_modules\rea-agents\scripts\rea.mjs'
node $ReaCli setup --client codex --dry-run --json
```

保留runtime的package-lock；不要將node_modules、個人設定或金鑰提交GitHub。首次npm下載會用網路。這裡停用lifecycle scripts；某些額外provider可能仍缺依賴，僅在具體任務需要且取得授權後處理。

先看dry-run的客戶端、設定位置、備份與skill覆蓋範圍。確認符合本次安裝授權後，以同一client執行：

```bash
node "$REA_CLI" setup --client codex --yes --json
node "$REA_CLI" doctor --client codex --json
```

PowerShell使用 `node $ReaCli ...`。Claude Code client ID是 `claude_code`，Antigravity是 `antigravity`；只替換要用的client，不用 `--all-detected`。官方setup通常會同步其內附REA skill，與此工具包原版指引相同；不要加入 `--install-hopper`，除非另有明確需求及授權。setup不會自動連接EP、SB或lcdda。

## 3. GUI PATH與握手驗證

終端能跑Node不代表桌面客戶端也能找到。若MCP報 `node not found`，在該機查 `command -v node`（Windows用 `Get-Command node`），確認REA註冊使用該機的launcher；在**REA自己的env.PATH**補該Node所在資料夾及原PATH，保留其他環境設定。不得直接貼另一台的 `/Users/...` 路徑或覆蓋整份config。nvm切換／刪除Node版本後須重驗。

Codex可用Python3.11+執行以下讀取現有註冊的檢查；它會啟動REA並只呼叫initialize/tools-list，不分析應用、不修改config，也不輸出金鑰或server stderr：

```bash
python3 scripts/rea/check_codex_mcp.py
```

Windows可用 `py -3.11 scripts/rea/check_codex_mcp.py`。若使用非預設profile：`--config /實際路徑/config.toml`。先檢查該檔的REA command是可信的本機安裝，因為驗證會執行該command；若它是npx，可能下載套件。其他客戶端用其實際MCP工具列表確認，這個checker只讀Codex TOML。

判讀：

- `PASS`和非零tool_count表示stdio握手／完整工具列表成功，**不是目前聊天已載入**。
- 重啟客戶端或開新session，確認REA工具實際出現，再呼叫 `$reverse-engineer-anything`。
- doctor的registration aligned與provider healthy分開看。缺原生引擎不等於MCP握手失敗，也不阻擋不依賴該引擎的JS靜態工作。
- 工具缺席先查啟動錯誤與PATH；不要反覆setup或自動安裝所有引擎。
- EP專題使用 `$ep-tool-investigation`；EP／中央SB／lcdda連線須各自具備。沒有這些連線時只能做可取得的研究，SB更新標pending。

## 4. 使用與回復

例：`使用 $ep-tool-investigation 研究指定分析工具如何補強EP，先核對原始碼與既有部署，再提出固定資料驗收契約。`

只有發行檔、未公開格式或來源無法解答的行為問題才轉REA。一般開源碼研究不必呼叫REA。分析結果可能進入agent模型上下文；不得把秘密或未授權私人資料交給工具輸出。

遇到失敗保留diagnostic及版本，不把安裝成功當分析成功。回復時先比對後續使用者改動，只回復此次REA設定／skill，不整份覆蓋舊config；備份可能含秘密，留本機且不進SB／Git。無需為停用MCP刪除分析證據或清除所有快取。

## 驗證範圍

發布驗收記錄見 [REA發布驗證](rea-release-2026-10-18.md)。本機macOS的既有REA6.5.0握手、隔離skill同步及checker失敗分支可驗；另一台實際安裝、Windows、各provider與跨模型效果，須在目標機完成後才標成功。
