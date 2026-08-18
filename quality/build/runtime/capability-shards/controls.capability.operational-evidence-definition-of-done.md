<!-- GENERATED from source/controls/31-operational-procedure-compilation-authority-and-measurement.md#controls.capability.operational-evidence-definition-of-done; canonical truth remains source/. -->

## Operational Evidence & Definition of Done
<!-- id: controls.capability.operational-evidence-definition-of-done -->

**Targets:** OPERATIONAL_EVIDENCE.md  
**Requirement:** Map material steps and decisions to proportionate evidence, records, handoff acceptance, and observable definition-of-done criteria.

### Contract — BQ-1286
<!-- id: control.bq-1286 -->

- **MUST:** Map material steps and decisions to proportionate evidence, records, handoff acceptance, and observable definition-of-done criteria.
- Preserve truthful unknowns, applicable professional/licensing boundaries, organization authority, external-source provenance, and proportionate evidence.
- A detailed generated procedure is not automatically an approved or authoritative procedure.
- Do not invent approval limits, KPI targets, retention periods, credentials, jurisdictional requirements, system names, manufacturer steps, or regulatory thresholds.

### Procedure — BQ-1287
<!-- id: control.bq-1287 -->

1. Identify material steps, decisions, exceptions, handoffs, and outcomes that require observable proof proportional to consequence and reconstruction cost.
2. Define each evidence record with stable evidence_id, linked step/decision, required content, responsible recorder, system/repository when known, reviewer/consumer when relevant, and retention provenance if a retention rule is stated.
3. Reference evidence IDs from steps, exceptions, handoffs, and each Definition-of-Done criterion; reject dangling or unreferenced critical evidence.
4. Compile Definition of Done as observable closure criteria including required actions/checks, approvals, records, exception disposition, downstream acceptance, and deferred follow-up ownership as applicable.
5. Confirm that a handoff is accepted by an explicit receiving owner and acceptance criteria; “sent” is not equivalent to transferred responsibility.

### Evidence Gate — BQ-1288
<!-- id: control.bq-1288 -->

- **PASS only if** the requirement is directly evidenced in the compiled role/procedure/metric record and another competent reader can identify the actor, trigger, decision boundary, evidence, and completion condition without guessing material facts.
- Authoritative claims require adequate source provenance and applicability evidence.
- If required source/currentness/organization authority evidence is unavailable, mark the affected portion **UNVERIFIED** or draft; do not silently pass it.

### Recovery — BQ-1289
<!-- id: control.bq-1289 -->

- Block authoritative or production-use claims for the affected portion.
- Downgrade authority classification when provenance is insufficient, surface unknowns, obtain/verify the missing source or organization fact where tools/evidence permit, and repair the smallest upstream ambiguity.
- Re-run affected decision-rights, evidence, KPI, risk, handoff, and change-control checks after repair.

### Regression — BQ-1290
<!-- id: control.bq-1290 -->

- Maintain **normal**, **ambiguous/edge**, and **failure/unavailable-evidence** fixtures.
- The ambiguous case must preserve unknown authority or applicability instead of inventing specificity.
- The failure case must trigger Recovery when a procedure is detailed but lacks evidence required for its claimed authority or completion state.
- Real operational failures should become regression fixtures when they expose a reusable process weakness.
