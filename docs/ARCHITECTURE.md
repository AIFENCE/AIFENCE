# AIFENCE Architecture

AIFENCE merges three previously separate services into **one FastAPI
application** with a shared foundation and pluggable subsystems.

## Layers

```text
        ┌───────────────────────── aifence.app.create_app() ─────────────────────────┐
        │  shared middleware · error envelope · health · metrics · OpenAPI · lifespan │
        └───────────────┬───────────────────┬───────────────────────┬────────────────┘
                        │ register()        │ register()            │ register()
                 ┌──────▼──────┐      ┌──────▼──────┐         ┌──────▼──────┐
                 │  quality    │      │   guard     │         │    bus      │
                 │  (gate)     │─────▶│ enforcement │────────▶│  transport  │
                 └─────────────┘      └─────────────┘         └─────────────┘
                        └──────────── aifence.core ────────────┘
                 config · db (one Base/engine) · errors · middleware · metrics · telemetry
```

## Why a shared core, not a merged monolith

The three projects overlapped heavily on infrastructure (FastAPI, SQLAlchemy,
Alembic, pydantic, cryptography, Prometheus) but their *domain* configuration
and models are large and distinct. `aifence.core` promotes only the
cross-cutting infrastructure — the pieces all three genuinely share — while each
subsystem keeps its own settings, models, and routers. This is what keeps the
merged codebase maintainable: one place for shared concerns, clear seams for
domain code.

## The composition seam

`aifence.subsystems` defines a `register(app, ctx)` protocol and discovers
installed subsystems in flow order (`quality` → `guard` → `bus`). `create_app`
never imports a subsystem directly, so:

- subsystems can be ported one at a time without touching the factory;
- the app runs with any subset installed;
- each subsystem mounts its router, wires workers into the shared lifespan, and
  reads its own configuration.

## One database, one migration history

All subsystem models declare against `aifence.core.db.Base`. A single Alembic
history (`alembic/`) therefore builds the entire schema, and one connection pool
serves every tier. PostgreSQL row-level-security context uses the `aifence`
`set_config` namespace.

## Data flow

1. **Quality gate** (`aifence.quality`) scores the requested artifact/work
   against the quality-control registry and emits a quality decision.
2. **Guard** (`aifence.guard`) treats that decision as one detector input,
   compiles the mandatory + tenant policy into an enforcement plan, and issues
   an exact-action capability (allow / constrain / transform / approve / deny /
   quarantine).
3. **Bus** (`aifence.bus`) carries the resulting minimum-sufficient semantic
   state to the downstream agent or tool via durable handoff.

Every step shares the request id, audit chain, and telemetry established by
`aifence.core`.
