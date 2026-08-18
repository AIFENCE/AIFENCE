<!-- GENERATED from source/controls/31-operational-procedure-compilation-authority-and-measurement.md#controls.capability.decision-checkpoint-stop-sequencing; canonical truth remains source/. -->

## Decision Checkpoint & Stop Sequencing
<!-- id: controls.capability.decision-checkpoint-stop-sequencing -->

**Targets:** OPERATIONAL_PROCEDURE_COMPILER.md / DECISION_RIGHTS.md  
**Requirement:** Expose consequential decision criteria, quality/risk checkpoints, stop conditions, restart requirements, and the owner of each branch instead of hiding them in vague prose.

### Contract — BQ-1276
<!-- id: control.bq-1276 -->

- **MUST:** Expose consequential decision criteria, quality/risk checkpoints, stop conditions, restart requirements, and the owner of each branch instead of hiding them in vague prose.
- Preserve truthful unknowns, applicable professional/licensing boundaries, organization authority, external-source provenance, and proportionate evidence.
- A detailed generated procedure is not automatically an approved or authoritative procedure.
- Do not invent approval limits, KPI targets, retention periods, credentials, jurisdictional requirements, system names, manufacturer steps, or regulatory thresholds.

### Procedure — BQ-1277
<!-- id: control.bq-1277 -->

1. Extract consequential branch points from the step sequence and define signal/condition, decision owner, criteria, allowed choices, evidence, and resulting next state.
2. Insert quality/risk checkpoints before irreversible or high-consequence transitions rather than after the outcome is already committed.
3. For every stop condition, specify what is preserved/contained, who is notified, and the exact restart condition; identify restart authorizer when verified approval is required.
4. Trace each branch forward and ensure no path dead-ends in “as appropriate,” “if needed,” or an ownerless escalation.
5. Revalidate ordering after step, owner, authority, or system changes because a correct checkpoint in the wrong sequence is not a valid control.

### Evidence Gate — BQ-1278
<!-- id: control.bq-1278 -->

- **PASS only if** the requirement is directly evidenced in the compiled role/procedure/metric record and another competent reader can identify the actor, trigger, decision boundary, evidence, and completion condition without guessing material facts.
- Authoritative claims require adequate source provenance and applicability evidence.
- If required source/currentness/organization authority evidence is unavailable, mark the affected portion **UNVERIFIED** or draft; do not silently pass it.

### Recovery — BQ-1279
<!-- id: control.bq-1279 -->

- Block authoritative or production-use claims for the affected portion.
- Downgrade authority classification when provenance is insufficient, surface unknowns, obtain/verify the missing source or organization fact where tools/evidence permit, and repair the smallest upstream ambiguity.
- Re-run affected decision-rights, evidence, KPI, risk, handoff, and change-control checks after repair.

### Regression — BQ-1280
<!-- id: control.bq-1280 -->

- Maintain **normal**, **ambiguous/edge**, and **failure/unavailable-evidence** fixtures.
- The ambiguous case must preserve unknown authority or applicability instead of inventing specificity.
- The failure case must trigger Recovery when a procedure is detailed but lacks evidence required for its claimed authority or completion state.
- Real operational failures should become regression fixtures when they expose a reusable process weakness.
