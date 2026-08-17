# AIFENCE

**One governed fence around AI agents.** AIFENCE unifies three tiers — quality
gating, security enforcement, and semantic transport — into a single control
plane with one identity model, one audit chain, and one telemetry pipeline.

| Tier | Package | Responsibility |
| --- | --- | --- |
| **Quality** | `aifence.quality` | Gate AI-generated artifacts/work against production quality controls. *How good the output is.* |
| **Guard** | `aifence.guard` | Evaluate and enforce every sensitive action: policy, capability tokens, approvals, detectors, evidence. *What agents may do.* |
| **Bus** | `aifence.bus` | Carry minimum-sufficient semantic state between agents: durable handoff, content-addressed refs, learned patterns. *How agents talk.* |

## The logical flow

A request moves through the fence as one pipeline:

```text
request ─▶ quality gate ─▶ guard enforcement ─▶ bus handoff ─▶ downstream agent/tool
           (quality)         (policy+capability)   (semantic state)
             │                    │                     │
             └──────────── one identity · one audit chain · one telemetry ───────────┘
```

The quality gate scores the artifact; guard compiles and enforces the policy
decision; the bus durably delivers the vetted payload to the receiver.
Merging — not co-locating — is the point.

## Architecture

The composed application is built by one factory, `aifence.app.create_app()`.
It owns the shared foundation (`aifence.core`: config, database, errors,
middleware, metrics, telemetry) and then invites each installed subsystem to
mount itself through the `register(app, ctx)` hook in `aifence.subsystems`.
There is no import-time database work and no module-level `app`, so the
application is safe to build repeatedly.

```text
src/aifence/
  core/         shared config, db, errors, middleware, metrics, telemetry
  app.py        create_app(): composes subsystems + shared surface
  main.py       ASGI entrypoint (aifence-api)
  subsystems.py registration protocol + discovery (the merge seam)
  bus/          semantic transport subsystem (sub-app at /bus)
  guard/        enforcement plane subsystem (sub-app at /guard)
  quality/      quality-gate bridge (router at /v1/quality)
  flow.py       the fence flow (/v1/fence): quality → guard → bus
  security.py   shared API-key identity for the composed routers
quality/        quality-control source pack + Node builder
sdks/           Python, TypeScript and Go clients + framework hooks
deploy/helm/    production Helm chart (control plane + worker roles)
alembic/        one merged migration history
```

## Status

**All three tiers are merged and compose into one application; the fence flow
runs end to end.** The whole test suite is green and the tree is always runnable.

- **Quality** (`aifence.quality`) — quality-gate router at `/v1/quality`.
- **Guard** (`aifence.guard`) — enforcement plane mounted at `/guard`, sharing the core engine + `Base`.
- **Bus** (`aifence.bus`) — semantic transport mounted at `/bus`, on the shared database.
- **Fence flow** (`aifence.flow`) — `/v1/fence`, wiring the three tiers into one governed pipeline.
- **Unified shell** — one `pyproject`, `Makefile`, Alembic history, Docker/compose, CI, OpenAPI, and license.

### The fence flow in action

`POST /v1/fence/submit` runs one request through all three tiers:

```jsonc
// quality passes -> guard allows (read, low-risk) -> bus durably delivers a claimable handoff
{ "allowed": true, "final_outcome": "handed_off",
  "stages": { "quality": {"score": 100}, "guard": {"outcome": "allow"},
              "bus": {"delivered": true, "message_id": "M…"} } }
```

A placeholder-laden artifact stops at `blocked_by_quality`; a destructive high-risk
action passes quality but stops at `blocked_by_guard` — never reaching the bus. On a
full pass-through, the delivered handoff is a real durable message the receiver can claim.

## Quick start

```bash
python -m venv .venv
. .venv/Scripts/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
aifence-api                     # serves on 0.0.0.0:8080
```

Then:

```bash
curl http://127.0.0.1:8080/health/ready
```

## Development

```bash
make verify        # ruff + mypy(strict) + pytest
make test
```

Configuration uses the `AIFENCE_` environment prefix (a small set of legacy
variable names is also honored for backward compatibility). See
[`docs/CONFIGURATION.md`](docs/CONFIGURATION.md) and
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## License

AIFENCE is dual-licensed under **AGPL-3.0-or-later** or a separate
**commercial license**. See [LICENSING.md](LICENSING.md).
