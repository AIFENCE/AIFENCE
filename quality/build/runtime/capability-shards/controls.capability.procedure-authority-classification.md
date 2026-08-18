<!-- GENERATED from source/controls/31-operational-procedure-compilation-authority-and-measurement.md#controls.capability.procedure-authority-classification; canonical truth remains source/. -->

## Procedure Authority Classification
<!-- id: controls.capability.procedure-authority-classification -->

**Targets:** PROCEDURE_AUTHORITY.md  
**Requirement:** Classify each material procedure as general guidance, organization draft, verified organization procedure, external authoritative requirement, or mixed, with truthful provenance and verification state.

### Contract — BQ-1261
<!-- id: control.bq-1261 -->

- **MUST:** Classify each material procedure as general guidance, organization draft, verified organization procedure, external authoritative requirement, or mixed, with truthful provenance and verification state.
- Preserve truthful unknowns, applicable professional/licensing boundaries, organization authority, external-source provenance, and proportionate evidence.
- A detailed generated procedure is not automatically an approved or authoritative procedure.
- Do not invent approval limits, KPI targets, retention periods, credentials, jurisdictional requirements, system names, manufacturer steps, or regulatory thresholds.

### Procedure — BQ-1262
<!-- id: control.bq-1262 -->

1. Classify the procedure and each material authority-bearing section as GENERAL_GUIDANCE, ORGANIZATION_DRAFT, VERIFIED_ORGANIZATION_PROCEDURE, EXTERNAL_AUTHORITATIVE_REQUIREMENT, or MIXED.
2. For every strong authority source, capture stable source ID, title, issuer/owner, scope, applicability basis, supplied/retrieved date, verification state, and version/effective/currentness evidence.
3. For MIXED procedures, build an authority_map covering every material step/section; strong entries must reference verified authority_source_ids.
4. Separate source requirement, organization control, and AIFENCE recommendation; do not let nearby verified content confer authority on draft guidance.
5. If applicability/currentness cannot be proven, downgrade the affected section to draft/general guidance or keep it UNVERIFIED and create a verification task.

### Evidence Gate — BQ-1263
<!-- id: control.bq-1263 -->

- **PASS only if** the requirement is directly evidenced in the compiled role/procedure/metric record and another competent reader can identify the actor, trigger, decision boundary, evidence, and completion condition without guessing material facts.
- Authoritative claims require adequate source provenance and applicability evidence.
- If required source/currentness/organization authority evidence is unavailable, mark the affected portion **UNVERIFIED** or draft; do not silently pass it.

### Recovery — BQ-1264
<!-- id: control.bq-1264 -->

- Block authoritative or production-use claims for the affected portion.
- Downgrade authority classification when provenance is insufficient, surface unknowns, obtain/verify the missing source or organization fact where tools/evidence permit, and repair the smallest upstream ambiguity.
- Re-run affected decision-rights, evidence, KPI, risk, handoff, and change-control checks after repair.

### Regression — BQ-1265
<!-- id: control.bq-1265 -->

- Maintain **normal**, **ambiguous/edge**, and **failure/unavailable-evidence** fixtures.
- The ambiguous case must preserve unknown authority or applicability instead of inventing specificity.
- The failure case must trigger Recovery when a procedure is detailed but lacks evidence required for its claimed authority or completion state.
- Real operational failures should become regression fixtures when they expose a reusable process weakness.
