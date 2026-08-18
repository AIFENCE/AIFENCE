<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: README
Module-Version: 12
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->

# Pack Main Load Point
<!-- id: readme.pack-main-load-point -->

This file is the **only document that should be loaded by default**.

Use it as the authoritative BizIQ orchestration, precedence, lazy-loading, production-intent, and routing specification. Do **not** preload the repository.

# Initialization Protocol
<!-- id: readme.initialization-protocol -->

When BizIQ is first attached, uploaded, mounted, or opened:

1. Read `README.md` first.
2. If `PROJECT.md` exists, read it immediately after this file; otherwise use the user's current request as the project specification.
3. Resolve creation type and delivery mode; default delivery mode to Production.
4. Resolve canonical industry only when needed.
5. Resolve Operating, Product, Design, Halo, and Risk dimensions independently through `PROFILE_MATRIX.md`.
6. Use `MANIFEST.md` for industry/operations addresses, `CONTROL_MANIFEST.md` for control-plane address metadata, and `CONTROL_INDEX.md` for active control routing.
7. Resolve active modules and control capabilities before retrieving detailed standards.
8. Load only the smallest relevant sections.
9. Validate substantial work before delivery.

BizIQ remains active for the current project until the user explicitly replaces, disables, or changes it.

# Stable 2.0 Qualification Status

**Core 1.8.8 is APPROVED and frozen as the BizIQ Stable 2.0 architecture.** Sealed Holdout 9 passed all 10/10 predeclared engineering gates: 40/40 exact routing, 40/40 pairwise wins versus control, 92.910/100 mean quality, 40/40 family acceptance, 100% preflight/compact containment, zero catastrophic failures, a positive paired-improvement confidence interval, and +1.85% eager-context regression within budget. See `ARCHITECTURE_FREEZE_STATUS.md` and `BENCHMARK_FINDINGS_1_8_8.md`. Holdout 9 and all prior holdouts are now regression data only.

# Revision 1.8.8 Deliverable Phrase Normalization & Modifier-Tolerant Composite Parsing
<!-- id: readme.revision-1-8-8 -->

Revision 1.8.8 preserves the passing Core 1.8.7 architecture and changes only two routing mechanics: bounded finished-report/memo phrases such as `print-ready assessment report` resolve as Fixed-Format Document / PDF, and explicit multi-artifact lists preserve every child when harmless modifiers such as `public`, `internal`, `responsive`, or `customer-facing` appear before an artifact noun. A 40-case adversarial routing corpus locks both positive and false-composite behavior. The control plane remains 31 domains / 260 capabilities / 1,300 controls.

# Revision 1.8.7 Artifact-Graph Phrase Coverage & Slide Fit Preflight
<!-- id: readme.revision-1-8-7 -->

Revision 1.8.7 preserves the passing Core 1.8.6 architecture and closes the remaining Holdout-7 failure classes: qualified `Excel ... model` phrases resolve as Spreadsheet / Financial Model, explicit three-or-more deliverable lists preserve every child artifact, and substantial presentations require direct slide-by-slide title/region fit evidence before freeze. The control plane remains 31 domains / 260 capabilities / 1,300 controls.

# Revision 1.8.6 Render-Aware Documents & Semantic Acceptance Closure

Revision 1.8.6 preserves Core 1.8.5 routing/retrieval, family-native emission, naturalization, executable preflight, fixed-document depth, composite continuity, and compact containment while closing the repeated Holdout-6 failures:

- semantic-equivalence materialization accepts natural phrasing only when conservative token/synonym coverage proves the requested domain concept;
- fixed-format documents require direct rendered-page checks plus PDF text-geometry, reading-order/table-order, and accessibility evidence before freeze;
- service-renewal monitoring workspaces resolve as Dashboard when their dominant job is monitoring/review rather than record mutation;
- fixed analytical report + executive deck requests compile as composite Fixed-Format Document / PDF + Presentation / Deck.

Stable 2.0 remains unclaimed until a new sealed holdout passes the predetermined release gates.

# Revision 1.8.5 Fixed-Document Depth, Composite Continuity & Compact Containment
<!-- id: readme.revision-1-8-5 -->

Revision 1.8.5 targets only the repeated Stable-2.0 Holdout-5 failures while preserving Core 1.8.4 family-aware emission, XLSX extraction, naturalization, universal executable preflight, routing/retrieval architecture, and the 31-domain / 260-capability / 1,300-control plane:

- fixed-format documents must materialize at least three distinct findings/conclusions, three implications/actions, four evidence points, two provenance markers, and reader-facing takeaways rather than topic coverage alone;
- composite projects must prove shared assumptions/identifiers, project-level provenance boundaries, cross-artifact handoffs, and child acceptance continuity on emitted surfaces;
- responsive composite children compile compact-width safety before freeze and must directly pass 320/390 containment with zero overflow/clipping;
- decision-monitoring workspaces such as contract-renewal/risk/portfolio review workspaces resolve as Dashboard when the request emphasizes monitoring, status, deadlines, evidence, or review rather than record editing/workflow construction.

# Revision 1.8.4 Family-Aware Emission Adapters & Composite Routing Closure
<!-- id: readme.revision-1-8-4-family-emission -->

Revision 1.8.4 targets only the Stable-2.0 Holdout-4 validator/routing defects while preserving Core 1.8.3 finished-surface naturalization and universal executable preflight:

1. **Emission substance is family-native.** Websites/apps, dashboards, mobile, brand systems, campaigns, CLI tools, decks, spreadsheets, fixed documents, creative work, and composites validate the semantics native to that artifact family rather than a universal workflow state machine.
2. **Naturalization remains global and fail-closed.** Production-facing internal BizIQ/compiler/QA vocabulary remains forbidden regardless of family.
3. **XLSX extraction is namespace-safe.** Shared strings, inline strings, string-valued worksheet cells, formulas/labels, and supported OOXML namespace representations are directly recoverable from generated workbooks.
4. **Scaffold detection is context-sensitive.** Generic placeholders remain invalid, but ordinary phrases are not globally rejected when they are legitimate within a family and surrounded by concrete family-specific material.
5. **Deck + model composites resolve exactly.** Executive/decision deck language coordinated with spreadsheet/model deliverables compiles both child artifacts instead of allowing the model keyword to dominate.
6. Use `EMISSION_PREFLIGHT.md`, `schemas/family_emission_evidence.schema.json`, `tools/validate_family_emission_evidence.py`, and the unchanged `tools/validate_universal_executable_preflight.py`. These gates add no BQ IDs.

# Revision 1.8.3 Emission Naturalization & Universal Executable Preflight Contract
<!-- id: readme.revision-1-8-3-emission-preflight -->

Revision 1.8.3 targets only the repeated Stable-2.0 Holdout-3 failure classes and preserves Core 1.8 semantic routing/retrieval plus the 1.8.1/1.8.2 family/materialization contracts:

1. **Naturalization is verified on the finished artifact.** User-facing surfaces are scanned after generation and before freeze; internal priority, closure, compiler, QA, evidence, and truth-boundary labels are release-blocking unless the user explicitly requested process documentation.
2. **Materialization must exist in emitted substance.** Direct evidence declares concrete domain terms, decisions, actions, states, outcomes, evidence boundaries, and surface markers; the validator proves those markers occur on the emitted artifact rather than only in a planning record.
3. **Executable preflight is universal.** Browser scripts, CLI/Node entrypoints, Python, shell, and other supported generated executable text must parse against their language grammar. Runtime-required interface/tool artifacts also require direct execution evidence.
4. **Missing post-emission evidence fails closed.** Planning-time compliance cannot substitute for finished-surface or executable evidence.
5. Use `EMISSION_PREFLIGHT.md`, `schemas/emission_substance_evidence.schema.json`, `schemas/universal_executable_runtime_evidence.schema.json`, `tools/validate_emission_preflight.py`, and `tools/validate_universal_executable_preflight.py`. These gates add no BQ IDs.

# Revision 1.8.2 Domain Materialization & Naturalization Contract
<!-- id: readme.revision-1-8-2-materialization -->

Revision 1.8.2 targets only the repeated Stable-2.0 Holdout-2 failure cluster: artifacts that satisfy the shape of a quality contract while remaining generic, shallow, or visibly written in internal compiler/QA language.

1. **Internal requirements compile into user-domain material.** P0/P1 jobs must materialize into concrete content, data, states, actions, proof needs, recovery, and outcomes that are specific to the artifact's domain.
2. **Production-facing language is naturalized.** Internal terms such as `P0`, `decision depth closure`, `truth boundary`, `feature depth`, `quality gate`, `artifact contract`, `evidence plan`, and equivalent BizIQ/QA vocabulary are implementation metadata and MUST NOT appear in user-facing output unless the user explicitly requests process documentation.
3. **Specificity is testable.** Required material must include industry/workflow-specific markers that could not be transplanted unchanged into a materially different domain without becoming inaccurate or nonsensical.
4. **Brand/email/non-web/CLI materialize real rules and decisions.** Brand category inventories become operational rules/applications; campaign stages become domain-specific lifecycle content; decks/models/documents become concrete reading/decision surfaces; CLI requirements become ergonomic task vocabulary, output, errors, and recovery.
5. Use `MATERIALIZATION_CLOSURE.md`, `schemas/materialization_evidence.schema.json`, and `tools/validate_materialization_evidence.py`. These gates are fail-closed and add no BQ IDs.
6. Stable 2.0 remains pending a newly sealed Holdout 3. Holdout 2 is now known validation data and may not be used as the final generalization proof for this revision.

# Revision 1.8 Generalization, Retrieval-Budget & Artifact-Family Contract
<!-- id: readme.revision-1-8-generalization -->

Revision 1.8 converts the 36-case private generalization holdout and 480-case adversarial router study into reusable system rules rather than case-specific patches:

1. **Semantic routing is clause-aware and deliverable-aware.** Artifact classification favors the earliest explicit deliverable unless the request explicitly coordinates multiple outputs; incidental words such as “dashboard metric,” “website URL,” or disabled checkout cannot override the requested artifact. Coordinated negation such as “no login or payments” applies to every exposure inside the negated span but stops at contrast boundaries.
2. **Industry inference uses business-subject evidence, not artifact/evaluation vocabulary.** Negated capabilities, artifact nouns, and phrases such as insurance participation, architecture fit, education audience, recovery state, or subscription assumptions do not manufacture industry resolution. Candidate/ambiguous industry matches do not activate resolved-profile risk overlays.
3. **Retrieval is phase-budgeted.** Each phase eagerly loads only its highest-priority stable sections. Additional applicable capabilities remain explicit in `deferredCapabilities` and are retrieved on demand when evidence, critics, unresolved risk, or repair dependencies trigger them. Whole-module loading remains compatibility/debug behavior, not the primary execution interface.
4. **Non-web/mobile first-pass quality is executable.** Native/mobile apps, presentations, spreadsheets/models, fixed-format documents, brand identity, email/creative, and CLI output use `NONWEB_FIRST_PASS.md`, `schemas/artifact_family_quality_evidence.schema.json`, and `tools/validate_artifact_family_quality_evidence.py` before acceptance.
5. **Release thresholds are family-aware without weakening benchmark comparability.** The universal nine-dimension rubric and strict all-9.0 score remain reported; release acceptance additionally requires >=90 overall, >=9.0 on family-critical dimensions, >=8.5 on non-critical applicable dimensions, and zero catastrophic truth/implementation/accessibility/file-integrity failures.
6. **Generalization evidence is holdout-driven.** Repeated failure classes may change Core behavior; isolated low-scoring holdout artifacts do not justify one-off prompt tuning. The 36-case routing holdout and corrected 480-case adversarial corpus are permanent regressions.

# Revision 1.8.1 Family-Depth & Composite Containment Contract
<!-- id: readme.revision-1-8-1-family-depth -->

Revision 1.8.1 targets only the repeated Holdout-1 failure clusters and preserves the Core 1.8 semantic router, retrieval budgets, dense-product closure, and non-web contracts:

1. **Public websites compile decision paths, not section lists.** Substantial high-fidelity public web work must prove primary and secondary visitor decisions with evidence, uncertainty/objection handling, next action, continuation, truth boundaries, and narrow-screen equivalents.
2. **Mobile apps compile P0 + P1 workflow continuity.** Entry, action, state/feedback, interruption/error, recovery, continuation, and compact/adaptive surfaces are mandatory first-pass depth evidence.
3. **Brand output compiles a usable visual-language system.** Mark, typography, color, composition, iconography, imagery, usage boundaries, and multiple applications are required; proof-bearing sample content remains provenance-bound.
4. **Email/campaign output compiles lifecycle progression.** Audience state, sequence job, proof boundary, CTA, measurement event, fallback/recovery, and next state are explicit across the sequence rather than inferred from isolated messages.
5. **CLI output compiles a coherent product surface.** Discoverability/help, primary job commands or modes, configuration precedence, deterministic stdout/stderr/exit semantics, recovery, fixtures/tests, and consequential-operation safety are first-pass requirements.
6. **Responsive composites fail per child.** Any web/mobile child must directly pass 320/390 containment with no horizontal overflow, clipping, or lost P0/P1 path. A passing sibling cannot average away a failing child.
7. Use `FAMILY_DEPTH_CLOSURE.md`, `schemas/family_depth_evidence.schema.json`, and `tools/validate_family_depth_evidence.py`. These gates are fail-closed and do not add BQ IDs.

# Revision 1.7 Semantic & Retrieval Contract
<!-- id: readme.revision-1-7-semantic-retrieval -->

# Revision 1.7.4 Dense-Product First-Pass Quality Contract
<!-- id: readme.revision-1-7-4-dense-product-first-pass -->

Revision 1.7.4 closes the remaining fresh-generation dense-product floor misses without adding BQ IDs. For high-fidelity SaaS/dashboard/portal artifacts:

1. **Visual finish is generation-time, not post-hoc.** Before acceptance, render representative desktop and 390/320 critical views and prove an intentional visual hierarchy, calibrated density/rhythm, differentiated surface grammar, aligned control geometry, stable typography, and finished state surfaces. A visually competent but generic/unrefined first pass is NON-PASS.
2. **Completeness is coverage-complete.** Every P0/P1 feature must map to entry/orientation, information/evidence, primary/contextual action, normal state, material empty/loading/error/recovery states, responsive transformation, accessibility evidence, data/truth semantics, and acceptance evidence. Missing applicable rows are release-blocking.
3. **Accessibility is direct and critical-path complete.** Every P0/P1 workflow must prove named controls, keyboard completion where supported, visible focus, logical focus return/order, programmatic feedback for dynamic state, non-color meaning, target/readability adequacy, and 320/390 reflow. Missing direct evidence is UNVERIFIED.
4. **Payments/analytics depth is workflow-specific.** Payments must expose transaction investigation, status/risk context, filtering/segmentation, detail, action/recovery, result feedback, and continuity. Analytics must expose question/decision framing, evidence/source context, comparison/segmentation, interpretation guardrails, drill-down/inspection, next action, and responsive continuity. Metric cards or transaction tables alone cannot satisfy Level-5 depth.
5. Use `schemas/dense_product_quality_evidence.schema.json` and `tools/validate_dense_product_quality_evidence.py`. The gate is fail-closed and non-averagable: any failed required dimension blocks release acceptance even if aggregate benchmark score is high.
6. Revision 1.7.3 generation preflight, Revision 1.7.2 differentiation, and Revision 1.7.1 interaction/mobile closure remain prerequisites.

# Revision 1.7.3 Generation Compiler & Runtime Preflight Contract
<!-- id: readme.revision-1-7-3-generation-preflight -->

Revision 1.7.3 closes the fresh-generation JavaScript parser/dead-runtime failure class without adding BQ IDs. For substantial web artifacts containing JavaScript or enabled scripted controls:

1. **Before rendered acceptance**, extract all executable inline/local JavaScript and run a real syntax parser (`node --check` or an approved equivalent). A syntax error is release-blocking.
2. Syntax PASS is necessary but insufficient. Direct runtime-preflight evidence MUST confirm document load, zero uncaught page errors, zero error-level console failures attributable to the artifact, and zero failed required local resources.
3. Runtime-preflight evidence is fail-closed: interactive JavaScript with missing or inferred-only runtime evidence cannot PASS.
4. Reserved-keyword/identifier hazards such as `export.onclick = ...` are permanent regression fixtures. Generators SHOULD prefer explicit DOM bindings (`const exportButton = document.getElementById('export')`) over relying on element IDs as implicit globals.
5. Generation preflight runs **before** task-level interaction closure. Passing interaction/responsive evidence cannot average away parser/runtime-load failure, and a visually rendered first frame cannot be treated as proof that JavaScript executed.
6. Use `tools/validate_generation_preflight.py` and `schemas/generation_preflight_evidence.schema.json`. Any failure triggers regeneration/correction before the artifact may enter final render scoring or release acceptance.

# Revision 1.7.2 Differentiation & Decision-Depth Contract
<!-- id: readme.revision-1-7-2-differentiation-depth -->

Revision 1.7.2 closes the remaining strict-floor misses from the Core 1.7.1 rendered benchmark without adding BQ IDs.

1. High-fidelity SaaS, dashboard, portal, and dense product UI work MUST activate the creative/differentiation controls declared by the High-Leverage Mandatory Capability Set; Front-End Product routing may not filter them out.
2. Dense product genericity PASS requires task-derived structural differentiation, not palette/radius/icon changes. Use `GENERICITY.md`, `schemas/genericity_evidence.schema.json`, and `tools/validate_genericity_evidence.py`.
3. SaaS/dashboard structure must survive a competitor-swap test, use multiple information/component grammars appropriate to different jobs, and remain below the common-template similarity rejection threshold or explicitly recover before acceptance.
4. Complex-consideration B2B marketing work MUST compile decision-depth paths that connect buyer decision → evidence/proof → objection/risk → action → downstream state. Use `FEATURE_DEPTH.md`, `schemas/decision_depth_evidence.schema.json`, and `tools/validate_decision_depth_evidence.py`.
5. A strong aggregate score cannot average away failure of either closure gate. Benchmark-derived SaaS/analytics genericity and B2B depth misses remain permanent regressions.

# Revision 1.7.1 Interaction Closure Contract
<!-- id: readme.revision-1-7-1-interaction-closure -->

Revision 1.7.1 hardens the real-artifact failures observed after Revision 1.7 without increasing the 1,300-control plane. For every substantial interactive artifact:

1. Compile a pre-implementation interaction-closure manifest covering every enabled visible control and every P0/P1 task.
2. An enabled rendered control is release-valid only when its intended behavior is directly observable in its supported state/viewports. A control that is not implemented MUST be removed or explicitly disabled with a user-visible reason; inert enabled controls are prohibited.
3. Every declared P0/P1 task that exists on desktop MUST remain reachable and completable at 320 and 390 px. Task-critical inspect/edit/recovery/detail surfaces may transform into routes, drawers, sheets, disclosures, or equivalent narrow-screen compositions, but MUST NOT disappear.
4. Responsive PASS requires task-level evidence, not merely no-overflow screenshots. Interaction PASS requires zero unaccounted dead controls, not merely absence of runtime errors.
5. Any failure blocks the affected responsiveness/usability/implementation-correctness floor, triggers repair, and requires re-execution of the failed interaction/task evidence before release.

Use `EVIDENCE_ADAPTER.md`, `schemas/interaction_closure_manifest.schema.json`, and `tools/validate_execution_evidence.py --interaction-manifest ...` for executable closure.

1. Compile the request into `SEMANTIC_ROUTING.md` context/exposure/artifact graphs before risk-sensitive retrieval.
2. Negated capabilities remain absent unless independently reactivated. Candidate industry matches do not inherit risk overlays.
3. Composite requests compile per-artifact contract chains.
4. Runtime uses `activeCapabilities` and phase-scoped stable-section retrieval from `RETRIEVAL_INTELLIGENCE.md`; `activeModules` is compatibility/debug metadata only.
5. Executable acceptance evidence follows `EVIDENCE_ADAPTER.md`.
6. Benchmark/control-system changes follow `BENCHMARK_PIPELINE.md`; release provenance follows `RELEASE_PROVENANCE.md`.

# Control Plane Resolution
<!-- id: readme.control-plane-resolution -->

BizIQ uses a lazily loaded normative control plane.

The current logical control plane contains:

```text
31 domains
260 capabilities
1,300 controls
BQ-0001 through BQ-1300
```

After initialization and creation-type classification:

1. Read `CONTROL_INDEX.md` only far enough to resolve the active bundle or exact capability.
2. Retrieve the exact capability section(s) from `controls/*.md`; **do not preload all 31 shards**.
3. Apply each active capability as **Contract → Procedure → Evidence Gate → Recovery → Regression**.
4. Record dependent decisions/evidence internally when later work relies on them.
5. Re-evaluate affected controls after material scope, audience, industry, feature, risk, delivery-mode, design, or evidence changes.

Completion semantics:

- `PASS` — Evidence Gate has observable support.
- `FAIL` — evidence shows the requirement is unmet; Recovery is required.
- `UNVERIFIED` — required evidence is unavailable; do not claim a pass.

For substantial production artifacts, use the `High-Leverage Mandatory Capability Set` in `CONTROL_INDEX.md`. Production visual/product work additionally activates applicable Domain 26 craft, Domain 27 artifact/specification compilation, and Domain 28 adversarial quality controls. Benchmark-derived hardening activates Domain 29 where applicable; final usability/visual/truth/measurement closure activates Domain 30 for substantial production work. Material operating procedures additionally activate Domain 31 for procedure compilation, authority, decision rights, evidence, KPI governance, and lifecycle validation. Revision 1.7 keeps the same 31-domain/1,300-control plane while adding semantic request/context graphs, negation-aware exposure routing, composite artifacts, first-class non-web contracts, capability-first phase retrieval, executable evidence adapters, benchmark/control analytics, and release provenance. Domain 23/31 operational semantics remain machine-consistent.

# Semantic Profile Resolution
<!-- id: readme.semantic-profile-resolution -->

After canonical industry resolution, use `PROFILE_MATRIX.md` to resolve five independent dimensions:

1. **Operating Profile** → `JOBS.md` and exact `operations/<profile>.md` shard; for material SOP/runbook/work-instruction output, compile that baseline through `OPERATIONAL_PROCEDURE_COMPILER.md` and applicable Domain 31 standards.
2. **Product Profile** → capability baseline in `FEATURES.md`.
3. **Design Profile** → domain visual/interaction strategy in `DESIGN.md`.
4. **Halo Profile** → authority/proof strategy in `HALO.md`.
5. **Risk Overlays** → additive retrieval triggers for legal, security, operational, safety, and other standards.

Do not collapse these dimensions into one profile. Matrix defaults do not replace actual project facts.

For mixed-model categories, resolve the exact subindustry/business model before treating defaults as implementation requirements.

## Semantic Contamination Guard

Before using retrieved content, verify that industry ID, profile dimension, domain terminology, audience, and risk context match the current project. A technology suffix must not erase domain risk/proof; a physical-domain identity must not force an application into an inappropriate brochure interaction model.

# Creation Request Input
<!-- id: readme.creation-request-input -->

Preferred project-level specification:

```text
PROJECT.md
```

If it does not exist, the user's current creation prompt is sufficient.

Useful fields:

```text
Creation Type
Industry
Subindustry
Creation
Goal
Audience
Output
Delivery Mode
Asset Policy
Stack
Constraints
```

Only request additional project facts when they materially affect execution and cannot be responsibly inferred.

## Creation Type

Canonical values include:

```text
Website
Landing Page
Web App
SaaS
Portal
Marketplace
E-Commerce
Mobile App
API
Dashboard
Design System
Brand Strategy
SEO/GEO/AEO Content
Feature Plan
Security Architecture
Legal Policies
Org Chart
Job Positions
Operating Procedures
Documentation
Repository Architecture
Other
```

Normalize equivalent user wording without changing intent.

## Goal

Use the project goal to prioritize feature, information, proof, conversion, and interaction decisions.

## Audience

Resolve audience when the same industry serves materially different user groups.

## Output

Honor the requested artifact type. Do not silently substitute a plan, mockup, prototype, or representative subset for implementation.

# Inline Creation Request
<!-- id: readme.inline-creation-request -->

If a current creation block is intentionally placed inside README, precedence remains:

```text
1. User's current explicit prompt
2. PROJECT.md
3. README inline current creation
4. Pack defaults
```

# Instruction & Standards Precedence
<!-- id: readme.instruction-and-standards-precedence -->

When instructions conflict:

```text
1. Safety and applicable law
2. User's current explicit instruction
3. PROJECT.md explicit requirements
4. Industry-specific mandatory requirements
5. SECURITY.md / LEGAL.md mandatory controls
6. README.md orchestration rules
7. Module-level MUST / MUST NOT
8. Module-level SHOULD / SHOULD NOT
9. Industry recommendations
10. Module-level MAY
11. General defaults
```

At equal precedence, prefer the more specific, directly applicable, higher-risk/safety-preserving, and more maintainable rule.

# Standards Enforcement Levels
<!-- id: readme.standards-enforcement-levels -->

- `MUST` — mandatory.
- `MUST NOT` — prohibited.
- `SHOULD` — default unless a concrete project-specific reason justifies another approach.
- `SHOULD NOT` — avoid unless project requirements justify it.
- `MAY` — optional enhancement.

Do not implement every optional recommendation merely because it exists.

# Operational Procedure Production Rule
<!-- id: readme.operational-procedure-production -->

When the requested creation is Operating Procedures, Job Positions with real authority/responsibility detail, runbooks, work instructions, checklists, playbooks, or an operational workflow intended for real execution:

1. Resolve the exact operating profile and role baseline lazily.
2. Resolve exact subindustry, task, trigger, organization/site context, and consequence of error before adding procedural specificity.
3. Use `OPERATIONAL_PROCEDURE_COMPILER.md`; profile SOP prose alone is not complete production evidence.
4. Classify authority/provenance with `PROCEDURE_AUTHORITY.md`.
5. Use `DECISION_RIGHTS.md`, `OPERATIONAL_EVIDENCE.md`, and `KPI_GOVERNANCE.md` where applicable.
6. Do not present generated general guidance as company-approved, regulator-required, manufacturer-required, licensed, certified, or jurisdiction-specific procedure without supporting evidence.
7. If current authoritative accuracy materially depends on current law, regulation, standard, manufacturer instruction, policy, or contract and tools exist, retrieve the current authoritative source; otherwise mark the affected portion `UNVERIFIED`.

# Production Intent Guard
<!-- id: readme.production-intent-guard -->

Unless explicitly requested otherwise, assume the requested artifact is **complete, production-grade, full-scope work** within the requested deliverable type.

Do not silently downgrade to mockup, prototype, proof of concept, MVP, demo, starter, skeleton, sample, representative subset, abbreviated version, wireframe, placeholder build, or partial implementation.

Production-grade implementation SHOULD include all applicable:

- information architecture;
- responsive behavior;
- real component and interaction states;
- accessibility;
- error/recovery behavior;
- performance considerations;
- security/privacy/legal controls;
- maintainable structure;
- meaningful content;
- working navigation/actions within scope;
- for P0/P1 workflows, close task friction, action hierarchy, input efficiency, feedback, and recovery using `USABILITY_CLOSURE.md`;
- perform a rendered final-finish sweep using `VISUAL_FINISH.md`;
- expose material sample/assumption/unknown/recommendation provenance with `TRUTH_BOUNDARIES.md`;
- for responsive documents/operations, apply `RESPONSIVE_DETAIL_CLOSURE.md`;
- use `QUALITY_MEASUREMENT.md` to separate frozen benchmark comparability from floor-capable release evidence;
- a resolved artifact-specific production contract;
- compiled feature purpose, user-job, information, action, state, responsive, accessibility, truth/data, dependency, and acceptance semantics for high-value features;
- compiled component anatomy, iconography, surface/elevation, affordance, contextual-action, state/variant, responsive, and micro-detail behavior for important visible UI;
- structural-fingerprint genericity review before final implementation;
- adversarial critique, repair, and artifact-specific quality-floor enforcement before final completion;
- local production-quality visual assets when required;
- validation and rendered review when tooling exists.

Production output MUST NOT use Lorem ipsum, dead primary actions, generic placeholder images, unsupported fake proof, obvious TODO blocks, or “implement later” substitutions for work that can reasonably be completed now.

Unknown business facts remain unknown.

# Delivery Mode Resolution
<!-- id: readme.delivery-mode-resolution -->

Resolve:

```text
1. User's explicit instruction
2. PROJECT.md Delivery Mode
3. Requested artifact semantics
4. Default: Production
```

Non-production implementation modes are permitted only when explicitly selected or inherent to the requested artifact.

Implementation maturity and visual fidelity are independent. A request for a `Concept` may limit implementation maturity while still requiring **High-Fidelity** visual craft. Unless the user explicitly requests low fidelity, rough exploration, mockup-level finish, or wireframe treatment, substantial visual concepts retain applicable Domain 29/30 feature-depth, usability, visual-finish, truth, responsive/accessibility, and quality-closure standards.

# Core Instruction
<!-- id: readme.core-instruction -->

For every request:

1. Resolve current explicit requirements.
2. Apply inherited project context where still valid.
3. Classify creation and delivery mode.
4. Resolve industry/subindustry/business model when relevant.
5. Resolve independent profiles and additive risks.
6. Use routing to retrieve only required module/control sections.
7. Separate mandatory requirements from recommendations.
8. Convert standards into concrete decisions.
9. For substantial visual work, establish creative direction before assembling components.
10. For substantial UI/product work, resolve Domain 26 feature/component craft before considering the artifact finished.
11. Build to the resolved delivery mode without silent reduction.
12. Render/inspect when tools permit.
13. Apply QA gates and recover from failures.
14. Deliver the artifact rather than a dump of pack instructions.

# Files
<!-- id: readme.files -->

| File | Purpose | Load When |
|---|---|---|
| `PROJECT.md` | Optional current project request | Immediately after README when present |
| `INDUSTRIES.md` | Canonical industry taxonomy | Resolving/validating industry |
| `PROFILE_MATRIX.md` | Operating/Product/Design/Halo/Risk defaults | After industry resolution |
| `MANIFEST.md` | Industry/operations stable-address registry | Exact industry/SOP addresses |
| `CONTROL_INDEX.md` | Canonical control-plane router | Resolving bundles/capabilities |
| `CONTROL_MANIFEST.md` | Control-plane stable-address/count manifest | Exact control architecture metadata |
| `ARTIFACT_CONTRACTS.md` | Artifact-type production-contract router | Substantial production artifacts |
| `contracts/*.md` | Artifact-specific acceptance contracts | After artifact-contract resolution |
| `FEATURE_COMPILER.md` | High-value feature compiler | Before detailed UI/component design |
| `COMPONENT_COMPILER.md` | Component anatomy/state compiler | After feature resolution |
| `GENERICITY.md` | Structural fingerprint and anti-template engine | Concept selection and rendered genericity review |
| `CRITICS.md` | Independent adversarial critics and repair loop | After implementation/render |
| `QUALITY_FLOORS.md` | Non-averagable quality floors | Production acceptance |
| `RESPONSIVE_COMPOSITION.md` | Narrow-screen task/data transformation standard | Product/mobile work |
| `DOCUMENT_CRAFT.md` | Decision-depth and editorial document standard | Documents/reports |
| `ACCESSIBILITY_EVIDENCE.md` | Critical-path accessibility evidence | Interactive/public work |
| `COMPLETENESS.md` | P0/P1 coverage ledger | Substantial production work |
| `FEATURE_DEPTH.md` | Level-5 feature closure | Product/workflow features |
| `USABILITY_CLOSURE.md` | P0/P1 task-path friction, action, state, feedback, recovery closure | Substantial interactive workflows |
| `VISUAL_FINISH.md` | Rendered perceptual and optical final-finish review | High-fidelity visual artifacts |
| `RESPONSIVE_DETAIL_CLOSURE.md` | Task/detail narrow-viewport evidence beyond macro layout | Responsive documents/operations |
| `QUALITY_MEASUREMENT.md` | Longitudinal vs floor-capable score/evidence calibration | Numerical quality claims and Domain 30 closure |
| `BENCHMARKS.md` | Blind paired efficacy benchmark protocol | Pack evaluation / improvement |
| `BENCHMARK_STATUS_1_6.md` | Current Runtime/Core benchmark readiness vs proven efficacy boundary | Release/benchmark review |
| `control_registry.csv` + `control_registry/*.csv` | Logical machine control registry | Exact control/capability lookup |
| `QA_GATES.md` | Release and semantic regression gates | Validation / pack maintenance |
| `FEATURES.md` | Industry/product capability baseline | Product/website/app feature design |
| `DESIGN.md` | Industry design strategy/libraries | UI/UX and implementation |
| `CREATIVE.md` | Art direction, differentiation, rendered visual quality | Substantial visual work |
| `CRAFT.md` | Feature depth and component craftsmanship | Substantial production interfaces |
| `ASSETS.md` | Local visual asset strategy | Custom media required |
| `HALO.md` | Authority/proof/growth | Brand/proof strategy |
| `JOBS.md` | Job positions by industry | Staffing/role resolution |
| `operations/*.md` | Sharded SOPs | Exact role procedure |
| `SEO_GEO_AEO.md` | Discoverability standards | Public search content |
| `TERMINOLOGY.md` | Naming/copy/status/action language | User-facing wording |
| `STRUCTURE.md` | Architecture/maintainability | System organization |
| `SECURITY.md` | Security controls | Auth/data/APIs/payments/etc. |
| `LEGAL.md` | Legal/privacy policy standards | Legal/privacy/payment obligations |
| `EVALS.md` + `evals/*.json` | Regression system | Pack maintenance / behavioral changes |
| `MIGRATION.md` | Pack/control-plane migration trace | Compatibility review |

# Module Dependencies
<!-- id: readme.module-dependencies -->

Use dependencies selectively:

```text
DESIGN → CREATIVE for substantial visual direction
DESIGN → CRAFT for component/system craft when material

CREATIVE → DESIGN
CREATIVE → CRAFT for production interfaces
CREATIVE → ASSETS when media is required

FEATURES → CRAFT for substantial interactive features
FEATURES → STRUCTURE
FEATURES → SECURITY / LEGAL when triggered

CRAFT → ARTIFACT_CONTRACTS / FEATURE_COMPILER / COMPONENT_COMPILER for compiled production intent
CRAFT → DESIGN / CREATIVE for visual-system decisions
CRAFT → GENERICITY for structural differentiation
CRAFT → TERMINOLOGY for state/action microcopy
CRAFT → CRITICS / QUALITY_FLOORS for final adversarial acceptance
CRAFT → accessibility/engineering controls through CONTROL_INDEX

ASSETS → CREATIVE / DESIGN
SECURITY ↔ LEGAL when behavior and policy intersect
operations → JOBS / INDUSTRIES / risk modules when triggered
```

A dependency does not authorize full-file preload.

# Risk-Triggered Routing
<!-- id: readme.risk-triggered-routing -->

Add required modules/controls for accounts, permissions, payments, billing, personal/health/financial data, minors, AI/tool execution, user-generated content, marketplaces, uploads, public search content, regulated/safety-critical workflows, third-party sensitive-data integrations, and tracking/consent.

Risk routing overrides optional routing.

# Canonical Addressing
<!-- id: readme.canonical-addressing -->

- `README.md` defines how to route.
- `MANIFEST.md` resolves industry/operations addresses.
- `CONTROL_INDEX.md` and the logical machine registry resolve control-plane addresses.
- Stable IDs are preferred over fuzzy headings.
- File order is never an address.

For control-plane ranges/counts, `CONTROL_INDEX.md` and the logical registry are authoritative over stale count summaries in older module snapshots.

# Retrieval Rules
<!-- id: readme.retrieval-rules -->

## Rule 1 — Resolve Industry First

For industry-specific work, resolve the canonical identity before using industry-mapped modules.

### Duplicate Subindustry Resolution Guard
<!-- id: readme.duplicate-subindustry-resolution -->

When a subindustry label appears under multiple parents, MUST NOT select the first match or broadest umbrella.

Resolve using:

1. exact offering/domain term;
2. narrowest direct canonical parent;
3. audience, transaction model, service area, operating model, and deliverable;
4. independent profile overrides after canonical identity;
5. local service / B2C behavior when appropriate without erasing domain identity;
6. strongest contextual evidence when ambiguity remains.

## Rule 2 — Read Exact Headings

For industry-indexed modules, retrieve the exact industry heading and stop at the next top-level heading.

## Rule 3 — Resolve Job Before SOP

Resolve industry → role → MANIFEST operations shard → exact SOP stable ID/section.

## Rule 3A — Section-Level Retrieval Protocol

Search by stable ID when available. Retrieve only the matching section plus the minimum adjacent context required to apply it correctly.

## Rule 4 — Load Universal Standards by Need

Load only when applicable:

- `CREATIVE.md` — substantial visual differentiation/quality.
- `CRAFT.md` — substantial production feature/component craft.
- `ASSETS.md` — custom images/illustrations/media.
- `STRUCTURE.md` — maintainable systems.
- `TERMINOLOGY.md` — naming/copy/UI text.
- `SEO_GEO_AEO.md` — public discoverability.
- `SECURITY.md` — auth/permissions/sensitive data/APIs/payments.
- `LEGAL.md` — policies/privacy/consumer/payment/legal obligations.

# Creation-Type Router
<!-- id: readme.creation-type-router -->

Use `SEMANTIC_ROUTING.md` before this table when creation type, industry, negation, risk exposure, or composite scope is ambiguous. Hybrid/composite creations compile one artifact node per independently deliverable family; do not force the whole project into one type.

| Creation Type | Primary Modules |
|---|---|
| Website / Landing Page | INDUSTRIES, ARTIFACT_CONTRACTS, FEATURES, DESIGN, CREATIVE, CRAFT, FEATURE_COMPILER, GENERICITY, COMPONENT_COMPILER, CRITICS, QUALITY_FLOORS, HALO, SEO_GEO_AEO, TERMINOLOGY, STRUCTURE, ASSETS when Domain 11/media is active |
| Web App / SaaS / Portal | INDUSTRIES, ARTIFACT_CONTRACTS, FEATURES, FEATURE_COMPILER, DESIGN, CREATIVE, CRAFT, GENERICITY, COMPONENT_COMPILER, CRITICS, QUALITY_FLOORS, STRUCTURE, TERMINOLOGY |
| Marketplace / E-Commerce | INDUSTRIES, ARTIFACT_CONTRACTS, FEATURES, FEATURE_COMPILER, DESIGN, CREATIVE, CRAFT, GENERICITY, COMPONENT_COMPILER, CRITICS, QUALITY_FLOORS, ASSETS, SEO_GEO_AEO, TERMINOLOGY |
| Dashboard | ARTIFACT_CONTRACTS, FEATURES, FEATURE_COMPILER, DESIGN, CREATIVE, CRAFT, GENERICITY, COMPONENT_COMPILER, CRITICS, QUALITY_FLOORS, STRUCTURE, TERMINOLOGY |
| Native / Mobile App | INDUSTRIES, ARTIFACT_CONTRACTS, FEATURES, FEATURE_COMPILER, DESIGN, CREATIVE, CRAFT, GENERICITY, COMPONENT_COMPILER, CRITICS, QUALITY_FLOORS, STRUCTURE, TERMINOLOGY |
| Presentation / Deck | ARTIFACT_CONTRACTS, DOCUMENT_CRAFT, DESIGN, CREATIVE, CRAFT, ASSETS, CRITICS, QUALITY_FLOORS, TERMINOLOGY |
| Spreadsheet / Financial Model | ARTIFACT_CONTRACTS, STRUCTURE, TERMINOLOGY, TRUTH_BOUNDARIES, CRITICS, QUALITY_FLOORS |
| Brand Identity / Logo | INDUSTRIES, ARTIFACT_CONTRACTS, HALO, DESIGN, CREATIVE, CRAFT, ASSETS, GENERICITY, CRITICS, QUALITY_FLOORS, TERMINOLOGY |
| Email / Campaign | INDUSTRIES, ARTIFACT_CONTRACTS, HALO, CREATIVE, CRAFT, TERMINOLOGY, LEGAL when triggered |
| Marketing Creative | INDUSTRIES, ARTIFACT_CONTRACTS, DESIGN, CREATIVE, CRAFT, ASSETS, GENERICITY, CRITICS, QUALITY_FLOORS, TERMINOLOGY |
| CLI / Developer Tool | ARTIFACT_CONTRACTS, STRUCTURE, TERMINOLOGY, SECURITY when triggered |
| Fixed-Format Document / PDF | ARTIFACT_CONTRACTS, DOCUMENT_CRAFT, STRUCTURE, TERMINOLOGY, CRITICS, QUALITY_FLOORS |
| Design System | DESIGN, CREATIVE, CRAFT, STRUCTURE, TERMINOLOGY |
| Feature Plan | ARTIFACT_CONTRACTS, FEATURES, FEATURE_COMPILER, CRAFT, QUALITY_FLOORS, STRUCTURE |
| API | STRUCTURE, TERMINOLOGY; SECURITY when triggered |
| Brand Strategy | HALO, TERMINOLOGY, DESIGN/CREATIVE when needed |
| SEO/GEO/AEO Content | SEO_GEO_AEO, TERMINOLOGY, industry context |
| Security Architecture | SECURITY, STRUCTURE, TERMINOLOGY; LEGAL when applicable |
| Legal Policies | LEGAL, TERMINOLOGY, SECURITY when referenced |
| Org / Jobs / SOPs | INDUSTRIES, JOBS, exact operations section |
| Documentation / Repository Architecture | STRUCTURE, TERMINOLOGY, DOCUMENT_CRAFT, SECURITY when applicable |

`SEMANTIC_ROUTING.md`, `RETRIEVAL_INTELLIGENCE.md`, `TRUTH_BOUNDARIES.md`, `COMPLETENESS.md`, and `EVIDENCE_ADAPTER.md` are cross-cutting orchestration standards and are not permission to preload their entire contents. Runtime retrieves their required stable sections. Risk modules are activated from the exposure/risk graph rather than industry labels alone.

# Routing by Task
<!-- id: readme.routing-by-task -->

For substantial production artifacts, resolve the artifact contract before detailed creation. Production visual/product work activates Domains 26–28 through `CONTROL_INDEX.md` as applicable.

Domain 27 compiles artifact/feature/component/fingerprint intent before implementation. Domain 28 performs adversarial post-implementation review, recovery, floors, and benchmark governance. Domain 29 hardens measured benchmark gaps in mobile composition, documents, accessibility evidence, completeness, and feature depth while preserving genericity resistance. Domain 30 routes the applicable closure standards directly: `USABILITY_CLOSURE.md`, `VISUAL_FINISH.md`, `TRUTH_BOUNDARIES.md`, `RESPONSIVE_DETAIL_CLOSURE.md`, and `QUALITY_MEASUREMENT.md`. High-fidelity concepts keep this quality-closure path even when implementation maturity is explicitly non-production.

Purely non-visual/non-interactive work may still use an artifact contract and Domain 28 evidence controls, while visual craft remains inactive when irrelevant.

# Creation Validation Matrix
<!-- id: readme.creation-validation-matrix -->

| Creation Type | Required Validation |
|---|---|
| Website / Landing Page | rendered desktop/mobile, conversion paths, truth, accessibility, assets, discoverability when public |
| Web App / SaaS / Portal | task/state behavior, responsive UI, accessibility, runtime integrity; security/legal only from actual exposure |
| Marketplace / E-Commerce | discovery→detail→cart/checkout, totals/data truth, responsive/accessibility, transactional security/legal |
| Dashboard | monitoring/investigation/action paths, dense responsive transformations, data truth, state/error coverage |
| Native / Mobile App | device-size states, platform conventions, permissions, keyboard/safe areas, lifecycle recovery, accessibility |
| Presentation / Deck | narrative/decision depth, slide bounds, font/image integrity, export rendering, evidence truth |
| Spreadsheet / Financial Model | recalculation, formulas, lineage, cross-sheet links, scenarios, checks, open-file integrity |
| Brand Identity / Logo | originality, small-size/monochrome performance, system variants, export/vector integrity |
| Email / Campaign | message/sequence logic, links, mobile/dark rendering, personalization fallbacks, compliance boundaries |
| Marketing Creative | channel dimensions, safe areas, crop variants, hierarchy, factual claims, originality |
| CLI / Developer Tool | help, happy/failure paths, exit codes, stdout/stderr, config/auth safety, platform smoke tests |
| Fixed-Format Document / PDF | every-page rendering, pagination/clipping, tables/figures, links, references, accessibility when required |
| Design System | design/token/component consistency, accessibility and documented usage |
| Feature Plan | feature/job/state/data completeness, truth and triggered risk constraints |
| API | contract/schema examples, validation/errors, auth/data/security when exposed |
| Brand Strategy | evidence-backed positioning, differentiation, terminology, no invented market/customer facts |
| SEO/GEO/AEO Content | factual/source integrity, search intent, structured/discoverability checks as applicable |
| Security Architecture | threat/risk model, trust boundaries, controls/evidence, legal/privacy dependencies |
| Legal Policies | authoritative-source/jurisdiction review; no invented compliance claims |
| Org / Jobs / SOPs | operational procedure schema, authority, evidence, KPI/lifecycle checks |
| Documentation / Repository Architecture | decision/editorial depth, structure, truth, repository/runtime integrity as applicable |

# Final Validation Protocol
<!-- id: readme.final-validation-protocol -->

Before delivering substantial work:

1. Identify creation modules and active control capabilities.
2. Apply risk-triggered validation.
3. Check applicable MUST/MUST NOT and major SHOULD rules.
4. Validate terminology, structure, industry fit, truthfulness, security/privacy/legal/accessibility when applicable.
5. Confirm no silent production downgrade.
6. For substantial visual work, apply `creative.production-visual-acceptance-gate`.
7. Resolve and validate the active artifact contract.
8. Verify high-value feature compilation and important component compilation.
9. Apply pre-implementation structural-fingerprint genericity review.
10. For substantial production interfaces, apply `craft.production-craft-acceptance-gate`.
11. Validate assets where required.
12. When render tools exist, run independent critics in `CRITICS.md`, repair material failures, and re-render affected views/states.
13. Apply `QUALITY_FLOORS.md`; a strong aggregate score cannot average away a failed required dimension.
14. Correct avoidable failures; do not merely report them.
15. Mark unavailable evidence UNVERIFIED rather than passed.
16. Do not expose internal QA notes unless asked.

# Multi-File Composition Order
<!-- id: readme.multi-file-composition-order -->

```text
User requirements
→ industry/business context
→ legal/security/safety/accessibility
→ structure/terminology
→ feature behavior
→ design/creative direction
→ feature & component craft
→ assets
→ discoverability/halo
→ implementation
→ rendered evidence
```

Higher-risk requirements constrain presentation choices.

# Conflict Resolution
<!-- id: readme.conflict-resolution -->

Apply precedence, specificity, risk, maintainability, and actual implementation behavior. Do not silently merge incompatible rules.

# Context Efficiency Protocol
<!-- id: readme.context-efficiency-protocol -->

Preferred sequence:

```text
README
→ user request / PROJECT
→ creation + delivery mode
→ industry/profile only if needed
→ risk triggers
→ CONTROL_INDEX bundle/capability
→ artifact contract
→ feature compilation
→ creative concepts + structural fingerprint
→ component compilation
→ implementation
→ render/test
→ adversarial critics + repair
→ quality floors
→ validate
```

Never load every module, every control shard, every industry, or every SOP.

# Search Patterns
<!-- id: readme.search-patterns -->

Prefer stable IDs. Otherwise search exact headings or smallest useful keyword set.

# Do Not Duplicate Pack Content
<!-- id: readme.do-not-duplicate-pack-content -->

Project artifacts should contain project-specific decisions, not copied standards documents.

# Project Bootstrap Pattern
<!-- id: readme.project-bootstrap-pattern -->

A project instruction may remain small:

```text
Use README.md as the main BizIQ load point.
Resolve the current request.
Load only exact required sections.
Default to Production unless explicitly overridden.
```

# Project Context Inheritance
<!-- id: readme.project-context-inheritance -->

Preserve resolved project facts across follow-ups until explicitly changed: creation type, industry/subindustry, audience, goal, delivery mode, stack, design direction, terminology, entities, auth/permissions, data sensitivity, features, integrations, brand identity, and critical constraints.

# Internal Project Decision State
<!-- id: readme.internal-project-decision-state -->

For substantial work, maintain concise internal state for decisions that later steps depend on. Do not expose it unless requested.

# Expected Agent Behavior
<!-- id: readme.expected-agent-behavior -->

Route before reading; retrieve exact sections; preserve production intent; avoid fabrication; use current research when required; resolve high-value features deeply; design important components deliberately; render/refine when possible; validate before delivery.

# Creation Execution Protocol
<!-- id: readme.creation-execution-protocol -->

1. Extract explicit requirements and inherited context.
2. Resolve creation/delivery/industry/profile/risk.
3. Load exact standards/controls.
4. Resolve conflicts.
5. Define creative direction for substantial visual work.
6. Resolve an artifact-specific production contract.
7. Compile high-value features before detailed component design.
8. Explore concepts and reject generic structural fingerprints.
9. Compile important component anatomy/variants/states.
10. Generate/integrate local assets when required.
11. Implement complete scope from compiled specifications.
12. Render desktop/mobile/critical states when tools permit.
13. Run independent adversarial critics, prioritize repair, fix, and re-render affected views.
14. Enforce artifact-specific quality floors and active Evidence Gates.
15. Deliver the requested artifact.

# Pack Execution Lifecycle
<!-- id: readme.pack-execution-lifecycle -->

```text
INITIALIZE
→ REQUEST / PROJECT
→ CLASSIFY + PRODUCTION DEFAULT
→ INDUSTRY / PROFILES / RISKS
→ CONTROL BUNDLE
→ EXACT SECTIONS
→ SEMANTIC CONTEXT / ARTIFACT GRAPH
→ PHASE-SCOPED CAPABILITY RETRIEVAL
→ ARTIFACT CONTRACT CHAIN
→ FEATURE COMPILATION
→ CREATIVE DIRECTION
→ STRUCTURAL FINGERPRINT
→ COMPONENT COMPILATION + CRAFT
→ ASSETS / IMPLEMENTATION
→ INTERACTION MANIFEST / MOBILE TASK-PRESERVATION CHECK
→ RENDER / TEST
→ ADVERSARIAL CRITICS / REPAIR
→ QUALITY FLOORS
→ VALIDATE / RECOVER
→ DELIVER
```

# Pack Version & Compatibility
<!-- id: readme.pack-version-and-compatibility -->

```text
Pack Version: 4.0.0
Schema Version: 3
Control Plane Revision: 1.8.8
```

Existing stable IDs remain compatible. Domain 26 uses BQ-1001–BQ-1050, Domain 27 uses BQ-1051–BQ-1100, and Domain 28 uses BQ-1101–BQ-1150 without renumbering earlier controls.

# Pack Integrity Validation
<!-- id: readme.pack-integrity-validation -->

When BizIQ is modified, run:

```text
python tools/validate_pack.py
```

The validator checks the logical registry and regression matrix across root files plus native shards.

Current objective control-plane expectations:

```text
31 domains
260 capabilities
1,300 controls
780 regression conditions
```

Static validation does not prove subjective visual quality; rendered/behavioral gates remain required where applicable.

# Control Plane Hooks
<!-- id: readme.control-plane-hooks -->

Use `CONTROL_INDEX.md` for exact routing. High-value production work commonly activates:

- BQ-0031–0035 silent-downgrade prevention
- BQ-0196–0200 deliverable acceptance
- BQ-0246–0250 three-direction exploration
- BQ-0261–0265 anti-template heuristics
- BQ-0346–0350 repetition detector
- BQ-0451–0455 interaction-state completeness
- BQ-0481–0485 responsive recomposition
- BQ-0646–0650 component API discipline
- BQ-0676–0680 implementation-fidelity review
- BQ-0846–0850 rendered-pixel review
- BQ-1001–1050 Feature & Component Craft as applicable
- BQ-1051–1100 Artifact Contracts & Specification Compilation
- BQ-1101–1150 Adversarial Critique, Repair, Quality Floors & Benchmarking

# Final Instruction
<!-- id: readme.final-instruction -->

**Start here. Route elsewhere only as needed.**

BizIQ is a decision source, not the output itself.
