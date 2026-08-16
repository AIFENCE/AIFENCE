# AIFENCE Configuration

Configuration is read from the environment (and an optional `.env`). Every
variable uses the `AIFENCE_` prefix. To ease migration, the original `SAGE_*`
and `AGENTDANCE_*` names are accepted as **legacy fallbacks** — if the
`AIFENCE_`-prefixed variable is unset, the legacy name is used.

## Core settings (`aifence.core.config.CoreSettings`)

| Variable | Default | Legacy fallback | Purpose |
| --- | --- | --- | --- |
| `AIFENCE_ENVIRONMENT` | `development` | `AGENTDANCE_ENVIRONMENT`, `SAGE_ENV` | `development` / `test` / `staging` / `production`. |
| `AIFENCE_RUNTIME_ROLE` | `control-plane` | `AGENTDANCE_RUNTIME_ROLE` | Worker role (control-plane / dispatcher / lifecycle / anchor / migration / maintenance). |
| `AIFENCE_LOG_LEVEL` | `INFO` | `AGENTDANCE_LOG_LEVEL` | Root log level. |
| `AIFENCE_BIND_HOST` | `0.0.0.0` | `AGENTDANCE_BIND_HOST` | Bind host for `aifence-api`. |
| `AIFENCE_BIND_PORT` | `8080` | `AGENTDANCE_BIND_PORT` | Bind port. |
| `AIFENCE_PUBLIC_BASE_URL` | `http://localhost:8080` | `AGENTDANCE_PUBLIC_BASE_URL` | Advertised server URL in OpenAPI. |
| `AIFENCE_DOCS_ENABLED` | `true` | `AGENTDANCE_DOCS_ENABLED`, `SAGE_DOCS_ENABLED` | Expose `/docs`, `/redoc`, `/openapi.json`. |
| `AIFENCE_ALLOWED_ORIGINS` | *(empty)* | `AGENTDANCE_ALLOWED_ORIGINS` | CORS allowlist (CSV). |
| `AIFENCE_ALLOWED_HOSTS` | *(empty)* | `SAGE_ALLOWED_HOSTS` | Trusted Host allowlist (CSV). |
| `AIFENCE_MAX_REQUEST_BYTES` | `2097152` | `AGENTDANCE_MAX_REQUEST_BYTES` | Global request body ceiling. |
| `AIFENCE_DATABASE_URL` | `sqlite+pysqlite:///./aifence.db` | `AGENTDANCE_DATABASE_URL`, `SAGE_DATABASE_URL` | SQLAlchemy URL (also honors `*_FILE`). |
| `AIFENCE_DB_POOL_SIZE` | `20` | `AGENTDANCE_DB_POOL_SIZE`, `SAGE_DB_POOL_SIZE` | Pool size (non-SQLite). |
| `AIFENCE_DB_MAX_OVERFLOW` | `20` | `AGENTDANCE_DB_MAX_OVERFLOW`, `SAGE_DB_MAX_OVERFLOW` | Pool overflow (non-SQLite). |
| `AIFENCE_AUTO_CREATE_SCHEMA` | `true` | `AGENTDANCE_AUTO_CREATE_SCHEMA`, `SAGE_AUTO_CREATE_SCHEMA` | Dev schema creation; use Alembic in production. |
| `AIFENCE_OTEL_SERVICE_NAME` | `aifence` | `AGENTDANCE_OTEL_SERVICE_NAME` | OpenTelemetry service name. |
| `AIFENCE_OTEL_EXPORTER_OTLP_ENDPOINT` | *(empty)* | `AGENTDANCE_OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP HTTP endpoint; telemetry is off when empty. |
| `AIFENCE_METRICS_PUBLIC` | `false` | `SAGE_METRICS_PUBLIC` | Allow unauthenticated `/metrics`. |

Secrets can be provided indirectly: for any secret-backed variable, setting
`<NAME>_FILE` to a path reads the trimmed file contents.

## Subsystem settings

Each subsystem contributes its own configuration block, documented alongside the
subsystem as it is ported:

- **Guard** (`aifence.guard`) — signing, KMS, artifact storage, audit anchors,
  workers, workload identity. Legacy prefix `AGENTDANCE_`.
- **Bus** (`aifence.bus`) — semantic compiler thresholds, pattern learning,
  references, federation, budgets. Legacy prefix `SAGE_`.
- **Quality** (`aifence.quality`) — BizIQ runtime location and gate policy.
