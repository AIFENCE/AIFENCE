# Security Policy

## Reporting a vulnerability

**Do not open a public issue for a security vulnerability.**

Report privately through GitHub's [private vulnerability
reporting](https://github.com/AIFENCE/AIFENCE/security/advisories/new), or email
**security@digitalacre.org**.

Please include:

- the affected component (`aifence.guard`, `aifence.bus`, `aifence.quality`, or
  the composed application);
- the version or commit;
- a description of the impact, and steps or a proof of concept if you have one.

You will get an acknowledgement within three business days and an assessment
with a remediation plan or a rejection rationale within ten.

## Scope

AIFENCE is a security control plane, so findings in these areas are of
particular interest:

- **Enforcement bypass** — reaching an action without a decision, or executing
  something other than the action a capability token was bound to.
- **Authentication and isolation** — cross-tenant access, scope escalation, or
  authenticating without a valid credential on any surface.
- **Fail-open behaviour** — any path where an unavailable or failing component
  results in an action being permitted rather than refused.
- **Evidence integrity** — forging or silently altering signed receipts,
  the hash-chained audit log, or anchored checkpoints.
- **Data exposure** — sensitive content reaching logs, findings, receipts, or a
  broker fan-out.

Findings in the vendored quality-control pack under `quality/` and in the SDKs
under `sdks/` are also in scope.

## Out of scope

- Missing hardening in a `development`-mode deployment. Production validation is
  strict and fails closed; running in development mode is not a vulnerability.
- Denial of service through resource exhaustion against a deployment you control.
- Vulnerabilities in third-party dependencies without a demonstrated impact on
  AIFENCE — report those upstream.

## Disclosure

We ask for coordinated disclosure: give us the remediation window above before
publishing. We will credit reporters in the release notes unless you prefer
otherwise.
