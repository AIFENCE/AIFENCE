<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: CONTROLS
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-09
-->

# 29. Benchmark-Driven Quality Hardening
<!-- id: controls.domain.29 -->

Domain 29 addresses measured Revision 1.2 benchmark gaps in responsive composition, document craftsmanship, accessibility evidence, completeness, and feature depth while preserving the existing genericity system.

## Mobile Priority & Recomposition
<!-- id: controls.capability.mobile-priority-recomposition -->

**Targets:** RESPONSIVE_COMPOSITION.md  
**Requirement:** Require an explicit mobile priority map and task-preserving layout recomposition rather than desktop stacking or compression.

### Contract — BQ-1151
<!-- id: control.bq-1151 -->

- **MUST:** Require an explicit mobile priority map and task-preserving layout recomposition rather than desktop stacking or compression.
- Preserve higher-precedence requirements, truthful unknowns, and applicable artifact-specific floors.

### Procedure — BQ-1152
<!-- id: control.bq-1152 -->

1. Resolve the active artifact contract and affected P0/P1 user jobs.
2. Produce the required plan/evidence structure before claiming completion.
3. Exercise representative normal, edge, mobile/document/accessibility states as applicable.
4. Record direct evidence and affected quality dimensions.
5. Re-run after material repair.

### Evidence Gate — BQ-1153
<!-- id: control.bq-1153 -->

- **PASS only if** direct specification/render/runtime/document evidence demonstrates the requirement.
- Missing required evidence is **UNVERIFIED**, not PASS.
- Evidence must identify viewport/path/section/state and observed result.

### Recovery — BQ-1154
<!-- id: control.bq-1154 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate affected adjacent dimensions including genericity resistance.
- Never delete a requirement or hide task-critical content merely to remove a failure.

### Regression — BQ-1155
<!-- id: control.bq-1155 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Benchmark-derived failures must remain reproducible regression cases.

## Dense Mobile Control Compression
<!-- id: controls.capability.dense-mobile-control-compression -->

**Targets:** RESPONSIVE_COMPOSITION.md  
**Requirement:** Transform search/filter/date/view/bulk/primary-action toolbars into a narrow-screen interaction model without clipping, crowding, or hidden critical state.

### Contract — BQ-1156
<!-- id: control.bq-1156 -->

- **MUST:** Transform search/filter/date/view/bulk/primary-action toolbars into a narrow-screen interaction model without clipping, crowding, or hidden critical state.
- Preserve higher-precedence requirements, truthful unknowns, and applicable artifact-specific floors.

### Procedure — BQ-1157
<!-- id: control.bq-1157 -->

1. Resolve the active artifact contract and affected P0/P1 user jobs.
2. Produce the required plan/evidence structure before claiming completion.
3. Exercise representative normal, edge, mobile/document/accessibility states as applicable.
4. Record direct evidence and affected quality dimensions.
5. Re-run after material repair.

### Evidence Gate — BQ-1158
<!-- id: control.bq-1158 -->

- **PASS only if** direct specification/render/runtime/document evidence demonstrates the requirement.
- Missing required evidence is **UNVERIFIED**, not PASS.
- Evidence must identify viewport/path/section/state and observed result.

### Recovery — BQ-1159
<!-- id: control.bq-1159 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate affected adjacent dimensions including genericity resistance.
- Never delete a requirement or hide task-critical content merely to remove a failure.

### Regression — BQ-1160
<!-- id: control.bq-1160 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Benchmark-derived failures must remain reproducible regression cases.

## Responsive Data Transformation
<!-- id: controls.capability.responsive-data-transformation -->

**Targets:** RESPONSIVE_COMPOSITION.md  
**Requirement:** Give tables, comparison, charts, and dense lists an explicit mobile data strategy that preserves decision context and task completion.

### Contract — BQ-1161
<!-- id: control.bq-1161 -->

- **MUST:** Give tables, comparison, charts, and dense lists an explicit mobile data strategy that preserves decision context and task completion.
- Preserve higher-precedence requirements, truthful unknowns, and applicable artifact-specific floors.

### Procedure — BQ-1162
<!-- id: control.bq-1162 -->

1. Resolve the active artifact contract and affected P0/P1 user jobs.
2. Produce the required plan/evidence structure before claiming completion.
3. Exercise representative normal, edge, mobile/document/accessibility states as applicable.
4. Record direct evidence and affected quality dimensions.
5. Re-run after material repair.

### Evidence Gate — BQ-1163
<!-- id: control.bq-1163 -->

- **PASS only if** direct specification/render/runtime/document evidence demonstrates the requirement.
- Missing required evidence is **UNVERIFIED**, not PASS.
- Evidence must identify viewport/path/section/state and observed result.

### Recovery — BQ-1164
<!-- id: control.bq-1164 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate affected adjacent dimensions including genericity resistance.
- Never delete a requirement or hide task-critical content merely to remove a failure.

### Regression — BQ-1165
<!-- id: control.bq-1165 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Benchmark-derived failures must remain reproducible regression cases.

## Document Decision Depth
<!-- id: controls.capability.document-decision-depth -->

**Targets:** DOCUMENT_CRAFT.md  
**Requirement:** Evaluate substantial documents through decision/evidence depth, traceability, risks, alternatives, recommendation, and action closure rather than UI feature counts.

### Contract — BQ-1166
<!-- id: control.bq-1166 -->

- **MUST:** Evaluate substantial documents through decision/evidence depth, traceability, risks, alternatives, recommendation, and action closure rather than UI feature counts.
- Preserve higher-precedence requirements, truthful unknowns, and applicable artifact-specific floors.

### Procedure — BQ-1167
<!-- id: control.bq-1167 -->

1. Resolve the active artifact contract and affected P0/P1 user jobs.
2. Produce the required plan/evidence structure before claiming completion.
3. Exercise representative normal, edge, mobile/document/accessibility states as applicable.
4. Record direct evidence and affected quality dimensions.
5. Re-run after material repair.

### Evidence Gate — BQ-1168
<!-- id: control.bq-1168 -->

- **PASS only if** direct specification/render/runtime/document evidence demonstrates the requirement.
- Missing required evidence is **UNVERIFIED**, not PASS.
- Evidence must identify viewport/path/section/state and observed result.

### Recovery — BQ-1169
<!-- id: control.bq-1169 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate affected adjacent dimensions including genericity resistance.
- Never delete a requirement or hide task-critical content merely to remove a failure.

### Regression — BQ-1170
<!-- id: control.bq-1170 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Benchmark-derived failures must remain reproducible regression cases.

## Document Editorial Craft
<!-- id: controls.capability.document-editorial-craft -->

**Targets:** DOCUMENT_CRAFT.md  
**Requirement:** Use document-type-specific information architecture and editorial visual grammar with purposeful tables, diagrams, timelines, matrices, hierarchy, and page rhythm.

### Contract — BQ-1171
<!-- id: control.bq-1171 -->

- **MUST:** Use document-type-specific information architecture and editorial visual grammar with purposeful tables, diagrams, timelines, matrices, hierarchy, and page rhythm.
- Preserve higher-precedence requirements, truthful unknowns, and applicable artifact-specific floors.

### Procedure — BQ-1172
<!-- id: control.bq-1172 -->

1. Resolve the active artifact contract and affected P0/P1 user jobs.
2. Produce the required plan/evidence structure before claiming completion.
3. Exercise representative normal, edge, mobile/document/accessibility states as applicable.
4. Record direct evidence and affected quality dimensions.
5. Re-run after material repair.

### Evidence Gate — BQ-1173
<!-- id: control.bq-1173 -->

- **PASS only if** direct specification/render/runtime/document evidence demonstrates the requirement.
- Missing required evidence is **UNVERIFIED**, not PASS.
- Evidence must identify viewport/path/section/state and observed result.

### Recovery — BQ-1174
<!-- id: control.bq-1174 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate affected adjacent dimensions including genericity resistance.
- Never delete a requirement or hide task-critical content merely to remove a failure.

### Regression — BQ-1175
<!-- id: control.bq-1175 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Benchmark-derived failures must remain reproducible regression cases.

## Accessibility Evidence Matrix
<!-- id: controls.capability.accessibility-evidence-matrix -->

**Targets:** ACCESSIBILITY_EVIDENCE.md  
**Requirement:** Require observable accessibility evidence for critical paths instead of passing from static semantics or automated inference alone.

### Contract — BQ-1176
<!-- id: control.bq-1176 -->

- **MUST:** Require observable accessibility evidence for critical paths instead of passing from static semantics or automated inference alone.
- Preserve higher-precedence requirements, truthful unknowns, and applicable artifact-specific floors.

### Procedure — BQ-1177
<!-- id: control.bq-1177 -->

1. Resolve the active artifact contract and affected P0/P1 user jobs.
2. Produce the required plan/evidence structure before claiming completion.
3. Exercise representative normal, edge, mobile/document/accessibility states as applicable.
4. Record direct evidence and affected quality dimensions.
5. Re-run after material repair.

### Evidence Gate — BQ-1178
<!-- id: control.bq-1178 -->

- **PASS only if** direct specification/render/runtime/document evidence demonstrates the requirement.
- Missing required evidence is **UNVERIFIED**, not PASS.
- Evidence must identify viewport/path/section/state and observed result.

### Recovery — BQ-1179
<!-- id: control.bq-1179 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate affected adjacent dimensions including genericity resistance.
- Never delete a requirement or hide task-critical content merely to remove a failure.

### Regression — BQ-1180
<!-- id: control.bq-1180 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Benchmark-derived failures must remain reproducible regression cases.

## Keyboard Focus & Dynamic Feedback
<!-- id: controls.capability.keyboard-focus-dynamic-feedback -->

**Targets:** ACCESSIBILITY_EVIDENCE.md  
**Requirement:** Verify keyboard completion, visible/logical focus, focus entry/return, validation association, and programmatic status/error feedback on critical paths.

### Contract — BQ-1181
<!-- id: control.bq-1181 -->

- **MUST:** Verify keyboard completion, visible/logical focus, focus entry/return, validation association, and programmatic status/error feedback on critical paths.
- Preserve higher-precedence requirements, truthful unknowns, and applicable artifact-specific floors.

### Procedure — BQ-1182
<!-- id: control.bq-1182 -->

1. Resolve the active artifact contract and affected P0/P1 user jobs.
2. Produce the required plan/evidence structure before claiming completion.
3. Exercise representative normal, edge, mobile/document/accessibility states as applicable.
4. Record direct evidence and affected quality dimensions.
5. Re-run after material repair.

### Evidence Gate — BQ-1183
<!-- id: control.bq-1183 -->

- **PASS only if** direct specification/render/runtime/document evidence demonstrates the requirement.
- Missing required evidence is **UNVERIFIED**, not PASS.
- Evidence must identify viewport/path/section/state and observed result.

### Recovery — BQ-1184
<!-- id: control.bq-1184 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate affected adjacent dimensions including genericity resistance.
- Never delete a requirement or hide task-critical content merely to remove a failure.

### Regression — BQ-1185
<!-- id: control.bq-1185 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Benchmark-derived failures must remain reproducible regression cases.

## Completion Coverage Ledger
<!-- id: controls.capability.completion-coverage-ledger -->

**Targets:** COMPLETENESS.md  
**Requirement:** Track P0/P1 user-job, path, state, responsive, accessibility, truth, dependency, and evidence closure so omissions cannot hide behind aggregate completeness.

### Contract — BQ-1186
<!-- id: control.bq-1186 -->

- **MUST:** Track P0/P1 user-job, path, state, responsive, accessibility, truth, dependency, and evidence closure so omissions cannot hide behind aggregate completeness.
- Preserve higher-precedence requirements, truthful unknowns, and applicable artifact-specific floors.

### Procedure — BQ-1187
<!-- id: control.bq-1187 -->

1. Resolve the active artifact contract and affected P0/P1 user jobs.
2. Produce the required plan/evidence structure before claiming completion.
3. Exercise representative normal, edge, mobile/document/accessibility states as applicable.
4. Record direct evidence and affected quality dimensions.
5. Re-run after material repair.

### Evidence Gate — BQ-1188
<!-- id: control.bq-1188 -->

- **PASS only if** direct specification/render/runtime/document evidence demonstrates the requirement.
- Missing required evidence is **UNVERIFIED**, not PASS.
- Evidence must identify viewport/path/section/state and observed result.

### Recovery — BQ-1189
<!-- id: control.bq-1189 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate affected adjacent dimensions including genericity resistance.
- Never delete a requirement or hide task-critical content merely to remove a failure.

### Regression — BQ-1190
<!-- id: control.bq-1190 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Benchmark-derived failures must remain reproducible regression cases.

## Feature Depth Closure
<!-- id: controls.capability.feature-depth-closure -->

**Targets:** FEATURE_DEPTH.md  
**Requirement:** Require production P0/P1 features to close information, action, state/recovery, responsive, accessibility, dependency, acceptance, and applicable buyer-decision/workflow integration dimensions.

### Contract — BQ-1191
<!-- id: control.bq-1191 -->

- **MUST:** Require production P0/P1 features to close information, action, state/recovery, responsive, accessibility, dependency, acceptance, and applicable buyer-decision/workflow integration dimensions.
- Preserve higher-precedence requirements, truthful unknowns, and applicable artifact-specific floors.

### Procedure — BQ-1192
<!-- id: control.bq-1192 -->

1. Resolve the active artifact contract and affected P0/P1 user jobs.
2. Produce the required plan/evidence structure before claiming completion.
3. Exercise representative normal, edge, mobile/document/accessibility states as applicable.
4. Record direct evidence and affected quality dimensions.
5. Re-run after material repair.

### Evidence Gate — BQ-1193
<!-- id: control.bq-1193 -->

- **PASS only if** direct specification/render/runtime/document evidence demonstrates the requirement.
- Missing required evidence is **UNVERIFIED**, not PASS.
- Evidence must identify viewport/path/section/state and observed result.

### Recovery — BQ-1194
<!-- id: control.bq-1194 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate affected adjacent dimensions including genericity resistance.
- Never delete a requirement or hide task-critical content merely to remove a failure.

### Regression — BQ-1195
<!-- id: control.bq-1195 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Benchmark-derived failures must remain reproducible regression cases.

## Cross-Dimension Repair Preservation
<!-- id: controls.capability.cross-dimension-repair-preservation -->

**Targets:** CRITICS.md / GENERICITY.md / QUALITY_FLOORS.md  
**Requirement:** After targeted repairs, revalidate adjacent quality dimensions and preserve genericity resistance; a fix cannot pass by creating template sameness, truth regression, or task loss.

### Contract — BQ-1196
<!-- id: control.bq-1196 -->

- **MUST:** After targeted repairs, revalidate adjacent quality dimensions and preserve genericity resistance; a fix cannot pass by creating template sameness, truth regression, or task loss.
- Preserve higher-precedence requirements, truthful unknowns, and applicable artifact-specific floors.

### Procedure — BQ-1197
<!-- id: control.bq-1197 -->

1. Resolve the active artifact contract and affected P0/P1 user jobs.
2. Produce the required plan/evidence structure before claiming completion.
3. Exercise representative normal, edge, mobile/document/accessibility states as applicable.
4. Record direct evidence and affected quality dimensions.
5. Re-run after material repair.

### Evidence Gate — BQ-1198
<!-- id: control.bq-1198 -->

- **PASS only if** direct specification/render/runtime/document evidence demonstrates the requirement.
- Missing required evidence is **UNVERIFIED**, not PASS.
- Evidence must identify viewport/path/section/state and observed result.

### Recovery — BQ-1199
<!-- id: control.bq-1199 -->

- Block dependent completion on FAIL.
- Repair the smallest upstream cause, then revalidate affected adjacent dimensions including genericity resistance.
- Never delete a requirement or hide task-critical content merely to remove a failure.

### Regression — BQ-1200
<!-- id: control.bq-1200 -->

- Maintain normal, ambiguous/edge, and failure/unavailable-evidence fixtures.
- Benchmark-derived failures must remain reproducible regression cases.
