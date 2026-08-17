---
title: Deployment
summary: Migrations, containers, Helm, multi-region topology and broker transports.
infobox:
  Chart: deploy/helm/aifence
  Migrations: alembic upgrade head
  Topology: active / standby
  Image: non-root, port 8080
---

## Database migrations

Production must run with `AIFENCE_AUTO_CREATE_SCHEMA=false`; Alembic is then the
only thing that creates tables. One migration history builds the whole merged
schema, because every tier declares models against the same `Base`:

```bash
alembic upgrade head
```

A test asserts the committed migrations produce exactly the declared models and
that the history has a single head, so a subsystem cannot add a table without a
migration and two branches cannot diverge unnoticed.

## Container

```bash
docker compose up --build      # PostgreSQL + the control plane
```

The image installs the `postgres`, `otel` and `s3` extras, runs as a non-root
user, and serves `aifence-api` on port 8080.

## Helm

The chart is [`deploy/helm/aifence`](https://github.com/AIFENCE/AIFENCE/tree/main/deploy/helm/aifence).
It deploys the control plane plus the dispatcher, lifecycle and audit-anchor
worker roles, a migration job, network policy, HPA, PDB and ingress.

```bash
helm upgrade --install aifence deploy/helm/aifence -f my-values.yaml
```

Workers share the control plane's signing identity and must not auto-create
schema. Secrets are mounted as files and consumed through the `<NAME>_FILE`
convention rather than being placed in the pod spec.

## Environment inheritance

The composed application owns the settings the tiers must agree on —
`environment`, `runtime_role`, `log_level`, `database_url`, `auto_create_schema`
and `docs_enabled` — and injects them into each subsystem. Setting
`AIFENCE_ENVIRONMENT=production` therefore places **every** tier in production,
including the guard tier's fail-closed validation.

Guard's production validation is strict by design. It refuses to start without
PostgreSQL over `sslmode=verify-full`, mTLS, an external KMS and non-exportable
signing backend, S3-backed evidence storage, an independent audit-anchor
webhook, controlled egress, and SPIFFE workload identity. A failed start lists
every unmet requirement at once, so hardening is one pass rather than a dozen.

## Multi-region topology

Exactly one region is **active**: it owns the writable database and runs the
durable workers. Every other region is a **standby** — it serves the control
plane from a read replica and stays warm for promotion.

```yaml
# active region
region: { name: eu-west-1, role: active }
# standby region
region: { name: us-east-1, role: standby }
```

Three independent guardrails enforce this, so a misconfigured standby cannot
corrupt the active region:

1. **Startup validation** refuses a standby configured with a durable worker role.
2. **The chart** does not render worker deployments or the migration job outside
   the active region.
3. **Readiness publishes `accepts_writes`**, so a global load balancer sends
   write traffic only to the active region while still health-checking standbys.

```jsonc
GET /health/ready
{ "ready": true, "region": "us-east-1", "region_role": "standby",
  "accepts_writes": false }
```

### Failover

1. Demote the current active region to `standby` (or scale it to zero) **first**,
   so only one region ever runs durable writers.
2. Promote the replica database in the standby region.
3. Set `region.role: active` there and redeploy — workers and the migration job
   begin rendering.

Guard's leases, fencing tokens and idempotency keys mean a briefly overlapping
worker cannot double-apply an effect, but the ordering above is still the
supported procedure.

## Bus transports

By default the durable bus is the only carrier. Larger deployments can fan
committed handoffs out to a broker:

```bash
AIFENCE_BUS_TRANSPORT=redis          # or kafka, rabbitmq, memory, none
AIFENCE_BUS_TRANSPORT_URL=redis://redis:6379/0
AIFENCE_BUS_TRANSPORT_TOPIC=aifence.handoffs
```

Install the matching extra (`.[redis]`, `.[kafka]`, `.[rabbitmq]`). Publication
happens **after** the durable commit and carries only message identity and
routing metadata — never semantic content, which subscribers resolve from the
bus. A broker outage is reported in the receipt's `fanout` field rather than
failing the request or faking a delivery. See [Bus](bus.md#broker-transports).

## Health and observability

| Path | Purpose |
| --- | --- |
| `/health/live` | Liveness probe. |
| `/health/ready` | Readiness; reports subsystems, region and `accepts_writes`. |
| `/metrics` | Prometheus scrape target. |

Set `AIFENCE_OTEL_EXPORTER_OTLP_ENDPOINT` to enable OpenTelemetry tracing. See
[Operations](operations.md).
