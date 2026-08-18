<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: CONTROLS
Module-Version: 1
Control-Domain: 13
Last-Updated: 2026-08-10
-->

# 13. Responsive, Mobile & Cross-Device Design
<!-- id: controls.domain.13 -->

This shard is normative but lazily loaded. Load only the exact capability sections required by the active task or decision. 
Each capability implements five linked controls: **Contract → Procedure → Evidence Gate → Recovery → Regression**. 
A capability is not satisfied by model confidence or a prose assertion; the evidence gate governs completion claims.

## Domain Execution Rule
<!-- id: controls.domain.13.execution -->

For an active capability in this domain:
1. Apply its **Contract** before making a dependent design, routing, implementation, or delivery decision.
2. Follow its **Procedure** in order; later task changes that invalidate inputs require re-evaluation.
3. Do not mark it passed until its **Evidence Gate** is supported by observable evidence.
4. If the gate cannot pass, execute **Recovery** and keep the dependent result provisional or blocked.
5. Use the **Regression** clause when changing AIFENCE or evaluating a real-world failure.

## Responsive recomposition
<!-- id: controls.capability.responsive-recomposition -->

**Targets:** CREATIVE.md / DESIGN.md  
**Requirement:** Require meaningful layout recomposition at narrow widths instead of merely stacking desktop columns.

### Contract — BQ-0481
<!-- id: control.bq-0481 -->

- **MUST:** Require meaningful layout recomposition at narrow widths instead of merely stacking desktop columns.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0482
<!-- id: control.bq-0482 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Require meaningful layout recomposition at narrow widths instead of merely stacking desktop columns.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0483
<!-- id: control.bq-0483 -->

- **PASS only if** the requirement is demonstrated by responsive captures, breakpoint behavior, touch-target checks, or cross-device task completion.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0484
<!-- id: control.bq-0484 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0485
<!-- id: control.bq-0485 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Mobile-first priority check
<!-- id: controls.capability.mobile-first-priority-check -->

**Targets:** DESIGN.md / QA_GATES.md  
**Requirement:** Verify that critical content, proof, navigation, CTAs, and P0/P1 task entry/completion controls remain reachable and usable on small screens; task-critical behavior may transform but may not disappear.

**Revision 1.7.1 closure:** Evidence is exhaustive for the declared interaction/task inventory. Sampling, page-level no-overflow, source-only handler inspection, or hiding task-critical UI at a breakpoint cannot satisfy PASS.

### Contract — BQ-0486
<!-- id: control.bq-0486 -->

- **MUST:** Verify that critical content, proof, navigation, CTAs, and P0/P1 task entry/completion controls remain reachable and usable on small screens; task-critical behavior may transform but may not disappear.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0487
<!-- id: control.bq-0487 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Verify that critical content, proof, navigation, CTAs, and P0/P1 task entry/completion controls remain reachable and usable on small screens; task-critical behavior may transform but may not disappear.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0488
<!-- id: control.bq-0488 -->

- **PASS only if** the requirement is demonstrated by responsive captures, breakpoint behavior, touch-target checks, or cross-device task completion.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0489
<!-- id: control.bq-0489 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0490
<!-- id: control.bq-0490 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Breakpoint rationale
<!-- id: controls.capability.breakpoint-rationale -->

**Targets:** DESIGN.md  
**Requirement:** Choose breakpoints from content failure points rather than device-name conventions alone.

### Contract — BQ-0491
<!-- id: control.bq-0491 -->

- **MUST:** Choose breakpoints from content failure points rather than device-name conventions alone.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0492
<!-- id: control.bq-0492 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Choose breakpoints from content failure points rather than device-name conventions alone.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0493
<!-- id: control.bq-0493 -->

- **PASS only if** the requirement is demonstrated by responsive captures, breakpoint behavior, touch-target checks, or cross-device task completion.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0494
<!-- id: control.bq-0494 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0495
<!-- id: control.bq-0495 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Touch-target system
<!-- id: controls.capability.touch-target-system -->

**Targets:** DESIGN.md / QA_GATES.md  
**Requirement:** Enforce minimum usable target size, spacing, and edge avoidance for touch interactions.

### Contract — BQ-0496
<!-- id: control.bq-0496 -->

- **MUST:** Enforce minimum usable target size, spacing, and edge avoidance for touch interactions.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0497
<!-- id: control.bq-0497 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Enforce minimum usable target size, spacing, and edge avoidance for touch interactions.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0498
<!-- id: control.bq-0498 -->

- **PASS only if** the requirement is demonstrated by responsive captures, breakpoint behavior, touch-target checks, or cross-device task completion.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0499
<!-- id: control.bq-0499 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0500
<!-- id: control.bq-0500 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Mobile navigation states
<!-- id: controls.capability.mobile-navigation-states -->

**Targets:** STRUCTURE.md / DESIGN.md  
**Requirement:** Specify open, close, focus, scroll-lock, nested navigation, escape, and orientation-change behavior.

### Contract — BQ-0501
<!-- id: control.bq-0501 -->

- **MUST:** Specify open, close, focus, scroll-lock, nested navigation, escape, and orientation-change behavior.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0502
<!-- id: control.bq-0502 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Specify open, close, focus, scroll-lock, nested navigation, escape, and orientation-change behavior.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0503
<!-- id: control.bq-0503 -->

- **PASS only if** the requirement is demonstrated by responsive captures, breakpoint behavior, touch-target checks, or cross-device task completion.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0504
<!-- id: control.bq-0504 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0505
<!-- id: control.bq-0505 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Responsive-media policy
<!-- id: controls.capability.responsive-media-policy -->

**Targets:** ASSETS.md / DESIGN.md  
**Requirement:** Define source selection, crop, resolution, art direction, and loading behavior per viewport class.

### Contract — BQ-0506
<!-- id: control.bq-0506 -->

- **MUST:** Define source selection, crop, resolution, art direction, and loading behavior per viewport class.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0507
<!-- id: control.bq-0507 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Define source selection, crop, resolution, art direction, and loading behavior per viewport class.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0508
<!-- id: control.bq-0508 -->

- **PASS only if** the requirement is demonstrated by responsive captures, breakpoint behavior, touch-target checks, or cross-device task completion.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0509
<!-- id: control.bq-0509 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0510
<!-- id: control.bq-0510 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Dense-UI adaptation
<!-- id: controls.capability.dense-ui-adaptation -->

**Targets:** DESIGN.md  
**Requirement:** Preserve every P0/P1 monitor, inspect, edit, recover, and act task on 320/390 px through an explicit narrow-screen transformation; task-critical panes/actions may move into routes, drawers, sheets, or disclosures but may not disappear.

**Revision 1.7.1 closure:** Evidence is exhaustive for the declared interaction/task inventory. Sampling, page-level no-overflow, source-only handler inspection, or hiding task-critical UI at a breakpoint cannot satisfy PASS.

### Contract — BQ-0511
<!-- id: control.bq-0511 -->

- **MUST:** Preserve every P0/P1 monitor, inspect, edit, recover, and act task on 320/390 px through an explicit narrow-screen transformation; task-critical panes/actions may move into routes, drawers, sheets, or disclosures but may not disappear.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0512
<!-- id: control.bq-0512 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Preserve every P0/P1 monitor, inspect, edit, recover, and act task on 320/390 px through an explicit narrow-screen transformation; task-critical panes/actions may move into routes, drawers, sheets, or disclosures but may not disappear.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0513
<!-- id: control.bq-0513 -->

- **PASS only if** the requirement is demonstrated by responsive captures, breakpoint behavior, touch-target checks, or cross-device task completion.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0514
<!-- id: control.bq-0514 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0515
<!-- id: control.bq-0515 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Cross-device continuity
<!-- id: controls.capability.cross-device-continuity -->

**Targets:** FEATURES.md / STRUCTURE.md  
**Requirement:** Preserve user state, task context, and interaction semantics across viewport/device classes; every declared P0/P1 task must remain reachable and completable at required narrow widths.

**Revision 1.7.1 closure:** Evidence is exhaustive for the declared interaction/task inventory. Sampling, page-level no-overflow, source-only handler inspection, or hiding task-critical UI at a breakpoint cannot satisfy PASS.

### Contract — BQ-0516
<!-- id: control.bq-0516 -->

- **MUST:** Preserve user state, task context, and interaction semantics across viewport/device classes; every declared P0/P1 task must remain reachable and completable at required narrow widths.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0517
<!-- id: control.bq-0517 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Preserve user state, task context, and interaction semantics across viewport/device classes; every declared P0/P1 task must remain reachable and completable at required narrow widths.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0518
<!-- id: control.bq-0518 -->

- **PASS only if** the requirement is demonstrated by responsive captures, breakpoint behavior, touch-target checks, or cross-device task completion.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0519
<!-- id: control.bq-0519 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0520
<!-- id: control.bq-0520 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.
