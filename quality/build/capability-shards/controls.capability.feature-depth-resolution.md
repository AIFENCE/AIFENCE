<!-- GENERATED from source/controls/26-feature-component-craft.md#controls.capability.feature-depth-resolution; canonical truth remains source/. -->

## Feature Depth Resolution
<!-- id: controls.capability.feature-depth-resolution -->

**Targets:** CRAFT.md / FEATURES.md / STRUCTURE.md  
**Requirement:** Define high-value features by purpose, user job, priority, information, actions, interaction model, data/truth semantics, dependencies, decision support when applicable, and observable acceptance criteria rather than feature names alone.

### Contract — BQ-1026
<!-- id: control.bq-1026 -->

- **MUST:** Define high-value features by purpose, user job, priority, information, actions, interaction model, data/truth semantics, dependencies, decision support when applicable, and observable acceptance criteria rather than feature names alone.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, feature noun, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-1027
<!-- id: control.bq-1027 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence; distinguish known, inferred, unknown, and sample/demo inputs.
3. Apply the requirement exactly: Define high-value features by purpose, user job, priority, information, actions, interaction model, data/truth semantics, dependencies, decision support when applicable, and observable acceptance criteria rather than feature names alone.
4. Resolve ties using README precedence, user/business goal fit, accessibility, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in project decision state or artifact evidence when later work depends on it.
6. Re-evaluate after material changes to scope, audience, feature set, device behavior, delivery mode, design direction, or evidence.

### Evidence Gate — BQ-1028
<!-- id: control.bq-1028 -->

- **PASS only if** the requirement is demonstrated by a feature/component contract, source implementation, runtime behavior, rendered captures, scenario checks, or other direct artifact evidence appropriate to the capability.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct runtime/rendered evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-1029
<!-- id: control.bq-1029 -->

- On failure or insufficient evidence, block completion claims that depend on this capability.
- Correct the underlying feature definition, component anatomy, visual system, interaction behavior, responsive treatment, or implementation as applicable, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting evidence, or lower the production/quality target to make the gate pass.

### Regression — BQ-1030
<!-- id: control.bq-1030 -->

- Maintain three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must preserve ambiguity or use deterministic tie-breaking; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability should strengthen a reusable regression fixture rather than produce only a one-off artifact patch.
