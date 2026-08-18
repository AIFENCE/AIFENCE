# Installation

## Runtime

Requirements: Node.js 20+ and Python for BizIQ's deterministic validators.

```bash
npm install
node src/cli.js doctor
node src/cli.js verify
```

If installed as an npm binary or linked with `npm link`, use `biziq ...` instead of `node src/cli.js ...`.

## Project installation

```bash
biziq install skill --project .
biziq install claude --project .
biziq install gemini --project .
biziq install vscode --project .
biziq install cursor --project .
biziq install openai --project .
# or
biziq install all --project .
```

Use `--dry-run` to inspect paths. Runtime refuses automated global/home mutation; use each platform's native global installer if desired. Existing JSON config is merged and backed up as `<file>.biziq-backup` before first mutation.
