<!-- GENERATED from source/controls/31-operational-procedure-compilation-authority-and-measurement.md#controls.capability.kpi-definition-metric-governance; canonical truth remains source/. -->

## KPI Definition & Metric Governance
<!-- id: controls.capability.kpi-definition-metric-governance -->

**Targets:** KPI_GOVERNANCE.md  
**Requirement:** Define reproducible KPI formulas, scope, sources, ownership, cadence, target provenance, balancing measures, and response rules without inventing targets or thresholds.

### Contract — BQ-1291
<!-- id: control.bq-1291 -->

- **MUST:** Define reproducible KPI formulas, scope, sources, ownership, cadence, target provenance, balancing measures, and response rules without inventing targets or thresholds.
- Preserve truthful unknowns, applicable professional/licensing boundaries, organization authority, external-source provenance, and proportionate evidence.
- A detailed generated procedure is not automatically an approved or authoritative procedure.
- Do not invent approval limits, KPI targets, retention periods, credentials, jurisdictional requirements, system names, manufacturer steps, or regulatory thresholds.

### Procedure — BQ-1292
<!-- id: control.bq-1292 -->

1. Identify the operational decision each KPI supports before selecting the metric.
2. Define operational meaning, population/scope, formula/calculation rule, numerator/denominator when applicable, inclusions/exclusions, time window, source systems/events, metric/data owners, calculation frequency, and review cadence.
3. If material calculation facts remain unknown, set calculation_state to UNRESOLVED and list open_unknowns; do not label the KPI production-defined.
4. Resolve target_provenance independently from calculation definition. If no verified target exists, use ORGANIZATION_SPECIFIC_NOT_SUPPLIED rather than inventing a target/threshold.
5. Add audit/reconciliation evidence, balancing-measure consideration, data-quality risk, and gaming/perverse-incentive review; test whether another competent person can reproduce the metric without guessing.

### Evidence Gate — BQ-1293
<!-- id: control.bq-1293 -->

- **PASS only if** the requirement is directly evidenced in the compiled role/procedure/metric record and another competent reader can identify the actor, trigger, decision boundary, evidence, and completion condition without guessing material facts.
- Authoritative claims require adequate source provenance and applicability evidence.
- If required source/currentness/organization authority evidence is unavailable, mark the affected portion **UNVERIFIED** or draft; do not silently pass it.

### Recovery — BQ-1294
<!-- id: control.bq-1294 -->

- Block authoritative or production-use claims for the affected portion.
- Downgrade authority classification when provenance is insufficient, surface unknowns, obtain/verify the missing source or organization fact where tools/evidence permit, and repair the smallest upstream ambiguity.
- Re-run affected decision-rights, evidence, KPI, risk, handoff, and change-control checks after repair.

### Regression — BQ-1295
<!-- id: control.bq-1295 -->

- Maintain **normal**, **ambiguous/edge**, and **failure/unavailable-evidence** fixtures.
- The ambiguous case must preserve unknown authority or applicability instead of inventing specificity.
- The failure case must trigger Recovery when a procedure is detailed but lacks evidence required for its claimed authority or completion state.
- Real operational failures should become regression fixtures when they expose a reusable process weakness.
