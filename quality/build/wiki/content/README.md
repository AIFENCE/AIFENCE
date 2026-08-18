# AIFENCE

AIFENCE is a source-driven production quality/control system for AI-generated artifacts and operational work.

**Stable 2.0 status:** Core 1.8.8 passed the sealed Holdout 9 internal engineering qualification (10/10 predeclared gates) and is frozen as the Stable 2.0 architecture. Runtime packaging is 2.0.0. See `source/ARCHITECTURE_FREEZE_STATUS.md`.

## Performance evidence

On the fresh 30-brief **External Value Benchmark 1**, the locked same-environment engineering score was **96.800/100 for AIFENCE 2.0**, **85.867/100 for a strong handcrafted production prompt**, and **65.200/100 for brief-only/default generation**. AIFENCE won **30/30 paired comparisons** against both baselines and achieved **30/30 production acceptance** under the benchmark's family-native engineering checks.

These are controlled engineering benchmark results, not independent third-party preference ratings. See [`docs/PERFORMANCE_EVIDENCE.md`](docs/PERFORMANCE_EVIDENCE.md) for the protocol, category breakdown, Stable 2.0 qualification results, reproducibility hashes, and reporting boundaries.

This repository deliberately separates **canonical AIFENCE source** from **generated interoperability builds**.

```text
source/   canonical AIFENCE standards, controls, schemas, profiles, operations and validators
   │
   ▼
tooling/  deterministic generator + templates
   │
   ▼
build/    generated Skill, MCP Runtime, CLI, UI and platform adapters
   │
   ▼
dist/     release archives generated locally/CI; not committed
```

## Canonical source

`source/README.md` is the authoritative AIFENCE entry point. All policy/control changes belong in `source/`, never directly in `build/`.

The canonical source remains a complete AIFENCE pack, including Markdown standards, stable control registries, JSON schemas, operational profiles, benchmark definitions, and validation tools.

## Prerequisites

- Node.js 20+
- Python 3.12+
- Python validator dependencies declared in `source/requirements.txt`

Install/check the Python validation environment once per clone or virtual environment:

```bash
npm run setup:python
npm run check:python
```

GitHub Actions installs the exact same declared requirements before build/test/release jobs. The builder also performs a dependency preflight and fails with this setup command instead of a nested Python import traceback.

## Generated build

Run:

```bash
npm run build
```

The builder validates the canonical pack, reads its Markdown metadata/headings/stable IDs and registries, derives the current Core revision and architecture counts, generates a searchable source index, then rebuilds:

Source integrity is cross-platform: textual source files are canonicalized to LF for hashing, so Git line-ending normalization does not change Core/build lock identity. Binary files remain byte-exact.

- `build/skill/aifence/` — portable Agent Skill with source-derived progressive references
- `build/runtime/` — CLI + MCP stdio/HTTP server + local/MCP App UI
- `build/adapters/` — Claude, Gemini, VS Code/Copilot, Cursor, OpenAI/Codex and generic adapters
- `build/SOURCE_INDEX.json` — generated Markdown document/heading/stable-ID index
- `build/BUILD_MANIFEST.json` — source-derived version/architecture manifest
- `build/BUILD_LOCK.json` — generated-file integrity lock
- `build/wiki/` — source-driven GitHub Pages wiki generated from canonical Markdown and repository docs

**Do not hand-edit `build/`.** Edit `source/` or the generator/templates, then rebuild.

## Documentation wiki

AIFENCE includes a generated wiki-style GitHub Pages site. The wiki indexes canonical Markdown, keeps a curated navigation layer for the most important project/Core/Runtime/Operations documents, and links every source-backed page directly to GitHub.

```bash
npm run build
npm run test:wiki
npm run wiki:serve
```

Local preview defaults to `http://127.0.0.1:4173`. GitHub Pages deployment is handled by `.github/workflows/pages.yml` from `build/wiki/`. Do not hand-edit the generated wiki.

## Validate

```bash
npm test
```

This runs the canonical AIFENCE pack validation, Operations 2.0 executable regressions, generated-build integrity checks, and Runtime unit/integration tests.

## Ship a release

```bash
npm run ship
```

That performs build → validation → deterministic release packaging. Release files are written to `dist/` and should be uploaded to **GitHub Releases**, not committed to the repository.

Generated packages include source-only, standalone Runtime-with-Core, portable Skill, Claude plugin, Gemini extension, and all-adapters bundles.

## Update workflow

```text
1. Edit source/
2. Run npm run build
3. Review generated diff
4. Run npm test
5. Commit source + generated build together
6. Tag release
7. CI generates dist/ artifacts from the tag
```

If a source change makes a required contract/profile/control structure unresolvable, the builder fails instead of silently emitting stale platform integrations.

See `docs/REPOSITORY_LAYOUT.md`, `docs/BUILD_SYSTEM.md`, and `docs/RELEASES.md`.
