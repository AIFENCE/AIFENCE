# AIFENCE Configuration

Configuration is read from the environment (and an optional `.env`). Every
variable uses the `AIFENCE_` prefix. A small set of legacy variable names is
also accepted as a fallback so pre-existing deployments can migrate without an
immediate rewrite; those fallbacks are intentionally undocumented here to keep
this reference focused on the current names.

## Core settings (`aifence.core.config.CoreSettings`)

| Variable | Default | Purpose |
| --- | --- | --- |
| `AIFENCE_ENVIRONMENT` | `development` | `development` / `test` / `staging` / `production`. |
| `AIFENCE_RUNTIME_ROLE` | `control-plane` | Worker role (control-plane / dispatcher / lifecycle / anchor / migration / maintenance). |
| `AIFENCE_LOG_LEVEL` | `INFO` | Root log level. |
| `AIFENCE_BIND_HOST` | `0.0.0.0` | Bind host for `aifence-api`. |
| `AIFENCE_BIND_PORT` | `8080` | Bind port. |
| `AIFENCE_PUBLIC_BASE_URL` | `http://localhost:8080` | Advertised server URL in OpenAPI. |
| `AIFENCE_DOCS_ENABLED` | `true` | Expose `/docs`, `/redoc`, `/openapi.json`. |
| `AIFENCE_ALLOWED_ORIGINS` | *(empty)* | CORS allowlist (CSV). |
| `AIFENCE_ALLOWED_HOSTS` | *(empty)* | Trusted Host allowlist (CSV). |
| `AIFENCE_MAX_REQUEST_BYTES` | `2097152` | Global request body ceiling. |
| `AIFENCE_DATABASE_URL` | `sqlite+pysqlite:///./aifence.db` | SQLAlchemy URL (also honors `*_FILE`). |
| `AIFENCE_DB_POOL_SIZE` | `20` | Pool size (non-SQLite). |
| `AIFENCE_DB_MAX_OVERFLOW` | `20` | Pool overflow (non-SQLite). |
| `AIFENCE_AUTO_CREATE_SCHEMA` | `true` | Dev schema creation; use Alembic in production. |
| `AIFENCE_OTEL_SERVICE_NAME` | `aifence` | OpenTelemetry service name. |
| `AIFENCE_OTEL_EXPORTER_OTLP_ENDPOINT` | *(empty)* | OTLP HTTP endpoint; telemetry is off when empty. |
| `AIFENCE_METRICS_PUBLIC` | `false` | Allow unauthenticated `/metrics`. |

Secrets can be provided indirectly: for any secret-backed variable, setting
`<NAME>_FILE` to a path reads the trimmed file contents.

## Fence flow resilience

Each tier of the flow runs under its own latency budget and circuit breaker.

| Variable | Default | Purpose |
| --- | --- | --- |
| `AIFENCE_FLOW_QUALITY_TIMEOUT_SECONDS` | `5.0` | Latency budget for the quality gate. |
| `AIFENCE_FLOW_GUARD_TIMEOUT_SECONDS` | `5.0` | Latency budget for enforcement. |
| `AIFENCE_FLOW_BUS_TIMEOUT_SECONDS` | `10.0` | Latency budget for the durable handoff. |
| `AIFENCE_FLOW_FAILURE_THRESHOLD` | `5` | Consecutive failures before a tier's breaker trips open. |
| `AIFENCE_FLOW_RECOVERY_SECONDS` | `30.0` | How long a tripped breaker waits before probing the tier again. |
| `AIFENCE_FLOW_FAIL_OPEN_TIERS` | *(empty)* | Tiers permitted to fail open (CSV). Only `quality` and `bus` are accepted. |

**Every tier is fail-closed by default**: a tier that cannot produce a verdict
within its budget causes the request to be refused with `503 tier_unavailable`.
Listing a tier in `AIFENCE_FLOW_FAIL_OPEN_TIERS` makes it advisory instead — the
flow continues, and the receipt names the tier in `degraded_tiers` so a
degraded run is never mistaken for a clean one.

`guard` **cannot** be made fail-open; naming it is rejected at startup rather
than silently ignored, because an unavailable enforcement tier must never become
an open door. When the bus tier fails open the receipt reports
`authorized_not_delivered` rather than `handed_off`, so a handoff is never
claimed that did not happen.

## Subsystem settings

Each subsystem contributes its own configuration block:

- **Guard** (`aifence.guard`) — signing, KMS, artifact storage, audit anchors,
  workers, workload identity. Accepts the `AIFENCE_GUARD_` prefix.
- **Bus** (`aifence.bus`) — semantic compiler thresholds, pattern learning,
  references, federation, budgets. Accepts the `AIFENCE_BUS_` prefix.
- **Quality** (`aifence.quality`) — quality-control registry location and gate policy.
