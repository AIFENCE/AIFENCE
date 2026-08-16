# Repository Layout

## `source/` — canonical

The complete BizIQ control plane. `source/README.md` is authoritative. This tree owns all semantic truth: routing, profiles, stable control IDs, artifact contracts, operations standards, schemas, evals and validators.

Files in `source/` may be consumed directly by an agent even if Runtime is unavailable.

## `tooling/` — build implementation

Contains the deterministic build/release scripts plus templates/runtime implementation used to generate cross-model distributions. Changes here affect packaging/interoperability, not BizIQ policy unless accompanied by a canonical source change.

## `build/` — generated, committed

Generated interoperability output. It is committed so users and agents can consume Skill/MCP/adapters directly from GitHub without running a build first. `build/wiki/` is the generated GitHub Pages documentation site and is rebuilt from the same canonical source/index metadata.

Every build is locked. CI regenerates it and fails if the checked-in build is stale.

## `dist/` — generated, not committed

Binary release ZIPs. GitHub Releases is the distribution surface for these artifacts.

## Authority rule

When there is a conflict:

```text
source/ > generated build/ > platform adapter behavior
```

A conflict is a build defect and should be fixed in tooling/templates, not patched manually in `build/`.
