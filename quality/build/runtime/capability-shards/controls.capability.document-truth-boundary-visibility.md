<!-- GENERATED from source/controls/30-usability-visual-finish-truth-and-quality-closure.md#controls.capability.document-truth-boundary-visibility; canonical truth remains source/. -->

## Document Truth Boundary Visibility
<!-- id: controls.capability.document-truth-boundary-visibility -->

**Targets:** TRUTH_BOUNDARIES.md  
**Requirement:** Require documents to visibly distinguish supplied or verified evidence from assumptions, unknowns, interpretations, and recommendations where ambiguity is material.

### Contract — BQ-1231
<!-- id: control.bq-1231 -->

- **MUST:** Require documents to visibly distinguish supplied or verified evidence from assumptions, unknowns, interpretations, and recommendations where ambiguity is material.
- Preserve truthful unknowns, active artifact contracts, accessibility, responsive task completion, implementation correctness, and genericity resistance.

### Procedure — BQ-1232
<!-- id: control.bq-1232 -->

1. Resolve the active artifact contract and P0/P1 user jobs or decision paths.
2. Identify the exact failure mechanism observed in evidence rather than adding generic polish.
3. Apply the smallest upstream repair that removes avoidable friction or ambiguity.
4. Render/exercise representative desktop, narrow viewport, keyboard, error/recovery, and document evidence states as applicable.
5. Record direct evidence and re-run adjacent critics/floors after material repair.

### Evidence Gate — BQ-1233
<!-- id: control.bq-1233 -->

- **PASS only if** direct rendered/runtime/document evidence demonstrates the requirement on the affected critical path.
- A proxy metric that cannot measure the active quality floor is non-dispositive.
- Missing required evidence is **UNVERIFIED**, not PASS.

### Recovery — BQ-1234
<!-- id: control.bq-1234 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate usability, truth, visual quality, responsive/accessibility behavior, implementation correctness, and genericity as affected.
- Never remove task-critical information, provenance, or differentiated structure merely to improve a local score.

### Regression — BQ-1235
<!-- id: control.bq-1235 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Preserve benchmark-derived failures as regressions and verify that fixes do not regress genericity or previously passing Revision 1.3 hardening gates.
