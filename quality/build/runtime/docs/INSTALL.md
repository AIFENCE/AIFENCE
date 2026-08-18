# Installation

## Runtime

Requirements: Node.js 20+ and Python for AIFENCE's deterministic validators.

```bash
npm install
node src/cli.js doctor
node src/cli.js verify
```

If installed as an npm binary or linked with `npm link`, use `aifence ...` instead of `node src/cli.js ...`.

## Project installation

```bash
aifence install skill --project .
aifence install claude --project .
aifence install gemini --project .
aifence install vscode --project .
aifence install cursor --project .
aifence install openai --project .
# or
aifence install all --project .
```

Use `--dry-run` to inspect paths. Runtime refuses automated global/home mutation; use each platform's native global installer if desired. Existing JSON config is merged and backed up as `<file>.aifence-backup` before first mutation.
