---
title: Glossary
summary: Terms used across the quality, guard and bus tiers.
infobox:
  Scope: cross-tier terminology
---

**Acknowledgement (ack)** — Confirmation that a receiver consumed a handoff.
Receiver knowledge advances only after an ack, so a claimed-but-unacked message
is redelivered rather than lost.

**Anchor** — Publication of an audit checkpoint to an independently administered
external destination, so tampering is detectable by a party that does not
control the deployment.

**Capability token** — A token bound to one exact action (tool, operation,
resource, arguments) with a TTL and use limit. An allow decision issues one;
it cannot be replayed against a different action. See [Guard](guard.md#capability-tokens).

**Circuit breaker** — Per-tier failure tracker. After a threshold of consecutive
failures it *trips open* and short-circuits the tier for a recovery window
instead of spending each request's latency budget on a sick dependency.

**Content classification** — Deriving data classes from the payload itself
rather than trusting the caller's declaration. See [Security](security.md#content-classification).

**Data class** — A category of sensitive content (`financial`, `credential`,
`government_id`, `health`, …). Declared by the caller *and* observed by the
classifier; enforcement uses the union.

**Degraded tier** — A tier that failed but was configured to fail open. Named in
the receipt's `degraded_tiers` so a degraded run is never mistaken for a clean one.

**Detector** — A guard component that inspects a decision request and emits
findings with a category, severity and confidence.

**Fail closed / fail open** — Whether a tier that cannot answer refuses the
request (closed) or lets it continue (open). Closed is the default everywhere;
the guard tier is closed permanently.

**Fence flow** — The composed pipeline quality → guard → bus, exposed as
`POST /v1/fence/submit`. See [Fence flow](fence-flow.md).

**Fencing token** — A monotonically increasing token attached to a lease so a
delayed worker cannot apply a stale write after its lease expired.

**Finding** — A detector's output: category, severity, confidence, evidence.
Policy rules match on finding categories.

**Grounding** — Checking numeric claims in an artifact against supplied source
material. See [Quality](quality.md#grounding).

**Handoff** — A durable, claimable message carrying semantic state from one
agent to another.

**Lease** — A time-bounded claim on a message or job. Expiry returns the work to
the queue, which is what makes at-least-once delivery safe.

**Mandatory check** — A quality check whose failure rejects the artifact
regardless of the weighted score.

**Outcome** — Guard's verdict: `allow`, `allow_with_limits`,
`redact_or_transform`, `require_approval`, `deny`, `quarantine_and_terminate`.

**Receipt** — The signed record of a decision, or the response describing what
each tier did in a fence submission.

**Reference** — A content-addressed pointer (`aifence:sha256:…`) to stored
content, with authorization and lifetime as separate grants.

**Region role** — `active` (owns writes and durable workers) or `standby`
(serves reads from a replica). See [Deployment](deployment.md#multi-region-topology).

**Risk score** — 0–100, derived from finding severities and confidences plus
action attributes (destructive, irreversible, external effect, amount).

**Runtime role** — Which part of the system a process runs as: `control-plane`,
`dispatcher`, `lifecycle`, `anchor`, `migration`, `maintenance`.

**Semantic unit** — The smallest meaning-bearing element the bus compiler
extracts from content.

**Subsystem** — A tier that registers itself into the composed application via
the `register(app, ctx)` hook. See [Architecture](architecture.md).

**Tenant** — The isolation boundary. Enforced by PostgreSQL row-level security
and carried on every API key.

**Transport** — Optional broker fan-out for committed handoffs
(`redis`, `kafka`, `rabbitmq`). Not the delivery guarantee — the durable bus is.

**Workspace** — The bus's routing and fairness scope, orthogonal to tenant.
