---
title: Fence flow
summary: The three tiers as one governed pipeline, with a single receipt.
infobox:
  Endpoint: POST /v1/fence/submit
  Module: aifence.flow
  Required scope: decisions:write
  Order: quality → guard → bus
---

The **fence flow** is what makes AIFENCE a merged system rather than three
co-located services. One authenticated request runs through all three tiers
in process, and returns a single receipt describing what each tier decided.

```text
POST /v1/fence/submit
   │
   ├── quality gate ──── fails ──▶ blocked_by_quality   (guard never runs)
   │        │ passes
   ├── guard enforcement ─ denies ─▶ blocked_by_guard    (bus never runs)
   │        │ allows
   └── durable handoff ─── degraded ─▶ authorized_not_delivered
            │ delivered
            └──────────────────────▶ handed_off
```

Each tier runs under its own [latency budget and circuit
breaker](#resilience), and short-circuiting is the point: a placeholder-laden
artifact never consumes an enforcement decision, and a denied action never
reaches transport.

## Outcomes

| `final_outcome` | `allowed` | Meaning |
| --- | --- | --- |
| `handed_off` | `true` | Passed every tier; a claimable message was persisted. |
| `blocked_by_quality` | `false` | The artifact failed the quality gate. |
| `blocked_by_guard` | `false` | Policy denied or required approval. |
| `authorized_not_delivered` | `true` | Permitted, but transport was degraded. |

`authorized_not_delivered` exists so the receipt never claims a handoff that did
not happen. It is a deliberately uncomfortable outcome: the action was
authorized and the caller must decide whether to retry.

## The receipt

```jsonc
{
  "request_id": "req_…",
  "tenant_id": "ten_…",
  "allowed": true,
  "final_outcome": "handed_off",
  "degraded_tiers": [],
  "stages": {
    "quality": { "tier": "quality", "passed": true, "score": 100, "checks": [ … ] },
    "guard":   { "tier": "guard", "outcome": "allow", "policy_version": "…",
                 "matched_rule": "baseline:read-only-low-risk" },
    "bus":     { "tier": "bus", "delivered": true, "message_id": "M…",
                 "wire_bytes": 265, "raw_bytes": 103,
                 "content_ref": "aifence:sha256:…",
                 "fanout": { "backend": "none", "published": false } }
  }
}
```

`request_id` correlates the receipt with the audit chain and telemetry;
`tenant_id` records who submitted it. `degraded_tiers` names any tier that
failed open, so a degraded run is never mistaken for a clean one.

## Resilience

Every tier is **fail-closed by default**: a tier that cannot answer within its
budget causes `503 tier_unavailable` rather than a silent pass. Repeated
failures trip a circuit breaker that short-circuits the tier for a recovery
window, so one sick dependency does not consume every request's latency budget.

`quality` and `bus` may be made advisory with `AIFENCE_FLOW_FAIL_OPEN_TIERS`.
**`guard` cannot** — naming it is rejected at startup rather than silently
ignored, because an unavailable enforcement tier must never become an open door.

See [Configuration](configuration.md#fence-flow-resilience) for the timeouts and
thresholds.

## Grounding a submission

Supplying `sources` enables the quality tier's grounding check for the whole
flow, so fabricated figures are stopped before enforcement:

```jsonc
{
  "artifact": "# Q3\n\nRevenue reached 9.9 million…",
  "content_type": "text/markdown",
  "sources": ["Q3 revenue was 4.2 million, up 12 percent, across 1500 accounts."],
  "action": { "operation": "read" }
}
// → blocked_by_quality: 4 numeric claim(s) absent from sources
```

## Relationship to the guard API

Two entry points, both using the same credential:

| Endpoint | Use when |
| --- | --- |
| `POST /guard/v1/decisions` | You want an enforcement decision only. |
| `POST /v1/fence/submit` | You want the full pipeline and a durable handoff. |
