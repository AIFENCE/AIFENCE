<!-- GENERATED from source/controls/16-conversion-trust-and-business-outcomes.md#controls.capability.conversion-path-model; canonical truth remains source/. -->

## Conversion-path model
<!-- id: controls.capability.conversion-path-model -->

**Targets:** CREATIVE.md / FEATURES.md  
**Requirement:** Map primary and secondary conversion paths including commitment level, required proof, friction, and post-action expectation.

### Contract — BQ-0601
<!-- id: control.bq-0601 -->

- **MUST:** Map primary and secondary conversion paths including commitment level, required proof, friction, and post-action expectation.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0602
<!-- id: control.bq-0602 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Map primary and secondary conversion paths including commitment level, required proof, friction, and post-action expectation.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0603
<!-- id: control.bq-0603 -->

- **PASS only if** the requirement is demonstrated by conversion map, proof/trust evidence, form-friction review, CTA hierarchy, or post-conversion state.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0604
<!-- id: control.bq-0604 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0605
<!-- id: control.bq-0605 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.
