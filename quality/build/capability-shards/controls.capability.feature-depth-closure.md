<!-- GENERATED from source/controls/29-benchmark-driven-quality-hardening.md#controls.capability.feature-depth-closure; canonical truth remains source/. -->

## Feature Depth Closure
<!-- id: controls.capability.feature-depth-closure -->

**Targets:** FEATURE_DEPTH.md  
**Requirement:** Require production P0/P1 features to close information, action, state/recovery, responsive, accessibility, dependency, acceptance, and applicable buyer-decision/workflow integration dimensions.

### Contract — BQ-1191
<!-- id: control.bq-1191 -->

- **MUST:** Require production P0/P1 features to close information, action, state/recovery, responsive, accessibility, dependency, acceptance, and applicable buyer-decision/workflow integration dimensions.
- Preserve higher-precedence requirements, truthful unknowns, and applicable artifact-specific floors.

### Procedure — BQ-1192
<!-- id: control.bq-1192 -->

1. Resolve the active artifact contract and affected P0/P1 user jobs.
2. Produce the required plan/evidence structure before claiming completion.
3. Exercise representative normal, edge, mobile/document/accessibility states as applicable.
4. Record direct evidence and affected quality dimensions.
5. Re-run after material repair.

### Evidence Gate — BQ-1193
<!-- id: control.bq-1193 -->

- **PASS only if** direct specification/render/runtime/document evidence demonstrates the requirement.
- Missing required evidence is **UNVERIFIED**, not PASS.
- Evidence must identify viewport/path/section/state and observed result.

### Recovery — BQ-1194
<!-- id: control.bq-1194 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate affected adjacent dimensions including genericity resistance.
- Never delete a requirement or hide task-critical content merely to remove a failure.

### Regression — BQ-1195
<!-- id: control.bq-1195 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Benchmark-derived failures must remain reproducible regression cases.
