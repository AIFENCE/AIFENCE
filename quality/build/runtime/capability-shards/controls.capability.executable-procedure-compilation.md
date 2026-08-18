<!-- GENERATED from source/controls/31-operational-procedure-compilation-authority-and-measurement.md#controls.capability.executable-procedure-compilation; canonical truth remains source/. -->

## Executable Procedure Compilation
<!-- id: controls.capability.executable-procedure-compilation -->

**Targets:** OPERATIONAL_PROCEDURE_COMPILER.md  
**Requirement:** Compile triggers, prerequisites, inputs, actor-specific ordered steps, decisions, checks, evidence, failure paths, outputs, and observable definition of done for material operating procedures.

### Contract — BQ-1266
<!-- id: control.bq-1266 -->

- **MUST:** Compile triggers, prerequisites, inputs, actor-specific ordered steps, decisions, checks, evidence, failure paths, outputs, and observable definition of done for material operating procedures.
- Preserve truthful unknowns, applicable professional/licensing boundaries, organization authority, external-source provenance, and proportionate evidence.
- A detailed generated procedure is not automatically an approved or authoritative procedure.
- Do not invent approval limits, KPI targets, retention periods, credentials, jurisdictional requirements, system names, manufacturer steps, or regulatory thresholds.

### Procedure — BQ-1267
<!-- id: control.bq-1267 -->

1. Define procedure purpose, scope/exclusions, trigger, entry conditions, required inputs, prerequisites, and responsible role before writing steps.
2. For each MATERIAL step specify actor, observable action, acceptance check, failure path, and evidence reference or explicit evidence-not-required reason.
3. Attach systems/methods, boundaries, authority references, decisions, and measurements only where they materially affect execution.
4. Walk the sequence from trigger to Definition of Done and verify every branch reaches a next state, recovery/escalation path, or explicit controlled stop.
5. Reject vague verbs such as review/ensure/handle/follow-policy when the available facts support a concrete action/check/evidence definition.

### Evidence Gate — BQ-1268
<!-- id: control.bq-1268 -->

- **PASS only if** the requirement is directly evidenced in the compiled role/procedure/metric record and another competent reader can identify the actor, trigger, decision boundary, evidence, and completion condition without guessing material facts.
- Authoritative claims require adequate source provenance and applicability evidence.
- If required source/currentness/organization authority evidence is unavailable, mark the affected portion **UNVERIFIED** or draft; do not silently pass it.

### Recovery — BQ-1269
<!-- id: control.bq-1269 -->

- Block authoritative or production-use claims for the affected portion.
- Downgrade authority classification when provenance is insufficient, surface unknowns, obtain/verify the missing source or organization fact where tools/evidence permit, and repair the smallest upstream ambiguity.
- Re-run affected decision-rights, evidence, KPI, risk, handoff, and change-control checks after repair.

### Regression — BQ-1270
<!-- id: control.bq-1270 -->

- Maintain **normal**, **ambiguous/edge**, and **failure/unavailable-evidence** fixtures.
- The ambiguous case must preserve unknown authority or applicability instead of inventing specificity.
- The failure case must trigger Recovery when a procedure is detailed but lacks evidence required for its claimed authority or completion state.
- Real operational failures should become regression fixtures when they expose a reusable process weakness.
