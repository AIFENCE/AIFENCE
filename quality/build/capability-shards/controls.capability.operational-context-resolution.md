<!-- GENERATED from source/controls/31-operational-procedure-compilation-authority-and-measurement.md#controls.capability.operational-context-resolution; canonical truth remains source/. -->

## Operational Context Resolution
<!-- id: controls.capability.operational-context-resolution -->

**Targets:** OPERATIONAL_PROCEDURE_COMPILER.md / JOBS.md / operations/*  
**Requirement:** Resolve exact industry, subindustry, business model, organization/site context, role, task, trigger, risk, systems, and material unknowns before compiling an operational procedure.

### Contract — BQ-1251
<!-- id: control.bq-1251 -->

- **MUST:** Resolve exact industry, subindustry, business model, organization/site context, role, task, trigger, risk, systems, and material unknowns before compiling an operational procedure.
- Preserve truthful unknowns, applicable professional/licensing boundaries, organization authority, external-source provenance, and proportionate evidence.
- A detailed generated procedure is not automatically an approved or authoritative procedure.
- Do not invent approval limits, KPI targets, retention periods, credentials, jurisdictional requirements, system names, manufacturer steps, or regulatory thresholds.

### Procedure — BQ-1252
<!-- id: control.bq-1252 -->

1. Resolve canonical industry/subindustry, business model, site/team context, exact role, task, trigger, systems/equipment, consequence class, and downstream handoff.
2. Classify each input as supplied fact, verified authority, organization-specific fact, inference, or unknown; record material unknowns explicitly.
3. Determine which unknowns block safe compilation versus which can remain placeholders without changing execution meaning.
4. Produce a context record that downstream role, authority, procedure, evidence, and KPI compilation can reference.
5. Re-run context resolution after changes to jurisdiction, facility/product/system scope, role authority, source version, or risk.

### Evidence Gate — BQ-1253
<!-- id: control.bq-1253 -->

- **PASS only if** the requirement is directly evidenced in the compiled role/procedure/metric record and another competent reader can identify the actor, trigger, decision boundary, evidence, and completion condition without guessing material facts.
- Authoritative claims require adequate source provenance and applicability evidence.
- If required source/currentness/organization authority evidence is unavailable, mark the affected portion **UNVERIFIED** or draft; do not silently pass it.

### Recovery — BQ-1254
<!-- id: control.bq-1254 -->

- Block authoritative or production-use claims for the affected portion.
- Downgrade authority classification when provenance is insufficient, surface unknowns, obtain/verify the missing source or organization fact where tools/evidence permit, and repair the smallest upstream ambiguity.
- Re-run affected decision-rights, evidence, KPI, risk, handoff, and change-control checks after repair.

### Regression — BQ-1255
<!-- id: control.bq-1255 -->

- Maintain **normal**, **ambiguous/edge**, and **failure/unavailable-evidence** fixtures.
- The ambiguous case must preserve unknown authority or applicability instead of inventing specificity.
- The failure case must trigger Recovery when a procedure is detailed but lacks evidence required for its claimed authority or completion state.
- Real operational failures should become regression fixtures when they expose a reusable process weakness.
