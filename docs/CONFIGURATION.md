---
title: Configuration
summary: Every AIFENCE_ environment variable and what it controls.
infobox:
  Prefix: AIFENCE_
  Subsystems: AIFENCE_GUARD_ · AIFENCE_BUS_
  Secrets: "&lt;NAME&gt;_FILE supported"
  Validation: fail closed at startup
---

Configuration is read from the environment (and an optional `.env`). Every
variable uses the `AIFENCE_` prefix. A small set of legacy variable names is
also accepted as a fallback so pre-existing deployments migrate without an
immediate rewrite; those fallbacks are intentionally undocumented here to keep
this reference focused on the current names.

Invalid configuration is rejected **at startup**, and production validation
reports every unmet requirement at once rather than failing one at a time.

## Core

| Variable | Default | Purpose |
| --- | --- | --- |
| `AIFENCE_ENVIRONMENT` | `development` | `development` / `test` / `staging` / `production`. |
| `AIFENCE_RUNTIME_ROLE` | `control-plane` | `control-plane`, `dispatcher`, `lifecycle`, `anchor`, `migration`, `maintenance`. |
| `AIFENCE_LOG_LEVEL` | `INFO` | Root log level. |
| `AIFENCE_BIND_HOST` | `0.0.0.0` | Bind host for `aifence-api`. |
| `AIFENCE_BIND_PORT` | `8080` | Bind port. |
| `AIFENCE_PUBLIC_BASE_URL` | `http://localhost:8080` | Advertised server URL in OpenAPI. |
| `AIFENCE_DOCS_ENABLED` | `true` | Expose `/docs`, `/redoc`, `/openapi.json`. |
| `AIFENCE_ALLOWED_ORIGINS` | *(empty)* | CORS allowlist (CSV). |
| `AIFENCE_ALLOWED_HOSTS` | *(empty)* | Trusted Host allowlist (CSV). |
| `AIFENCE_MAX_REQUEST_BYTES` | `2097152` | Global request body ceiling. |

## Persistence

| Variable | Default | Purpose |
| --- | --- | --- |
| `AIFENCE_DATABASE_URL` | `sqlite+pysqlite:///./aifence.db` | SQLAlchemy URL. |
| `AIFENCE_DB_POOL_SIZE` | `20` | Pool size (non-SQLite). |
| `AIFENCE_DB_MAX_OVERFLOW` | `20` | Pool overflow (non-SQLite). |
| `AIFENCE_AUTO_CREATE_SCHEMA` | `true` | Development schema creation; use Alembic in production. |

## Observability

| Variable | Default | Purpose |
| --- | --- | --- |
| `AIFENCE_OTEL_SERVICE_NAME` | `aifence` | OpenTelemetry service name. |
| `AIFENCE_OTEL_EXPORTER_OTLP_ENDPOINT` | *(empty)* | OTLP HTTP endpoint; tracing is off when empty. |
| `AIFENCE_METRICS_PUBLIC` | `false` | Allow unauthenticated `/metrics`. |

## Fence flow resilience

Each tier runs under its own latency budget and circuit breaker.

| Variable | Default | Purpose |
| --- | --- | --- |
| `AIFENCE_FLOW_QUALITY_TIMEOUT_SECONDS` | `5.0` | Budget for the quality gate. |
| `AIFENCE_FLOW_GUARD_TIMEOUT_SECONDS` | `5.0` | Budget for enforcement. |
| `AIFENCE_FLOW_BUS_TIMEOUT_SECONDS` | `10.0` | Budget for the durable handoff. |
| `AIFENCE_FLOW_FAILURE_THRESHOLD` | `5` | Consecutive failures before the breaker trips. |
| `AIFENCE_FLOW_RECOVERY_SECONDS` | `30.0` | How long a tripped breaker waits before probing again. |
| `AIFENCE_FLOW_FAIL_OPEN_TIERS` | *(empty)* | Tiers permitted to fail open (CSV). Only `quality` and `bus`. |

**Every tier is fail-closed by default**: a tier that cannot produce a verdict
within its budget causes `503 tier_unavailable`. Listing a tier in
`AIFENCE_FLOW_FAIL_OPEN_TIERS` makes it advisory instead, and the receipt names
it in `degraded_tiers` so a degraded run is never mistaken for a clean one.

`guard` **cannot** be made fail-open. Naming it is rejected at startup rather
than silently ignored, because an unavailable enforcement tier must never become
an open door. When the bus tier fails open the receipt reports
`authorized_not_delivered` rather than `handed_off`.

## Multi-region and transport

| Variable | Default | Purpose |
| --- | --- | --- |
| `AIFENCE_REGION` | *(empty)* | Region identifier, surfaced in readiness and the console. |
| `AIFENCE_REGION_ROLE` | `active` | `active` owns writes and durable workers; `standby` serves reads. |
| `AIFENCE_BUS_TRANSPORT` | `none` | Broker fan-out: `none`, `memory`, `redis`, `kafka`, `rabbitmq`. |
| `AIFENCE_BUS_TRANSPORT_URL` | *(empty)* | Broker URL; required for broker backends. |
| `AIFENCE_BUS_TRANSPORT_TOPIC` | `aifence.handoffs` | Stream, topic or exchange name. |

A standby region refuses durable worker roles at startup, and `/health/ready`
reports `accepts_writes: false` so a load balancer routes writes correctly.
See [Deployment](deployment.md#multi-region-topology).

## Secrets

For any secret-backed variable, setting `<NAME>_FILE` to a path reads the
trimmed file contents instead. This is how the Helm chart mounts the database
URL, signing tokens and API-key peppers without placing them in the pod spec.

## Subsystem settings

Each tier contributes its own configuration block:

- **[Guard](guard.md)** — signing, KMS, artifact storage, audit anchors, worker
  tuning, workload identity. Prefix `AIFENCE_GUARD_`.
- **[Bus](bus.md)** — semantic compiler thresholds, pattern learning,
  references, federation, budgets. Prefix `AIFENCE_BUS_`.
- **[Quality](quality.md)** — control registry location and gate policy.

The composed application injects the settings it owns — environment, runtime
role, log level, database URL, schema creation and docs — into every subsystem,
so a production fence cannot start an unhardened tier.

## Operator console

`GET /v1/console/` renders a server-side dashboard;
`GET /v1/console/status` returns the same data as JSON. Both require an API key
with `decisions:read`. See [Operations](operations.md#operator-console).
