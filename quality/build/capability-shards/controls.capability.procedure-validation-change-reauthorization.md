<!-- GENERATED from source/controls/31-operational-procedure-compilation-authority-and-measurement.md#controls.capability.procedure-validation-change-reauthorization; canonical truth remains source/. -->

## Procedure Validation, Change & Reauthorization
<!-- id: controls.capability.procedure-validation-change-reauthorization -->

**Targets:** PROCEDURE_AUTHORITY.md / OPERATIONAL_PROCEDURE_COMPILER.md  
**Requirement:** Require validation, approval state, effective scope, change triggers, source-currentness review, supersession, and reauthorization for material procedure changes.

### Contract — BQ-1296
<!-- id: control.bq-1296 -->

- **MUST:** Require validation, approval state, effective scope, change triggers, source-currentness review, supersession, and reauthorization for material procedure changes.
- Preserve truthful unknowns, applicable professional/licensing boundaries, organization authority, external-source provenance, and proportionate evidence.
- A detailed generated procedure is not automatically an approved or authoritative procedure.
- Do not invent approval limits, KPI targets, retention periods, credentials, jurisdictional requirements, system names, manufacturer steps, or regulatory thresholds.

### Procedure — BQ-1297
<!-- id: control.bq-1297 -->

1. Set procedure_version, procedure_owner, approval_state, source versions/currentness, and validation plan explicitly; generated content remains DRAFT absent approval evidence.
2. Require approver plus approval_evidence for APPROVED/EFFECTIVE states and effective_date for EFFECTIVE; record supersession linkage for SUPERSEDED.
3. Define review/reauthorization triggers for material changes to law/policy/source version, jurisdiction/scope, systems/equipment, role authority, incidents, or control failures.
4. On change, identify affected steps/decisions/evidence/KPIs and revalidate them rather than treating version metadata as sufficient change control.
5. Prevent stale or conflicted authority from remaining silently effective: suspend/downgrade affected claims, preserve conflict evidence, and route to the responsible approval owner.

### Evidence Gate — BQ-1298
<!-- id: control.bq-1298 -->

- **PASS only if** the requirement is directly evidenced in the compiled role/procedure/metric record and another competent reader can identify the actor, trigger, decision boundary, evidence, and completion condition without guessing material facts.
- Authoritative claims require adequate source provenance and applicability evidence.
- If required source/currentness/organization authority evidence is unavailable, mark the affected portion **UNVERIFIED** or draft; do not silently pass it.

### Recovery — BQ-1299
<!-- id: control.bq-1299 -->

- Block authoritative or production-use claims for the affected portion.
- Downgrade authority classification when provenance is insufficient, surface unknowns, obtain/verify the missing source or organization fact where tools/evidence permit, and repair the smallest upstream ambiguity.
- Re-run affected decision-rights, evidence, KPI, risk, handoff, and change-control checks after repair.

### Regression — BQ-1300
<!-- id: control.bq-1300 -->

- Maintain **normal**, **ambiguous/edge**, and **failure/unavailable-evidence** fixtures.
- The ambiguous case must preserve unknown authority or applicability instead of inventing specificity.
- The failure case must trigger Recovery when a procedure is detailed but lacks evidence required for its claimed authority or completion state.
- Real operational failures should become regression fixtures when they expose a reusable process weakness.
