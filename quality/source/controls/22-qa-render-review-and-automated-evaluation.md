<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: CONTROLS
Module-Version: 1
Control-Domain: 22
Last-Updated: 2026-08-09
-->

# 22. QA, Render Review & Automated Evaluation
<!-- id: controls.domain.22 -->

This shard is normative but lazily loaded. Load only the exact capability sections required by the active task or decision. 
Each capability implements five linked controls: **Contract → Procedure → Evidence Gate → Recovery → Regression**. 
A capability is not satisfied by model confidence or a prose assertion; the evidence gate governs completion claims.

## Domain Execution Rule
<!-- id: controls.domain.22.execution -->

For an active capability in this domain:
1. Apply its **Contract** before making a dependent design, routing, implementation, or delivery decision.
2. Follow its **Procedure** in order; later task changes that invalidate inputs require re-evaluation.
3. Do not mark it passed until its **Evidence Gate** is supported by observable evidence.
4. If the gate cannot pass, execute **Recovery** and keep the dependent result provisional or blocked.
5. Use the **Regression** clause when changing BizIQ or evaluating a real-world failure.

## Evidence-based completion
<!-- id: controls.capability.evidence-based-completion -->

**Targets:** QA_GATES.md  
**Requirement:** Require concrete evidence for each claimed validation step and prohibit generic statements such as all checks passed without check details.

### Contract — BQ-0841
<!-- id: control.bq-0841 -->

- **MUST:** Require concrete evidence for each claimed validation step and prohibit generic statements such as all checks passed without check details.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0842
<!-- id: control.bq-0842 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Require concrete evidence for each claimed validation step and prohibit generic statements such as all checks passed without check details.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0843
<!-- id: control.bq-0843 -->

- **PASS only if** the requirement is demonstrated by test output, rendered captures, scorecards, defect logs, or regression results.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0844
<!-- id: control.bq-0844 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0845
<!-- id: control.bq-0845 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Rendered-pixel review
<!-- id: controls.capability.rendered-pixel-review -->

**Targets:** CREATIVE.md / QA_GATES.md  
**Requirement:** Judge actual rendered output at representative desktop and mobile sizes rather than inferring quality from source code.

### Contract — BQ-0846
<!-- id: control.bq-0846 -->

- **MUST:** Judge actual rendered output at representative desktop and mobile sizes rather than inferring quality from source code.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0847
<!-- id: control.bq-0847 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Judge actual rendered output at representative desktop and mobile sizes rather than inferring quality from source code.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0848
<!-- id: control.bq-0848 -->

- **PASS only if** the requirement is demonstrated by test output, rendered captures, scorecards, defect logs, or regression results.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0849
<!-- id: control.bq-0849 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0850
<!-- id: control.bq-0850 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Visual-regression fixtures
<!-- id: controls.capability.visual-regression-fixtures -->

**Targets:** QA_GATES.md  
**Requirement:** Preserve representative screenshots or structural snapshots for high-value creation tests so pack changes can reveal quality regressions.

### Contract — BQ-0851
<!-- id: control.bq-0851 -->

- **MUST:** Preserve representative screenshots or structural snapshots for high-value creation tests so pack changes can reveal quality regressions.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0852
<!-- id: control.bq-0852 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Preserve representative screenshots or structural snapshots for high-value creation tests so pack changes can reveal quality regressions.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0853
<!-- id: control.bq-0853 -->

- **PASS only if** the requirement is demonstrated by test output, rendered captures, scorecards, defect logs, or regression results.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0854
<!-- id: control.bq-0854 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0855
<!-- id: control.bq-0855 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Cross-browser smoke testing
<!-- id: controls.capability.cross-browser-smoke-testing -->

**Targets:** QA_GATES.md  
**Requirement:** Define minimum browser-engine coverage appropriate to the project and test primary flows rather than only page load.

**Requirement:** Define minimum browser-engine coverage appropriate to the project and test primary flows rather than only page load.

**Revision 1.7.3 prerequisite:** Before flow testing, generated browser code MUST pass script syntax parsing and direct runtime initialization checks. Page/console parser or initialization failures block this capability regardless of visual render quality.

### Contract — BQ-0856
<!-- id: control.bq-0856 -->

- **MUST:** Define minimum browser-engine coverage appropriate to the project and test primary flows rather than only page load.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0857
<!-- id: control.bq-0857 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Define minimum browser-engine coverage appropriate to the project and test primary flows rather than only page load.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0858
<!-- id: control.bq-0858 -->

- **PASS only if** the requirement is demonstrated by test output, rendered captures, scorecards, defect logs, or regression results.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0859
<!-- id: control.bq-0859 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0860
<!-- id: control.bq-0860 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Broken-path detection
<!-- id: controls.capability.broken-path-detection -->

**Targets:** QA_GATES.md  
**Requirement:** Check links, anchors, routes, assets, forms, buttons, downloads, media, and navigation targets for broken or dead behavior.

**Requirement:** Check links, anchors, routes, assets, forms, buttons, downloads, media, and navigation targets for broken or dead behavior.

**Revision 1.7.3 prerequisite:** Treat any JavaScript parser error, uncaught initialization error, or required local-script load failure as a broken-path P0. Do not continue to acceptance from a visually rendered but non-executing shell.

### Contract — BQ-0861
<!-- id: control.bq-0861 -->

- **MUST:** Check links, anchors, routes, assets, forms, buttons, downloads, media, and navigation targets for broken or dead behavior.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0862
<!-- id: control.bq-0862 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Check links, anchors, routes, assets, forms, buttons, downloads, media, and navigation targets for broken or dead behavior.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0863
<!-- id: control.bq-0863 -->

- **PASS only if** the requirement is demonstrated by test output, rendered captures, scorecards, defect logs, or regression results.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0864
<!-- id: control.bq-0864 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0865
<!-- id: control.bq-0865 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Quality-score evidence
<!-- id: controls.capability.quality-score-evidence -->

**Targets:** CREATIVE.md / QA_GATES.md  
**Requirement:** Require each visual-score category to cite observable evidence and prevent the model from self-awarding unsupported high scores.

### Contract — BQ-0866
<!-- id: control.bq-0866 -->

- **MUST:** Require each visual-score category to cite observable evidence and prevent the model from self-awarding unsupported high scores.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0867
<!-- id: control.bq-0867 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Require each visual-score category to cite observable evidence and prevent the model from self-awarding unsupported high scores.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0868
<!-- id: control.bq-0868 -->

- **PASS only if** the requirement is demonstrated by test output, rendered captures, scorecards, defect logs, or regression results.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0869
<!-- id: control.bq-0869 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0870
<!-- id: control.bq-0870 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Failure-severity model
<!-- id: controls.capability.failure-severity-model -->

**Targets:** QA_GATES.md  
**Requirement:** Classify blockers, criticals, majors, minors, and polish issues so unresolved severity determines whether delivery is allowed.

### Contract — BQ-0871
<!-- id: control.bq-0871 -->

- **MUST:** Classify blockers, criticals, majors, minors, and polish issues so unresolved severity determines whether delivery is allowed.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0872
<!-- id: control.bq-0872 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Classify blockers, criticals, majors, minors, and polish issues so unresolved severity determines whether delivery is allowed.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0873
<!-- id: control.bq-0873 -->

- **PASS only if** the requirement is demonstrated by test output, rendered captures, scorecards, defect logs, or regression results.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0874
<!-- id: control.bq-0874 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0875
<!-- id: control.bq-0875 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Creation-regression suite
<!-- id: controls.capability.creation-regression-suite -->

**Targets:** tools/validate_pack.py / QA_GATES.md  
**Requirement:** Maintain representative prompt fixtures across industries and creation types to test routing, output completeness, genericity, and visual quality after pack changes.

### Contract — BQ-0876
<!-- id: control.bq-0876 -->

- **MUST:** Maintain representative prompt fixtures across industries and creation types to test routing, output completeness, genericity, and visual quality after pack changes.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0877
<!-- id: control.bq-0877 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Maintain representative prompt fixtures across industries and creation types to test routing, output completeness, genericity, and visual quality after pack changes.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0878
<!-- id: control.bq-0878 -->

- **PASS only if** the requirement is demonstrated by test output, rendered captures, scorecards, defect logs, or regression results.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0879
<!-- id: control.bq-0879 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0880
<!-- id: control.bq-0880 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.
