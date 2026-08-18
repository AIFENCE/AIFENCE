<!-- GENERATED from source/controls/30-usability-visual-finish-truth-and-quality-closure.md#controls.capability.typographic-spatial-surface-calibration; canonical truth remains source/. -->

## Typographic Spatial Surface Calibration
<!-- id: controls.capability.typographic-spatial-surface-calibration -->

**Targets:** VISUAL_FINISH.md  
**Requirement:** Require final optical calibration of typography, spacing, surfaces, icon/control alignment, media treatment, and cross-viewport rhythm.

### Contract — BQ-1226
<!-- id: control.bq-1226 -->

- **MUST:** Require final optical calibration of typography, spacing, surfaces, icon/control alignment, media treatment, and cross-viewport rhythm.
- Preserve truthful unknowns, active artifact contracts, accessibility, responsive task completion, implementation correctness, and genericity resistance.

### Procedure — BQ-1227
<!-- id: control.bq-1227 -->

1. Resolve the active artifact contract and P0/P1 user jobs or decision paths.
2. Identify the exact failure mechanism observed in evidence rather than adding generic polish.
3. Apply the smallest upstream repair that removes avoidable friction or ambiguity.
4. Render/exercise representative desktop, narrow viewport, keyboard, error/recovery, and document evidence states as applicable.
5. Record direct evidence and re-run adjacent critics/floors after material repair.

### Evidence Gate — BQ-1228
<!-- id: control.bq-1228 -->

- **PASS only if** direct rendered/runtime/document evidence demonstrates the requirement on the affected critical path.
- A proxy metric that cannot measure the active quality floor is non-dispositive.
- Missing required evidence is **UNVERIFIED**, not PASS.

### Recovery — BQ-1229
<!-- id: control.bq-1229 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate usability, truth, visual quality, responsive/accessibility behavior, implementation correctness, and genericity as affected.
- Never remove task-critical information, provenance, or differentiated structure merely to improve a local score.

### Regression — BQ-1230
<!-- id: control.bq-1230 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Preserve benchmark-derived failures as regressions and verify that fixes do not regress genericity or previously passing Revision 1.3 hardening gates.
