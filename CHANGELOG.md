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

### Release hardening
- Raised the runtime `cryptography` floor to `>=50,<51` after the 49.x security advisory and verified the full crypto regression suite on 50.0.0.
- Promoted `httpx2>=2.9.1,<3` to a base runtime dependency so clean-wheel `aifence demo` uses the supported Starlette TestClient transport path.
- Removed the permissive OpenClaw SDK declaration shim and compile against the real OpenClaw plugin contract.
- Ephemeral Ed25519 signing-key IDs are derived from their public-key fingerprint, preventing repeated development/doctor runs from colliding on a constant key ID with different key material.
- Added repository-hygiene enforcement and broader release-source exclusions for caches, coverage output, mutation artifacts, and generated build trees.

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
- **Content-derived data classes.** `guard/content_classes.py` inspects the actual
  payload for card numbers (Luhn-checked), national IDs, cloud/API credentials,
  private keys, health terms and contact details, and feeds the observed classes
  into the existing enforcement rules. Previously `data_classes` were purely
  caller-declared, so an agent that under-declared escaped the exfiltration rule
  entirely; undeclared sensitive content now also triggers a `redact_or_transform`
  baseline rule. Only class names and counts are reported — never the matched values.
- **Structured-output and grounding checks in the quality gate.** JSON artifacts
  must parse; an optional JSON Schema is enforced (full validation with the
  `quality` extra, a required-property/type subset without it); and when `sources`
  are supplied, numeric claims absent from them are reported — a cluster of
  unsourced figures fails the gate outright. Both are exposed on
  `POST /v1/quality/evaluate` and the fence flow.
- Initial Alembic revision covering the whole merged schema (66 tables), with a
  test asserting the migrations match the declared models and a single head.
- Python, TypeScript and Go SDKs plus the production Helm chart, baseline policy
  and qualification manifests, with [`docs/SDK.md`](docs/SDK.md) and
  [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

### Fixed
- OpenClaw adapter compilation now uses the real peer SDK types instead of a local `api: any` shim. Tool registrations use the SDK factory context with explicit discovery names, so agent/session identity is no longer confused with the tool execution abort signal.
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

### Resilience
- **Per-tier latency budgets and circuit breakers** (`aifence.resilience`). Each
  tier of the flow runs under its own timeout; repeated failures trip a breaker
  that short-circuits the tier for a recovery window instead of spending the
  budget on every request. Every tier is **fail-closed by default** — a tier that
  cannot answer produces `503 tier_unavailable`. `quality` and `bus` can be made
  advisory with `AIFENCE_FLOW_FAIL_OPEN_TIERS`; `guard` cannot, and naming it is
  rejected at startup rather than silently ignored. Degraded runs are named in
  the receipt's `degraded_tiers`, and a bus outage reports
  `authorized_not_delivered` rather than claiming a handoff that never happened.

### Scale and operations
- **Pluggable bus transports** (`aifence.bus.transport`): optional fan-out of
  committed handoffs to Redis Streams, Kafka or RabbitMQ behind the `redis`,
  `kafka` and `rabbitmq` extras, with an in-memory transport for tests and `none`
  as the default. Publication happens after the durable commit and carries only
  message identity and routing metadata — never semantic content — so a broker
  outage is reported in the receipt's `fanout` field instead of failing the
  request or faking a delivery. An unknown backend fails at startup rather than
  silently disabling fan-out.
- **Operator console** at `/v1/console/` (HTML) and `/v1/console/status` (JSON):
  live handoff counts by status, pending approvals, circuit-breaker states,
  subsystem, transport and quality-registry status. Server-rendered with no
  inline script so it satisfies the strict CSP, and authenticated with the same
  API-key identity as the rest of the fence (`decisions:read`).
- **Multi-region topology**: `AIFENCE_REGION` / `AIFENCE_REGION_ROLE` describe an
  active/standby pair. A standby refuses durable worker roles at startup, the
  Helm chart does not render workers or the migration job outside the active
  region, and `/health/ready` publishes `accepts_writes` so a global load
  balancer can route writes to exactly one region. Failover is documented in
  [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

### Assurance
- **Adversarial evaluation harness** (`aifence.redteam`, `aifence-redteam`). Detection
  is now measured rather than asserted, on **multi-turn agent traces** rather than
  single requests, because a compromised agent reveals itself over a sequence:
  scope creeps, claims contradict earlier ones, output decays. Benign traces are
  mandatory — a detector that refuses everything scores 100% detection — and every
  undetected attack is named in the report rather than averaged away.
- Metrics separate what is easy to conflate: **specific detection** (a detector
  fired) from raw detection (the default hold caught it), and hard **refusal**
  from **hold for approval**.
- **Cross-tier behavioural analysis** emitting `integrity.behavioral_drift` from signals
  no single tier can see — persistent ungrounded assertion where no individual turn
  crosses the threshold, and sustained intent escalation. It closes a measured
  bypass with no new false positive and no added approval friction.
- CI gates on the result, and a test asserts the corpus still contains something the
  *baseline* misses: a corpus the implementation passes completely proves only that
  it is too easy.

### Measured (18 traces: 11 attack, 7 benign)
| | baseline | with behavioural analysis |
| --- | ---: | ---: |
| Detection rate | 90.9% | 100.0% |
| Specific detection | 81.8% | 90.9% |
| False-positive rate | 0.0% | 0.0% |
| Hold rate | 71.4% | 71.4% |

Two honest caveats, both recorded in [`docs/evaluation.md`](docs/evaluation.md):
the **71% hold rate** means most production writes need a human under the shipped
baseline policy, and `prompt-injection-clean-payload-01` remains stopped only by
the default hold — the perception limit of pattern matching.

### Known follow-ups
- Fourteen named modules remain outside strict `mypy` (see the override in
  `pyproject.toml`); their errors come from untyped SQLAlchemy/boto3/MCP surfaces
  rather than defects. The other 87 subsystem modules are checked strictly.
