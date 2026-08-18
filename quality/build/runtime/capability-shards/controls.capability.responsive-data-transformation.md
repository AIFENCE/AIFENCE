<!-- GENERATED from source/controls/29-benchmark-driven-quality-hardening.md#controls.capability.responsive-data-transformation; canonical truth remains source/. -->

## Responsive Data Transformation
<!-- id: controls.capability.responsive-data-transformation -->

**Targets:** RESPONSIVE_COMPOSITION.md  
**Requirement:** Give tables, comparison, charts, and dense lists an explicit mobile data strategy that preserves decision context and task completion.

### Contract — BQ-1161
<!-- id: control.bq-1161 -->

- **MUST:** Give tables, comparison, charts, and dense lists an explicit mobile data strategy that preserves decision context and task completion.
- Preserve higher-precedence requirements, truthful unknowns, and applicable artifact-specific floors.

### Procedure — BQ-1162
<!-- id: control.bq-1162 -->

1. Resolve the active artifact contract and affected P0/P1 user jobs.
2. Produce the required plan/evidence structure before claiming completion.
3. Exercise representative normal, edge, mobile/document/accessibility states as applicable.
4. Record direct evidence and affected quality dimensions.
5. Re-run after material repair.

### Evidence Gate — BQ-1163
<!-- id: control.bq-1163 -->

- **PASS only if** direct specification/render/runtime/document evidence demonstrates the requirement.
- Missing required evidence is **UNVERIFIED**, not PASS.
- Evidence must identify viewport/path/section/state and observed result.

### Recovery — BQ-1164
<!-- id: control.bq-1164 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate affected adjacent dimensions including genericity resistance.
- Never delete a requirement or hide task-critical content merely to remove a failure.

### Regression — BQ-1165
<!-- id: control.bq-1165 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Benchmark-derived failures must remain reproducible regression cases.
