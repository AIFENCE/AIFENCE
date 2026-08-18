<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: CONTROLS
Module-Version: 1
Control-Domain: 28
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-09
-->

# 28. Adversarial Critique, Repair, Quality Floors & Benchmarking
<!-- id: controls.domain.28 -->

Use exact capability sections only.


## Iterative Render Critique Loop
<!-- id: controls.capability.iterative-render-critique-loop -->

**Targets:** CRITICS.md / QA_GATES.md  
**Requirement:** After the first substantial implementation render, run adversarial critique, repair material failures, re-render affected views/states, and repeat until required gates/floors pass or evidence is genuinely unavailable.

### Contract — BQ-1101
<!-- id: control.bq-1101 -->

- **MUST:** After the first substantial implementation render, run adversarial critique, repair material failures, re-render affected views/states, and repeat until required gates/floors pass or evidence is genuinely unavailable.
- Inputs are the minimum project facts, resolved artifact contract, and upstream decisions needed for deterministic execution.
- Output is an explicit decision, compiled specification, evidence record, quality state, or benchmark artifact.
- Invariants: higher-precedence instructions control; unknown facts remain unknown; production intent cannot be silently weakened; evidence cannot be fabricated.
- Prohibited shortcut: treating a feature/component name, generic template, design intention, confidence, or unverified assumption as completion.

### Procedure — BQ-1102
<!-- id: control.bq-1102 -->

1. Confirm this capability is triggered by artifact contract, production mode, dependency, or evaluation protocol.
2. Gather minimum relevant facts and upstream compiled outputs; mark unknown/unavailable evidence explicitly.
3. Execute the requirement exactly.
4. Resolve conflicts using README precedence, artifact specificity, risk, accessibility, truthfulness, and maintainability.
5. Persist the result when later work depends on it.
6. Re-evaluate after material scope, artifact, feature, data, visual, responsive, implementation, or evidence changes.

### Evidence Gate — BQ-1103
<!-- id: control.bq-1103 -->

- **PASS only if** direct specification/artifact/runtime/render/benchmark evidence demonstrates the requirement.
- Evidence identifies what was checked and the observed result. “Looks good,” “should work,” and design intention do not pass.
- Direct runtime/render/measurement evidence outranks prose/source inference when applicable.
- Unavailable required evidence is **UNVERIFIED**, never PASS.

### Recovery — BQ-1104
<!-- id: control.bq-1104 -->

- Block dependent completion claims on FAIL.
- Correct the upstream contract, feature/component specification, fingerprint, implementation, evaluation method, or repair plan and re-run the Evidence Gate.
- If correction is impossible with available facts/tools, preserve the limitation and safest non-fabricating fallback.
- Never lower a quality target, delete an applicable state, weaken a floor, or disclose a benchmark condition merely to pass.

### Regression — BQ-1105
<!-- id: control.bq-1105 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence conditions.
- Normal must produce the intended result; edge must preserve ambiguity or deterministic tie-breaking; failure must trigger Recovery.
- Real failures should strengthen a reusable regression fixture or benchmark case rather than only patch one artifact.

## Visual Quality Critic
<!-- id: controls.capability.visual-quality-critic -->

**Targets:** CRITICS.md / CREATIVE.md / CRAFT.md  
**Requirement:** Evaluate rendered hierarchy, composition, typography, media, spacing, surfaces, component finish, iconography, density, transitions, and visual defects with an adversarial rejection mindset.

### Contract — BQ-1106
<!-- id: control.bq-1106 -->

- **MUST:** Evaluate rendered hierarchy, composition, typography, media, spacing, surfaces, component finish, iconography, density, transitions, and visual defects with an adversarial rejection mindset.
- Inputs are the minimum project facts, resolved artifact contract, and upstream decisions needed for deterministic execution.
- Output is an explicit decision, compiled specification, evidence record, quality state, or benchmark artifact.
- Invariants: higher-precedence instructions control; unknown facts remain unknown; production intent cannot be silently weakened; evidence cannot be fabricated.
- Prohibited shortcut: treating a feature/component name, generic template, design intention, confidence, or unverified assumption as completion.

### Procedure — BQ-1107
<!-- id: control.bq-1107 -->

1. Confirm this capability is triggered by artifact contract, production mode, dependency, or evaluation protocol.
2. Gather minimum relevant facts and upstream compiled outputs; mark unknown/unavailable evidence explicitly.
3. Execute the requirement exactly.
4. Resolve conflicts using README precedence, artifact specificity, risk, accessibility, truthfulness, and maintainability.
5. Persist the result when later work depends on it.
6. Re-evaluate after material scope, artifact, feature, data, visual, responsive, implementation, or evidence changes.

### Evidence Gate — BQ-1108
<!-- id: control.bq-1108 -->

- **PASS only if** direct specification/artifact/runtime/render/benchmark evidence demonstrates the requirement.
- Evidence identifies what was checked and the observed result. “Looks good,” “should work,” and design intention do not pass.
- Direct runtime/render/measurement evidence outranks prose/source inference when applicable.
- Unavailable required evidence is **UNVERIFIED**, never PASS.

### Recovery — BQ-1109
<!-- id: control.bq-1109 -->

- Block dependent completion claims on FAIL.
- Correct the upstream contract, feature/component specification, fingerprint, implementation, evaluation method, or repair plan and re-run the Evidence Gate.
- If correction is impossible with available facts/tools, preserve the limitation and safest non-fabricating fallback.
- Never lower a quality target, delete an applicable state, weaken a floor, or disclose a benchmark condition merely to pass.

### Regression — BQ-1110
<!-- id: control.bq-1110 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence conditions.
- Normal must produce the intended result; edge must preserve ambiguity or deterministic tie-breaking; failure must trigger Recovery.
- Real failures should strengthen a reusable regression fixture or benchmark case rather than only patch one artifact.

## Feature Depth Critic
<!-- id: controls.capability.feature-depth-critic -->

**Targets:** CRITICS.md / FEATURE_COMPILER.md  
**Requirement:** Attempt to find shallow feature definitions, missing information/actions/states, dead ends, unclear recovery, weak user-job support, and implementation drift from compiled feature acceptance criteria.

### Contract — BQ-1111
<!-- id: control.bq-1111 -->

- **MUST:** Attempt to find shallow feature definitions, missing information/actions/states, dead ends, unclear recovery, weak user-job support, and implementation drift from compiled feature acceptance criteria.
- Inputs are the minimum project facts, resolved artifact contract, and upstream decisions needed for deterministic execution.
- Output is an explicit decision, compiled specification, evidence record, quality state, or benchmark artifact.
- Invariants: higher-precedence instructions control; unknown facts remain unknown; production intent cannot be silently weakened; evidence cannot be fabricated.
- Prohibited shortcut: treating a feature/component name, generic template, design intention, confidence, or unverified assumption as completion.

### Procedure — BQ-1112
<!-- id: control.bq-1112 -->

1. Confirm this capability is triggered by artifact contract, production mode, dependency, or evaluation protocol.
2. Gather minimum relevant facts and upstream compiled outputs; mark unknown/unavailable evidence explicitly.
3. Execute the requirement exactly.
4. Resolve conflicts using README precedence, artifact specificity, risk, accessibility, truthfulness, and maintainability.
5. Persist the result when later work depends on it.
6. Re-evaluate after material scope, artifact, feature, data, visual, responsive, implementation, or evidence changes.

### Evidence Gate — BQ-1113
<!-- id: control.bq-1113 -->

- **PASS only if** direct specification/artifact/runtime/render/benchmark evidence demonstrates the requirement.
- Evidence identifies what was checked and the observed result. “Looks good,” “should work,” and design intention do not pass.
- Direct runtime/render/measurement evidence outranks prose/source inference when applicable.
- Unavailable required evidence is **UNVERIFIED**, never PASS.

### Recovery — BQ-1114
<!-- id: control.bq-1114 -->

- Block dependent completion claims on FAIL.
- Correct the upstream contract, feature/component specification, fingerprint, implementation, evaluation method, or repair plan and re-run the Evidence Gate.
- If correction is impossible with available facts/tools, preserve the limitation and safest non-fabricating fallback.
- Never lower a quality target, delete an applicable state, weaken a floor, or disclose a benchmark condition merely to pass.

### Regression — BQ-1115
<!-- id: control.bq-1115 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence conditions.
- Normal must produce the intended result; edge must preserve ambiguity or deterministic tie-breaking; failure must trigger Recovery.
- Real failures should strengthen a reusable regression fixture or benchmark case rather than only patch one artifact.

## Accessibility Responsive Critic
<!-- id: controls.capability.accessibility-responsive-critic -->

**Targets:** CRITICS.md / DESIGN.md / QA_GATES.md  
**Requirement:** Attempt to find accessibility, keyboard, focus, contrast, target-size, zoom/reflow, table/mobile transformation, density, and desktop-stacking failures in critical paths.

### Contract — BQ-1116
<!-- id: control.bq-1116 -->

- **MUST:** Attempt to find accessibility, keyboard, focus, contrast, target-size, zoom/reflow, table/mobile transformation, density, and desktop-stacking failures in critical paths.
- Inputs are the minimum project facts, resolved artifact contract, and upstream decisions needed for deterministic execution.
- Output is an explicit decision, compiled specification, evidence record, quality state, or benchmark artifact.
- Invariants: higher-precedence instructions control; unknown facts remain unknown; production intent cannot be silently weakened; evidence cannot be fabricated.
- Prohibited shortcut: treating a feature/component name, generic template, design intention, confidence, or unverified assumption as completion.

### Procedure — BQ-1117
<!-- id: control.bq-1117 -->

1. Confirm this capability is triggered by artifact contract, production mode, dependency, or evaluation protocol.
2. Gather minimum relevant facts and upstream compiled outputs; mark unknown/unavailable evidence explicitly.
3. Execute the requirement exactly.
4. Resolve conflicts using README precedence, artifact specificity, risk, accessibility, truthfulness, and maintainability.
5. Persist the result when later work depends on it.
6. Re-evaluate after material scope, artifact, feature, data, visual, responsive, implementation, or evidence changes.

### Evidence Gate — BQ-1118
<!-- id: control.bq-1118 -->

- **PASS only if** direct specification/artifact/runtime/render/benchmark evidence demonstrates the requirement.
- Evidence identifies what was checked and the observed result. “Looks good,” “should work,” and design intention do not pass.
- Direct runtime/render/measurement evidence outranks prose/source inference when applicable.
- Unavailable required evidence is **UNVERIFIED**, never PASS.

### Recovery — BQ-1119
<!-- id: control.bq-1119 -->

- Block dependent completion claims on FAIL.
- Correct the upstream contract, feature/component specification, fingerprint, implementation, evaluation method, or repair plan and re-run the Evidence Gate.
- If correction is impossible with available facts/tools, preserve the limitation and safest non-fabricating fallback.
- Never lower a quality target, delete an applicable state, weaken a floor, or disclose a benchmark condition merely to pass.

### Regression — BQ-1120
<!-- id: control.bq-1120 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence conditions.
- Normal must produce the intended result; edge must preserve ambiguity or deterministic tie-breaking; failure must trigger Recovery.
- Real failures should strengthen a reusable regression fixture or benchmark case rather than only patch one artifact.

## Truth Implementation Critic
<!-- id: controls.capability.truth-implementation-critic -->

**Targets:** CRITICS.md / SECURITY.md / LEGAL.md / QA_GATES.md  
**Requirement:** Attempt to find fabricated claims, unlabeled sample data, fake backend semantics, dead controls, broken paths/assets, runtime errors, and mismatches between promised and implemented behavior.

### Contract — BQ-1121
<!-- id: control.bq-1121 -->

- **MUST:** Attempt to find fabricated claims, unlabeled sample data, fake backend semantics, dead controls, broken paths/assets, runtime errors, and mismatches between promised and implemented behavior.
- Inputs are the minimum project facts, resolved artifact contract, and upstream decisions needed for deterministic execution.
- Output is an explicit decision, compiled specification, evidence record, quality state, or benchmark artifact.
- Invariants: higher-precedence instructions control; unknown facts remain unknown; production intent cannot be silently weakened; evidence cannot be fabricated.
- Prohibited shortcut: treating a feature/component name, generic template, design intention, confidence, or unverified assumption as completion.

### Procedure — BQ-1122
<!-- id: control.bq-1122 -->

1. Confirm this capability is triggered by artifact contract, production mode, dependency, or evaluation protocol.
2. Gather minimum relevant facts and upstream compiled outputs; mark unknown/unavailable evidence explicitly.
3. Execute the requirement exactly.
4. Resolve conflicts using README precedence, artifact specificity, risk, accessibility, truthfulness, and maintainability.
5. Persist the result when later work depends on it.
6. Re-evaluate after material scope, artifact, feature, data, visual, responsive, implementation, or evidence changes.

### Evidence Gate — BQ-1123
<!-- id: control.bq-1123 -->

- **PASS only if** direct specification/artifact/runtime/render/benchmark evidence demonstrates the requirement.
- Evidence identifies what was checked and the observed result. “Looks good,” “should work,” and design intention do not pass.
- Direct runtime/render/measurement evidence outranks prose/source inference when applicable.
- Unavailable required evidence is **UNVERIFIED**, never PASS.

### Recovery — BQ-1124
<!-- id: control.bq-1124 -->

- Block dependent completion claims on FAIL.
- Correct the upstream contract, feature/component specification, fingerprint, implementation, evaluation method, or repair plan and re-run the Evidence Gate.
- If correction is impossible with available facts/tools, preserve the limitation and safest non-fabricating fallback.
- Never lower a quality target, delete an applicable state, weaken a floor, or disclose a benchmark condition merely to pass.

### Regression — BQ-1125
<!-- id: control.bq-1125 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence conditions.
- Normal must produce the intended result; edge must preserve ambiguity or deterministic tie-breaking; failure must trigger Recovery.
- Real failures should strengthen a reusable regression fixture or benchmark case rather than only patch one artifact.

## Genericity Critic
<!-- id: controls.capability.genericity-critic -->

**Targets:** CRITICS.md / GENERICITY.md  
**Requirement:** Attempt to disprove project specificity from the rendered artifact by identifying common template sequences, universal card grammar, interchangeable sections, and weak domain/task differentiation.

### Contract — BQ-1126
<!-- id: control.bq-1126 -->

- **MUST:** Attempt to disprove project specificity from the rendered artifact by identifying common template sequences, universal card grammar, interchangeable sections, and weak domain/task differentiation.
- Inputs are the minimum project facts, resolved artifact contract, and upstream decisions needed for deterministic execution.
- Output is an explicit decision, compiled specification, evidence record, quality state, or benchmark artifact.
- Invariants: higher-precedence instructions control; unknown facts remain unknown; production intent cannot be silently weakened; evidence cannot be fabricated.
- Prohibited shortcut: treating a feature/component name, generic template, design intention, confidence, or unverified assumption as completion.

### Procedure — BQ-1127
<!-- id: control.bq-1127 -->

1. Confirm this capability is triggered by artifact contract, production mode, dependency, or evaluation protocol.
2. Gather minimum relevant facts and upstream compiled outputs; mark unknown/unavailable evidence explicitly.
3. Execute the requirement exactly.
4. Resolve conflicts using README precedence, artifact specificity, risk, accessibility, truthfulness, and maintainability.
5. Persist the result when later work depends on it.
6. Re-evaluate after material scope, artifact, feature, data, visual, responsive, implementation, or evidence changes.

### Evidence Gate — BQ-1128
<!-- id: control.bq-1128 -->

- **PASS only if** direct specification/artifact/runtime/render/benchmark evidence demonstrates the requirement.
- Evidence identifies what was checked and the observed result. “Looks good,” “should work,” and design intention do not pass.
- Direct runtime/render/measurement evidence outranks prose/source inference when applicable.
- Unavailable required evidence is **UNVERIFIED**, never PASS.

### Recovery — BQ-1129
<!-- id: control.bq-1129 -->

- Block dependent completion claims on FAIL.
- Correct the upstream contract, feature/component specification, fingerprint, implementation, evaluation method, or repair plan and re-run the Evidence Gate.
- If correction is impossible with available facts/tools, preserve the limitation and safest non-fabricating fallback.
- Never lower a quality target, delete an applicable state, weaken a floor, or disclose a benchmark condition merely to pass.

### Regression — BQ-1130
<!-- id: control.bq-1130 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence conditions.
- Normal must produce the intended result; edge must preserve ambiguity or deterministic tie-breaking; failure must trigger Recovery.
- Real failures should strengthen a reusable regression fixture or benchmark case rather than only patch one artifact.

## Repair Plan Prioritization
<!-- id: controls.capability.repair-plan-prioritization -->

**Targets:** CRITICS.md  
**Requirement:** Consolidate critic findings into a severity- and dependency-aware repair plan that fixes truth/safety/task correctness before genericity, component craft, and decorative polish.

### Contract — BQ-1131
<!-- id: control.bq-1131 -->

- **MUST:** Consolidate critic findings into a severity- and dependency-aware repair plan that fixes truth/safety/task correctness before genericity, component craft, and decorative polish.
- Inputs are the minimum project facts, resolved artifact contract, and upstream decisions needed for deterministic execution.
- Output is an explicit decision, compiled specification, evidence record, quality state, or benchmark artifact.
- Invariants: higher-precedence instructions control; unknown facts remain unknown; production intent cannot be silently weakened; evidence cannot be fabricated.
- Prohibited shortcut: treating a feature/component name, generic template, design intention, confidence, or unverified assumption as completion.

### Procedure — BQ-1132
<!-- id: control.bq-1132 -->

1. Confirm this capability is triggered by artifact contract, production mode, dependency, or evaluation protocol.
2. Gather minimum relevant facts and upstream compiled outputs; mark unknown/unavailable evidence explicitly.
3. Execute the requirement exactly.
4. Resolve conflicts using README precedence, artifact specificity, risk, accessibility, truthfulness, and maintainability.
5. Persist the result when later work depends on it.
6. Re-evaluate after material scope, artifact, feature, data, visual, responsive, implementation, or evidence changes.

### Evidence Gate — BQ-1133
<!-- id: control.bq-1133 -->

- **PASS only if** direct specification/artifact/runtime/render/benchmark evidence demonstrates the requirement.
- Evidence identifies what was checked and the observed result. “Looks good,” “should work,” and design intention do not pass.
- Direct runtime/render/measurement evidence outranks prose/source inference when applicable.
- Unavailable required evidence is **UNVERIFIED**, never PASS.

### Recovery — BQ-1134
<!-- id: control.bq-1134 -->

- Block dependent completion claims on FAIL.
- Correct the upstream contract, feature/component specification, fingerprint, implementation, evaluation method, or repair plan and re-run the Evidence Gate.
- If correction is impossible with available facts/tools, preserve the limitation and safest non-fabricating fallback.
- Never lower a quality target, delete an applicable state, weaken a floor, or disclose a benchmark condition merely to pass.

### Regression — BQ-1135
<!-- id: control.bq-1135 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence conditions.
- Normal must produce the intended result; edge must preserve ambiguity or deterministic tie-breaking; failure must trigger Recovery.
- Real failures should strengthen a reusable regression fixture or benchmark case rather than only patch one artifact.

## Category Floor Enforcement
<!-- id: controls.capability.category-floor-enforcement -->

**Targets:** QUALITY_FLOORS.md / contracts/*  
**Requirement:** Block production completion when any applicable artifact-specific dimension floor fails even if the aggregate score is high; never average away truth, accessibility, responsiveness, feature-depth, or implementation failures.

### Contract — BQ-1136
<!-- id: control.bq-1136 -->

- **MUST:** Block production completion when any applicable artifact-specific dimension floor fails even if the aggregate score is high; never average away truth, accessibility, responsiveness, feature-depth, or implementation failures.
- Inputs are the minimum project facts, resolved artifact contract, and upstream decisions needed for deterministic execution.
- Output is an explicit decision, compiled specification, evidence record, quality state, or benchmark artifact.
- Invariants: higher-precedence instructions control; unknown facts remain unknown; production intent cannot be silently weakened; evidence cannot be fabricated.
- Prohibited shortcut: treating a feature/component name, generic template, design intention, confidence, or unverified assumption as completion.

### Procedure — BQ-1137
<!-- id: control.bq-1137 -->

1. Confirm this capability is triggered by artifact contract, production mode, dependency, or evaluation protocol.
2. Gather minimum relevant facts and upstream compiled outputs; mark unknown/unavailable evidence explicitly.
3. Execute the requirement exactly.
4. Resolve conflicts using README precedence, artifact specificity, risk, accessibility, truthfulness, and maintainability.
5. Persist the result when later work depends on it.
6. Re-evaluate after material scope, artifact, feature, data, visual, responsive, implementation, or evidence changes.

### Evidence Gate — BQ-1138
<!-- id: control.bq-1138 -->

- **PASS only if** direct specification/artifact/runtime/render/benchmark evidence demonstrates the requirement.
- Evidence identifies what was checked and the observed result. “Looks good,” “should work,” and design intention do not pass.
- Direct runtime/render/measurement evidence outranks prose/source inference when applicable.
- Unavailable required evidence is **UNVERIFIED**, never PASS.

### Recovery — BQ-1139
<!-- id: control.bq-1139 -->

- Block dependent completion claims on FAIL.
- Correct the upstream contract, feature/component specification, fingerprint, implementation, evaluation method, or repair plan and re-run the Evidence Gate.
- If correction is impossible with available facts/tools, preserve the limitation and safest non-fabricating fallback.
- Never lower a quality target, delete an applicable state, weaken a floor, or disclose a benchmark condition merely to pass.

### Regression — BQ-1140
<!-- id: control.bq-1140 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence conditions.
- Normal must produce the intended result; edge must preserve ambiguity or deterministic tie-breaking; failure must trigger Recovery.
- Real failures should strengthen a reusable regression fixture or benchmark case rather than only patch one artifact.

## Blind Benchmark Protocol
<!-- id: controls.capability.blind-benchmark-protocol -->

**Targets:** BENCHMARKS.md / benchmarks/* / tools/prepare_benchmark.py  
**Requirement:** Evaluate AIFENCE efficacy with matched control/AIFENCE conditions, randomized opaque artifact IDs, locked blind scoring, multiple independent evidence sources, and unblinding only after scores are fixed.

### Contract — BQ-1141
<!-- id: control.bq-1141 -->

- **MUST:** Evaluate AIFENCE efficacy with matched control/AIFENCE conditions, randomized opaque artifact IDs, locked blind scoring, multiple independent evidence sources, and unblinding only after scores are fixed.
- Inputs are the minimum project facts, resolved artifact contract, and upstream decisions needed for deterministic execution.
- Output is an explicit decision, compiled specification, evidence record, quality state, or benchmark artifact.
- Invariants: higher-precedence instructions control; unknown facts remain unknown; production intent cannot be silently weakened; evidence cannot be fabricated.
- Prohibited shortcut: treating a feature/component name, generic template, design intention, confidence, or unverified assumption as completion.

### Procedure — BQ-1142
<!-- id: control.bq-1142 -->

1. Confirm this capability is triggered by artifact contract, production mode, dependency, or evaluation protocol.
2. Gather minimum relevant facts and upstream compiled outputs; mark unknown/unavailable evidence explicitly.
3. Execute the requirement exactly.
4. Resolve conflicts using README precedence, artifact specificity, risk, accessibility, truthfulness, and maintainability.
5. Persist the result when later work depends on it.
6. Re-evaluate after material scope, artifact, feature, data, visual, responsive, implementation, or evidence changes.

### Evidence Gate — BQ-1143
<!-- id: control.bq-1143 -->

- **PASS only if** direct specification/artifact/runtime/render/benchmark evidence demonstrates the requirement.
- Evidence identifies what was checked and the observed result. “Looks good,” “should work,” and design intention do not pass.
- Direct runtime/render/measurement evidence outranks prose/source inference when applicable.
- Unavailable required evidence is **UNVERIFIED**, never PASS.

### Recovery — BQ-1144
<!-- id: control.bq-1144 -->

- Block dependent completion claims on FAIL.
- Correct the upstream contract, feature/component specification, fingerprint, implementation, evaluation method, or repair plan and re-run the Evidence Gate.
- If correction is impossible with available facts/tools, preserve the limitation and safest non-fabricating fallback.
- Never lower a quality target, delete an applicable state, weaken a floor, or disclose a benchmark condition merely to pass.

### Regression — BQ-1145
<!-- id: control.bq-1145 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence conditions.
- Normal must produce the intended result; edge must preserve ambiguity or deterministic tie-breaking; failure must trigger Recovery.
- Real failures should strengthen a reusable regression fixture or benchmark case rather than only patch one artifact.

## Holdout Regression Governance
<!-- id: controls.capability.holdout-regression-governance -->

**Targets:** BENCHMARKS.md / EVALS.md  
**Requirement:** Maintain a private external holdout, rotate it after major improvements, compare category/dimension regressions, and prevent public-benchmark overfitting or single-judge optimization.

### Contract — BQ-1146
<!-- id: control.bq-1146 -->

- **MUST:** Maintain a private external holdout, rotate it after major improvements, compare category/dimension regressions, and prevent public-benchmark overfitting or single-judge optimization.
- Inputs are the minimum project facts, resolved artifact contract, and upstream decisions needed for deterministic execution.
- Output is an explicit decision, compiled specification, evidence record, quality state, or benchmark artifact.
- Invariants: higher-precedence instructions control; unknown facts remain unknown; production intent cannot be silently weakened; evidence cannot be fabricated.
- Prohibited shortcut: treating a feature/component name, generic template, design intention, confidence, or unverified assumption as completion.

### Procedure — BQ-1147
<!-- id: control.bq-1147 -->

1. Confirm this capability is triggered by artifact contract, production mode, dependency, or evaluation protocol.
2. Gather minimum relevant facts and upstream compiled outputs; mark unknown/unavailable evidence explicitly.
3. Execute the requirement exactly.
4. Resolve conflicts using README precedence, artifact specificity, risk, accessibility, truthfulness, and maintainability.
5. Persist the result when later work depends on it.
6. Re-evaluate after material scope, artifact, feature, data, visual, responsive, implementation, or evidence changes.

### Evidence Gate — BQ-1148
<!-- id: control.bq-1148 -->

- **PASS only if** direct specification/artifact/runtime/render/benchmark evidence demonstrates the requirement.
- Evidence identifies what was checked and the observed result. “Looks good,” “should work,” and design intention do not pass.
- Direct runtime/render/measurement evidence outranks prose/source inference when applicable.
- Unavailable required evidence is **UNVERIFIED**, never PASS.

### Recovery — BQ-1149
<!-- id: control.bq-1149 -->

- Block dependent completion claims on FAIL.
- Correct the upstream contract, feature/component specification, fingerprint, implementation, evaluation method, or repair plan and re-run the Evidence Gate.
- If correction is impossible with available facts/tools, preserve the limitation and safest non-fabricating fallback.
- Never lower a quality target, delete an applicable state, weaken a floor, or disclose a benchmark condition merely to pass.

### Regression — BQ-1150
<!-- id: control.bq-1150 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence conditions.
- Normal must produce the intended result; edge must preserve ambiguity or deterministic tie-breaking; failure must trigger Recovery.
- Real failures should strengthen a reusable regression fixture or benchmark case rather than only patch one artifact.
