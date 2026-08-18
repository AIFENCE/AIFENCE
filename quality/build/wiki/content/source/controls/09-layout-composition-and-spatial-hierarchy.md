<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: CONTROLS
Module-Version: 1
Control-Domain: 09
Last-Updated: 2026-08-09
-->

# 09. Layout, Composition & Spatial Hierarchy
<!-- id: controls.domain.09 -->

This shard is normative but lazily loaded. Load only the exact capability sections required by the active task or decision. 
Each capability implements five linked controls: **Contract → Procedure → Evidence Gate → Recovery → Regression**. 
A capability is not satisfied by model confidence or a prose assertion; the evidence gate governs completion claims.

## Domain Execution Rule
<!-- id: controls.domain.09.execution -->

For an active capability in this domain:
1. Apply its **Contract** before making a dependent design, routing, implementation, or delivery decision.
2. Follow its **Procedure** in order; later task changes that invalidate inputs require re-evaluation.
3. Do not mark it passed until its **Evidence Gate** is supported by observable evidence.
4. If the gate cannot pass, execute **Recovery** and keep the dependent result provisional or blocked.
5. Use the **Regression** clause when changing AIFENCE or evaluating a real-world failure.

## Section-purpose uniqueness
<!-- id: controls.capability.section-purpose-uniqueness -->

**Targets:** CREATIVE.md / DESIGN.md  
**Requirement:** Require every major section to have a distinct communication purpose and composition rather than repeating one section template.

### Contract — BQ-0321
<!-- id: control.bq-0321 -->

- **MUST:** Require every major section to have a distinct communication purpose and composition rather than repeating one section template.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0322
<!-- id: control.bq-0322 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Require every major section to have a distinct communication purpose and composition rather than repeating one section template.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0323
<!-- id: control.bq-0323 -->

- **PASS only if** the requirement is demonstrated by rendered layouts, spacing/grid evidence, viewport captures, or composition review notes.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0324
<!-- id: control.bq-0324 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0325
<!-- id: control.bq-0325 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Macro-rhythm system
<!-- id: controls.capability.macro-rhythm-system -->

**Targets:** CREATIVE.md / DESIGN.md  
**Requirement:** Define deliberate alternation of density, whitespace, media, proof, interaction, and emphasis across the full page or product.

### Contract — BQ-0326
<!-- id: control.bq-0326 -->

- **MUST:** Define deliberate alternation of density, whitespace, media, proof, interaction, and emphasis across the full page or product.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0327
<!-- id: control.bq-0327 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Define deliberate alternation of density, whitespace, media, proof, interaction, and emphasis across the full page or product.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0328
<!-- id: control.bq-0328 -->

- **PASS only if** the requirement is demonstrated by rendered layouts, spacing/grid evidence, viewport captures, or composition review notes.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0329
<!-- id: control.bq-0329 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0330
<!-- id: control.bq-0330 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Visual-anchor strategy
<!-- id: controls.capability.visual-anchor-strategy -->

**Targets:** CREATIVE.md  
**Requirement:** Place strong focal anchors at intentional points so long pages do not feel uniformly weighted or visually flat.

### Contract — BQ-0331
<!-- id: control.bq-0331 -->

- **MUST:** Place strong focal anchors at intentional points so long pages do not feel uniformly weighted or visually flat.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0332
<!-- id: control.bq-0332 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Place strong focal anchors at intentional points so long pages do not feel uniformly weighted or visually flat.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0333
<!-- id: control.bq-0333 -->

- **PASS only if** the requirement is demonstrated by rendered layouts, spacing/grid evidence, viewport captures, or composition review notes.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0334
<!-- id: control.bq-0334 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0335
<!-- id: control.bq-0335 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Grid variation discipline
<!-- id: controls.capability.grid-variation-discipline -->

**Targets:** DESIGN.md  
**Requirement:** Allow controlled grid changes that support meaning while preserving alignment logic and responsive predictability.

### Contract — BQ-0336
<!-- id: control.bq-0336 -->

- **MUST:** Allow controlled grid changes that support meaning while preserving alignment logic and responsive predictability.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0337
<!-- id: control.bq-0337 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Allow controlled grid changes that support meaning while preserving alignment logic and responsive predictability.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0338
<!-- id: control.bq-0338 -->

- **PASS only if** the requirement is demonstrated by rendered layouts, spacing/grid evidence, viewport captures, or composition review notes.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0339
<!-- id: control.bq-0339 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0340
<!-- id: control.bq-0340 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Hero composition diversity
<!-- id: controls.capability.hero-composition-diversity -->

**Targets:** CREATIVE.md  
**Requirement:** Require hero composition to emerge from brand and content needs rather than defaulting to text-left/image-right.

### Contract — BQ-0341
<!-- id: control.bq-0341 -->

- **MUST:** Require hero composition to emerge from brand and content needs rather than defaulting to text-left/image-right.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0342
<!-- id: control.bq-0342 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Require hero composition to emerge from brand and content needs rather than defaulting to text-left/image-right.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0343
<!-- id: control.bq-0343 -->

- **PASS only if** the requirement is demonstrated by rendered layouts, spacing/grid evidence, viewport captures, or composition review notes.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0344
<!-- id: control.bq-0344 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0345
<!-- id: control.bq-0345 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Repetition detector
<!-- id: controls.capability.repetition-detector -->

**Targets:** QA_GATES.md  
**Requirement:** Measure repeated card structures, identical widths/spacing/alignment, generic dashboard/master-detail grammar, and other repetition that signals template construction; distinguish useful repeated data structures from convenience-driven sameness.

### Contract — BQ-0346
<!-- id: control.bq-0346 -->

- **MUST:** Measure repeated card structures, identical widths/spacing/alignment, generic dashboard/master-detail grammar, and other repetition that signals template construction; distinguish useful repeated data structures from convenience-driven sameness.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0347
<!-- id: control.bq-0347 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Measure repeated card structures, identical widths/spacing/alignment, generic dashboard/master-detail grammar, and other repetition that signals template construction; distinguish useful repeated data structures from convenience-driven sameness.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0348
<!-- id: control.bq-0348 -->

- **PASS only if** the requirement is demonstrated by rendered layouts, spacing/grid evidence, viewport captures, or composition review notes.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0349
<!-- id: control.bq-0349 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0350
<!-- id: control.bq-0350 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Viewport composition review
<!-- id: controls.capability.viewport-composition-review -->

**Targets:** CREATIVE.md / QA_GATES.md  
**Requirement:** Evaluate what users see above the fold and at major scroll transitions instead of judging sections independently.

### Contract — BQ-0351
<!-- id: control.bq-0351 -->

- **MUST:** Evaluate what users see above the fold and at major scroll transitions instead of judging sections independently.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0352
<!-- id: control.bq-0352 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Evaluate what users see above the fold and at major scroll transitions instead of judging sections independently.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0353
<!-- id: control.bq-0353 -->

- **PASS only if** the requirement is demonstrated by rendered layouts, spacing/grid evidence, viewport captures, or composition review notes.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0354
<!-- id: control.bq-0354 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0355
<!-- id: control.bq-0355 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Whitespace intentionality
<!-- id: controls.capability.whitespace-intentionality -->

**Targets:** CREATIVE.md  
**Requirement:** Distinguish premium breathing room from accidental emptiness by requiring whitespace to support hierarchy, focus, or rhythm.

### Contract — BQ-0356
<!-- id: control.bq-0356 -->

- **MUST:** Distinguish premium breathing room from accidental emptiness by requiring whitespace to support hierarchy, focus, or rhythm.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0357
<!-- id: control.bq-0357 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Distinguish premium breathing room from accidental emptiness by requiring whitespace to support hierarchy, focus, or rhythm.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0358
<!-- id: control.bq-0358 -->

- **PASS only if** the requirement is demonstrated by rendered layouts, spacing/grid evidence, viewport captures, or composition review notes.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0359
<!-- id: control.bq-0359 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0360
<!-- id: control.bq-0360 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.
