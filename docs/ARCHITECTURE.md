---
title: Architecture
summary: How three previously separate systems compose into one application.
infobox:
  Factory: aifence.app.create_app()
  Seam: register(app, ctx)
  Schema: one shared declarative Base
  Guard/Bus: mounted sub-applications
  Quality/Flow: native routers
---

AIFENCE is one FastAPI application built by one factory. It owns the shared
foundation and then invites each installed subsystem to mount itself.

```text
        ┌───────────────── aifence.app.create_app() ──────────────────┐
        │ middleware · error envelope · health · metrics · OpenAPI    │
        │ lifespan (bridged) · circuit breakers · identity            │
        └──────┬──────────────────┬───────────────────┬───────────────┘
               │ register()       │ register()        │ register()
        ┌──────▼─────┐     ┌──────▼──────┐     ┌──────▼──────┐
        │  quality   │────▶│    guard    │────▶│     bus     │
        │  (gate)    │     │ enforcement │     │  transport  │
        └────────────┘     └─────────────┘     └─────────────┘
               └──────────────── aifence.core ───────────────┘
          config · db (one Base/engine) · errors · middleware
                   metrics · telemetry · env helpers
```

## Why a shared core rather than a merged monolith

The three source projects overlapped heavily on infrastructure — FastAPI,
SQLAlchemy, Alembic, pydantic, cryptography, Prometheus — but their *domain*
configuration and models are large and genuinely distinct. The guard tier alone
carries roughly 150 settings for signing, KMS, artifact storage and workers.

`aifence.core` therefore promotes only the cross-cutting infrastructure that all
three genuinely share, while each subsystem keeps its own settings, models and
routers. That split is what makes one codebase maintainable instead of
collapsing every knob into a single god-object.

## The composition seam

`aifence.subsystems` defines a `register(app, ctx)` protocol and discovers
installed subsystems in flow order (quality → guard → bus). `create_app` never
imports a subsystem directly, which means:

- subsystems can be added or ported one at a time without touching the factory;
- the application runs with any subset installed;
- each subsystem mounts its own router, wires workers into the shared lifespan,
  and reads its own configuration.

`SubsystemContext` hands each subsystem the shared settings, engine and session
factory, so nothing builds a second connection pool.

## Mounted sub-applications

Guard and bus are mounted as FastAPI **sub-applications** at `/guard` and `/bus`
rather than having their routes spliced into the root app. They keep their
proven internals and their own router-level authentication, while sharing the
core engine, declarative `Base`, and metrics registry.

Two consequences follow, both handled explicitly:

**Lifespans must be bridged.** Starlette does not run a mounted application's
lifespan. Without intervention, each subsystem's HTTP clients, durable workers
and object-store clients would never start or be cleaned up. `create_app`
enters every mounted lifespan through an `AsyncExitStack`, so the whole fence
starts and shuts down as one unit.

**OpenAPI must be merged.** Sub-app paths would otherwise live only in
`/guard/openapi.json` and `/bus/openapi.json`. The factory folds them into the
single root document, re-basing paths under their mount and namespacing
component schemas to avoid collisions.

## Native routers

The quality tier, the [fence flow](fence-flow.md) and the
[operator console](operations.md#operator-console) are composed directly onto
the application rather than mounted. They therefore do **not** inherit guard's
router-level authentication, and `aifence.security` binds them to the same
identity explicitly. See [Security](security.md#one-identity-model).

## One database, one migration history

Every subsystem declares its models against `aifence.core.db.Base`, so a single
Alembic history builds the entire 66-table schema and one connection pool serves
every tier. A test asserts the committed migrations match the declared models,
so a subsystem cannot add a table without a migration.

PostgreSQL row-level security uses the `aifence` `set_config` namespace.

## Settings ownership

The composed application owns the settings the tiers must agree on —
environment, runtime role, log level, database URL, schema creation and docs —
and injects them into each subsystem. Without this, setting
`AIFENCE_ENVIRONMENT=production` would leave a subsystem on its own default and
silently skip its fail-closed validation. Tier-specific settings remain under
the `AIFENCE_GUARD_` and `AIFENCE_BUS_` prefixes.

## Data flow

1. **Quality** scores the artifact against the control registry and emits a
   quality decision.
2. **Guard** compiles the mandatory and tenant policy into an enforcement plan
   and issues an exact-action capability.
3. **Bus** durably persists the vetted payload as a claimable handoff, then
   optionally fans out to a broker.

Every step shares the request id, audit chain and telemetry established by the
core. See [Fence flow](fence-flow.md).
