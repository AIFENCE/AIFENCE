---
title: Getting started
summary: Install AIFENCE, mint a key, and run an artifact through the fence.
infobox:
  Python: 3.12+
  Entry point: aifence-api
  Default port: 8080
---

## Install

```bash
python -m venv .venv
. .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Optional extras: `postgres`, `s3`, `mcp`, `otel`, `quality` (full JSON Schema),
`redis` / `kafka` / `rabbitmq` (bus fan-out), `bench`.

## Run

```bash
aifence-api
```

The composed application serves on `0.0.0.0:8080`. In development it creates the
schema automatically; in production use [migrations](deployment.md#database-migrations).

```bash
curl http://127.0.0.1:8080/health/ready
```

```jsonc
{ "ready": true, "subsystems": ["aifence.quality","aifence.guard","aifence.bus"],
  "region_role": "active", "accepts_writes": true }
```

## Create a tenant and API key

Every authenticated surface uses guard-issued keys. Bootstrap the first tenant
and administrative key:

```bash
python -c "
from aifence.app import create_app
from aifence.core.config import CoreSettings
app = create_app(CoreSettings())
with app.state.session_factory() as s:
    _t, _k, secret = app.state.guard_app.state.service.create_tenant_and_key(
        s, tenant_name='Example Org', key_name='bootstrap', scopes=['*'])
print(secret)
"
```

The secret is printed once. Store it in a secret manager immediately.

## Run an artifact through the fence

```bash
curl -X POST http://127.0.0.1:8080/v1/fence/submit \
  -H "Authorization: Bearer $AIFENCE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "artifact": "# Q3 Report\n\nRevenue grew 12% to $4.2M across all regions.",
    "content_type": "text/markdown",
    "receiver": "analytics-agent",
    "action": { "operation": "read" }
  }'
```

A successful run returns `final_outcome: "handed_off"` and a `message_id` the
receiver can claim from the [bus](bus.md).

### Watch it block

Placeholders fail the [quality gate](quality.md) before enforcement runs:

```bash
-d '{"artifact": "# Draft\n\nTODO: write this.", "content_type": "text/markdown"}'
# → blocked_by_quality
```

A destructive, high-risk action passes quality but is stopped by
[guard](guard.md):

```bash
-d '{"artifact": "…", "action": {"operation": "delete", "destructive": true},
     "risk_score": 80}'
# → blocked_by_guard
```

## Watch the fence

The [operator console](operations.md#operator-console) shows live handoff
counts, pending approvals and circuit-breaker states:

```text
http://127.0.0.1:8080/v1/console/
```

## Next steps

- [Fence flow](fence-flow.md) — outcomes and the receipt format.
- [Configuration](configuration.md) — the full environment surface.
- [SDKs](sdk.md) — Python, TypeScript and Go clients with framework hooks.
- [Deployment](deployment.md) — migrations, Helm, multi-region.
