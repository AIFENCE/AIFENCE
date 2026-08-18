<!-- GENERATED from source/controls/29-benchmark-driven-quality-hardening.md#controls.capability.dense-mobile-control-compression; canonical truth remains source/. -->

## Dense Mobile Control Compression
<!-- id: controls.capability.dense-mobile-control-compression -->

**Targets:** RESPONSIVE_COMPOSITION.md  
**Requirement:** Transform search/filter/date/view/bulk/primary-action toolbars into a narrow-screen interaction model without clipping, crowding, or hidden critical state.

### Contract — BQ-1156
<!-- id: control.bq-1156 -->

- **MUST:** Transform search/filter/date/view/bulk/primary-action toolbars into a narrow-screen interaction model without clipping, crowding, or hidden critical state.
- Preserve higher-precedence requirements, truthful unknowns, and applicable artifact-specific floors.

### Procedure — BQ-1157
<!-- id: control.bq-1157 -->

1. Resolve the active artifact contract and affected P0/P1 user jobs.
2. Produce the required plan/evidence structure before claiming completion.
3. Exercise representative normal, edge, mobile/document/accessibility states as applicable.
4. Record direct evidence and affected quality dimensions.
5. Re-run after material repair.

### Evidence Gate — BQ-1158
<!-- id: control.bq-1158 -->

- **PASS only if** direct specification/render/runtime/document evidence demonstrates the requirement.
- Missing required evidence is **UNVERIFIED**, not PASS.
- Evidence must identify viewport/path/section/state and observed result.

### Recovery — BQ-1159
<!-- id: control.bq-1159 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate affected adjacent dimensions including genericity resistance.
- Never delete a requirement or hide task-critical content merely to remove a failure.

### Regression — BQ-1160
<!-- id: control.bq-1160 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Benchmark-derived failures must remain reproducible regression cases.
