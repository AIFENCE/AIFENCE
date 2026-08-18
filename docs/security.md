---
title: Security model
summary: Authentication, content classification, evidence, and the fail-closed posture.
infobox:
  Identity: scoped API keys + SPIFFE
  Isolation: PostgreSQL row-level security
  Evidence: signed receipts, hash-chained audit
  Posture: fail closed
---

## One identity model

Every authenticated surface in AIFENCE uses the same API keys the
[guard tier](guard.md) issues. The fence flow, the quality endpoints and the
operator console are composed onto the application rather than mounted inside
the guard sub-application, so they do not inherit its router-level
authentication automatically — `aifence.security` binds them to it explicitly.

That module **fails closed**: if no identity provider is composed in, the
endpoints refuse to serve rather than silently accepting anonymous callers.

| Surface | Authentication |
| --- | --- |
| `/health/live`, `/health/ready`, `/metrics` | Public, so probes and scrapers work. |
| `/v1/fence/submit` | API key with `decisions:write`. |
| `/v1/quality/*` | API key. |
| `/v1/console/*` | API key with `decisions:read`. |
| `/guard/*` | Guard's own router-level authentication. |

## Scopes

Keys carry explicit scopes — `decisions:read`, `decisions:write`,
`approvals:write`, `capabilities:issue`, `audit:anchor`, `policies:activate`,
`memory:quarantine`, `tenants:lifecycle` and others. A key may additionally be
bound to an immutable agent manifest, workload identity, instance and principal;
a bound key cannot change that identity through request fields.

## Content classification

Data classes are supplied by the caller, so enforcement that relies on them
alone is only as honest as the agent. AIFENCE therefore inspects the payload
itself and reports which sensitive classes are **observed**, feeding those into
the same exfiltration and secret-exposure rules.

The practical effect: an agent that under-declares no longer escapes the rules.

| Class | Signal | Precision measure |
| --- | --- | --- |
| `financial` | Card numbers, IBANs | Card numbers must pass a **Luhn** check. |
| `government_id` | National IDs | Structurally invalid ranges excluded. |
| `credential` | AWS/GitHub/Slack keys, JWTs, assigned secrets | Generic secrets need an assignment context. |
| `secret` | Private key blocks | Explicit PEM header. |
| `health` | Clinical terminology | Keyword set, reported not enforced. |
| `personal_data` | Email, phone | Informational; not in the sensitive set. |

Precision is favoured over recall because observed classes feed
rules whose baseline outcome is `deny`. A Luhn-invalid number, an SSN in the
`000`/`666`/`9xx` ranges, and a long token in ordinary prose all produce nothing.

**Matched values are never returned.** The classifier reports class names and
counts only — the matched text *is* the sensitive data, and must not reach
findings, logs or receipts.

## Fail-closed posture

The system refuses rather than degrading silently:

- A [tier](fence-flow.md#resilience) that cannot answer produces `503`.
- The enforcement tier can never be configured to fail open.
- Unknown policy constraints fail closed rather than being ignored.
- A standby [region](deployment.md#multi-region-topology) refuses durable worker
  roles at startup.
- An unknown bus transport backend fails at startup rather than quietly
  disabling fan-out.
- Production configuration validation reports every unmet requirement at once
  and refuses to start until they are met.

## Evidence

Decisions produce signed receipts. Events are written to a hash-chained audit
log with periodic checkpoints, which can be anchored to independently
administered external destinations so tampering is detectable by a party that
does not control the deployment. Tenant exports are portable, and legal holds
suspend retention.

## Network controls

Outbound calls are confined: HTTPS-only destinations, canonical path
confinement, DNS revalidation with connection-time IP pinning, preserved TLS
SNI and Host, no redirect following, egress through a controlled proxy, and
bounded response sizes.

## Reporting a vulnerability

Do not open a public issue. See `SECURITY.md` in the repository for the
disclosure process.
