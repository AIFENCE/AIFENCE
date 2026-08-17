# Changelog

All notable changes to AIFENCE are recorded here.

## [0.1.0] — unreleased

The initial release: one maintainable codebase that operates as a single
governed flow across three tiers — quality, enforcement, and semantic transport.

### Added
- **Shared foundation** `aifence.core`: one `CoreSettings` (with the `AIFENCE_`
  prefix and a few legacy fallbacks), one declarative `Base`/engine/session, and
  shared errors, middleware, metrics, and telemetry.
- **Composition seam** `aifence.subsystems` + `aifence.app.create_app()`: subsystems
  register themselves; the factory never imports them directly.
- **Guard tier** `aifence.guard` mounted at `/guard`, sharing the core engine and
  `Base` so its tables join the one merged schema.
- **Bus tier** `aifence.bus` mounted at `/bus`, on the shared database.
- **Quality tier** `aifence.quality`: a deterministic quality gate over the
  quality-control registry, exposed at `/v1/quality`.
- **The fence flow** `aifence.flow` at `/v1/fence/submit`: one request runs
  quality → guard → bus, ending in a real durable, claimable handoff, with a
  unified receipt and shared request id.
- Unified `pyproject.toml` (reconciled dependency set, Python 3.12), `Makefile`,
  single Alembic history, Dockerfile, `compose.yaml`, CI workflow, one unified
  OpenAPI document, and a single dual-license set.

### Quality
- Full test suite green across `tests/{core,guard,bus,quality,integration}`.
- Fixed real bugs surfaced while unifying the code: a Windows directory-fsync
  crash in `guard/artifact_store.py`, and a latent `NameError` in guard's
  `GET /v1/executions` endpoint.
- Brought all subsystems under one `ruff` configuration.

### Known follow-ups
- Bring the guard/bus subsystems under the unified strict `mypy` (currently a
  documented override).
- Wire guard sub-app shutdown cleanup into the composed lifespan.
- The fixed-window rate-limit test can flake on a wall-clock minute boundary
  (passes on retry).
