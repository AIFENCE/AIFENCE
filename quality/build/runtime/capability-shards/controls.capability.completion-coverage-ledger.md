<!-- GENERATED from source/controls/29-benchmark-driven-quality-hardening.md#controls.capability.completion-coverage-ledger; canonical truth remains source/. -->

## Completion Coverage Ledger
<!-- id: controls.capability.completion-coverage-ledger -->

**Targets:** COMPLETENESS.md  
**Requirement:** Track P0/P1 user-job, path, state, responsive, accessibility, truth, dependency, and evidence closure so omissions cannot hide behind aggregate completeness.

### Contract — BQ-1186
<!-- id: control.bq-1186 -->

- **MUST:** Track P0/P1 user-job, path, state, responsive, accessibility, truth, dependency, and evidence closure so omissions cannot hide behind aggregate completeness.
- Preserve higher-precedence requirements, truthful unknowns, and applicable artifact-specific floors.

### Procedure — BQ-1187
<!-- id: control.bq-1187 -->

1. Resolve the active artifact contract and affected P0/P1 user jobs.
2. Produce the required plan/evidence structure before claiming completion.
3. Exercise representative normal, edge, mobile/document/accessibility states as applicable.
4. Record direct evidence and affected quality dimensions.
5. Re-run after material repair.

### Evidence Gate — BQ-1188
<!-- id: control.bq-1188 -->

- **PASS only if** direct specification/render/runtime/document evidence demonstrates the requirement.
- Missing required evidence is **UNVERIFIED**, not PASS.
- Evidence must identify viewport/path/section/state and observed result.

### Recovery — BQ-1189
<!-- id: control.bq-1189 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate affected adjacent dimensions including genericity resistance.
- Never delete a requirement or hide task-critical content merely to remove a failure.

### Regression — BQ-1190
<!-- id: control.bq-1190 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Benchmark-derived failures must remain reproducible regression cases.
