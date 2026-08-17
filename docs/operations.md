---
title: Operations
summary: Running the fence — console, health, metrics, tracing and degradation.
infobox:
  Console: /v1/console/
  Metrics: /metrics (Prometheus)
  Tracing: OpenTelemetry (OTLP)
  Probes: /health/live, /health/ready
---

## Operator console

`GET /v1/console/` renders a server-side dashboard; `GET /v1/console/status`
returns the same data as JSON. Both require an API key with `decisions:read` —
there is no separate console login.

The console shows:

- **Handoffs** — durable bus message counts by status.
- **Approvals pending** — decisions awaiting a human, for the caller's tenant.
- **Circuit breakers** — per-tier state (`closed` / `half_open` / `open`) and paradigm.
- **Subsystems** — which tiers composed into this process.
- **Quality controls** — size of the loaded control registry.
- **Bus transport** — the configured fan-out backend.

The page is rendered server-side with no inline script, so it satisfies the
strict Content-Security-Policy the application sends. It refreshes on a meta
refresh rather than a fetch loop.

## Health probes

| Path | Use |
| --- | --- |
| `/health/live` | Liveness. Is the process up? |
| `/health/ready` | Readiness. Also reports region and `accepts_writes`. |

`accepts_writes` is the field a global load balancer should key on in a
[multi-region](deployment.md#multi-region-topology) deployment: a standby region
is *ready* but must not receive write traffic.

## Metrics

Prometheus metrics are exposed at `/metrics`, unauthenticated only when
`AIFENCE_METRICS_PUBLIC` is set. Alongside the shared HTTP request counter and
latency histogram, the guard tier exports decision outcomes, capability and
approval lifecycle events, execution transitions, outbox backlog, dispatch and
dependency latency, and audit-anchor events.

## Tracing

Setting `AIFENCE_OTEL_EXPORTER_OTLP_ENDPOINT` enables OpenTelemetry tracing for
the application and SQLAlchemy. Health and metrics paths are excluded. Protocol
measurements are emitted without placing content payloads in span attributes.

## Reading a degraded run

Two signals distinguish a degraded run from a clean one:

- `degraded_tiers` in the [receipt](fence-flow.md#the-receipt) names any tier
  that failed open.
- `final_outcome: "authorized_not_delivered"` means the action was permitted but
  the handoff did not persist — the caller must decide whether to retry.

A `503 tier_unavailable` response means a fail-closed tier could not answer;
the `details.tier` field names which one. Check the console for that tier's
breaker state: `open` means it is being short-circuited after repeated failures
and will be probed again after the recovery window.

## Retention and lifecycle

Audit evidence and artifacts have independent retention periods. The lifecycle
worker performs tenant export and crypto-erase; the anchor worker publishes
audit checkpoints to external destinations. Both are durable worker roles and
run only in the active region.

## Verification

```bash
make verify     # ruff + mypy (strict) + pytest
make test
```

The suite covers the shared core, both subsystem ports, the quality gate and
end-to-end composition, including authentication, lifespan cleanup, circuit
breaker behaviour, migration/model drift and multi-region guardrails.
