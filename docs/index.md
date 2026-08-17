---
title: AIFENCE
summary: A governed control plane that quality-gates, enforces, and transports AI agent actions.
infobox:
  Type: AI agent control plane
  Tiers: Quality · Guard · Bus
  Language: Python 3.12
  Framework: FastAPI
  Database: PostgreSQL / SQLite
  License: AGPL-3.0-or-later or commercial
  Repository: AIFENCE/AIFENCE
---

**AIFENCE** is a control plane that sits between an AI agent and everything it
can affect. It answers three questions about every action an agent takes — *is
the output good enough*, *is the action permitted*, and *how does the result
travel* — and it answers them as one governed pipeline rather than three
disconnected tools.

The system unifies three previously separate projects into a single codebase:
a production quality-control pack, a security enforcement plane, and a semantic
communication runtime. They share one identity model, one database and schema,
one audit chain, and one telemetry pipeline.

## The three tiers

| Tier | Package | Question it answers |
| --- | --- | --- |
| [Quality](quality.md) | `aifence.quality` | Is this output fit to ship? |
| [Guard](guard.md) | `aifence.guard` | Is this action permitted? |
| [Bus](bus.md) | `aifence.bus` | How does the result reach its receiver? |

## The fence flow

A single request traverses all three tiers through
[`POST /v1/fence/submit`](fence-flow.md):

```text
request ─▶ quality gate ─▶ guard enforcement ─▶ durable handoff ─▶ receiver
             score            allow / deny         claimable message
```

Any tier can stop the request. A placeholder-laden artifact never reaches
enforcement; a destructive high-risk action never reaches transport. The
response is one receipt describing exactly what happened at each stage.

See [Fence flow](fence-flow.md) for the outcomes and the receipt format.

## Design principles

**Fail closed.** Every tier refuses when it cannot render a verdict. The
enforcement tier cannot be configured to fail open at all — naming it in the
fail-open list is rejected at startup, because an unavailable guard must never
become an open door.

**Never claim what did not happen.** If the transport tier is degraded, the
receipt reports `authorized_not_delivered` rather than `handed_off`. If a broker
fan-out fails, that failure appears in the receipt instead of being swallowed
into a success.

**Do not trust self-declaration.** Callers declare the data classes their
payload contains, but the [content classifier](security.md#content-classification)
inspects the payload itself, so an agent that under-declares does not thereby
escape the exfiltration rules.

**One identity.** The fence flow, the quality endpoints and the operator console
all authenticate against the same API keys the guard tier issues. There is no
second, weaker credential path.

## Getting started

```bash
pip install -e ".[dev]"
aifence-api
```

Then read [Getting started](getting-started.md), or jump to
[Configuration](configuration.md), [Deployment](deployment.md), or the
[API reference](api.md).
