# Source-Driven Build System

`tooling/build.mjs` turns canonical BizIQ source into portable builds.

## Inputs

The generator reads, at minimum:

- `source/README.md` metadata and routing sections
- `source/CONTROL_MANIFEST.md`
- `source/CONTROL_INDEX.md`
- `source/PROFILE_MATRIX.md`
- `source/TRUTH_BOUNDARIES.md`
- `source/QA_GATES.md`
- Operations 2.0 source modules
- `source/contracts/*.md`
- `source/operations/*.md`
- root and extension control registries
- all Markdown files for heading/stable-ID indexing

Before generation it runs the source pack validator and Operations 2.0 executable regressions.

## Derived values

Nothing in an adapter should manually decide the current Core version or control count. The builder derives:

- Pack version
- Control-plane revision
- domain/capability/control counts
- first/last stable control ID
- artifact contract list
- operations profile list
- Markdown file hashes
- Markdown headings and `<!-- id: ... -->` stable IDs

These values are stamped into generated manifests/runtime configuration.

## Progressive Skill references

The Skill itself remains compact. Its `references/` files are regenerated from selected canonical source sections, so an update to routing/truth/QA/operations rules flows into the portable Skill automatically.

## Standalone Runtime

Inside the repository, Runtime reads `source/` directly. A release archive vendors the same source tree as `core/`, allowing the identical Runtime to operate standalone.

`BIZIQ_SOURCE_DIR` may explicitly point Runtime at another canonical source checkout.

## Build safety

The build fails when:

- canonical metadata is missing;
- source validation/regressions fail;
- control registries cannot be derived;
- required build templates are absent.

`build/BUILD_LOCK.json` and `build/runtime/RUNTIME_LOCK.json` make generated drift detectable.

## Python validation environment

Canonical Python validator dependencies live in `source/requirements.txt`, so the standalone source package, local development, CI, and release jobs share one dependency declaration.

Use:

```bash
npm run setup:python
npm run check:python
```

`tooling/build.mjs` and `tooling/test-core.mjs` preflight these dependencies before invoking source validators. They never silently skip Operations 2.0 validation.

## Cross-platform deterministic text identity

Git can normalize text line endings during commit/checkout. BizIQ therefore treats LF and CRLF as the same source content for integrity purposes.

The builder canonicalizes textual bytes to LF **before hashing** source documents and registries. The standalone Runtime uses the same rule when verifying its vendored Core, and the release packager writes textual release files with canonical LF bytes.

This prevents a Windows-generated source tree from producing different `CORE_LOCK.json`, `BUILD_MANIFEST.json`, `RUNTIME_LOCK.json`, or `BUILD_LOCK.json` values after GitHub checks the repository out on Linux. Binary assets remain byte-exact and are never newline-normalized.

`npm test` includes a portability regression that requires equivalent LF/CRLF fixtures to produce identical canonical hashes. CI keeps `git diff --exit-code -- build` enabled so reproducibility failures are detected rather than hidden.

## Source-driven wiki

The same generator creates `build/wiki/`. It copies canonical Markdown into an on-demand content tree, derives titles/summaries/headings/search metadata, creates curated navigation for high-value BizIQ documentation, and stamps the current Core/Runtime/control-plane metadata into the wiki index.

The wiki shell is dependency-free and supports full-text search, responsive sidebar navigation, a page outline, light/dark themes, copyable commands, and source-provenance links. `npm run test:wiki` validates generated routes/content and JavaScript syntax. `npm run wiki:serve` previews the generated Pages artifact locally.

GitHub Pages deploys `build/wiki/` only after rebuilding from canonical source and confirming that committed generated output has no drift.

## Revision 1.7 bounded retrieval

The build derives `build/capability-shards/` from canonical stable-ID capability sections. These shards are reproducible generated views, never independent policy sources. Runtime plans retrieve phase-scoped stable sections by default and retain `activeModules` only for compatibility/debug inspection.
