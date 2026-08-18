<!-- GENERATED from source/controls/29-benchmark-driven-quality-hardening.md#controls.capability.accessibility-evidence-matrix; canonical truth remains source/. -->

## Accessibility Evidence Matrix
<!-- id: controls.capability.accessibility-evidence-matrix -->

**Targets:** ACCESSIBILITY_EVIDENCE.md  
**Requirement:** Require observable accessibility evidence for critical paths instead of passing from static semantics or automated inference alone.

### Contract — BQ-1176
<!-- id: control.bq-1176 -->

- **MUST:** Require observable accessibility evidence for critical paths instead of passing from static semantics or automated inference alone.
- Preserve higher-precedence requirements, truthful unknowns, and applicable artifact-specific floors.

### Procedure — BQ-1177
<!-- id: control.bq-1177 -->

1. Resolve the active artifact contract and affected P0/P1 user jobs.
2. Produce the required plan/evidence structure before claiming completion.
3. Exercise representative normal, edge, mobile/document/accessibility states as applicable.
4. Record direct evidence and affected quality dimensions.
5. Re-run after material repair.

### Evidence Gate — BQ-1178
<!-- id: control.bq-1178 -->

- **PASS only if** direct specification/render/runtime/document evidence demonstrates the requirement.
- Missing required evidence is **UNVERIFIED**, not PASS.
- Evidence must identify viewport/path/section/state and observed result.

### Recovery — BQ-1179
<!-- id: control.bq-1179 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate affected adjacent dimensions including genericity resistance.
- Never delete a requirement or hide task-critical content merely to remove a failure.

### Regression — BQ-1180
<!-- id: control.bq-1180 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Benchmark-derived failures must remain reproducible regression cases.
