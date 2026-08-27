# Active Skills 改善稽核（2026-08-27）

## 範圍與結果

- 範圍：`skills/` 下 38 個 active Skills。
- Validator：`skills/skill-qa-gate/scripts/lint_skill.py`。
- 修正前：8 PASS、29 WARN、1 FAIL。
- 修正後：8 PASS、30 WARN、0 FAIL。
- WARN 分布：15 個 trigger description、21 個跨產品 frontmatter、51 個英文長句、23 個缺少 Codex UI metadata。

WARN 數量是規則命中數，不等於 110 個獨立缺陷。同一 Skill 可以同時命中多類警告。

## 本次已修正

### P0：結構阻斷

- 將目錄 `skills/code-review` 更名為 `skills/sp-code-review`，使目錄與 frontmatter `name` 一致。
- 更新 `ask-matt`、`tdd`、README 與 acknowledgement 中的路由名稱。
- 新增 `sp-code-review/agents/openai.yaml`，並把 description 改成可觸發的使用情境。
- 同步工具會在新版存在後，把本機舊 `code-review` 目錄移到可復原的 `skills-archive`。

### P1：倉庫衛生

- 將 323 個已追蹤的 macOS `._*` 與 `.Rhistory` 中繼檔移出 Git index。
- `.gitignore` 已涵蓋 `.DS_Store`、`._*`、`.Rhistory`、`__pycache__/` 與 Python bytecode。
- 將 `ralph-loop` 的「如有必要」改成可驗證條件：只有產生尚未記錄的可重用慣例時才更新 Agent 指引。

## 建議後續改善

### P1：Codex 顯示與觸發準確度

下列 23 個 active Skills 缺少 `agents/openai.yaml`：

`autonomous-pilot`、`checkpoint-manager`、`code-simplifier`、`docx`、`domain-modeling`、`improve-architecture`、`lecture-converter`、`mcp-builder`、`pdf`、`planning-with-files`、`pptx`、`project-architect`、`ralph-loop`、`skill-architect`、`skill-creator`、`sp-brainstorming`、`sp-executing-plans`、`sp-fix-test`、`sp-git-worktrees`、`sp-learn-codebase`、`sp-subagent-dev`、`sp-writing-plans`、`xlsx`。

建議分批補上 UI metadata，每批都測試 `default_prompt` 是否明確包含 `$skill-name`。其中 15 個 Skill 的 description 也應加入具體觸發條件；description 修改會影響自動路由，需用真實 prompts 做前向測試，不應一次機械改寫。

### P2：跨產品 frontmatter

21 個警告來自 `allowed-tools`、`disable-model-invocation`、`argument-hint`、`license` 等 Claude／產品專用欄位。這些是可攜性警告，不是執行錯誤。建議保留 Claude 必要欄位，並用 `agents/openai.yaml` 表達 Codex 介面與 implicit invocation policy，不要為消除警告而刪除既有安全邊界。

### P2：長句與上游同步

51 個英文長句集中在 `domain-modeling`、`pptx`、`tdd`、`teach`、`to-questionnaire`、`wait-what`、`writing-for-agents`。建議只在確認 actors、modality、conditions、numbers 與 failure behavior 完整保留後拆句。Matt Pocock 上游 Skills 應保留來源追蹤，避免本地重寫阻礙後續更新。

### P3：停用 Skills

本次沒有把 `disabled_skills/` 納入 active 品質結論。任何停用 Skill 重新啟用前，應先清除 AppleDouble 中繼檔、補 UI metadata、執行 deterministic validator 與專屬測試。

## 建議執行順序

1. 先補高頻 Skill 的 `agents/openai.yaml`：`sp-code-review` 已完成；下一批處理 `sp-brainstorming`、`sp-writing-plans` 與 `sp-fix-test`。
2. 再以真實 prompts 改善 15 個 description，量測漏觸發與誤觸發。
3. 最後處理英文長句與 disabled Skills；這兩項不阻擋目前發布。
