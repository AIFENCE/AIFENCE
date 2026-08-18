<!-- GENERATED from source/controls/30-usability-visual-finish-truth-and-quality-closure.md#controls.capability.feedback-recovery-legibility; canonical truth remains source/. -->

## Feedback & Recovery Legibility
<!-- id: controls.capability.feedback-recovery-legibility -->

**Targets:** USABILITY_CLOSURE.md  
**Requirement:** Require consequential actions to expose pending/success/error state and preserve a clear recovery or continuation path.

### Contract — BQ-1216
<!-- id: control.bq-1216 -->

- **MUST:** Require consequential actions to expose pending/success/error state and preserve a clear recovery or continuation path.
- Preserve truthful unknowns, active artifact contracts, accessibility, responsive task completion, implementation correctness, and genericity resistance.

### Procedure — BQ-1217
<!-- id: control.bq-1217 -->

1. Resolve the active artifact contract and P0/P1 user jobs or decision paths.
2. Identify the exact failure mechanism observed in evidence rather than adding generic polish.
3. Apply the smallest upstream repair that removes avoidable friction or ambiguity.
4. Render/exercise representative desktop, narrow viewport, keyboard, error/recovery, and document evidence states as applicable.
5. Record direct evidence and re-run adjacent critics/floors after material repair.

### Evidence Gate — BQ-1218
<!-- id: control.bq-1218 -->

- **PASS only if** direct rendered/runtime/document evidence demonstrates the requirement on the affected critical path.
- A proxy metric that cannot measure the active quality floor is non-dispositive.
- Missing required evidence is **UNVERIFIED**, not PASS.

### Recovery — BQ-1219
<!-- id: control.bq-1219 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate usability, truth, visual quality, responsive/accessibility behavior, implementation correctness, and genericity as affected.
- Never remove task-critical information, provenance, or differentiated structure merely to improve a local score.

### Regression — BQ-1220
<!-- id: control.bq-1220 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Preserve benchmark-derived failures as regressions and verify that fixes do not regress genericity or previously passing Revision 1.3 hardening gates.
