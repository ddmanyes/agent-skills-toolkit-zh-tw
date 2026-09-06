# Build and bundle with the existing helpers

Read this when a new React artifact needs scaffolding or a single HTML bundle is requested. Reuse these scripts; do not replace them merely because their location differs from the working directory.

## Prerequisites and paths

Resolve this Skill's absolute directory as `SKILL_DIR`. The helpers are [init-artifact.sh](../scripts/init-artifact.sh) and [bundle-artifact.sh](../scripts/bundle-artifact.sh). They require Bash, Node, and pnpm; use the configured runtime. On Windows, invoke a supported Bash environment directly.

Check that pnpm is available before initialization: the current initializer attempts a global npm install if pnpm is missing. Use an already authorized managed setup, or report that prerequisite instead of letting a project request silently install global tools.

For a new project, run the initializer from the authorized parent directory with a new project name. Do not point it at an existing project with unrelated files.

```bash
bash "$SKILL_DIR/scripts/init-artifact.sh" <project-name>
cd <project-name>
```

The helper creates a Vite/React/TypeScript project, adds Tailwind and shadcn/ui components, configures aliases, and extracts its bundled component archive. Its Node-version branches and package selections are implementation details, not a guarantee that every current dependency combination works. Check its exit status and the generated package scripts.

## Development

Edit the generated code using the requested design. Reuse existing components and styles. The bundled archive supplies Radix/shadcn components; read only the component APIs needed for the implementation. Official component reference: [shadcn/ui components](https://ui.shadcn.com/docs/components).

## Single HTML output

Run the bundler from the actual project root containing `package.json` and `index.html`:

```bash
bash "$SKILL_DIR/scripts/bundle-artifact.sh"
```

The script installs Parcel and inlining dependencies, creates `.parcelrc` if absent, builds `index.html`, and writes `bundle.html`. It removes that project's `dist` and `bundle.html` first. Before running it, verify the resolved working directory and preserve any existing output that is not disposable. Keep unrelated files outside the helper's generated-output targets.

Check `bundle.html` exists and contains the intended output. Dependencies requested by runtime code, remote fonts, or external media may still require a network connection; inspect and test the resulting file before claiming it is self-contained or offline-ready.

## Delivery verification

Run required project checks, then render the actual deliverable and exercise each main user flow. Check keyboard operation, readable text, overflow, load errors, and requested reset/export actions. Fix observed defects and rerun the affected checks. Report command failures and environment limitations accurately; preserve a usable source tree when a dependency or browser prevents completion.
