<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: CONTROLS
Module-Version: 1
Control-Domain: 18
Last-Updated: 2026-08-09
-->

# 18. Application Logic, Data & Integrations
<!-- id: controls.domain.18 -->

This shard is normative but lazily loaded. Load only the exact capability sections required by the active task or decision. 
Each capability implements five linked controls: **Contract → Procedure → Evidence Gate → Recovery → Regression**. 
A capability is not satisfied by model confidence or a prose assertion; the evidence gate governs completion claims.

## Domain Execution Rule
<!-- id: controls.domain.18.execution -->

For an active capability in this domain:
1. Apply its **Contract** before making a dependent design, routing, implementation, or delivery decision.
2. Follow its **Procedure** in order; later task changes that invalidate inputs require re-evaluation.
3. Do not mark it passed until its **Evidence Gate** is supported by observable evidence.
4. If the gate cannot pass, execute **Recovery** and keep the dependent result provisional or blocked.
5. Use the **Regression** clause when changing BizIQ or evaluating a real-world failure.

## Data-model-first planning
<!-- id: controls.capability.data-model-first-planning -->

**Targets:** FEATURES.md / STRUCTURE.md  
**Requirement:** Define core entities, relationships, ownership, lifecycle, validation, and retention before implementing complex application flows.

### Contract — BQ-0681
<!-- id: control.bq-0681 -->

- **MUST:** Define core entities, relationships, ownership, lifecycle, validation, and retention before implementing complex application flows.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0682
<!-- id: control.bq-0682 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Define core entities, relationships, ownership, lifecycle, validation, and retention before implementing complex application flows.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0683
<!-- id: control.bq-0683 -->

- **PASS only if** the requirement is demonstrated by data/permission models, integration contracts, failure states, audit records, or destructive-action safeguards.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0684
<!-- id: control.bq-0684 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0685
<!-- id: control.bq-0685 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Permission-model resolution
<!-- id: controls.capability.permission-model-resolution -->

**Targets:** FEATURES.md / SECURITY.md  
**Requirement:** Specify roles, capabilities, resource ownership, inheritance, exceptions, and denial behavior before exposing privileged actions.

### Contract — BQ-0686
<!-- id: control.bq-0686 -->

- **MUST:** Specify roles, capabilities, resource ownership, inheritance, exceptions, and denial behavior before exposing privileged actions.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0687
<!-- id: control.bq-0687 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Specify roles, capabilities, resource ownership, inheritance, exceptions, and denial behavior before exposing privileged actions.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0688
<!-- id: control.bq-0688 -->

- **PASS only if** the requirement is demonstrated by data/permission models, integration contracts, failure states, audit records, or destructive-action safeguards.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0689
<!-- id: control.bq-0689 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0690
<!-- id: control.bq-0690 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Integration-contract standard
<!-- id: controls.capability.integration-contract-standard -->

**Targets:** FEATURES.md / SECURITY.md  
**Requirement:** Document authentication, inputs, outputs, rate limits, retries, timeouts, idempotency, errors, and data sensitivity for integrations.

### Contract — BQ-0691
<!-- id: control.bq-0691 -->

- **MUST:** Document authentication, inputs, outputs, rate limits, retries, timeouts, idempotency, errors, and data sensitivity for integrations.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0692
<!-- id: control.bq-0692 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Document authentication, inputs, outputs, rate limits, retries, timeouts, idempotency, errors, and data sensitivity for integrations.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0693
<!-- id: control.bq-0693 -->

- **PASS only if** the requirement is demonstrated by data/permission models, integration contracts, failure states, audit records, or destructive-action safeguards.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0694
<!-- id: control.bq-0694 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0695
<!-- id: control.bq-0695 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Offline-and-failure behavior
<!-- id: controls.capability.offline-and-failure-behavior -->

**Targets:** FEATURES.md  
**Requirement:** Define user-visible behavior when APIs, networks, third parties, or background jobs are unavailable.

### Contract — BQ-0696
<!-- id: control.bq-0696 -->

- **MUST:** Define user-visible behavior when APIs, networks, third parties, or background jobs are unavailable.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0697
<!-- id: control.bq-0697 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Define user-visible behavior when APIs, networks, third parties, or background jobs are unavailable.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0698
<!-- id: control.bq-0698 -->

- **PASS only if** the requirement is demonstrated by data/permission models, integration contracts, failure states, audit records, or destructive-action safeguards.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0699
<!-- id: control.bq-0699 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0700
<!-- id: control.bq-0700 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Data-freshness semantics
<!-- id: controls.capability.data-freshness-semantics -->

**Targets:** FEATURES.md / TERMINOLOGY.md  
**Requirement:** Show when data was last updated and distinguish live, cached, delayed, estimated, and stale values where material.

### Contract — BQ-0701
<!-- id: control.bq-0701 -->

- **MUST:** Show when data was last updated and distinguish live, cached, delayed, estimated, and stale values where material.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0702
<!-- id: control.bq-0702 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Show when data was last updated and distinguish live, cached, delayed, estimated, and stale values where material.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0703
<!-- id: control.bq-0703 -->

- **PASS only if** the requirement is demonstrated by data/permission models, integration contracts, failure states, audit records, or destructive-action safeguards.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0704
<!-- id: control.bq-0704 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0705
<!-- id: control.bq-0705 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Destructive-action safeguards
<!-- id: controls.capability.destructive-action-safeguards -->

**Targets:** FEATURES.md / DESIGN.md  
**Requirement:** Use confirmation, previews, undo, permissions, or delayed execution proportional to the reversibility and impact of the action.

### Contract — BQ-0706
<!-- id: control.bq-0706 -->

- **MUST:** Use confirmation, previews, undo, permissions, or delayed execution proportional to the reversibility and impact of the action.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0707
<!-- id: control.bq-0707 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Use confirmation, previews, undo, permissions, or delayed execution proportional to the reversibility and impact of the action.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0708
<!-- id: control.bq-0708 -->

- **PASS only if** the requirement is demonstrated by data/permission models, integration contracts, failure states, audit records, or destructive-action safeguards.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0709
<!-- id: control.bq-0709 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0710
<!-- id: control.bq-0710 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Import-export integrity
<!-- id: controls.capability.import-export-integrity -->

**Targets:** FEATURES.md / SECURITY.md  
**Requirement:** Validate file types, schema, size, encoding, partial failures, duplicate handling, and sensitive data exposure for bulk data flows.

### Contract — BQ-0711
<!-- id: control.bq-0711 -->

- **MUST:** Validate file types, schema, size, encoding, partial failures, duplicate handling, and sensitive data exposure for bulk data flows.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0712
<!-- id: control.bq-0712 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Validate file types, schema, size, encoding, partial failures, duplicate handling, and sensitive data exposure for bulk data flows.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0713
<!-- id: control.bq-0713 -->

- **PASS only if** the requirement is demonstrated by data/permission models, integration contracts, failure states, audit records, or destructive-action safeguards.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0714
<!-- id: control.bq-0714 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0715
<!-- id: control.bq-0715 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Auditability requirement
<!-- id: controls.capability.auditability-requirement -->

**Targets:** FEATURES.md / SECURITY.md  
**Requirement:** For high-impact workflows, preserve who did what, when, to which resource, and with what result.

### Contract — BQ-0716
<!-- id: control.bq-0716 -->

- **MUST:** For high-impact workflows, preserve who did what, when, to which resource, and with what result.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0717
<!-- id: control.bq-0717 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: For high-impact workflows, preserve who did what, when, to which resource, and with what result.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0718
<!-- id: control.bq-0718 -->

- **PASS only if** the requirement is demonstrated by data/permission models, integration contracts, failure states, audit records, or destructive-action safeguards.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0719
<!-- id: control.bq-0719 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0720
<!-- id: control.bq-0720 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.
