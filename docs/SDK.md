# AIFENCE SDKs and framework integration

Maintained clients live under [`sdks/`](../sdks):

| Language | Path | Package identifier |
| --- | --- | --- |
| Python | [`sdks/python`](../sdks/python) | `agentdance_client` |
| TypeScript | [`sdks/typescript`](../sdks/typescript) | `@agentdance/client` |
| Go | [`sdks/go`](../sdks/go) | `agentdance` |

> The client *package* identifiers are retained so existing integrations keep
> compiling. Only the documentation and deployment surfaces use AIFENCE naming.

## Base URL: point at the guard mount

The guard tier is mounted at `/guard` inside the composed application, and the
clients append `/v1/...` to whatever base URL they are given. So the only change
required against AIFENCE is the base URL:

```text
https://aifence.example.com/guard   ->  https://aifence.example.com/guard/v1/decisions
```

HTTPS is required by every client.

```python
from agentdance_client import AgentDanceClient

client = AgentDanceClient("https://aifence.example.com/guard", api_key)
```

## Framework integrations

The Python SDK ships framework-neutral enforcement hooks in
[`agentdance_client/integrations.py`](../sdks/python/agentdance_client/integrations.py),
covering:

- OpenAI Agents
- LangGraph
- CrewAI
- AutoGen
- Semantic Kernel

They wrap a tool call so every invocation is submitted for a decision before it
executes, and are driven by an immutable agent manifest.

## The fence flow vs. the guard API

Two entry points, both authenticated with the same API key:

| Endpoint | Use when |
| --- | --- |
| `POST /guard/v1/decisions` | You want an enforcement decision only. |
| `POST /v1/fence/submit` | You want the full pipeline: quality gate → enforcement → durable semantic handoff. |

The fence flow requires the `decisions:write` scope.
