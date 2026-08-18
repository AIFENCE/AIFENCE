<!-- GENERATED from source/controls/31-operational-procedure-compilation-authority-and-measurement.md#controls.capability.decision-rights-approval-boundaries; canonical truth remains source/. -->

## Decision Rights & Approval Boundaries
<!-- id: controls.capability.decision-rights-approval-boundaries -->

**Targets:** DECISION_RIGHTS.md  
**Requirement:** Make MUST, MAY, MUST NOT, approval-required, stop-and-escalate, consult, and inform boundaries explicit without inventing authority limits.

### Contract — BQ-1271
<!-- id: control.bq-1271 -->

- **MUST:** Make MUST, MAY, MUST NOT, approval-required, stop-and-escalate, consult, and inform boundaries explicit without inventing authority limits.
- Preserve truthful unknowns, applicable professional/licensing boundaries, organization authority, external-source provenance, and proportionate evidence.
- A detailed generated procedure is not automatically an approved or authoritative procedure.
- Do not invent approval limits, KPI targets, retention periods, credentials, jurisdictional requirements, system names, manufacturer steps, or regulatory thresholds.

### Procedure — BQ-1272
<!-- id: control.bq-1272 -->

1. Identify each consequential action or decision and assign MUST, MAY, MUST_NOT, APPROVAL_REQUIRED, STOP_AND_ESCALATE, CONSULT, or INFORM.
2. Name performer and decision owner; for APPROVAL_REQUIRED name the approval owner and record either a verified limit with provenance or ORGANIZATION_SPECIFIC_NOT_SUPPLIED.
3. For STOP_AND_ESCALATE define containment, notification targets, escalation path, required evidence, restart condition, and restart authority state.
4. Check segregation-of-duties needs for financial, security, privacy, safety, quality, and fraud-sensitive decisions without imposing unjustified separation.
5. Fail any decision-right record that converts an unknown permission or threshold into an invented authority value.

### Evidence Gate — BQ-1273
<!-- id: control.bq-1273 -->

- **PASS only if** the requirement is directly evidenced in the compiled role/procedure/metric record and another competent reader can identify the actor, trigger, decision boundary, evidence, and completion condition without guessing material facts.
- Authoritative claims require adequate source provenance and applicability evidence.
- If required source/currentness/organization authority evidence is unavailable, mark the affected portion **UNVERIFIED** or draft; do not silently pass it.

### Recovery — BQ-1274
<!-- id: control.bq-1274 -->

- Block authoritative or production-use claims for the affected portion.
- Downgrade authority classification when provenance is insufficient, surface unknowns, obtain/verify the missing source or organization fact where tools/evidence permit, and repair the smallest upstream ambiguity.
- Re-run affected decision-rights, evidence, KPI, risk, handoff, and change-control checks after repair.

### Regression — BQ-1275
<!-- id: control.bq-1275 -->

- Maintain **normal**, **ambiguous/edge**, and **failure/unavailable-evidence** fixtures.
- The ambiguous case must preserve unknown authority or applicability instead of inventing specificity.
- The failure case must trigger Recovery when a procedure is detailed but lacks evidence required for its claimed authority or completion state.
- Real operational failures should become regression fixtures when they expose a reusable process weakness.
