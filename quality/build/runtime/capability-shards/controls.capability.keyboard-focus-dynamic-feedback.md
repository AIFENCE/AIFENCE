<!-- GENERATED from source/controls/29-benchmark-driven-quality-hardening.md#controls.capability.keyboard-focus-dynamic-feedback; canonical truth remains source/. -->

## Keyboard Focus & Dynamic Feedback
<!-- id: controls.capability.keyboard-focus-dynamic-feedback -->

**Targets:** ACCESSIBILITY_EVIDENCE.md  
**Requirement:** Verify keyboard completion, visible/logical focus, focus entry/return, validation association, and programmatic status/error feedback on critical paths.

### Contract — BQ-1181
<!-- id: control.bq-1181 -->

- **MUST:** Verify keyboard completion, visible/logical focus, focus entry/return, validation association, and programmatic status/error feedback on critical paths.
- Preserve higher-precedence requirements, truthful unknowns, and applicable artifact-specific floors.

### Procedure — BQ-1182
<!-- id: control.bq-1182 -->

1. Resolve the active artifact contract and affected P0/P1 user jobs.
2. Produce the required plan/evidence structure before claiming completion.
3. Exercise representative normal, edge, mobile/document/accessibility states as applicable.
4. Record direct evidence and affected quality dimensions.
5. Re-run after material repair.

### Evidence Gate — BQ-1183
<!-- id: control.bq-1183 -->

- **PASS only if** direct specification/render/runtime/document evidence demonstrates the requirement.
- Missing required evidence is **UNVERIFIED**, not PASS.
- Evidence must identify viewport/path/section/state and observed result.

### Recovery — BQ-1184
<!-- id: control.bq-1184 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate affected adjacent dimensions including genericity resistance.
- Never delete a requirement or hide task-critical content merely to remove a failure.

### Regression — BQ-1185
<!-- id: control.bq-1185 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Benchmark-derived failures must remain reproducible regression cases.
