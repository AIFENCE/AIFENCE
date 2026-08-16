# AIFENCE

**One governed fence around AI agents.** AIFENCE unifies three tiers — quality
gating, security enforcement, and semantic transport — into a single control
plane with one identity model, one audit chain, and one telemetry pipeline.

| Tier | Package | Origin | Responsibility |
| --- | --- | --- | --- |
| **Quality** | `aifence.quality` | BizIQ | Gate AI-generated artifacts/work against production quality controls. *How good the output is.* |
| **Guard** | `aifence.guard` | AGENTDANCE | Evaluate and enforce every sensitive action: policy, capability tokens, approvals, detectors, evidence. *What agents may do.* |
| **Bus** | `aifence.bus` | SAGE | Carry minimum-sufficient semantic state between agents: durable handoff, content-addressed refs, learned patterns. *How agents talk.* |

## The logical flow

A request moves through the fence as one pipeline:

```text
request ─▶ quality gate ─▶ guard enforcement ─▶ bus handoff ─▶ downstream agent/tool
           (BizIQ)          (policy+capability)   (semantic state)
             │                    │                     │
             └──────────── one identity · one audit chain · one telemetry ───────────┘
```

The quality gate runs as a **guard detector**; the BizIQ runtime is a
guard-governed, bus-carried tool. Merging — not co-locating — is the point.

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
  bus/          semantic transport (SAGE)          [Phase 3]
  guard/        enforcement plane (AGENTDANCE)      [Phase 2]
  quality/      quality-gate bridge to BizIQ        [Phase 4]
quality/        BizIQ source pack + Node builder    [Phase 4]
alembic/        one merged migration history
```

## Status

Built incrementally so the tree is always runnable and tested. **All three tiers
are merged and compose into one app; the fence flow runs end to end.**

- [x] **Phase 1 — Foundation.** Shared `aifence.core`, `create_app()`, subsystem seam, health/metrics, strict tooling.
- [x] **Phase 2 — Guard** (`aifence.guard`) mounted at `/guard`, sharing the core engine + `Base`.
- [x] **Phase 3 — Bus** (`aifence.bus`) mounted at `/bus`, pinned to the shared database.
- [x] **Phase 4 — Quality** (`aifence.quality` + vendored BizIQ) at `/v1/quality`, plus the fence flow at `/v1/fence`.
- [~] **Phase 5 — Unified shell.** CI, Docker/compose, docs, single license — done. Porting each source
  repo's full test suite to reach parity, then retiring the original folders, remains a tracked follow-up.

### The fence flow in action

`POST /v1/fence/submit` runs one request through all three tiers:

```jsonc
// quality passes (score 100) -> guard allows (read, low-risk) -> bus hands off
{ "allowed": true, "final_outcome": "handed_off",
  "stages": { "quality": {"score": 100}, "guard": {"outcome": "allow"}, "bus": {"semantic_units": 3} } }
```

A placeholder-laden artifact stops at `blocked_by_quality`; a destructive high-risk
action passes quality but stops at `blocked_by_guard` — never reaching the bus.

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

Configuration uses the `AIFENCE_` environment prefix; the original `SAGE_*` and
`AGENTDANCE_*` variables are honored as legacy fallbacks during migration. See
[`docs/CONFIGURATION.md`](docs/CONFIGURATION.md) and
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## License

AIFENCE is dual-licensed under **AGPL-3.0-or-later** or a separate
**commercial license**. See [LICENSING.md](LICENSING.md). Inherited from the
merged projects (SAGE, AGENTDANCE, BizIQ), all of which shipped under the same
dual-license structure.
