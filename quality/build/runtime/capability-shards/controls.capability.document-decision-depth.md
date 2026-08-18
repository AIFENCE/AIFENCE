<!-- GENERATED from source/controls/29-benchmark-driven-quality-hardening.md#controls.capability.document-decision-depth; canonical truth remains source/. -->

## Document Decision Depth
<!-- id: controls.capability.document-decision-depth -->

**Targets:** DOCUMENT_CRAFT.md  
**Requirement:** Evaluate substantial documents through decision/evidence depth, traceability, risks, alternatives, recommendation, and action closure rather than UI feature counts.

### Contract — BQ-1166
<!-- id: control.bq-1166 -->

- **MUST:** Evaluate substantial documents through decision/evidence depth, traceability, risks, alternatives, recommendation, and action closure rather than UI feature counts.
- Preserve higher-precedence requirements, truthful unknowns, and applicable artifact-specific floors.

### Procedure — BQ-1167
<!-- id: control.bq-1167 -->

1. Resolve the active artifact contract and affected P0/P1 user jobs.
2. Produce the required plan/evidence structure before claiming completion.
3. Exercise representative normal, edge, mobile/document/accessibility states as applicable.
4. Record direct evidence and affected quality dimensions.
5. Re-run after material repair.

### Evidence Gate — BQ-1168
<!-- id: control.bq-1168 -->

- **PASS only if** direct specification/render/runtime/document evidence demonstrates the requirement.
- Missing required evidence is **UNVERIFIED**, not PASS.
- Evidence must identify viewport/path/section/state and observed result.

### Recovery — BQ-1169
<!-- id: control.bq-1169 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate affected adjacent dimensions including genericity resistance.
- Never delete a requirement or hide task-critical content merely to remove a failure.

### Regression — BQ-1170
<!-- id: control.bq-1170 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Benchmark-derived failures must remain reproducible regression cases.
