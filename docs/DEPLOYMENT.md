# AIFENCE Deployment

## Database migrations

Production must run with `AIFENCE_AUTO_CREATE_SCHEMA=false`; Alembic is then the
only thing that creates tables. One migration history builds the whole merged
schema (every tier declares models against the same `Base`):

```bash
alembic upgrade head
```

A test asserts the committed migrations produce exactly the declared models, so
a subsystem cannot add a table without a migration.

## Environment inheritance

The composed application owns the settings the tiers must agree on —
`environment`, `runtime_role`, `log_level`, `database_url`, `auto_create_schema`
and `docs_enabled`. Setting `AIFENCE_ENVIRONMENT=production` therefore places
**every** tier in production, including the guard tier's fail-closed validation.
Tier-specific settings use the `AIFENCE_GUARD_` and `AIFENCE_BUS_` prefixes.

Guard's production validation is strict by design: it refuses to start without
PostgreSQL over `sslmode=verify-full`, mTLS, an external KMS and signing backend,
S3-backed evidence storage, an independent audit-anchor webhook, controlled
egress, and SPIFFE workload identity. A failed start lists every unmet
requirement at once.

## Helm

The chart is [`deploy/helm/aifence`](../deploy/helm/aifence). It deploys the
control plane plus the dispatcher, lifecycle and audit-anchor worker roles, a
migration job, network policy, HPA, PDB and ingress.

```bash
helm upgrade --install aifence deploy/helm/aifence -f my-values.yaml
```

Set the `runtimeRole` per deployment; workers share the control plane's signing
identity and must not auto-create schema.

## Container

```bash
docker compose up --build      # local stack: PostgreSQL + the control plane
```

The image runs as a non-root user and serves `aifence-api` on port 8080.

## Health and observability

| Path | Purpose |
| --- | --- |
| `/health/live` | Liveness probe. |
| `/health/ready` | Readiness probe; lists composed subsystems. |
| `/metrics` | Prometheus scrape target. |

Set `AIFENCE_OTEL_EXPORTER_OTLP_ENDPOINT` to enable OpenTelemetry tracing.
