<!-- GENERATED from source/controls/30-usability-visual-finish-truth-and-quality-closure.md#controls.capability.action-hierarchy-progressive-disclosure; canonical truth remains source/. -->

## Action Hierarchy & Progressive Disclosure
<!-- id: controls.capability.action-hierarchy-progressive-disclosure -->

**Targets:** USABILITY_CLOSURE.md  
**Requirement:** Require clear primary/secondary/contextual/destructive action hierarchy and progressive disclosure that never hides the only P0 route.

### Contract — BQ-1206
<!-- id: control.bq-1206 -->

- **MUST:** Require clear primary/secondary/contextual/destructive action hierarchy and progressive disclosure that never hides the only P0 route.
- Preserve truthful unknowns, active artifact contracts, accessibility, responsive task completion, implementation correctness, and genericity resistance.

### Procedure — BQ-1207
<!-- id: control.bq-1207 -->

1. Resolve the active artifact contract and P0/P1 user jobs or decision paths.
2. Identify the exact failure mechanism observed in evidence rather than adding generic polish.
3. Apply the smallest upstream repair that removes avoidable friction or ambiguity.
4. Render/exercise representative desktop, narrow viewport, keyboard, error/recovery, and document evidence states as applicable.
5. Record direct evidence and re-run adjacent critics/floors after material repair.

### Evidence Gate — BQ-1208
<!-- id: control.bq-1208 -->

- **PASS only if** direct rendered/runtime/document evidence demonstrates the requirement on the affected critical path.
- A proxy metric that cannot measure the active quality floor is non-dispositive.
- Missing required evidence is **UNVERIFIED**, not PASS.

### Recovery — BQ-1209
<!-- id: control.bq-1209 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate usability, truth, visual quality, responsive/accessibility behavior, implementation correctness, and genericity as affected.
- Never remove task-critical information, provenance, or differentiated structure merely to improve a local score.

### Regression — BQ-1210
<!-- id: control.bq-1210 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Preserve benchmark-derived failures as regressions and verify that fixes do not regress genericity or previously passing Revision 1.3 hardening gates.
