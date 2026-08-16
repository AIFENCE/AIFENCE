# Changelog

All notable changes to AIFENCE are recorded here.

## [0.1.0] — unreleased

The initial unified release: SAGE, AGENTDANCE, and BizIQ merged into one
maintainable codebase that operates as a single governed flow.

### Added
- **Shared foundation** `aifence.core`: one `CoreSettings` (with `AIFENCE_` prefix
  and legacy `SAGE_*`/`AGENTDANCE_*` fallbacks), one declarative `Base`/engine/session,
  and shared errors, middleware, metrics, and telemetry.
- **Composition seam** `aifence.subsystems` + `aifence.app.create_app()`: subsystems
  register themselves; the factory never imports them directly.
- **Guard tier** `aifence.guard` (from AGENTDANCE) mounted at `/guard`, sharing the
  core engine and `Base` so its tables join the one merged schema.
- **Bus tier** `aifence.bus` (from SAGE) mounted at `/bus`, pinned to the shared database.
- **Quality tier** `aifence.quality` (bridge to the vendored BizIQ pack under `quality/`):
  a deterministic quality gate over BizIQ's control registry, exposed at `/v1/quality`.
- **The fence flow** `aifence.flow` at `/v1/fence/submit`: one request runs
  quality → guard → bus with a unified receipt and shared request id.
- Unified `pyproject.toml` (reconciled dependency set, Python 3.12), `Makefile`,
  single Alembic history, Dockerfile, `compose.yaml`, CI workflow, and dual-license set.

### Provenance
Merged from SAGE (`aifence.bus`), AGENTDANCE (`aifence.guard`), and BizIQ
(`aifence.quality`). See [LICENSING.md](LICENSING.md) and [NOTICE](NOTICE).

### Parity & unification (done)
- Ported each source repo's full test suite into `tests/{guard,bus}` (imports/patch
  targets/resource paths rewritten to `aifence.*`); whole suite green.
- Fixed real bugs surfaced by the merge: a Windows directory-fsync crash in
  `guard/artifact_store.py`, a latent `NameError` in guard's `GET /v1/executions`
  endpoint, and stale `sage_plugin` self-references in the bus source.
- Vendored the data the suites need: `evals/`, `scripts/` (rewritten to `aifence.bus`),
  and the bus `spec/`+`tck/` package data.
- Unified per-subsystem OpenAPI into one `/openapi.json` (guard/bus paths re-based under
  their mount, component schemas namespaced).
- Config prefix migration: `AIFENCE_GUARD_*` and `AIFENCE_BUS_*` now bridge to the
  historical `AGENTDANCE_*`/`SAGE_*` names (legacy still honored).
- Brought guard/bus under the unified `ruff` gate (upstream compact-statement style tolerated).

### Known follow-ups
- Bring the vendored guard/bus code under the unified strict `mypy` (currently retains a
  documented override; upstream configs enforced strict typing).
- Wire guard sub-app shutdown cleanup into the composed lifespan.
- The fixed-window rate-limit test can flake on a wall-clock minute boundary (passes on retry).
