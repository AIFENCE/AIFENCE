<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: QA_GATES
Module-Version: 6
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Pack Quality Gates
<!-- id: qa-gates.root -->

Purpose: prevent semantic contamination, silent incompleteness, routing drift, false validation claims, generic visual output, shallow feature behavior, under-finished components, evaluator self-confirmation, and benchmark overfitting.

# Release Gate
<!-- id: qa-gates.release-gate -->

A release MUST NOT be described as validated unless all applicable checks pass.

1. Taxonomy/module/profile/operations address coverage remains internally consistent.
2. Stable IDs are unique.
3. No silent downgrade from production occurs.
4. No deprecated operations fallback becomes active.
5. Pack/schema metadata remain compatible.
6. Mixed-model and duplicate-subindustry resolution remain explicit.
7. Production public visual work routes to CREATIVE acceptance.
8. Render claims require rendered evidence.
9. Proof-bearing media authenticity remains enforced.
10. Substantial visual/product work routes to Domain 26 craft controls.
11. Substantial production artifacts resolve an artifact contract through Domain 27.
12. High-value features are compiled before detailed component design.
13. Important components consume compiled feature behavior rather than inventing it.
14. Structural fingerprints are generated for substantial concepts and high genericity risk triggers refinement.
15. Production visual/product artifacts run applicable adversarial critics after implementation/render.
16. Repair re-renders affected views/states when render tooling exists.
17. Artifact-specific quality floors cannot be averaged away by a strong aggregate score.
18. Truthfulness and implementation correctness meet their stricter floor.
19. The logical control registry is exactly BQ-0001–BQ-1300.
20. The logical control matrix has normal/ambiguous/failure coverage for all 260 capabilities.
21. Public benchmark development prompts remain separate from private holdout governance.
22. Blind benchmark scoring cannot access condition labels before score lock.
23. Behavioral pack changes add/strengthen regression evidence rather than only patching an artifact.
24. Validator and benchmark tooling referenced by the pack exist and parse.
25. Web artifacts containing JavaScript pass generation preflight: executable scripts parse, direct runtime load is clean, and missing runtime evidence fails closed before rendered acceptance.

# Generation Compiler Preflight
<!-- id: qa-gates.generation-compiler-preflight -->

For a substantial browser artifact that contains executable JavaScript or enabled scripted controls, **generation preflight is a blocking compilation gate before final render acceptance**.

PASS requires all of the following:

- executable inline and local JavaScript parses with a real JavaScript parser;
- no reserved-word/identifier syntax failure or malformed generated script remains;
- direct runtime evidence confirms document load and JavaScript initialization;
- zero uncaught page errors;
- zero artifact-attributable error-level console failures;
- zero failed required local script/resource loads;
- runtime evidence provenance is `direct`, not inferred;
- interactive JavaScript does not omit runtime-preflight evidence.

A static screenshot, successful HTML parse, source inspection, or first-frame render cannot substitute for this gate. Generation preflight executes **before** exhaustive interaction closure; both gates must pass. On failure, the artifact remains BLOCKED and must be regenerated/corrected before acceptance.

Executable validator: `python tools/validate_generation_preflight.py <artifact.html> --runtime-evidence <evidence.json>`.

# Creation Quality Smoke Tests
<!-- id: qa-gates.creation-quality-smoke-tests -->

Representative tests include ambiguous local-service classification; production visual routing; generic template rejection; truth-safe proof; component craftsmanship; feature depth; dense dashboard operation; mobile recomposition; artifact-contract resolution; feature-compiler self-defining-noun rejection; component-compiler anatomy rejection; structural-fingerprint rejection; independent critic recovery; failed required dimension blocking a high aggregate score; no-render UNVERIFIED behavior; and blind score locking before unblinding.


Revision 1.7.3 adds a permanent parser/runtime-preflight regression for generated JavaScript (including reserved-keyword DOM-global hazards). Revision 1.7.1 adds permanent regressions for three real rendered failure classes: a payments dashboard may not hide transaction detail/recovery on 320/390; a SaaS list/detail editor may not remove the editable detail pane on 320/390; and analytics/navigation/period/overflow controls may not remain visibly enabled without observable behavior.

# Semantic Review Test
<!-- id: qa-gates.semantic-review-test -->

Independently resolve business model, product pattern, visual domain, proof model, artifact contract, primary user jobs, and risk triggers. Copying one answer across dimensions without justification requires review.

# Claim Standard
<!-- id: qa-gates.claim-standard -->

Do not claim objective perfection. Use evidence-backed release language. Numerical scores require evidence; otherwise use PASS/FAIL/UNVERIFIED.

# Compiled Artifact Gate
<!-- id: qa-gates.compiled-artifact-gate -->

Before substantial implementation:

- artifact contract resolved;
- high-value features compiled;
- substantial concept has a structural fingerprint;
- important components compile from feature behavior;
- unresolved compilation failures block implementation-fidelity PASS.

# Adversarial Acceptance Gate
<!-- id: qa-gates.adversarial-acceptance-gate -->

Before substantial production completion:

- applicable critics have run;
- no P0/P1 issue remains unresolved;
- repaired views/states are revalidated;
- required quality floors pass;
- render-dependent evidence is UNVERIFIED when rendering is unavailable;
- critical failures cannot be offset by aggregate scoring.

# Control Plane Release Gate
<!-- id: qa-gates.control-plane-release-gate -->

Every mandatory active capability must be PASS, FAIL, or UNVERIFIED; no release-blocking FAIL may remain; no UNVERIFIED requirement may be described as passed.

For BizIQ releases, `python tools/validate_pack.py` MUST pass. Behaviorally meaningful changes additionally require applicable curated end-to-end and benchmark protocol review.

# Control Plane Hooks
<!-- id: qa-gates.control-plane-hooks -->

Frequently applicable ranges:

- BQ-0031–0035 silent-downgrade prevention
- BQ-0191–0200 deliverable shortcuts/acceptance
- BQ-0246–0275 concept exploration/genericity
- BQ-0346–0355 repetition/viewport review
- BQ-0436–0440 asset rejection
- BQ-0451–0515 states/responsive/dense UI
- BQ-0521–0560 accessibility
- BQ-0596–0600 content realism
- BQ-0646–0680 component implementation fidelity
- BQ-0841–0880 evidence/render/regression
- BQ-0986–1000 prompt regression/postmortem/pruning
- BQ-1001–1050 Feature & Component Craft
- BQ-1051–1100 Artifact Contracts & Specification Compilation
- BQ-1101–1150 Adversarial Critique, Repair, Quality Floors & Benchmarking
- BQ-1151–1200 Benchmark-Driven Quality Hardening
- BQ-1201–1250 Usability, Visual Finish, Truth & Quality Closure
- BQ-1251–1300 Operational Procedure Compilation, Authority & Measurement

# Revision 1.3 Hardening Gate
<!-- id: qa-gates.revision-1-3-hardening -->
For applicable P0/P1 work: 320/390/768 responsive evidence passes; document decision-depth evidence passes; accessibility critical-path evidence passes; completion ledger closes; feature-depth evidence closes; and post-repair genericity resistance is revalidated.

For substantial interactive artifacts, additionally require:

- a schema-valid interaction-closure manifest produced before final acceptance;
- 100% accounting of enabled visible controls and **zero unaccounted dead controls**;
- direct control behavior evidence rather than source-only event-handler inference when browser/runtime execution exists;
- every declared P0/P1 task directly PASSing at both 320 and 390 px;
- task-critical desktop detail/edit/recovery/drill-down surfaces mapped to and exercised through an equivalent narrow-screen composition;
- failed interaction/mobile-task evidence to block implementation-correctness, usability, and responsiveness PASS until repaired and re-executed.

# Revision 1.4 Quality Closure Gate
<!-- id: qa-gates.revision-1-4-quality-closure -->
Before production release, where applicable verify:

- P0/P1 task-friction traces pass orientation/action/state/feedback/recovery checks;
- important rendered views pass final visual-finish critique after material implementation stabilizes;
- documents and proof-bearing interfaces expose material truth/provenance boundaries at point of use;
- responsive documents/operations pass task-level detail evidence at required viewports;
- active numerical scorers are capable of measuring the floors they are used to enforce;
- genericity resistance and prior Revision 1.3 hardening gates remain passing after repair.

# Benchmark Render-State Integrity Gate
<!-- id: qa-gates.benchmark-render-state-integrity -->
When BizIQ efficacy evidence uses browser screenshots, verify that each capture starts from the declared viewport and normalized scroll/focus/overlay state. Random prior-artifact browser state is a benchmark-integrity failure and requires symmetric rerendering before visual conclusions are accepted.

# Revision 1.5 Operations 2.0 Gate
<!-- id: qa-gates.operations-2 -->

For substantial operational procedures, PASS requires:

- exact role/task/trigger/context resolution;
- explicit procedure authority class and truthful provenance;
- executable P0/P1 steps with actor/action/check/evidence/failure path where material;
- consequential decision rights and approval boundaries without invented limits;
- exception, stop/escalate, recovery/restart, and handoff closure where applicable;
- observable definition of done and proportionate evidence;
- reproducible KPI definitions with target provenance when metrics are material;
- currentness/reauthorization checks for authoritative or changed procedures;
- no claim that a baseline `operations/*.md` SOP is organization-approved merely because it exists in BizIQ.

High-consequence external requirements remain `UNVERIFIED` if the authoritative source/applicability cannot be confirmed.

# Revision 1.6 Operations Integrity Gate
<!-- id: qa-gates.revision-1-6-operations-integrity -->

For changes to Domain 23/31 operational semantics, procedure schemas, authority, decision rights, evidence, KPI governance, or lifecycle behavior, release requires all of the following:

- `MANIFEST.md`, `CONTROL_MANIFEST.md`, and `CONTROL_INDEX.md` agree on current addressing and precedence.
- Domain 23 baseline coverage and Domain 31 specialization do not emit duplicate competing operational objects.
- `schemas/operational_procedure.schema.json` composes the authority, role-accountability, decision-rights, evidence, and KPI schemas.
- strong authority classes fail without verified provenance/currentness evidence; `MIXED` fails without material-step authority mapping.
- APPROVED/EFFECTIVE lifecycle claims fail without approval evidence; EFFECTIVE fails without effective date.
- APPROVAL_REQUIRED and STOP_AND_ESCALATE records satisfy their conditional machine fields.
- `DEFINED` KPIs are reproducible; unresolved KPIs expose `open_unknowns`; target values require verified provenance/source.
- `python tools/test_operations_2.py` passes all 30 Domain 31 executable fixtures.
- `python tools/validate_pack.py` passes the complete repository.

# Revision 1.7.2 Differentiation & Decision-Depth Gate
<!-- id: qa-gates.revision-1-7-2-differentiation-depth -->

For high-fidelity SaaS/dashboard/portal artifacts, validate `genericity_evidence.schema.json` and reject genericity PASS when dense-product structural evidence fails. For complex-consideration B2B marketing artifacts, validate `decision_depth_evidence.schema.json` and reject feature-depth PASS when buyer decision paths are absent or shallow. These gates are benchmark-derived and non-averagable.
# Revision 1.7.4 Dense-Product First-Pass Quality Gate
<!-- id: qa-gates.revision-1-7-4-dense-product-first-pass -->

For high-fidelity SaaS/dashboard/portal artifacts, final acceptance requires a schema-valid `dense_product_quality_evidence` record with four independent PASS sections: visual finish, completeness, accessibility, and feature depth. Direct rendered evidence must include desktop and 390/320 critical views. Applicable P0/P1 completion rows must be exhaustive. Accessibility must include critical-path keyboard/focus/feedback/reflow evidence. Payments/analytics must satisfy their workflow-specific Level-5 loops. Any failed or missing section is release-blocking and cannot be averaged away. Revision 1.7.3 generation preflight must PASS first.

# Revision 1.8.3 Emission Naturalization & Universal Executable Preflight Gate
<!-- id: qa-gates.revision-1-8-3-emission-preflight -->

Before artifact freeze or delivery, applicable high-fidelity work requires direct finished-surface emission evidence. Run `validate_emission_preflight.py` against the emitted artifact plus concrete substance evidence; any forbidden internal BizIQ/compiler/QA label, missing declared domain/decision/action/state/outcome/evidence marker, or generic scaffold substitution blocks acceptance. For every generated executable artifact, run `validate_universal_executable_preflight.py`; syntax/grammar failure is catastrophic, and interface/CLI work requiring execution must provide direct schema-valid runtime evidence. Planning or materialization records cannot average away a failed post-emission gate.

# Revision 1.8.2 Domain Materialization & Naturalization Gate
<!-- id: qa-gates.revision-1-8-2-materialization -->

Before accepting a substantial high-fidelity artifact in an applicable family, require direct `materialization_evidence` PASS. Reject artifacts that merely expose the compiler/evidence scaffold, use generic placeholder material, lack domain-specific P0/P1 content/states/actions, or leak internal BizIQ/QA terminology onto production-facing surfaces. The gate is non-averagable with aggregate quality scores.

# Revision 1.8.1 Family-Depth & Composite Containment Gate
<!-- id: qa-gates.revision-1-8-1-family-depth -->

For applicable substantial high-fidelity work, final acceptance requires a schema-valid `family_depth_evidence` record in addition to existing family/preflight evidence. Public websites require primary + secondary decision paths; mobile requires P0 + P1 workflow continuity through interruption/error recovery; brand requires a complete visual-language system with multiple applications; email requires sequence/lifecycle state depth; CLI requires discoverable commands, deterministic I/O/exit/recovery semantics, and safety boundaries; responsive composite children require direct 320/390 containment with zero overflow/clipping and preserved critical paths. Missing direct evidence is UNVERIFIED and cannot be averaged away.

