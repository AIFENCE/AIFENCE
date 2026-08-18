---
title: SDKs
summary: Python, TypeScript and Go clients, and the agent-framework enforcement hooks.
infobox:
  Languages: Python · TypeScript · Go
  Base URL: https://host/guard
  Frameworks: LangGraph · CrewAI · AutoGen · Semantic Kernel · OpenAI Agents
  Transport: HTTPS required
---

Maintained clients live under
[`sdks/`](https://github.com/AIFENCE/AIFENCE/tree/main/sdks):

| Language | Path | Package identifier |
| --- | --- | --- |
| Python | `sdks/python` | `agentdance_client` |
| TypeScript | `sdks/typescript` | `@agentdance/client` |
| Go | `sdks/go` | `agentdance` |

Package identifiers are held stable so existing integrations keep compiling.

## Base URL: point at the guard mount

The [guard tier](guard.md) is mounted at `/guard` inside the composed
application, and every client appends `/v1/...` to the base URL it is given. So
the only change required against AIFENCE is the base URL:

```text
https://aifence.example.com/guard  →  https://…/guard/v1/decisions
```

HTTPS is required by every client; they refuse a plaintext base URL.

```python
from agentdance_client import AgentDanceClient

client = AgentDanceClient("https://aifence.example.com/guard", api_key)
```

## Framework integrations

The Python SDK ships framework-neutral enforcement hooks in
`agentdance_client/integrations.py`, covering:

- OpenAI Agents
- LangGraph
- CrewAI
- AutoGen
- Semantic Kernel

Each wraps a tool call so every invocation is submitted for a decision *before*
it executes, driven by an immutable agent manifest. The wrapper is the
enforcement point: a denied decision raises rather than returning, so a tool
cannot run on a refused action.

## Two entry points

Both use the same API key; choose by how much of the fence you want:

| Endpoint | Use when |
| --- | --- |
| `POST /guard/v1/decisions` | You want an enforcement decision only. |
| `POST /v1/fence/submit` | You want the full pipeline: quality gate → enforcement → durable handoff. |

The [fence flow](fence-flow.md) requires the `decisions:write` scope and returns
a receipt covering all three tiers. See the [API reference](api.md) for the
complete endpoint list.

## Client behaviour

All three clients apply bounded request behaviour: explicit timeouts, capped
retries with `Retry-After` awareness, no redirect following, and a maximum
response size. They surface AIFENCE's structured error envelope
(`code`, `message`, `details`, `request_id`) rather than raw HTTP status codes,
so `request_id` can be correlated with the audit chain.
