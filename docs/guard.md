---
title: Guard tier
summary: The enforcement plane — decides and enforces what an agent is permitted to do.
infobox:
  Package: aifence.guard
  Mount: /guard
  Config prefix: AIFENCE_GUARD_
  Baseline policy: 18 mandatory rules
  Failure mode: always fail-closed
---

The **guard tier** is the enforcement plane. It sits outside the agent process
and evaluates every sensitive action before it reaches a model provider, tool,
data source, artifact store, or another agent. It is mounted as a
sub-application at `/guard` and shares the composed application's database,
identity model and audit chain.

Guard never treats a policy result as advisory: required controls must compile
into an executable enforcement plan, or the operation fails closed.

## Decision pipeline

```text
DecisionRequest
   │
   ├─▶ detectors ──────▶ findings (category, severity, confidence)
   │                        │
   ├─▶ content classifier ──┤   observed data classes
   │                        ▼
   ├─▶ risk scoring ─────▶ risk 0–100
   │                        │
   └─▶ policy engine ───────┴─▶ outcome + constraints
                                     │
                                     ▼
                            enforcement plan → capability token
```

## Outcomes

Ordered by severity; the most severe match wins across baseline and tenant
policy:

| Outcome | Meaning |
| --- | --- |
| `allow` | Proceed unchanged. |
| `allow_with_limits` | Proceed under constraints (rate, amount, destination). |
| `redact_or_transform` | Proceed only after the payload is transformed. |
| `require_approval` | Hold for a human decision. |
| `deny` | Refuse. |
| `quarantine_and_terminate` | Refuse, isolate the artifact, and end the run. |

## Detectors

Detectors emit findings in stable categories that policy rules match on:

- **`prompt_injection.detected`** — instruction injection in untrusted content.
- **`data.exfiltration`** — sensitive data heading to a non-private destination.
- **`data.secret_exposure`** — credential or key material in the request.
- **`data.undeclared_sensitive`** — sensitive content the caller did not declare.
- **`integrity.control_evasion`**, **`integrity.instruction_drift`** — attempts to
  evade controls or drift from the approved instruction.
- **`deception.material_misrepresentation`**, **`cheat.fabricated_completion`** —
  claims contradicted by observed facts.
- **`authorization.scope_violation`**, **`authorization.tool_not_allowed`** —
  action outside the approved objective or tool allowlist.
- **`execution.dangerous_command`**, **`delegation.excessive_depth`** — unsafe
  execution or runaway delegation.

See [Security model](security.md) for how content classification feeds these.

## Capability tokens

An allowed decision does not itself perform the action. Guard issues an
**exact-action capability token** bound to the decision: the tool, operation,
resource and arguments are fixed at issue time, with a TTL and a maximum use
count. Consuming a token for anything other than the bound action fails.

This is what makes an allow decision non-transferable — a token obtained for one
action cannot be replayed against another.

## Identity and access

Guard owns the identity model the whole fence uses:

- **Tenants** isolate data, enforced by PostgreSQL row-level security.
- **API keys** are scoped (`decisions:write`, `approvals:read`, `audit:anchor`, …)
  and may be bound to an immutable agent manifest, workload, instance and principal.
- **Workload identity** via trusted SPIFFE assertions from a mutually
  authenticated proxy.

A key bound to an agent cannot change that identity through request fields.

## Evidence

Every decision produces a signed receipt, and events are written to a
hash-chained audit log with periodic checkpoints. Checkpoints can be anchored to
independently administered external destinations, so tampering is detectable by
a party that does not control the deployment.

## Worker roles

Guard separates runtime roles so durable work can be deployed and scaled apart
from the control plane: `control-plane`, `dispatcher`, `lifecycle`, `anchor`,
`migration`, `maintenance`. Workers share the control plane's signing identity
and must not auto-create schema. In a [multi-region](deployment.md#multi-region-topology)
deployment they run only in the active region.

## Configuration

Guard reads roughly 150 settings under the `AIFENCE_GUARD_` prefix — signing,
KMS, artifact storage, audit anchors, worker tuning, workload identity. The
composed application injects the settings it owns (environment, runtime role,
log level, database URL, schema creation, docs) so a production fence cannot
start an unhardened guard tier.

Production validation is strict and reports every unmet requirement at once:
PostgreSQL over `sslmode=verify-full`, mTLS, non-exportable signing, external
KMS, S3-backed evidence, an independent audit-anchor webhook, controlled egress,
and SPIFFE workload identity.
