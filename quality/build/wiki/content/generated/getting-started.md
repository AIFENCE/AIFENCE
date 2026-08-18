# Getting Started

AIFENCE keeps canonical standards in `source/` and generates portable interoperability under `build/`.

## Clone and validate

```bash
npm run setup:python
npm run build
npm test
```

The build validates AIFENCE Core 1.8.8, runs Operations 2.0 executable regressions, regenerates the Skill/Runtime/adapters/wiki, and verifies generated integrity locks.

## Start the Runtime

```bash
cd build/runtime
npm install
node src/cli.js doctor
node src/cli.js verify
```

## Plan a production request

```bash
node src/cli.js plan "Create a premium production website for a local landscaping company"
```

## MCP transports

```bash
node src/cli.js mcp --stdio
node src/cli.js mcp --http --host 127.0.0.1 --port 3888
```

## Project installation

After linking the Runtime CLI with `npm link`, install integrations into a project scope:

```bash
aifence install all --project . --dry-run
aifence install all --project .
```

AIFENCE intentionally does not mutate global/home configuration automatically.
