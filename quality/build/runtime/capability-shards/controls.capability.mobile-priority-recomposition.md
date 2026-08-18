<!-- GENERATED from source/controls/29-benchmark-driven-quality-hardening.md#controls.capability.mobile-priority-recomposition; canonical truth remains source/. -->

## Mobile Priority & Recomposition
<!-- id: controls.capability.mobile-priority-recomposition -->

**Targets:** RESPONSIVE_COMPOSITION.md  
**Requirement:** Require an explicit mobile priority map and task-preserving layout recomposition rather than desktop stacking or compression.

### Contract — BQ-1151
<!-- id: control.bq-1151 -->

- **MUST:** Require an explicit mobile priority map and task-preserving layout recomposition rather than desktop stacking or compression.
- Preserve higher-precedence requirements, truthful unknowns, and applicable artifact-specific floors.

### Procedure — BQ-1152
<!-- id: control.bq-1152 -->

1. Resolve the active artifact contract and affected P0/P1 user jobs.
2. Produce the required plan/evidence structure before claiming completion.
3. Exercise representative normal, edge, mobile/document/accessibility states as applicable.
4. Record direct evidence and affected quality dimensions.
5. Re-run after material repair.

### Evidence Gate — BQ-1153
<!-- id: control.bq-1153 -->

- **PASS only if** direct specification/render/runtime/document evidence demonstrates the requirement.
- Missing required evidence is **UNVERIFIED**, not PASS.
- Evidence must identify viewport/path/section/state and observed result.

### Recovery — BQ-1154
<!-- id: control.bq-1154 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate affected adjacent dimensions including genericity resistance.
- Never delete a requirement or hide task-critical content merely to remove a failure.

### Regression — BQ-1155
<!-- id: control.bq-1155 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Benchmark-derived failures must remain reproducible regression cases.
