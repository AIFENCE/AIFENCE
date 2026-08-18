<!-- GENERATED from source/controls/07-brand-strategy-and-creative-direction.md#controls.capability.three-direction-exploration-quality; canonical truth remains source/. -->

## Three-direction exploration quality
<!-- id: controls.capability.three-direction-exploration-quality -->

**Targets:** CREATIVE.md  
**Requirement:** Require concept directions to differ structurally, typographically, compositionally, and emotionally rather than merely changing colors.

### Contract — BQ-0246
<!-- id: control.bq-0246 -->

- **MUST:** Require concept directions to differ structurally, typographically, compositionally, and emotionally rather than merely changing colors.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0247
<!-- id: control.bq-0247 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Require concept directions to differ structurally, typographically, compositionally, and emotionally rather than merely changing colors.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0248
<!-- id: control.bq-0248 -->

- **PASS only if** the requirement is demonstrated by concept alternatives, selection rubric, brand fingerprint, or rendered creative evidence.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0249
<!-- id: control.bq-0249 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0250
<!-- id: control.bq-0250 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.
