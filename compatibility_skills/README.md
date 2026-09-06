# Existing-install compatibility overlays

These 28 directories maintain already-used local Skill names. They are separate from the toolkit's active Skill inventory. The 25 `source-command-*` entries are explicitly manual commands; the other three retain their original workflow role.

Apply an approved overlay by merging only its maintained files into `<existing-skill-root>/<name>/`. Back up every destination file before replacement. Preserve unlisted files, existing environments and user data; never replace the whole Skill directory. Deployment is a separate main-workflow step, not performed by these files.

The canonical `skills/` packages and the compatibility names must be siblings in the installed root. Thus `source-command-docx-ooxml/../docx/ooxml.md` resolves to the maintained document reference. Do not rewrite these links to the repository's source layout, copy full canonical manuals into aliases, or run relative script commands from an alias directory.

`notebooklm` is a **requires existing install** documentation overlay. Its original runtime files are deliberately absent here; `manifest.json` lists the required files to check before deployment/use. The overlay does not install a notebook, browser, credentials, cookies, sources, or Python environment. Preserve the existing `.gitignore` and `data/` directory without committing either user data or secrets.

`image-to-prompt` includes the original local script with targeted fixes and network-free tests. Its localhost endpoint is preserved; no model files, model launcher, images, or generated prompts are packaged. `session-snapshot` is a documentation workflow and does not itself execute Git commands during installation.

Read [AUDIT.md](AUDIT.md) for all name comparisons, retained differences, verification evidence, and untested limitations. [manifest.json](manifest.json) records source hashes and installation dependencies.

## Verify before deployment

Use a Python environment containing PyYAML. From the repository root:

```bash
python compatibility_skills/tests/validate_overlays.py
python compatibility_skills/image-to-prompt/tests/test_generate_prompt.py
```

To check the existing NotebookLM files without invoking them, add `--existing-root <actual-skill-root>` to validate_overlays.py. The validator assembles a temporary shared install root, checks references and invocation policies, and removes only that temporary fixture. A successful static check does not establish live model, browser, or cross-model performance.

## 相容入口合併範例

以已安裝的 `source-command-docx-ooxml` 為例：先更新同一客戶端的 `docx` 正本，再依本頁上方的安裝規則合併。以下以 Claude Code 的 `~/.claude/skills` 為安裝根；Antigravity 改用 `~/.gemini/config/skills`。

| repository 來源 | 既有安裝的目標 |
| --- | --- |
| `compatibility_skills/source-command-docx-ooxml/SKILL.md` | `<安裝根>/source-command-docx-ooxml/SKILL.md` |
| `compatibility_skills/source-command-docx-ooxml/agents/openai.yaml` | `<安裝根>/source-command-docx-ooxml/agents/openai.yaml` |

1. 確認相容入口已存在，並檢查 [manifest.json](manifest.json) 的相依。
2. 將會覆寫的原檔備份到 Skill discovery 目錄外，保留原相對路徑；不存在的新檔也記錄於部署清單，便於回復。
3. 只合併表中受管檔案，保留其他檔案、環境與資料。正本與相容入口必須是安裝根下的同層目錄，才能解析 `../docx`。
4. 在有 PyYAML 的 Python 環境檢查實際安裝入口：

```powershell
python skills/skill-qa-gate/scripts/lint_skill.py "$HOME/.claude/skills/source-command-docx-ooxml"
```

NotebookLM 等 overlay 並非完整安裝包，另需核對 manifest 所列的既有 runtime 檔案。不要用整目錄替換、`--delete` 或清空目錄的方式套用。完成後重啟客戶端或開新 session。

本機更新數量取決於各客戶端已安裝的範圍，不等於 repository 的 Active Skills 總數；個別部署紀錄應留在本機。
