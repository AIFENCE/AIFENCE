<!-- GENERATED from source/controls/31-operational-procedure-compilation-authority-and-measurement.md#controls.capability.role-accountability-compilation; canonical truth remains source/. -->

## Role & Accountability Compilation
<!-- id: controls.capability.role-accountability-compilation -->

**Targets:** OPERATIONAL_PROCEDURE_COMPILER.md / JOBS.md  
**Requirement:** Compile purpose, accountabilities, scope boundaries, inputs, outputs, decisions, interfaces, evidence duties, KPI ownership, and explicit exclusions rather than relying on a title-only role description.

### Contract — BQ-1256
<!-- id: control.bq-1256 -->

- **MUST:** Compile purpose, accountabilities, scope boundaries, inputs, outputs, decisions, interfaces, evidence duties, KPI ownership, and explicit exclusions rather than relying on a title-only role description.
- Preserve truthful unknowns, applicable professional/licensing boundaries, organization authority, external-source provenance, and proportionate evidence.
- A detailed generated procedure is not automatically an approved or authoritative procedure.
- Do not invent approval limits, KPI targets, retention periods, credentials, jurisdictional requirements, system names, manufacturer steps, or regulatory thresholds.

### Procedure — BQ-1257
<!-- id: control.bq-1257 -->

1. Start from the exact role and task, then enumerate accountabilities, scope boundary, inputs, outputs, owned decisions, recommended decisions, interfaces, evidence duties, KPI ownership, and exclusions.
2. Distinguish responsibility from authority: do not infer licensure, system permission, spending/approval rights, credentials, or delegation from the title.
3. Map each consequential responsibility to either an owned decision, an approval dependency, a consult/inform interface, or an explicit exclusion.
4. Record unresolved authority/credential facts under authority_unknowns rather than filling them with defaults.
5. Check that the role specification supports the procedure steps and handoffs without orphan responsibilities or title-only ambiguity.

### Evidence Gate — BQ-1258
<!-- id: control.bq-1258 -->

- **PASS only if** the requirement is directly evidenced in the compiled role/procedure/metric record and another competent reader can identify the actor, trigger, decision boundary, evidence, and completion condition without guessing material facts.
- Authoritative claims require adequate source provenance and applicability evidence.
- If required source/currentness/organization authority evidence is unavailable, mark the affected portion **UNVERIFIED** or draft; do not silently pass it.

### Recovery — BQ-1259
<!-- id: control.bq-1259 -->

- Block authoritative or production-use claims for the affected portion.
- Downgrade authority classification when provenance is insufficient, surface unknowns, obtain/verify the missing source or organization fact where tools/evidence permit, and repair the smallest upstream ambiguity.
- Re-run affected decision-rights, evidence, KPI, risk, handoff, and change-control checks after repair.

### Regression — BQ-1260
<!-- id: control.bq-1260 -->

- Maintain **normal**, **ambiguous/edge**, and **failure/unavailable-evidence** fixtures.
- The ambiguous case must preserve unknown authority or applicability instead of inventing specificity.
- The failure case must trigger Recovery when a procedure is detailed but lacks evidence required for its claimed authority or completion state.
- Real operational failures should become regression fixtures when they expose a reusable process weakness.
