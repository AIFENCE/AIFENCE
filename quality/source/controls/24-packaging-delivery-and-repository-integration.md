<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: CONTROLS
Module-Version: 1
Control-Domain: 24
Last-Updated: 2026-08-09
-->

# 24. Packaging, Delivery & Repository Integration
<!-- id: controls.domain.24 -->

This shard is normative but lazily loaded. Load only the exact capability sections required by the active task or decision. 
Each capability implements five linked controls: **Contract → Procedure → Evidence Gate → Recovery → Regression**. 
A capability is not satisfied by model confidence or a prose assertion; the evidence gate governs completion claims.

## Domain Execution Rule
<!-- id: controls.domain.24.execution -->

For an active capability in this domain:
1. Apply its **Contract** before making a dependent design, routing, implementation, or delivery decision.
2. Follow its **Procedure** in order; later task changes that invalidate inputs require re-evaluation.
3. Do not mark it passed until its **Evidence Gate** is supported by observable evidence.
4. If the gate cannot pass, execute **Recovery** and keep the dependent result provisional or blocked.
5. Use the **Regression** clause when changing AIFENCE or evaluating a real-world failure.

## Deliverable manifest
<!-- id: controls.capability.deliverable-manifest -->

**Targets:** README.md / QA_GATES.md  
**Requirement:** Generate a final manifest of files, purposes, entry points, dependencies, assets, and known configuration requirements.

### Contract — BQ-0921
<!-- id: control.bq-0921 -->

- **MUST:** Generate a final manifest of files, purposes, entry points, dependencies, assets, and known configuration requirements.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0922
<!-- id: control.bq-0922 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Generate a final manifest of files, purposes, entry points, dependencies, assets, and known configuration requirements.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0923
<!-- id: control.bq-0923 -->

- **PASS only if** the requirement is demonstrated by deliverable manifest, filesystem/package checks, setup instructions, links, or handoff evidence.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0924
<!-- id: control.bq-0924 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0925
<!-- id: control.bq-0925 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Self-contained delivery check
<!-- id: controls.capability.self-contained-delivery-check -->

**Targets:** ASSETS.md / QA_GATES.md  
**Requirement:** Verify local deliverables do not depend on inaccessible temporary paths, placeholder URLs, hidden session state, or missing generated assets.

### Contract — BQ-0926
<!-- id: control.bq-0926 -->

- **MUST:** Verify local deliverables do not depend on inaccessible temporary paths, placeholder URLs, hidden session state, or missing generated assets.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0927
<!-- id: control.bq-0927 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Verify local deliverables do not depend on inaccessible temporary paths, placeholder URLs, hidden session state, or missing generated assets.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0928
<!-- id: control.bq-0928 -->

- **PASS only if** the requirement is demonstrated by deliverable manifest, filesystem/package checks, setup instructions, links, or handoff evidence.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0929
<!-- id: control.bq-0929 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0930
<!-- id: control.bq-0930 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Environment setup clarity
<!-- id: controls.capability.environment-setup-clarity -->

**Targets:** README.md  
**Requirement:** Include exact run, build, test, and configuration instructions proportional to the artifact's technical complexity.

### Contract — BQ-0931
<!-- id: control.bq-0931 -->

- **MUST:** Include exact run, build, test, and configuration instructions proportional to the artifact's technical complexity.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0932
<!-- id: control.bq-0932 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Include exact run, build, test, and configuration instructions proportional to the artifact's technical complexity.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0933
<!-- id: control.bq-0933 -->

- **PASS only if** the requirement is demonstrated by deliverable manifest, filesystem/package checks, setup instructions, links, or handoff evidence.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0934
<!-- id: control.bq-0934 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0935
<!-- id: control.bq-0935 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Config-vs-content separation
<!-- id: controls.capability.config-vs-content-separation -->

**Targets:** STRUCTURE.md  
**Requirement:** Keep user-editable business facts and settings separate from structural implementation where practical.

### Contract — BQ-0936
<!-- id: control.bq-0936 -->

- **MUST:** Keep user-editable business facts and settings separate from structural implementation where practical.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0937
<!-- id: control.bq-0937 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Keep user-editable business facts and settings separate from structural implementation where practical.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0938
<!-- id: control.bq-0938 -->

- **PASS only if** the requirement is demonstrated by deliverable manifest, filesystem/package checks, setup instructions, links, or handoff evidence.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0939
<!-- id: control.bq-0939 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0940
<!-- id: control.bq-0940 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Repository-scope guard
<!-- id: controls.capability.repository-scope-guard -->

**Targets:** README.md  
**Requirement:** When modifying an existing repository, constrain changes to the requested scope and avoid rewriting unrelated pack or project files.

### Contract — BQ-0941
<!-- id: control.bq-0941 -->

- **MUST:** When modifying an existing repository, constrain changes to the requested scope and avoid rewriting unrelated pack or project files.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0942
<!-- id: control.bq-0942 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: When modifying an existing repository, constrain changes to the requested scope and avoid rewriting unrelated pack or project files.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0943
<!-- id: control.bq-0943 -->

- **PASS only if** the requirement is demonstrated by deliverable manifest, filesystem/package checks, setup instructions, links, or handoff evidence.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0944
<!-- id: control.bq-0944 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0945
<!-- id: control.bq-0945 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Change-summary evidence
<!-- id: controls.capability.change-summary-evidence -->

**Targets:** QA_GATES.md  
**Requirement:** Report what changed, what was intentionally untouched, what checks ran, and any unresolved limitations after modifications.

### Contract — BQ-0946
<!-- id: control.bq-0946 -->

- **MUST:** Report what changed, what was intentionally untouched, what checks ran, and any unresolved limitations after modifications.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0947
<!-- id: control.bq-0947 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Report what changed, what was intentionally untouched, what checks ran, and any unresolved limitations after modifications.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0948
<!-- id: control.bq-0948 -->

- **PASS only if** the requirement is demonstrated by deliverable manifest, filesystem/package checks, setup instructions, links, or handoff evidence.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0949
<!-- id: control.bq-0949 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0950
<!-- id: control.bq-0950 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Artifact-link integrity
<!-- id: controls.capability.artifact-link-integrity -->

**Targets:** QA_GATES.md  
**Requirement:** Verify every delivered file actually exists at the referenced path and that archives contain the expected contents.

### Contract — BQ-0951
<!-- id: control.bq-0951 -->

- **MUST:** Verify every delivered file actually exists at the referenced path and that archives contain the expected contents.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0952
<!-- id: control.bq-0952 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Verify every delivered file actually exists at the referenced path and that archives contain the expected contents.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0953
<!-- id: control.bq-0953 -->

- **PASS only if** the requirement is demonstrated by deliverable manifest, filesystem/package checks, setup instructions, links, or handoff evidence.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0954
<!-- id: control.bq-0954 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0955
<!-- id: control.bq-0955 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.

## Handoff readiness
<!-- id: controls.capability.handoff-readiness -->

**Targets:** README.md / QA_GATES.md  
**Requirement:** Ensure another developer or operator can identify entry points, replace configuration, run the artifact, and understand known constraints without hidden context.

### Contract — BQ-0956
<!-- id: control.bq-0956 -->

- **MUST:** Ensure another developer or operator can identify entry points, replace configuration, run the artifact, and understand known constraints without hidden context.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, keyword match, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-0957
<!-- id: control.bq-0957 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence before selecting a result; distinguish known, inferred, and unknown inputs.
3. Apply the requirement exactly: Ensure another developer or operator can identify entry points, replace configuration, run the artifact, and understand known constraints without hidden context.
4. Resolve ties using README precedence, business/user goal fit, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in the project decision state or artifact evidence ledger when later work depends on it.
6. Re-evaluate when scope, audience, industry, feature set, risk, delivery mode, or evidence materially changes.

### Evidence Gate — BQ-0958
<!-- id: control.bq-0958 -->

- **PASS only if** the requirement is demonstrated by deliverable manifest, filesystem/package checks, setup instructions, links, or handoff evidence.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct artifact or runtime evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-0959
<!-- id: control.bq-0959 -->

- On failure or insufficient evidence, block any completion claim that depends on this capability.
- Correct the underlying cause when possible, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting facts, or lower the delivery/quality target to make the gate pass.

### Regression — BQ-0960
<!-- id: control.bq-0960 -->

- Maintain or execute three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must invoke deterministic tie-breaking or preserve ambiguity; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability becomes a regression fixture or a documented reason why a more general fixture covers it.
