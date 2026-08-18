<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: CONTROLS
Module-Version: 1
Control-Domain: 26
Last-Updated: 2026-08-10
-->

# 26. Feature & Component Craft
<!-- id: controls.domain.26 -->

This native shard extends the BizIQ 4 control plane with BQ-1001 through BQ-1050. Existing BQ-0001 through BQ-1000 remain stable and unchanged.

Load only the exact capability sections required by the active visual/product task. Resolve them through the canonical `CONTROL_INDEX.md`.

Each capability implements:

**Contract → Procedure → Evidence Gate → Recovery → Regression**

## Domain Execution Rule
<!-- id: controls.domain.26.execution -->

1. Apply the capability Contract before dependent feature/design/implementation decisions.
2. Follow the Procedure using the minimum relevant evidence.
3. Do not mark PASS until the Evidence Gate is observably supported.
4. On FAIL, execute Recovery and re-check affected work.
5. Preserve UNVERIFIED when required evidence is unavailable.
6. Use Regression clauses to prevent recurring shallow-feature or under-polished-component failures.


## Icon System Selection
<!-- id: controls.capability.icon-system-selection -->

**Targets:** CRAFT.md / DESIGN.md  
**Requirement:** Select one coherent professional icon system when iconography materially improves clarity, scanning, status recognition, navigation, or affordance, without forcing icons or mixing incompatible families.

### Contract — BQ-1001
<!-- id: control.bq-1001 -->

- **MUST:** Select one coherent professional icon system when iconography materially improves clarity, scanning, status recognition, navigation, or affordance, without forcing icons or mixing incompatible families.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, feature noun, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-1002
<!-- id: control.bq-1002 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence; distinguish known, inferred, unknown, and sample/demo inputs.
3. Apply the requirement exactly: Select one coherent professional icon system when iconography materially improves clarity, scanning, status recognition, navigation, or affordance, without forcing icons or mixing incompatible families.
4. Resolve ties using README precedence, user/business goal fit, accessibility, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in project decision state or artifact evidence when later work depends on it.
6. Re-evaluate after material changes to scope, audience, feature set, device behavior, delivery mode, design direction, or evidence.

### Evidence Gate — BQ-1003
<!-- id: control.bq-1003 -->

- **PASS only if** the requirement is demonstrated by a feature/component contract, source implementation, runtime behavior, rendered captures, scenario checks, or other direct artifact evidence appropriate to the capability.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct runtime/rendered evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-1004
<!-- id: control.bq-1004 -->

- On failure or insufficient evidence, block completion claims that depend on this capability.
- Correct the underlying feature definition, component anatomy, visual system, interaction behavior, responsive treatment, or implementation as applicable, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting evidence, or lower the production/quality target to make the gate pass.

### Regression — BQ-1005
<!-- id: control.bq-1005 -->

- Maintain three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must preserve ambiguity or use deterministic tie-breaking; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability should strengthen a reusable regression fixture rather than produce only a one-off artifact patch.

## Iconography Coverage Audit
<!-- id: controls.capability.iconography-coverage-audit -->

**Targets:** CRAFT.md / QA_GATES.md  
**Requirement:** Audit applicable navigation, utility actions, states, statuses, forms, contextual actions, and supporting UI for purposeful icon coverage and accessible labeling.

### Contract — BQ-1006
<!-- id: control.bq-1006 -->

- **MUST:** Audit applicable navigation, utility actions, states, statuses, forms, contextual actions, and supporting UI for purposeful icon coverage and accessible labeling.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, feature noun, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-1007
<!-- id: control.bq-1007 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence; distinguish known, inferred, unknown, and sample/demo inputs.
3. Apply the requirement exactly: Audit applicable navigation, utility actions, states, statuses, forms, contextual actions, and supporting UI for purposeful icon coverage and accessible labeling.
4. Resolve ties using README precedence, user/business goal fit, accessibility, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in project decision state or artifact evidence when later work depends on it.
6. Re-evaluate after material changes to scope, audience, feature set, device behavior, delivery mode, design direction, or evidence.

### Evidence Gate — BQ-1008
<!-- id: control.bq-1008 -->

- **PASS only if** the requirement is demonstrated by a feature/component contract, source implementation, runtime behavior, rendered captures, scenario checks, or other direct artifact evidence appropriate to the capability.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct runtime/rendered evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-1009
<!-- id: control.bq-1009 -->

- On failure or insufficient evidence, block completion claims that depend on this capability.
- Correct the underlying feature definition, component anatomy, visual system, interaction behavior, responsive treatment, or implementation as applicable, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting evidence, or lower the production/quality target to make the gate pass.

### Regression — BQ-1010
<!-- id: control.bq-1010 -->

- Maintain three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must preserve ambiguity or use deterministic tie-breaking; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability should strengthen a reusable regression fixture rather than produce only a one-off artifact patch.

## Component Anatomy Quality
<!-- id: controls.capability.component-anatomy-quality -->

**Targets:** CRAFT.md / CREATIVE.md / DESIGN.md  
**Requirement:** Require important reusable components to have task-specific hierarchy, anatomy, states, responsive behavior, and visual detail beyond generic border-radius-padding treatment.

### Contract — BQ-1011
<!-- id: control.bq-1011 -->

- **MUST:** Require important reusable components to have task-specific hierarchy, anatomy, states, responsive behavior, and visual detail beyond generic border-radius-padding treatment.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, feature noun, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-1012
<!-- id: control.bq-1012 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence; distinguish known, inferred, unknown, and sample/demo inputs.
3. Apply the requirement exactly: Require important reusable components to have task-specific hierarchy, anatomy, states, responsive behavior, and visual detail beyond generic border-radius-padding treatment.
4. Resolve ties using README precedence, user/business goal fit, accessibility, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in project decision state or artifact evidence when later work depends on it.
6. Re-evaluate after material changes to scope, audience, feature set, device behavior, delivery mode, design direction, or evidence.

### Evidence Gate — BQ-1013
<!-- id: control.bq-1013 -->

- **PASS only if** the requirement is demonstrated by a feature/component contract, source implementation, runtime behavior, rendered captures, scenario checks, or other direct artifact evidence appropriate to the capability.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct runtime/rendered evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-1014
<!-- id: control.bq-1014 -->

- On failure or insufficient evidence, block completion claims that depend on this capability.
- Correct the underlying feature definition, component anatomy, visual system, interaction behavior, responsive treatment, or implementation as applicable, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting evidence, or lower the production/quality target to make the gate pass.

### Regression — BQ-1015
<!-- id: control.bq-1015 -->

- Maintain three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must preserve ambiguity or use deterministic tie-breaking; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability should strengthen a reusable regression fixture rather than produce only a one-off artifact patch.

## Card Surface Specificity
<!-- id: controls.capability.card-surface-specificity -->

**Targets:** CRAFT.md / CREATIVE.md  
**Requirement:** Reject universal card grammar and major regions dominated by interchangeable rounded rectangles; require card anatomy and surface/elevation choices to reflect information and task.

### Contract — BQ-1016
<!-- id: control.bq-1016 -->

- **MUST:** Reject universal card grammar and major regions dominated by interchangeable rounded rectangles; require card anatomy and surface/elevation choices to reflect information and task.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, feature noun, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-1017
<!-- id: control.bq-1017 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence; distinguish known, inferred, unknown, and sample/demo inputs.
3. Apply the requirement exactly: Reject universal card grammar and major regions dominated by interchangeable rounded rectangles; require card anatomy and surface/elevation choices to reflect information and task.
4. Resolve ties using README precedence, user/business goal fit, accessibility, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in project decision state or artifact evidence when later work depends on it.
6. Re-evaluate after material changes to scope, audience, feature set, device behavior, delivery mode, design direction, or evidence.

### Evidence Gate — BQ-1018
<!-- id: control.bq-1018 -->

- **PASS only if** the requirement is demonstrated by a feature/component contract, source implementation, runtime behavior, rendered captures, scenario checks, or other direct artifact evidence appropriate to the capability.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct runtime/rendered evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-1019
<!-- id: control.bq-1019 -->

- On failure or insufficient evidence, block completion claims that depend on this capability.
- Correct the underlying feature definition, component anatomy, visual system, interaction behavior, responsive treatment, or implementation as applicable, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting evidence, or lower the production/quality target to make the gate pass.

### Regression — BQ-1020
<!-- id: control.bq-1020 -->

- Maintain three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must preserve ambiguity or use deterministic tie-breaking; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability should strengthen a reusable regression fixture rather than produce only a one-off artifact patch.

## Interaction Affordance Microdetail
<!-- id: controls.capability.interaction-affordance-microdetail -->

**Targets:** CRAFT.md / DESIGN.md / QA_GATES.md  
**Requirement:** Require clear pre-activation affordances, coherent state feedback, and meaningful micro-detail that improves hierarchy, recognition, scanning, or task completion.

### Contract — BQ-1021
<!-- id: control.bq-1021 -->

- **MUST:** Require clear pre-activation affordances, coherent state feedback, and meaningful micro-detail that improves hierarchy, recognition, scanning, or task completion.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, feature noun, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-1022
<!-- id: control.bq-1022 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence; distinguish known, inferred, unknown, and sample/demo inputs.
3. Apply the requirement exactly: Require clear pre-activation affordances, coherent state feedback, and meaningful micro-detail that improves hierarchy, recognition, scanning, or task completion.
4. Resolve ties using README precedence, user/business goal fit, accessibility, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in project decision state or artifact evidence when later work depends on it.
6. Re-evaluate after material changes to scope, audience, feature set, device behavior, delivery mode, design direction, or evidence.

### Evidence Gate — BQ-1023
<!-- id: control.bq-1023 -->

- **PASS only if** the requirement is demonstrated by a feature/component contract, source implementation, runtime behavior, rendered captures, scenario checks, or other direct artifact evidence appropriate to the capability.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct runtime/rendered evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-1024
<!-- id: control.bq-1024 -->

- On failure or insufficient evidence, block completion claims that depend on this capability.
- Correct the underlying feature definition, component anatomy, visual system, interaction behavior, responsive treatment, or implementation as applicable, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting evidence, or lower the production/quality target to make the gate pass.

### Regression — BQ-1025
<!-- id: control.bq-1025 -->

- Maintain three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must preserve ambiguity or use deterministic tie-breaking; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability should strengthen a reusable regression fixture rather than produce only a one-off artifact patch.

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

## Feature State Completeness
<!-- id: controls.capability.feature-state-completeness -->

**Targets:** CRAFT.md / FEATURES.md / QA_GATES.md  
**Requirement:** Resolve applicable default, loading, empty, filtered-empty/no-result, partial, error, success, disabled/unavailable, permission, offline, validation, and destructive states for important workflows.

### Contract — BQ-1031
<!-- id: control.bq-1031 -->

- **MUST:** Resolve applicable default, loading, empty, filtered-empty/no-result, partial, error, success, disabled/unavailable, permission, offline, validation, and destructive states for important workflows.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, feature noun, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-1032
<!-- id: control.bq-1032 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence; distinguish known, inferred, unknown, and sample/demo inputs.
3. Apply the requirement exactly: Resolve applicable default, loading, empty, filtered-empty/no-result, partial, error, success, disabled/unavailable, permission, offline, validation, and destructive states for important workflows.
4. Resolve ties using README precedence, user/business goal fit, accessibility, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in project decision state or artifact evidence when later work depends on it.
6. Re-evaluate after material changes to scope, audience, feature set, device behavior, delivery mode, design direction, or evidence.

### Evidence Gate — BQ-1033
<!-- id: control.bq-1033 -->

- **PASS only if** the requirement is demonstrated by a feature/component contract, source implementation, runtime behavior, rendered captures, scenario checks, or other direct artifact evidence appropriate to the capability.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct runtime/rendered evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-1034
<!-- id: control.bq-1034 -->

- On failure or insufficient evidence, block completion claims that depend on this capability.
- Correct the underlying feature definition, component anatomy, visual system, interaction behavior, responsive treatment, or implementation as applicable, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting evidence, or lower the production/quality target to make the gate pass.

### Regression — BQ-1035
<!-- id: control.bq-1035 -->

- Maintain three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must preserve ambiguity or use deterministic tie-breaking; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability should strengthen a reusable regression fixture rather than produce only a one-off artifact patch.

## Feature To Component Mapping
<!-- id: controls.capability.feature-to-component-mapping -->

**Targets:** CRAFT.md / FEATURES.md / DESIGN.md  
**Requirement:** Map substantial features to the UI primitives needed to express their real workflow and prevent convenience-driven collapse into one generic component type.

### Contract — BQ-1036
<!-- id: control.bq-1036 -->

- **MUST:** Map substantial features to the UI primitives needed to express their real workflow and prevent convenience-driven collapse into one generic component type.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, feature noun, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-1037
<!-- id: control.bq-1037 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence; distinguish known, inferred, unknown, and sample/demo inputs.
3. Apply the requirement exactly: Map substantial features to the UI primitives needed to express their real workflow and prevent convenience-driven collapse into one generic component type.
4. Resolve ties using README precedence, user/business goal fit, accessibility, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in project decision state or artifact evidence when later work depends on it.
6. Re-evaluate after material changes to scope, audience, feature set, device behavior, delivery mode, design direction, or evidence.

### Evidence Gate — BQ-1038
<!-- id: control.bq-1038 -->

- **PASS only if** the requirement is demonstrated by a feature/component contract, source implementation, runtime behavior, rendered captures, scenario checks, or other direct artifact evidence appropriate to the capability.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct runtime/rendered evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-1039
<!-- id: control.bq-1039 -->

- On failure or insufficient evidence, block completion claims that depend on this capability.
- Correct the underlying feature definition, component anatomy, visual system, interaction behavior, responsive treatment, or implementation as applicable, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting evidence, or lower the production/quality target to make the gate pass.

### Regression — BQ-1040
<!-- id: control.bq-1040 -->

- Maintain three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must preserve ambiguity or use deterministic tie-breaking; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability should strengthen a reusable regression fixture rather than produce only a one-off artifact patch.

## Responsive Feature Recomposition
<!-- id: controls.capability.responsive-feature-recomposition -->

**Targets:** CRAFT.md / DESIGN.md / FEATURES.md  
**Requirement:** Require substantial features to adapt priority, information density, controls, data presentation, and interaction patterns across device classes while preserving every declared P0/P1 task/state transition; hiding task-critical detail, edit, recovery, or action UI without an equivalent mobile path is prohibited.

**Revision 1.7.1 closure:** Evidence is exhaustive for the declared interaction/task inventory. Sampling, page-level no-overflow, source-only handler inspection, or hiding task-critical UI at a breakpoint cannot satisfy PASS.

### Contract — BQ-1041
<!-- id: control.bq-1041 -->

- **MUST:** Require substantial features to adapt priority, information density, controls, data presentation, and interaction patterns across device classes while preserving every declared P0/P1 task/state transition; hiding task-critical detail, edit, recovery, or action UI without an equivalent mobile path is prohibited.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, feature noun, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-1042
<!-- id: control.bq-1042 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence; distinguish known, inferred, unknown, and sample/demo inputs.
3. Apply the requirement exactly: Require substantial features to adapt priority, information density, controls, data presentation, and interaction patterns across device classes while preserving every declared P0/P1 task/state transition; hiding task-critical detail, edit, recovery, or action UI without an equivalent mobile path is prohibited.
4. Resolve ties using README precedence, user/business goal fit, accessibility, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in project decision state or artifact evidence when later work depends on it.
6. Re-evaluate after material changes to scope, audience, feature set, device behavior, delivery mode, design direction, or evidence.

### Evidence Gate — BQ-1043
<!-- id: control.bq-1043 -->

- **PASS only if** the requirement is demonstrated by a feature/component contract, source implementation, runtime behavior, rendered captures, scenario checks, or other direct artifact evidence appropriate to the capability.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct runtime/rendered evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-1044
<!-- id: control.bq-1044 -->

- On failure or insufficient evidence, block completion claims that depend on this capability.
- Correct the underlying feature definition, component anatomy, visual system, interaction behavior, responsive treatment, or implementation as applicable, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting evidence, or lower the production/quality target to make the gate pass.

### Regression — BQ-1045
<!-- id: control.bq-1045 -->

- Maintain three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must preserve ambiguity or use deterministic tie-breaking; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability should strengthen a reusable regression fixture rather than produce only a one-off artifact patch.

## Final Craft Evidence
<!-- id: controls.capability.final-craft-evidence -->

**Targets:** CRAFT.md / QA_GATES.md / CREATIVE.md  
**Requirement:** Before production completion, verify feature depth and component craft from observable implementation/runtime/rendered evidence and recover from shallow, generic, or under-detailed results.

### Contract — BQ-1046
<!-- id: control.bq-1046 -->

- **MUST:** Before production completion, verify feature depth and component craft from observable implementation/runtime/rendered evidence and recover from shallow, generic, or under-detailed results.
- Required inputs are the minimum task/project facts on which this decision depends; missing facts must remain explicitly unknown rather than invented.
- Required output is a concrete decision, state, artifact property, or constraint that downstream work can consume.
- Invariants: higher-precedence instructions remain controlling; production intent cannot be silently weakened; fabricated evidence is prohibited.
- Prohibited shortcut: treating an unverified assumption, feature noun, generic template pattern, or model confidence as satisfaction.

### Procedure — BQ-1047
<!-- id: control.bq-1047 -->

1. Determine whether this capability is triggered by the current scope or by a dependency of another active capability.
2. Gather the minimum relevant evidence; distinguish known, inferred, unknown, and sample/demo inputs.
3. Apply the requirement exactly: Before production completion, verify feature depth and component craft from observable implementation/runtime/rendered evidence and recover from shallow, generic, or under-detailed results.
4. Resolve ties using README precedence, user/business goal fit, accessibility, risk, and the most conservative non-fabricating fallback in that order.
5. Persist the result in project decision state or artifact evidence when later work depends on it.
6. Re-evaluate after material changes to scope, audience, feature set, device behavior, delivery mode, design direction, or evidence.

### Evidence Gate — BQ-1048
<!-- id: control.bq-1048 -->

- **PASS only if** the requirement is demonstrated by a feature/component contract, source implementation, runtime behavior, rendered captures, scenario checks, or other direct artifact evidence appropriate to the capability.
- Evidence must identify what was checked and the observed result. “Looks good,” “should work,” or model confidence alone does not pass.
- If the capability affects a user-visible artifact and rendering/testing tools are available, direct runtime/rendered evidence outranks source-code inference.
- If evidence is unavailable, mark the capability **UNVERIFIED**; do not translate absence of evidence into a pass.

### Recovery — BQ-1049
<!-- id: control.bq-1049 -->

- On failure or insufficient evidence, block completion claims that depend on this capability.
- Correct the underlying feature definition, component anatomy, visual system, interaction behavior, responsive treatment, or implementation as applicable, then re-run the procedure and evidence gate.
- When correction is impossible within available tools or facts, use the safest conservative fallback, record the limitation, and preserve unknowns explicitly.
- Never silently skip the control, fabricate supporting evidence, or lower the production/quality target to make the gate pass.

### Regression — BQ-1050
<!-- id: control.bq-1050 -->

- Maintain three regression conditions: **normal**, **ambiguous/edge**, and **failure/unavailable-evidence**.
- The normal case must produce the intended compliant result; the edge case must preserve ambiguity or use deterministic tie-breaking; the failure case must trigger Recovery rather than false completion.
- Any real-world failure involving this capability should strengthen a reusable regression fixture rather than produce only a one-off artifact patch.
