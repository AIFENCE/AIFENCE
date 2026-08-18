<!-- GENERATED from source/controls/28-adversarial-critique-repair-quality-floors-and-benchmarking.md#controls.capability.repair-plan-prioritization; canonical truth remains source/. -->

## Repair Plan Prioritization
<!-- id: controls.capability.repair-plan-prioritization -->

**Targets:** CRITICS.md  
**Requirement:** Consolidate critic findings into a severity- and dependency-aware repair plan that fixes truth/safety/task correctness before genericity, component craft, and decorative polish.

### Contract — BQ-1131
<!-- id: control.bq-1131 -->

- **MUST:** Consolidate critic findings into a severity- and dependency-aware repair plan that fixes truth/safety/task correctness before genericity, component craft, and decorative polish.
- Inputs are the minimum project facts, resolved artifact contract, and upstream decisions needed for deterministic execution.
- Output is an explicit decision, compiled specification, evidence record, quality state, or benchmark artifact.
- Invariants: higher-precedence instructions control; unknown facts remain unknown; production intent cannot be silently weakened; evidence cannot be fabricated.
- Prohibited shortcut: treating a feature/component name, generic template, design intention, confidence, or unverified assumption as completion.

### Procedure — BQ-1132
<!-- id: control.bq-1132 -->

1. Confirm this capability is triggered by artifact contract, production mode, dependency, or evaluation protocol.
2. Gather minimum relevant facts and upstream compiled outputs; mark unknown/unavailable evidence explicitly.
3. Execute the requirement exactly.
4. Resolve conflicts using README precedence, artifact specificity, risk, accessibility, truthfulness, and maintainability.
5. Persist the result when later work depends on it.
6. Re-evaluate after material scope, artifact, feature, data, visual, responsive, implementation, or evidence changes.

### Evidence Gate — BQ-1133
<!-- id: control.bq-1133 -->

- **PASS only if** direct specification/artifact/runtime/render/benchmark evidence demonstrates the requirement.
- Evidence identifies what was checked and the observed result. “Looks good,” “should work,” and design intention do not pass.
- Direct runtime/render/measurement evidence outranks prose/source inference when applicable.
- Unavailable required evidence is **UNVERIFIED**, never PASS.

### Recovery — BQ-1134
<!-- id: control.bq-1134 -->

- Block dependent completion claims on FAIL.
- Correct the upstream contract, feature/component specification, fingerprint, implementation, evaluation method, or repair plan and re-run the Evidence Gate.
- If correction is impossible with available facts/tools, preserve the limitation and safest non-fabricating fallback.
- Never lower a quality target, delete an applicable state, weaken a floor, or disclose a benchmark condition merely to pass.

### Regression — BQ-1135
<!-- id: control.bq-1135 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence conditions.
- Normal must produce the intended result; edge must preserve ambiguity or deterministic tie-breaking; failure must trigger Recovery.
- Real failures should strengthen a reusable regression fixture or benchmark case rather than only patch one artifact.
