<!-- GENERATED from source/controls/29-benchmark-driven-quality-hardening.md#controls.capability.cross-dimension-repair-preservation; canonical truth remains source/. -->

## Cross-Dimension Repair Preservation
<!-- id: controls.capability.cross-dimension-repair-preservation -->

**Targets:** CRITICS.md / GENERICITY.md / QUALITY_FLOORS.md  
**Requirement:** After targeted repairs, revalidate adjacent quality dimensions and preserve genericity resistance; a fix cannot pass by creating template sameness, truth regression, or task loss.

### Contract — BQ-1196
<!-- id: control.bq-1196 -->

- **MUST:** After targeted repairs, revalidate adjacent quality dimensions and preserve genericity resistance; a fix cannot pass by creating template sameness, truth regression, or task loss.
- Preserve higher-precedence requirements, truthful unknowns, and applicable artifact-specific floors.

### Procedure — BQ-1197
<!-- id: control.bq-1197 -->

1. Resolve the active artifact contract and affected P0/P1 user jobs.
2. Produce the required plan/evidence structure before claiming completion.
3. Exercise representative normal, edge, mobile/document/accessibility states as applicable.
4. Record direct evidence and affected quality dimensions.
5. Re-run after material repair.

### Evidence Gate — BQ-1198
<!-- id: control.bq-1198 -->

- **PASS only if** direct specification/render/runtime/document evidence demonstrates the requirement.
- Missing required evidence is **UNVERIFIED**, not PASS.
- Evidence must identify viewport/path/section/state and observed result.

### Recovery — BQ-1199
<!-- id: control.bq-1199 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate affected adjacent dimensions including genericity resistance.
- Never delete a requirement or hide task-critical content merely to remove a failure.

### Regression — BQ-1200
<!-- id: control.bq-1200 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Benchmark-derived failures must remain reproducible regression cases.
