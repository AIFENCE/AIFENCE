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

### Security
- **The fence flow and quality endpoints served anonymous callers.** They are
  composed onto the application rather than mounted inside the guard sub-app, so
  they did not inherit its router-level authentication: `POST /v1/fence/submit`
  returned `200` and performed a durable write without a credential, while
  `/guard/*` correctly returned `401`. Both routers now require the same API-key
  identity via `aifence.security`, the flow requires the `decisions:write` scope,
  and receipts record the submitting tenant. Health and metrics stay public.
- **Subsystems did not inherit the composed environment.** Setting
  `AIFENCE_ENVIRONMENT=production` left the guard tier in `development`, so none
  of its fail-closed production validation (mTLS, external KMS, disabled docs,
  durable dispatch) ever ran. The application now injects the settings it owns —
  environment, runtime role, log level, database URL, schema creation and docs —
  directly into each tier, so a production fence cannot start an unhardened tier.
- Guard's error hierarchy is rooted in `AIFenceError`, so a guard exception raised
  outside its sub-app renders as the correct status instead of a 500.

### Added
- Initial Alembic revision covering the whole merged schema (66 tables), with a
  test asserting the migrations match the declared models and a single head.
- Python, TypeScript and Go SDKs plus the production Helm chart, baseline policy
  and qualification manifests, with [`docs/SDK.md`](docs/SDK.md) and
  [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

### Fixed
- **Mounted sub-applications never started or cleaned up.** Starlette does not run
  a mounted app's lifespan, so each subsystem's HTTP client, durable workers, and
  object-store/KMS clients leaked on every restart. `create_app` now bridges every
  mounted sub-app lifespan into the composed one via `AsyncExitStack`, and shutdown
  hooks are individually guarded so one failure cannot abort the rest of teardown.
- A Windows directory-fsync crash in `guard/artifact_store.py` (atomic replace is
  preserved; the durability fsync is now best-effort where the OS forbids it).
- A latent `NameError` in guard's `GET /v1/executions` endpoint.
- `EngineConfig` / `TelemetryConfig` protocols declared mutable attributes, so
  frozen settings dataclasses did not actually satisfy them; they are now
  read-only properties.

### Quality
- Full test suite green across `tests/{core,guard,bus,quality,integration}`.
- `ruff` and strict `mypy` both pass over the tree (117 source files, no issues).
- All subsystems share one `ruff` configuration.

### Known follow-ups
- The guard/bus subsystems still carry a documented `mypy` `ignore_errors`
  override; their own upstream configs enforced strict typing.
- The fixed-window rate-limit test can flake on a wall-clock minute boundary
  (passes on retry).
- No initial Alembic revision is committed yet: the merged schema is currently
  built by `auto_create_schema`. Generate one before a production deploy.
