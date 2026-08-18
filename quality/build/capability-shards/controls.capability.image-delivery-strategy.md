<!-- GENERATED from source/controls/21-performance-reliability-and-resource-budgets.md#controls.capability.image-delivery-strategy; canonical truth remains source/. -->

## Image-delivery strategy
<!-- id: controls.capability.image-delivery-strategy -->

**Targets:** ASSETS.md  
**Requirement:** Choose formats, dimensions, compression, responsive sources, loading priority, and decoding based on actual placement and device needs.

### Contract — BQ-0811
<!-- id: control.bq-0811 -->

- **MUST:** Choose formats, dimensions, compression, responsive sources, loading priority, and decoding based on actual placement and device needs.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0812
<!-- id: control.bq-0812 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Choose formats, dimensions, compression, responsive sources, loading priority, and decoding based on actual placement and device needs.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0813
<!-- id: control.bq-0813 -->

- **PASS only if** the requirement is demonstrated by measured budgets, build/runtime metrics, network/resource evidence, or degradation behavior.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0814
<!-- id: control.bq-0814 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0815
<!-- id: control.bq-0815 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.
