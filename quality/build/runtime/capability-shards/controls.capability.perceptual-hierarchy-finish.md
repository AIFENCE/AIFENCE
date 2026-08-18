<!-- GENERATED from source/controls/30-usability-visual-finish-truth-and-quality-closure.md#controls.capability.perceptual-hierarchy-finish; canonical truth remains source/. -->

## Perceptual Hierarchy Finish
<!-- id: controls.capability.perceptual-hierarchy-finish -->

**Targets:** VISUAL_FINISH.md  
**Requirement:** Require rendered critical views to demonstrate intentional perceptual hierarchy and remove equal-weight or visibly unfinished regions.

### Contract — BQ-1221
<!-- id: control.bq-1221 -->

- **MUST:** Require rendered critical views to demonstrate intentional perceptual hierarchy and remove equal-weight or visibly unfinished regions.
- Preserve truthful unknowns, active artifact contracts, accessibility, responsive task completion, implementation correctness, and genericity resistance.

### Procedure — BQ-1222
<!-- id: control.bq-1222 -->

1. Resolve the active artifact contract and P0/P1 user jobs or decision paths.
2. Identify the exact failure mechanism observed in evidence rather than adding generic polish.
3. Apply the smallest upstream repair that removes avoidable friction or ambiguity.
4. Render/exercise representative desktop, narrow viewport, keyboard, error/recovery, and document evidence states as applicable.
5. Record direct evidence and re-run adjacent critics/floors after material repair.

### Evidence Gate — BQ-1223
<!-- id: control.bq-1223 -->

- **PASS only if** direct rendered/runtime/document evidence demonstrates the requirement on the affected critical path.
- A proxy metric that cannot measure the active quality floor is non-dispositive.
- Missing required evidence is **UNVERIFIED**, not PASS.

### Recovery — BQ-1224
<!-- id: control.bq-1224 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate usability, truth, visual quality, responsive/accessibility behavior, implementation correctness, and genericity as affected.
- Never remove task-critical information, provenance, or differentiated structure merely to improve a local score.

### Regression — BQ-1225
<!-- id: control.bq-1225 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Preserve benchmark-derived failures as regressions and verify that fixes do not regress genericity or previously passing Revision 1.3 hardening gates.
