<!-- GENERATED from source/controls/31-operational-procedure-compilation-authority-and-measurement.md#controls.capability.exception-recovery-continuity; canonical truth remains source/. -->

## Exception Recovery & Continuity
<!-- id: controls.capability.exception-recovery-continuity -->

**Targets:** OPERATIONAL_PROCEDURE_COMPILER.md / OPERATIONAL_EVIDENCE.md  
**Requirement:** Define exception detection, containment, escalation, recovery/rollback, deferred follow-up, and continuity paths for material failure states.

### Contract — BQ-1281
<!-- id: control.bq-1281 -->

- **MUST:** Define exception detection, containment, escalation, recovery/rollback, deferred follow-up, and continuity paths for material failure states.
- Preserve truthful unknowns, applicable professional/licensing boundaries, organization authority, external-source provenance, and proportionate evidence.
- A detailed generated procedure is not automatically an approved or authoritative procedure.
- Do not invent approval limits, KPI targets, retention periods, credentials, jurisdictional requirements, system names, manufacturer steps, or regulatory thresholds.

### Procedure — BQ-1282
<!-- id: control.bq-1282 -->

1. Enumerate material failure/exception states from inputs, decisions, systems, approvals, quality checks, evidence gaps, and downstream handoffs.
2. For each exception define detection signal, immediate containment, accountable owner, escalation path, recovery/rollback action, deferred follow-up if needed, and closure evidence.
3. Distinguish recoverable exceptions from conditions requiring STOP_AND_ESCALATE; do not continue execution merely to preserve throughput.
4. Ensure recovery returns the process to a defined safe/valid state or formally hands ownership to a named downstream owner.
5. After an incident or new failure mode, promote it into the regression set or document why an existing generalized fixture covers it.

### Evidence Gate — BQ-1283
<!-- id: control.bq-1283 -->

- **PASS only if** the requirement is directly evidenced in the compiled role/procedure/metric record and another competent reader can identify the actor, trigger, decision boundary, evidence, and completion condition without guessing material facts.
- Authoritative claims require adequate source provenance and applicability evidence.
- If required source/currentness/organization authority evidence is unavailable, mark the affected portion **UNVERIFIED** or draft; do not silently pass it.

### Recovery — BQ-1284
<!-- id: control.bq-1284 -->

- Block authoritative or production-use claims for the affected portion.
- Downgrade authority classification when provenance is insufficient, surface unknowns, obtain/verify the missing source or organization fact where tools/evidence permit, and repair the smallest upstream ambiguity.
- Re-run affected decision-rights, evidence, KPI, risk, handoff, and change-control checks after repair.

### Regression — BQ-1285
<!-- id: control.bq-1285 -->

- Maintain **normal**, **ambiguous/edge**, and **failure/unavailable-evidence** fixtures.
- The ambiguous case must preserve unknown authority or applicability instead of inventing specificity.
- The failure case must trigger Recovery when a procedure is detailed but lacks evidence required for its claimed authority or completion state.
- Real operational failures should become regression fixtures when they expose a reusable process weakness.
