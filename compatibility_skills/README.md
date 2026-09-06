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
