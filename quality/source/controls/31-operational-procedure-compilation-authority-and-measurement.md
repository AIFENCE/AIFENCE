<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: CONTROL_DOMAIN_31
Module-Version: 2
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-09
-->

# Domain 31 — Operational Procedure Compilation, Authority & Measurement
<!-- id: controls.domain-31 -->

Purpose: make AIFENCE operational outputs executable, authority-aware, measurable, auditable, and resistant to false procedural certainty. This domain strengthens Domain 23 rather than replacing its stable BQ controls.

## Domain Execution Rule
<!-- id: controls.domain-31.execution-rule -->

Use the smallest relevant capability set. For substantial operating procedures, activate operational context, authority classification, executable compilation, decision rights, exception/recovery, evidence/definition-of-done, KPI governance when metrics are material, and procedure lifecycle controls. Existing `operations/*.md` SOP sections provide baseline role/profile context; they are not proof that the compiled procedure is organization-approved or externally authoritative.

## Operational Context Resolution
<!-- id: controls.capability.operational-context-resolution -->

**Targets:** OPERATIONAL_PROCEDURE_COMPILER.md / JOBS.md / operations/*  
**Requirement:** Resolve exact industry, subindustry, business model, organization/site context, role, task, trigger, risk, systems, and material unknowns before compiling an operational procedure.

### Contract — BQ-1251
<!-- id: control.bq-1251 -->

- **MUST:** Resolve exact industry, subindustry, business model, organization/site context, role, task, trigger, risk, systems, and material unknowns before compiling an operational procedure.
- Preserve truthful unknowns, applicable professional/licensing boundaries, organization authority, external-source provenance, and proportionate evidence.
- A detailed generated procedure is not automatically an approved or authoritative procedure.
- Do not invent approval limits, KPI targets, retention periods, credentials, jurisdictional requirements, system names, manufacturer steps, or regulatory thresholds.

### Procedure — BQ-1252
<!-- id: control.bq-1252 -->

1. Resolve canonical industry/subindustry, business model, site/team context, exact role, task, trigger, systems/equipment, consequence class, and downstream handoff.
2. Classify each input as supplied fact, verified authority, organization-specific fact, inference, or unknown; record material unknowns explicitly.
3. Determine which unknowns block safe compilation versus which can remain placeholders without changing execution meaning.
4. Produce a context record that downstream role, authority, procedure, evidence, and KPI compilation can reference.
5. Re-run context resolution after changes to jurisdiction, facility/product/system scope, role authority, source version, or risk.

### Evidence Gate — BQ-1253
<!-- id: control.bq-1253 -->

- **PASS only if** the requirement is directly evidenced in the compiled role/procedure/metric record and another competent reader can identify the actor, trigger, decision boundary, evidence, and completion condition without guessing material facts.
- Authoritative claims require adequate source provenance and applicability evidence.
- If required source/currentness/organization authority evidence is unavailable, mark the affected portion **UNVERIFIED** or draft; do not silently pass it.

### Recovery — BQ-1254
<!-- id: control.bq-1254 -->

- Block authoritative or production-use claims for the affected portion.
- Downgrade authority classification when provenance is insufficient, surface unknowns, obtain/verify the missing source or organization fact where tools/evidence permit, and repair the smallest upstream ambiguity.
- Re-run affected decision-rights, evidence, KPI, risk, handoff, and change-control checks after repair.

### Regression — BQ-1255
<!-- id: control.bq-1255 -->

- Maintain **normal**, **ambiguous/edge**, and **failure/unavailable-evidence** fixtures.
- The ambiguous case must preserve unknown authority or applicability instead of inventing specificity.
- The failure case must trigger Recovery when a procedure is detailed but lacks evidence required for its claimed authority or completion state.
- Real operational failures should become regression fixtures when they expose a reusable process weakness.

## Role & Accountability Compilation
<!-- id: controls.capability.role-accountability-compilation -->

**Targets:** OPERATIONAL_PROCEDURE_COMPILER.md / JOBS.md  
**Requirement:** Compile purpose, accountabilities, scope boundaries, inputs, outputs, decisions, interfaces, evidence duties, KPI ownership, and explicit exclusions rather than relying on a title-only role description.

### Contract — BQ-1256
<!-- id: control.bq-1256 -->

- **MUST:** Compile purpose, accountabilities, scope boundaries, inputs, outputs, decisions, interfaces, evidence duties, KPI ownership, and explicit exclusions rather than relying on a title-only role description.
- Preserve truthful unknowns, applicable professional/licensing boundaries, organization authority, external-source provenance, and proportionate evidence.
- A detailed generated procedure is not automatically an approved or authoritative procedure.
- Do not invent approval limits, KPI targets, retention periods, credentials, jurisdictional requirements, system names, manufacturer steps, or regulatory thresholds.

### Procedure — BQ-1257
<!-- id: control.bq-1257 -->

1. Start from the exact role and task, then enumerate accountabilities, scope boundary, inputs, outputs, owned decisions, recommended decisions, interfaces, evidence duties, KPI ownership, and exclusions.
2. Distinguish responsibility from authority: do not infer licensure, system permission, spending/approval rights, credentials, or delegation from the title.
3. Map each consequential responsibility to either an owned decision, an approval dependency, a consult/inform interface, or an explicit exclusion.
4. Record unresolved authority/credential facts under authority_unknowns rather than filling them with defaults.
5. Check that the role specification supports the procedure steps and handoffs without orphan responsibilities or title-only ambiguity.

### Evidence Gate — BQ-1258
<!-- id: control.bq-1258 -->

- **PASS only if** the requirement is directly evidenced in the compiled role/procedure/metric record and another competent reader can identify the actor, trigger, decision boundary, evidence, and completion condition without guessing material facts.
- Authoritative claims require adequate source provenance and applicability evidence.
- If required source/currentness/organization authority evidence is unavailable, mark the affected portion **UNVERIFIED** or draft; do not silently pass it.

### Recovery — BQ-1259
<!-- id: control.bq-1259 -->

- Block authoritative or production-use claims for the affected portion.
- Downgrade authority classification when provenance is insufficient, surface unknowns, obtain/verify the missing source or organization fact where tools/evidence permit, and repair the smallest upstream ambiguity.
- Re-run affected decision-rights, evidence, KPI, risk, handoff, and change-control checks after repair.

### Regression — BQ-1260
<!-- id: control.bq-1260 -->

- Maintain **normal**, **ambiguous/edge**, and **failure/unavailable-evidence** fixtures.
- The ambiguous case must preserve unknown authority or applicability instead of inventing specificity.
- The failure case must trigger Recovery when a procedure is detailed but lacks evidence required for its claimed authority or completion state.
- Real operational failures should become regression fixtures when they expose a reusable process weakness.

## Procedure Authority Classification
<!-- id: controls.capability.procedure-authority-classification -->

**Targets:** PROCEDURE_AUTHORITY.md  
**Requirement:** Classify each material procedure as general guidance, organization draft, verified organization procedure, external authoritative requirement, or mixed, with truthful provenance and verification state.

### Contract — BQ-1261
<!-- id: control.bq-1261 -->

- **MUST:** Classify each material procedure as general guidance, organization draft, verified organization procedure, external authoritative requirement, or mixed, with truthful provenance and verification state.
- Preserve truthful unknowns, applicable professional/licensing boundaries, organization authority, external-source provenance, and proportionate evidence.
- A detailed generated procedure is not automatically an approved or authoritative procedure.
- Do not invent approval limits, KPI targets, retention periods, credentials, jurisdictional requirements, system names, manufacturer steps, or regulatory thresholds.

### Procedure — BQ-1262
<!-- id: control.bq-1262 -->

1. Classify the procedure and each material authority-bearing section as GENERAL_GUIDANCE, ORGANIZATION_DRAFT, VERIFIED_ORGANIZATION_PROCEDURE, EXTERNAL_AUTHORITATIVE_REQUIREMENT, or MIXED.
2. For every strong authority source, capture stable source ID, title, issuer/owner, scope, applicability basis, supplied/retrieved date, verification state, and version/effective/currentness evidence.
3. For MIXED procedures, build an authority_map covering every material step/section; strong entries must reference verified authority_source_ids.
4. Separate source requirement, organization control, and AIFENCE recommendation; do not let nearby verified content confer authority on draft guidance.
5. If applicability/currentness cannot be proven, downgrade the affected section to draft/general guidance or keep it UNVERIFIED and create a verification task.

### Evidence Gate — BQ-1263
<!-- id: control.bq-1263 -->

- **PASS only if** the requirement is directly evidenced in the compiled role/procedure/metric record and another competent reader can identify the actor, trigger, decision boundary, evidence, and completion condition without guessing material facts.
- Authoritative claims require adequate source provenance and applicability evidence.
- If required source/currentness/organization authority evidence is unavailable, mark the affected portion **UNVERIFIED** or draft; do not silently pass it.

### Recovery — BQ-1264
<!-- id: control.bq-1264 -->

- Block authoritative or production-use claims for the affected portion.
- Downgrade authority classification when provenance is insufficient, surface unknowns, obtain/verify the missing source or organization fact where tools/evidence permit, and repair the smallest upstream ambiguity.
- Re-run affected decision-rights, evidence, KPI, risk, handoff, and change-control checks after repair.

### Regression — BQ-1265
<!-- id: control.bq-1265 -->

- Maintain **normal**, **ambiguous/edge**, and **failure/unavailable-evidence** fixtures.
- The ambiguous case must preserve unknown authority or applicability instead of inventing specificity.
- The failure case must trigger Recovery when a procedure is detailed but lacks evidence required for its claimed authority or completion state.
- Real operational failures should become regression fixtures when they expose a reusable process weakness.

## Executable Procedure Compilation
<!-- id: controls.capability.executable-procedure-compilation -->

**Targets:** OPERATIONAL_PROCEDURE_COMPILER.md  
**Requirement:** Compile triggers, prerequisites, inputs, actor-specific ordered steps, decisions, checks, evidence, failure paths, outputs, and observable definition of done for material operating procedures.

### Contract — BQ-1266
<!-- id: control.bq-1266 -->

- **MUST:** Compile triggers, prerequisites, inputs, actor-specific ordered steps, decisions, checks, evidence, failure paths, outputs, and observable definition of done for material operating procedures.
- Preserve truthful unknowns, applicable professional/licensing boundaries, organization authority, external-source provenance, and proportionate evidence.
- A detailed generated procedure is not automatically an approved or authoritative procedure.
- Do not invent approval limits, KPI targets, retention periods, credentials, jurisdictional requirements, system names, manufacturer steps, or regulatory thresholds.

### Procedure — BQ-1267
<!-- id: control.bq-1267 -->

1. Define procedure purpose, scope/exclusions, trigger, entry conditions, required inputs, prerequisites, and responsible role before writing steps.
2. For each MATERIAL step specify actor, observable action, acceptance check, failure path, and evidence reference or explicit evidence-not-required reason.
3. Attach systems/methods, boundaries, authority references, decisions, and measurements only where they materially affect execution.
4. Walk the sequence from trigger to Definition of Done and verify every branch reaches a next state, recovery/escalation path, or explicit controlled stop.
5. Reject vague verbs such as review/ensure/handle/follow-policy when the available facts support a concrete action/check/evidence definition.

### Evidence Gate — BQ-1268
<!-- id: control.bq-1268 -->

- **PASS only if** the requirement is directly evidenced in the compiled role/procedure/metric record and another competent reader can identify the actor, trigger, decision boundary, evidence, and completion condition without guessing material facts.
- Authoritative claims require adequate source provenance and applicability evidence.
- If required source/currentness/organization authority evidence is unavailable, mark the affected portion **UNVERIFIED** or draft; do not silently pass it.

### Recovery — BQ-1269
<!-- id: control.bq-1269 -->

- Block authoritative or production-use claims for the affected portion.
- Downgrade authority classification when provenance is insufficient, surface unknowns, obtain/verify the missing source or organization fact where tools/evidence permit, and repair the smallest upstream ambiguity.
- Re-run affected decision-rights, evidence, KPI, risk, handoff, and change-control checks after repair.

### Regression — BQ-1270
<!-- id: control.bq-1270 -->

- Maintain **normal**, **ambiguous/edge**, and **failure/unavailable-evidence** fixtures.
- The ambiguous case must preserve unknown authority or applicability instead of inventing specificity.
- The failure case must trigger Recovery when a procedure is detailed but lacks evidence required for its claimed authority or completion state.
- Real operational failures should become regression fixtures when they expose a reusable process weakness.

## Decision Rights & Approval Boundaries
<!-- id: controls.capability.decision-rights-approval-boundaries -->

**Targets:** DECISION_RIGHTS.md  
**Requirement:** Make MUST, MAY, MUST NOT, approval-required, stop-and-escalate, consult, and inform boundaries explicit without inventing authority limits.

### Contract — BQ-1271
<!-- id: control.bq-1271 -->

- **MUST:** Make MUST, MAY, MUST NOT, approval-required, stop-and-escalate, consult, and inform boundaries explicit without inventing authority limits.
- Preserve truthful unknowns, applicable professional/licensing boundaries, organization authority, external-source provenance, and proportionate evidence.
- A detailed generated procedure is not automatically an approved or authoritative procedure.
- Do not invent approval limits, KPI targets, retention periods, credentials, jurisdictional requirements, system names, manufacturer steps, or regulatory thresholds.

### Procedure — BQ-1272
<!-- id: control.bq-1272 -->

1. Identify each consequential action or decision and assign MUST, MAY, MUST_NOT, APPROVAL_REQUIRED, STOP_AND_ESCALATE, CONSULT, or INFORM.
2. Name performer and decision owner; for APPROVAL_REQUIRED name the approval owner and record either a verified limit with provenance or ORGANIZATION_SPECIFIC_NOT_SUPPLIED.
3. For STOP_AND_ESCALATE define containment, notification targets, escalation path, required evidence, restart condition, and restart authority state.
4. Check segregation-of-duties needs for financial, security, privacy, safety, quality, and fraud-sensitive decisions without imposing unjustified separation.
5. Fail any decision-right record that converts an unknown permission or threshold into an invented authority value.

### Evidence Gate — BQ-1273
<!-- id: control.bq-1273 -->

- **PASS only if** the requirement is directly evidenced in the compiled role/procedure/metric record and another competent reader can identify the actor, trigger, decision boundary, evidence, and completion condition without guessing material facts.
- Authoritative claims require adequate source provenance and applicability evidence.
- If required source/currentness/organization authority evidence is unavailable, mark the affected portion **UNVERIFIED** or draft; do not silently pass it.

### Recovery — BQ-1274
<!-- id: control.bq-1274 -->

- Block authoritative or production-use claims for the affected portion.
- Downgrade authority classification when provenance is insufficient, surface unknowns, obtain/verify the missing source or organization fact where tools/evidence permit, and repair the smallest upstream ambiguity.
- Re-run affected decision-rights, evidence, KPI, risk, handoff, and change-control checks after repair.

### Regression — BQ-1275
<!-- id: control.bq-1275 -->

- Maintain **normal**, **ambiguous/edge**, and **failure/unavailable-evidence** fixtures.
- The ambiguous case must preserve unknown authority or applicability instead of inventing specificity.
- The failure case must trigger Recovery when a procedure is detailed but lacks evidence required for its claimed authority or completion state.
- Real operational failures should become regression fixtures when they expose a reusable process weakness.

## Decision Checkpoint & Stop Sequencing
<!-- id: controls.capability.decision-checkpoint-stop-sequencing -->

**Targets:** OPERATIONAL_PROCEDURE_COMPILER.md / DECISION_RIGHTS.md  
**Requirement:** Expose consequential decision criteria, quality/risk checkpoints, stop conditions, restart requirements, and the owner of each branch instead of hiding them in vague prose.

### Contract — BQ-1276
<!-- id: control.bq-1276 -->

- **MUST:** Expose consequential decision criteria, quality/risk checkpoints, stop conditions, restart requirements, and the owner of each branch instead of hiding them in vague prose.
- Preserve truthful unknowns, applicable professional/licensing boundaries, organization authority, external-source provenance, and proportionate evidence.
- A detailed generated procedure is not automatically an approved or authoritative procedure.
- Do not invent approval limits, KPI targets, retention periods, credentials, jurisdictional requirements, system names, manufacturer steps, or regulatory thresholds.

### Procedure — BQ-1277
<!-- id: control.bq-1277 -->

1. Extract consequential branch points from the step sequence and define signal/condition, decision owner, criteria, allowed choices, evidence, and resulting next state.
2. Insert quality/risk checkpoints before irreversible or high-consequence transitions rather than after the outcome is already committed.
3. For every stop condition, specify what is preserved/contained, who is notified, and the exact restart condition; identify restart authorizer when verified approval is required.
4. Trace each branch forward and ensure no path dead-ends in “as appropriate,” “if needed,” or an ownerless escalation.
5. Revalidate ordering after step, owner, authority, or system changes because a correct checkpoint in the wrong sequence is not a valid control.

### Evidence Gate — BQ-1278
<!-- id: control.bq-1278 -->

- **PASS only if** the requirement is directly evidenced in the compiled role/procedure/metric record and another competent reader can identify the actor, trigger, decision boundary, evidence, and completion condition without guessing material facts.
- Authoritative claims require adequate source provenance and applicability evidence.
- If required source/currentness/organization authority evidence is unavailable, mark the affected portion **UNVERIFIED** or draft; do not silently pass it.

### Recovery — BQ-1279
<!-- id: control.bq-1279 -->

- Block authoritative or production-use claims for the affected portion.
- Downgrade authority classification when provenance is insufficient, surface unknowns, obtain/verify the missing source or organization fact where tools/evidence permit, and repair the smallest upstream ambiguity.
- Re-run affected decision-rights, evidence, KPI, risk, handoff, and change-control checks after repair.

### Regression — BQ-1280
<!-- id: control.bq-1280 -->

- Maintain **normal**, **ambiguous/edge**, and **failure/unavailable-evidence** fixtures.
- The ambiguous case must preserve unknown authority or applicability instead of inventing specificity.
- The failure case must trigger Recovery when a procedure is detailed but lacks evidence required for its claimed authority or completion state.
- Real operational failures should become regression fixtures when they expose a reusable process weakness.

## Exception Recovery & Continuity
<!-- id: controls.capability.exception-recovery-continuity -->

**Targets:** OPERATIONAL_PROCEDURE_COMPILER.md / OPERATIONAL_EVIDENCE.md  
**Requirement:** Define exception detection, containment, escalation, recovery/rollback, deferred follow-up, and continuity paths for material failure states.

### Contract — BQ-1281
<!-- id: control.bq-1281 -->

- **MUST:** Define exception detection, containment, escalation, recovery/rollback, deferred follow-up, and continuity paths for material failure states.
- Preserve truthful unknowns, applicable professional/licensing boundaries, organization authority, external-source provenance, and proportionate evidence.
- A detailed generated procedure is not automatically an approved or authoritative procedure.
- Do not invent approval limits, KPI targets, retention periods, credentials, jurisdictional requirements, system names, manufacturer steps, or regulatory thresholds.

### Procedure — BQ-1282
<!-- id: control.bq-1282 -->

1. Enumerate material failure/exception states from inputs, decisions, systems, approvals, quality checks, evidence gaps, and downstream handoffs.
2. For each exception define detection signal, immediate containment, accountable owner, escalation path, recovery/rollback action, deferred follow-up if needed, and closure evidence.
3. Distinguish recoverable exceptions from conditions requiring STOP_AND_ESCALATE; do not continue execution merely to preserve throughput.
4. Ensure recovery returns the process to a defined safe/valid state or formally hands ownership to a named downstream owner.
5. After an incident or new failure mode, promote it into the regression set or document why an existing generalized fixture covers it.

### Evidence Gate — BQ-1283
<!-- id: control.bq-1283 -->

- **PASS only if** the requirement is directly evidenced in the compiled role/procedure/metric record and another competent reader can identify the actor, trigger, decision boundary, evidence, and completion condition without guessing material facts.
- Authoritative claims require adequate source provenance and applicability evidence.
- If required source/currentness/organization authority evidence is unavailable, mark the affected portion **UNVERIFIED** or draft; do not silently pass it.

### Recovery — BQ-1284
<!-- id: control.bq-1284 -->

- Block authoritative or production-use claims for the affected portion.
- Downgrade authority classification when provenance is insufficient, surface unknowns, obtain/verify the missing source or organization fact where tools/evidence permit, and repair the smallest upstream ambiguity.
- Re-run affected decision-rights, evidence, KPI, risk, handoff, and change-control checks after repair.

### Regression — BQ-1285
<!-- id: control.bq-1285 -->

- Maintain **normal**, **ambiguous/edge**, and **failure/unavailable-evidence** fixtures.
- The ambiguous case must preserve unknown authority or applicability instead of inventing specificity.
- The failure case must trigger Recovery when a procedure is detailed but lacks evidence required for its claimed authority or completion state.
- Real operational failures should become regression fixtures when they expose a reusable process weakness.

## Operational Evidence & Definition of Done
<!-- id: controls.capability.operational-evidence-definition-of-done -->

**Targets:** OPERATIONAL_EVIDENCE.md  
**Requirement:** Map material steps and decisions to proportionate evidence, records, handoff acceptance, and observable definition-of-done criteria.

### Contract — BQ-1286
<!-- id: control.bq-1286 -->

- **MUST:** Map material steps and decisions to proportionate evidence, records, handoff acceptance, and observable definition-of-done criteria.
- Preserve truthful unknowns, applicable professional/licensing boundaries, organization authority, external-source provenance, and proportionate evidence.
- A detailed generated procedure is not automatically an approved or authoritative procedure.
- Do not invent approval limits, KPI targets, retention periods, credentials, jurisdictional requirements, system names, manufacturer steps, or regulatory thresholds.

### Procedure — BQ-1287
<!-- id: control.bq-1287 -->

1. Identify material steps, decisions, exceptions, handoffs, and outcomes that require observable proof proportional to consequence and reconstruction cost.
2. Define each evidence record with stable evidence_id, linked step/decision, required content, responsible recorder, system/repository when known, reviewer/consumer when relevant, and retention provenance if a retention rule is stated.
3. Reference evidence IDs from steps, exceptions, handoffs, and each Definition-of-Done criterion; reject dangling or unreferenced critical evidence.
4. Compile Definition of Done as observable closure criteria including required actions/checks, approvals, records, exception disposition, downstream acceptance, and deferred follow-up ownership as applicable.
5. Confirm that a handoff is accepted by an explicit receiving owner and acceptance criteria; “sent” is not equivalent to transferred responsibility.

### Evidence Gate — BQ-1288
<!-- id: control.bq-1288 -->

- **PASS only if** the requirement is directly evidenced in the compiled role/procedure/metric record and another competent reader can identify the actor, trigger, decision boundary, evidence, and completion condition without guessing material facts.
- Authoritative claims require adequate source provenance and applicability evidence.
- If required source/currentness/organization authority evidence is unavailable, mark the affected portion **UNVERIFIED** or draft; do not silently pass it.

### Recovery — BQ-1289
<!-- id: control.bq-1289 -->

- Block authoritative or production-use claims for the affected portion.
- Downgrade authority classification when provenance is insufficient, surface unknowns, obtain/verify the missing source or organization fact where tools/evidence permit, and repair the smallest upstream ambiguity.
- Re-run affected decision-rights, evidence, KPI, risk, handoff, and change-control checks after repair.

### Regression — BQ-1290
<!-- id: control.bq-1290 -->

- Maintain **normal**, **ambiguous/edge**, and **failure/unavailable-evidence** fixtures.
- The ambiguous case must preserve unknown authority or applicability instead of inventing specificity.
- The failure case must trigger Recovery when a procedure is detailed but lacks evidence required for its claimed authority or completion state.
- Real operational failures should become regression fixtures when they expose a reusable process weakness.

## KPI Definition & Metric Governance
<!-- id: controls.capability.kpi-definition-metric-governance -->

**Targets:** KPI_GOVERNANCE.md  
**Requirement:** Define reproducible KPI formulas, scope, sources, ownership, cadence, target provenance, balancing measures, and response rules without inventing targets or thresholds.

### Contract — BQ-1291
<!-- id: control.bq-1291 -->

- **MUST:** Define reproducible KPI formulas, scope, sources, ownership, cadence, target provenance, balancing measures, and response rules without inventing targets or thresholds.
- Preserve truthful unknowns, applicable professional/licensing boundaries, organization authority, external-source provenance, and proportionate evidence.
- A detailed generated procedure is not automatically an approved or authoritative procedure.
- Do not invent approval limits, KPI targets, retention periods, credentials, jurisdictional requirements, system names, manufacturer steps, or regulatory thresholds.

### Procedure — BQ-1292
<!-- id: control.bq-1292 -->

1. Identify the operational decision each KPI supports before selecting the metric.
2. Define operational meaning, population/scope, formula/calculation rule, numerator/denominator when applicable, inclusions/exclusions, time window, source systems/events, metric/data owners, calculation frequency, and review cadence.
3. If material calculation facts remain unknown, set calculation_state to UNRESOLVED and list open_unknowns; do not label the KPI production-defined.
4. Resolve target_provenance independently from calculation definition. If no verified target exists, use ORGANIZATION_SPECIFIC_NOT_SUPPLIED rather than inventing a target/threshold.
5. Add audit/reconciliation evidence, balancing-measure consideration, data-quality risk, and gaming/perverse-incentive review; test whether another competent person can reproduce the metric without guessing.

### Evidence Gate — BQ-1293
<!-- id: control.bq-1293 -->

- **PASS only if** the requirement is directly evidenced in the compiled role/procedure/metric record and another competent reader can identify the actor, trigger, decision boundary, evidence, and completion condition without guessing material facts.
- Authoritative claims require adequate source provenance and applicability evidence.
- If required source/currentness/organization authority evidence is unavailable, mark the affected portion **UNVERIFIED** or draft; do not silently pass it.

### Recovery — BQ-1294
<!-- id: control.bq-1294 -->

- Block authoritative or production-use claims for the affected portion.
- Downgrade authority classification when provenance is insufficient, surface unknowns, obtain/verify the missing source or organization fact where tools/evidence permit, and repair the smallest upstream ambiguity.
- Re-run affected decision-rights, evidence, KPI, risk, handoff, and change-control checks after repair.

### Regression — BQ-1295
<!-- id: control.bq-1295 -->

- Maintain **normal**, **ambiguous/edge**, and **failure/unavailable-evidence** fixtures.
- The ambiguous case must preserve unknown authority or applicability instead of inventing specificity.
- The failure case must trigger Recovery when a procedure is detailed but lacks evidence required for its claimed authority or completion state.
- Real operational failures should become regression fixtures when they expose a reusable process weakness.

## Procedure Validation, Change & Reauthorization
<!-- id: controls.capability.procedure-validation-change-reauthorization -->

**Targets:** PROCEDURE_AUTHORITY.md / OPERATIONAL_PROCEDURE_COMPILER.md  
**Requirement:** Require validation, approval state, effective scope, change triggers, source-currentness review, supersession, and reauthorization for material procedure changes.

### Contract — BQ-1296
<!-- id: control.bq-1296 -->

- **MUST:** Require validation, approval state, effective scope, change triggers, source-currentness review, supersession, and reauthorization for material procedure changes.
- Preserve truthful unknowns, applicable professional/licensing boundaries, organization authority, external-source provenance, and proportionate evidence.
- A detailed generated procedure is not automatically an approved or authoritative procedure.
- Do not invent approval limits, KPI targets, retention periods, credentials, jurisdictional requirements, system names, manufacturer steps, or regulatory thresholds.

### Procedure — BQ-1297
<!-- id: control.bq-1297 -->

1. Set procedure_version, procedure_owner, approval_state, source versions/currentness, and validation plan explicitly; generated content remains DRAFT absent approval evidence.
2. Require approver plus approval_evidence for APPROVED/EFFECTIVE states and effective_date for EFFECTIVE; record supersession linkage for SUPERSEDED.
3. Define review/reauthorization triggers for material changes to law/policy/source version, jurisdiction/scope, systems/equipment, role authority, incidents, or control failures.
4. On change, identify affected steps/decisions/evidence/KPIs and revalidate them rather than treating version metadata as sufficient change control.
5. Prevent stale or conflicted authority from remaining silently effective: suspend/downgrade affected claims, preserve conflict evidence, and route to the responsible approval owner.

### Evidence Gate — BQ-1298
<!-- id: control.bq-1298 -->

- **PASS only if** the requirement is directly evidenced in the compiled role/procedure/metric record and another competent reader can identify the actor, trigger, decision boundary, evidence, and completion condition without guessing material facts.
- Authoritative claims require adequate source provenance and applicability evidence.
- If required source/currentness/organization authority evidence is unavailable, mark the affected portion **UNVERIFIED** or draft; do not silently pass it.

### Recovery — BQ-1299
<!-- id: control.bq-1299 -->

- Block authoritative or production-use claims for the affected portion.
- Downgrade authority classification when provenance is insufficient, surface unknowns, obtain/verify the missing source or organization fact where tools/evidence permit, and repair the smallest upstream ambiguity.
- Re-run affected decision-rights, evidence, KPI, risk, handoff, and change-control checks after repair.

### Regression — BQ-1300
<!-- id: control.bq-1300 -->

- Maintain **normal**, **ambiguous/edge**, and **failure/unavailable-evidence** fixtures.
- The ambiguous case must preserve unknown authority or applicability instead of inventing specificity.
- The failure case must trigger Recovery when a procedure is detailed but lacks evidence required for its claimed authority or completion state.
- Real operational failures should become regression fixtures when they expose a reusable process weakness.
