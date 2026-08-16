<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: CONTROL_INDEX
Module-Version: 5
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-09
-->

# BizIQ Control Index
<!-- id: control-index.root -->

This is the canonical routing index for the BizIQ control plane. It is **not** a request to preload every control. Resolve the active task first, then retrieve only the exact capability sections required by the current decision.

The logical control plane contains **31 domains, 260 capabilities, and 1,300 controls (`BQ-0001` through `BQ-1300`)**.

# Control Semantics
<!-- id: control-index.semantics -->

- Every capability has five mandatory controls: **Contract, Procedure, Evidence Gate, Recovery, Regression**.
- A dependent result is provisional until its Evidence Gate passes.
- `UNVERIFIED` is a valid state; silent pass is not.
- Controls strengthen domain modules but cannot override higher-precedence system/user instructions.
- When controls conflict, use README precedence; at equal precedence choose the more specific/higher-risk constraint and record the decision.
- Existing `BQ-0001` through `BQ-1250` retain their stable meaning. Domain 31 occupies `BQ-1251`–`BQ-1300`.

# Registry Resolution
<!-- id: control-index.registry-resolution -->

The machine-readable control registry is one logical registry with sharded storage:

1. Read `control_registry.csv` for the original control set.
2. Read only the required shard(s) under `control_registry/*.csv` when a capability outside the root registry is active.
3. Domain 26: `control_registry/26-feature-component-craft.csv`.
4. Domain 27: `control_registry/27-artifact-contracts-and-specification-compilation.csv`.
5. Domain 28: `control_registry/28-adversarial-critique-repair-quality-floors-and-benchmarking.csv`.
6. Domain 29: `control_registry/29-benchmark-driven-quality-hardening.csv`.
7. Domain 30: `control_registry/30-usability-visual-finish-truth-and-quality-closure.csv`.
8. Domain 31: `control_registry/31-operational-procedure-compilation-authority-and-measurement.csv`.
9. `CONTROL_MANIFEST.md` is canonical for current control-plane count/address metadata.
10. Do not preload all registry shards merely because they exist.

When an exact capability-to-shard mapping is not listed in the high-leverage routes below, search the logical machine registry by capability name or stable ID. The machine registry is canonical for exact control IDs; this index is canonical for activation/routing.

# Activation Bundles
<!-- id: control-index.activation-bundles -->

Use these bundles as retrieval hints. Load exact sections, not whole shards unless several capabilities from the same shard are simultaneously active.

| Bundle | Trigger | Required domains |
|---|---|---|
| Core Creation | Any new artifact or substantial modification | 01, 02, 05, 22, 24 |
| Business Classification | Industry/business-model-sensitive work | 03, 04 |
| Artifact Compilation | Substantial production artifact before detailed implementation | 27 |
| Public-Facing Visual | Website, landing page, brand, campaign, substantial visual frontend | 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 26, 27, 28 |
| Front-End Product | Website/app UI implementation | 06, 07, 08, 09, 10, 12, 13, 14, 17, 21, 22, 26, 27, 28 |
| Stateful Application | Accounts, data, permissions, workflows, APIs, integrations | 18, 19, 21, 22, 27, 28 |
| Search/Discovery | Indexable public web content | 15, 20 |
| Operational System | Jobs, SOPs, staffing, workflows | 23, 31, 22, 24, 27, 28 |
| Document / Report | Decision documents and formal reports | 15, 22, 24, 27, 28 |
| Pack Maintenance | BizIQ itself is being changed | 25, 22, 24, 28 |

Domain 26 is mandatory for substantial production visual/product interfaces when craft is material. Domain 27 is mandatory for substantial production artifacts that benefit from compilation. Domain 28 is mandatory for substantial production acceptance and behaviorally meaningful BizIQ benchmark changes unless clearly inapplicable. Domain 31 is mandatory for material SOPs, work instructions, runbooks, operational role specifications, and governed KPI/decision-rights systems intended for real execution.

# High-Leverage Mandatory Capability Set
<!-- id: control-index.high-leverage-set -->

For production public-facing websites/apps, the following capabilities are mandatory unless clearly inapplicable:

authoritative-entry verification; instruction-precedence ledger; silent-downgrade prevention; requirement completeness model; unknown-fact policy; goal hierarchy; audience resolution; scope boundary; canonical-industry confidence; duplicate-subindustry disambiguation; independent-profile dimensions; creation-type classifier; production-vs-concept distinction; deliverable acceptance contract; benchmark quality filter; differentiation ledger; three-direction exploration quality; concept selection rubric; brand-specific fingerprint; anti-template heuristics; primary-task mapping; journey-state model; content-priority hierarchy; edge-state architecture; section-purpose uniqueness; macro-rhythm system; hero composition diversity; repetition detector; viewport composition review; type-role specification; contrast-system validation; surface-depth discipline; proof-media hierarchy; hero-media fidelity; custom-image art direction; asset quality rejection; interaction-state completeness; responsive recomposition; mobile-first priority check; dense-UI adaptation; semantic-structure requirement; keyboard-completion gate; message-hierarchy map; claim-evidence pairing; content-realism gate; conversion-path model; trust-signal authenticity; CTA hierarchy; semantic-component mapping; component API discipline; no-dead-control gate; implementation-fidelity review; performance-budget declaration; evidence-based completion; rendered-pixel review; visual-regression fixtures; quality-score evidence; deliverable manifest; self-contained delivery check; handoff readiness; icon-system-selection; iconography-coverage-audit; component-anatomy-quality; card-surface-specificity; interaction-affordance-microdetail; feature-depth-resolution; feature-state-completeness; feature-to-component-mapping; responsive-feature-recomposition; final-craft-evidence; artifact-contract-resolution; artifact-contract-completeness; feature-specification-compiler; feature-information-action-model; user-job-state-data-model; component-design-compiler; component-variant-state-matrix; structural-fingerprint-generation; genericity-similarity-rejection; compiled-specification-handoff; iterative-render-critique-loop; visual-quality-critic; feature-depth-critic; accessibility-responsive-critic; truth-implementation-critic; genericity-critic; repair-plan-prioritization; category-floor-enforcement.


## High-Leverage Operational Capability Set
<!-- id: control-index.high-leverage-operations -->

For substantial production operating procedures unless clearly inapplicable: role-scope integrity; SOP trigger conditions; SOP exception handling; operational evidence; role-to-SOP coverage; metric ownership; handoff contracts; operational-risk routing; operational-context-resolution; role-accountability-compilation; procedure-authority-classification; executable-procedure-compilation; decision-rights-approval-boundaries; decision-checkpoint-stop-sequencing; exception-recovery-continuity; operational-evidence-definition-of-done; kpi-definition-metric-governance; procedure-validation-change-reauthorization.

# Domain Registry
<!-- id: control-index.domain-registry -->

| Domain | Shard | Capabilities | BQ controls |
|---|---|---:|---:|
| 01. Initialization, Precedence & Agent Control | `controls/01-initialization-precedence-and-agent-control.md` | 8 | 40 |
| 02. Project Intake & Requirement Resolution | `controls/02-project-intake-and-requirement-resolution.md` | 8 | 40 |
| 03. Industry Taxonomy & Business-Model Classification | `controls/03-industry-taxonomy-and-business-model-classification.md` | 8 | 40 |
| 04. Semantic Profiles, Risk & Context Overlays | `controls/04-semantic-profiles-risk-and-context-overlays.md` | 8 | 40 |
| 05. Creation-Type Routing & Deliverable Semantics | `controls/05-creation-type-routing-and-deliverable-semantics.md` | 8 | 40 |
| 06. Research, Benchmarking & Reference Intelligence | `controls/06-research-benchmarking-and-reference-intelligence.md` | 8 | 40 |
| 07. Brand Strategy & Creative Direction | `controls/07-brand-strategy-and-creative-direction.md` | 8 | 40 |
| 08. UX Strategy & Information Architecture | `controls/08-ux-strategy-and-information-architecture.md` | 8 | 40 |
| 09. Layout, Composition & Spatial Hierarchy | `controls/09-layout-composition-and-spatial-hierarchy.md` | 8 | 40 |
| 10. Typography, Color & Design-System Foundations | `controls/10-typography-color-and-design-system-foundations.md` | 8 | 40 |
| 11. Imagery, Illustration & Asset Generation | `controls/11-imagery-illustration-and-asset-generation.md` | 8 | 40 |
| 12. Motion, Microinteraction & Behavioral Craft | `controls/12-motion-microinteraction-and-behavioral-craft.md` | 8 | 40 |
| 13. Responsive, Mobile & Cross-Device Design | `controls/13-responsive-mobile-and-cross-device-design.md` | 8 | 40 |
| 14. Accessibility & Inclusive Design | `controls/14-accessibility-and-inclusive-design.md` | 8 | 40 |
| 15. Content, Copy & Terminology | `controls/15-content-copy-and-terminology.md` | 8 | 40 |
| 16. Conversion, Trust & Business Outcomes | `controls/16-conversion-trust-and-business-outcomes.md` | 8 | 40 |
| 17. Front-End Engineering & Component Implementation | `controls/17-front-end-engineering-and-component-implementation.md` | 8 | 40 |
| 18. Application Logic, Data & Integrations | `controls/18-application-logic-data-and-integrations.md` | 8 | 40 |
| 19. Security, Privacy & Legal Compliance | `controls/19-security-privacy-and-legal-compliance.md` | 8 | 40 |
| 20. SEO, GEO, AEO & Discoverability | `controls/20-seo-geo-aeo-and-discoverability.md` | 8 | 40 |
| 21. Performance, Reliability & Resource Budgets | `controls/21-performance-reliability-and-resource-budgets.md` | 8 | 40 |
| 22. QA, Render Review & Automated Evaluation | `controls/22-qa-render-review-and-automated-evaluation.md` | 8 | 40 |
| 23. Jobs, SOPs & Operational Systems | `controls/23-jobs-sops-and-operational-systems.md` | 8 | 40 |
| 24. Packaging, Delivery & Repository Integration | `controls/24-packaging-delivery-and-repository-integration.md` | 8 | 40 |
| 25. Pack Governance, Versioning, Evals & Self-Improvement | `controls/25-pack-governance-versioning-evals-and-self-improvement.md` | 8 | 40 |
| 26. Feature & Component Craft | `controls/26-feature-component-craft.md` | 10 | 50 |
| 27. Artifact Contracts & Specification Compilation | `controls/27-artifact-contracts-and-specification-compilation.md` | 10 | 50 |
| 28. Adversarial Critique, Repair, Quality Floors & Benchmarking | `controls/28-adversarial-critique-repair-quality-floors-and-benchmarking.md` | 10 | 50 |
| 29. Benchmark-Driven Quality Hardening | `controls/29-benchmark-driven-quality-hardening.md` | 10 | 50 |
| 30. Usability, Visual Finish, Truth & Quality Closure | `controls/30-usability-visual-finish-truth-and-quality-closure.md` | 10 | 50 |
| 31. Operational Procedure Compilation, Authority & Measurement | `controls/31-operational-procedure-compilation-authority-and-measurement.md` | 10 | 50 |

# Capability Registry
<!-- id: control-index.capability-registry -->

For exact mappings across Domains 01–25, search the canonical logical machine registry (`control_registry.csv` plus applicable `control_registry/*.csv` shards) rather than expanding this routing file into a second copy of 200 registry rows.

The following high-leverage and Domain 26 mappings are retained here because they are frequently activated during production creation:

| Capability | Domain | Shard | Control IDs |
|---|---:|---|---|
| Silent-downgrade prevention | 01 | `controls/01-initialization-precedence-and-agent-control.md` | BQ-0031–BQ-0035 |
| Requirement completeness model | 02 | `controls/02-project-intake-and-requirement-resolution.md` | BQ-0041–BQ-0045 |
| Unknown-fact policy | 02 | `controls/02-project-intake-and-requirement-resolution.md` | BQ-0046–BQ-0050 |
| Canonical-industry confidence | 03 | `controls/03-industry-taxonomy-and-business-model-classification.md` | BQ-0081–BQ-0085 |
| Duplicate-subindustry disambiguation | 03 | `controls/03-industry-taxonomy-and-business-model-classification.md` | BQ-0086–BQ-0090 |
| Independent-profile dimensions | 04 | `controls/04-semantic-profiles-risk-and-context-overlays.md` | BQ-0121–BQ-0125 |
| Production-vs-concept distinction | 05 | `controls/05-creation-type-routing-and-deliverable-semantics.md` | BQ-0176–BQ-0180 |
| Deliverable acceptance contract | 05 | `controls/05-creation-type-routing-and-deliverable-semantics.md` | BQ-0196–BQ-0200 |
| Benchmark quality filter | 06 | `controls/06-research-benchmarking-and-reference-intelligence.md` | BQ-0206–BQ-0210 |
| Differentiation ledger | 06 | `controls/06-research-benchmarking-and-reference-intelligence.md` | BQ-0221–BQ-0225 |
| Three-direction exploration quality | 07 | `controls/07-brand-strategy-and-creative-direction.md` | BQ-0246–BQ-0250 |
| Brand-specific fingerprint | 07 | `controls/07-brand-strategy-and-creative-direction.md` | BQ-0256–BQ-0260 |
| Anti-template heuristics | 07 | `controls/07-brand-strategy-and-creative-direction.md` | BQ-0261–BQ-0265 |
| Primary-task mapping | 08 | `controls/08-ux-strategy-and-information-architecture.md` | BQ-0281–BQ-0285 |
| Journey-state model | 08 | `controls/08-ux-strategy-and-information-architecture.md` | BQ-0286–BQ-0290 |
| Edge-state architecture | 08 | `controls/08-ux-strategy-and-information-architecture.md` | BQ-0306–BQ-0310 |
| Repetition detector | 09 | `controls/09-layout-composition-and-spatial-hierarchy.md` | BQ-0346–BQ-0350 |
| Surface-depth discipline | 10 | `controls/10-typography-color-and-design-system-foundations.md` | BQ-0391–BQ-0395 |
| Asset quality rejection | 11 | `controls/11-imagery-illustration-and-asset-generation.md` | BQ-0436–BQ-0440 |
| Interaction-state completeness | 12 | `controls/12-motion-microinteraction-and-behavioral-craft.md` | BQ-0451–BQ-0455 |
| Responsive recomposition | 13 | `controls/13-responsive-mobile-and-cross-device-design.md` | BQ-0481–BQ-0485 |
| Dense-UI adaptation | 13 | `controls/13-responsive-mobile-and-cross-device-design.md` | BQ-0511–BQ-0515 |
| Keyboard-completion gate | 14 | `controls/14-accessibility-and-inclusive-design.md` | BQ-0526–BQ-0530 |
| Content-realism gate | 15 | `controls/15-content-copy-and-terminology.md` | BQ-0596–BQ-0600 |
| CTA hierarchy | 16 | `controls/16-conversion-trust-and-business-outcomes.md` | BQ-0621–BQ-0625 |
| Component API discipline | 17 | `controls/17-front-end-engineering-and-component-implementation.md` | BQ-0646–BQ-0650 |
| No-dead-control gate | 17 | `controls/17-front-end-engineering-and-component-implementation.md` | BQ-0656–BQ-0660 |
| Implementation-fidelity review | 17 | `controls/17-front-end-engineering-and-component-implementation.md` | BQ-0676–BQ-0680 |
| Performance-budget declaration | 21 | `controls/21-performance-reliability-and-resource-budgets.md` | BQ-0801–BQ-0805 |
| Evidence-based completion | 22 | `controls/22-qa-render-review-and-automated-evaluation.md` | BQ-0841–BQ-0845 |
| Rendered-pixel review | 22 | `controls/22-qa-render-review-and-automated-evaluation.md` | BQ-0846–BQ-0850 |
| Quality-score evidence | 22 | `controls/22-qa-render-review-and-automated-evaluation.md` | BQ-0866–BQ-0870 |
| Failure-postmortem loop | 25 | `controls/25-pack-governance-versioning-evals-and-self-improvement.md` | BQ-0991–BQ-0995 |
| Icon System Selection | 26 | `controls/26-feature-component-craft.md` | BQ-1001–BQ-1005 |
| Iconography Coverage Audit | 26 | `controls/26-feature-component-craft.md` | BQ-1006–BQ-1010 |
| Component Anatomy Quality | 26 | `controls/26-feature-component-craft.md` | BQ-1011–BQ-1015 |
| Card Surface Specificity | 26 | `controls/26-feature-component-craft.md` | BQ-1016–BQ-1020 |
| Interaction Affordance Microdetail | 26 | `controls/26-feature-component-craft.md` | BQ-1021–BQ-1025 |
| Feature Depth Resolution | 26 | `controls/26-feature-component-craft.md` | BQ-1026–BQ-1030 |
| Feature State Completeness | 26 | `controls/26-feature-component-craft.md` | BQ-1031–BQ-1035 |
| Feature To Component Mapping | 26 | `controls/26-feature-component-craft.md` | BQ-1036–BQ-1040 |
| Responsive Feature Recomposition | 26 | `controls/26-feature-component-craft.md` | BQ-1041–BQ-1045 |
| Final Craft Evidence | 26 | `controls/26-feature-component-craft.md` | BQ-1046–BQ-1050 |

| Artifact Contract Resolution | 27 | `controls/27-artifact-contracts-and-specification-compilation.md` | BQ-1051–BQ-1055 |
| Artifact Contract Completeness | 27 | `controls/27-artifact-contracts-and-specification-compilation.md` | BQ-1056–BQ-1060 |
| Feature Specification Compiler | 27 | `controls/27-artifact-contracts-and-specification-compilation.md` | BQ-1061–BQ-1065 |
| Feature Information Action Model | 27 | `controls/27-artifact-contracts-and-specification-compilation.md` | BQ-1066–BQ-1070 |
| User Job State Data Model | 27 | `controls/27-artifact-contracts-and-specification-compilation.md` | BQ-1071–BQ-1075 |
| Component Design Compiler | 27 | `controls/27-artifact-contracts-and-specification-compilation.md` | BQ-1076–BQ-1080 |
| Component Variant State Matrix | 27 | `controls/27-artifact-contracts-and-specification-compilation.md` | BQ-1081–BQ-1085 |
| Structural Fingerprint Generation | 27 | `controls/27-artifact-contracts-and-specification-compilation.md` | BQ-1086–BQ-1090 |
| Genericity Similarity Rejection | 27 | `controls/27-artifact-contracts-and-specification-compilation.md` | BQ-1091–BQ-1095 |
| Compiled Specification Handoff | 27 | `controls/27-artifact-contracts-and-specification-compilation.md` | BQ-1096–BQ-1100 |
| Iterative Render Critique Loop | 28 | `controls/28-adversarial-critique-repair-quality-floors-and-benchmarking.md` | BQ-1101–BQ-1105 |
| Visual Quality Critic | 28 | `controls/28-adversarial-critique-repair-quality-floors-and-benchmarking.md` | BQ-1106–BQ-1110 |
| Feature Depth Critic | 28 | `controls/28-adversarial-critique-repair-quality-floors-and-benchmarking.md` | BQ-1111–BQ-1115 |
| Accessibility Responsive Critic | 28 | `controls/28-adversarial-critique-repair-quality-floors-and-benchmarking.md` | BQ-1116–BQ-1120 |
| Truth Implementation Critic | 28 | `controls/28-adversarial-critique-repair-quality-floors-and-benchmarking.md` | BQ-1121–BQ-1125 |
| Genericity Critic | 28 | `controls/28-adversarial-critique-repair-quality-floors-and-benchmarking.md` | BQ-1126–BQ-1130 |
| Repair Plan Prioritization | 28 | `controls/28-adversarial-critique-repair-quality-floors-and-benchmarking.md` | BQ-1131–BQ-1135 |
| Category Floor Enforcement | 28 | `controls/28-adversarial-critique-repair-quality-floors-and-benchmarking.md` | BQ-1136–BQ-1140 |
| Blind Benchmark Protocol | 28 | `controls/28-adversarial-critique-repair-quality-floors-and-benchmarking.md` | BQ-1141–BQ-1145 |
| Holdout Regression Governance | 28 | `controls/28-adversarial-critique-repair-quality-floors-and-benchmarking.md` | BQ-1146–BQ-1150 |

| Mobile Priority & Recomposition | 29 | `controls/29-benchmark-driven-quality-hardening.md` | BQ-1151–BQ-1155 |
| Dense Mobile Control Compression | 29 | `controls/29-benchmark-driven-quality-hardening.md` | BQ-1156–BQ-1160 |
| Responsive Data Transformation | 29 | `controls/29-benchmark-driven-quality-hardening.md` | BQ-1161–BQ-1165 |
| Document Decision Depth | 29 | `controls/29-benchmark-driven-quality-hardening.md` | BQ-1166–BQ-1170 |
| Document Editorial Craft | 29 | `controls/29-benchmark-driven-quality-hardening.md` | BQ-1171–BQ-1175 |
| Accessibility Evidence Matrix | 29 | `controls/29-benchmark-driven-quality-hardening.md` | BQ-1176–BQ-1180 |
| Keyboard Focus & Dynamic Feedback | 29 | `controls/29-benchmark-driven-quality-hardening.md` | BQ-1181–BQ-1185 |
| Completion Coverage Ledger | 29 | `controls/29-benchmark-driven-quality-hardening.md` | BQ-1186–BQ-1190 |
| Feature Depth Closure | 29 | `controls/29-benchmark-driven-quality-hardening.md` | BQ-1191–BQ-1195 |
| Cross-Dimension Repair Preservation | 29 | `controls/29-benchmark-driven-quality-hardening.md` | BQ-1196–BQ-1200 |

| Primary Task Friction Closure | 30 | `controls/30-usability-visual-finish-truth-and-quality-closure.md` | BQ-1201–BQ-1205 |
| Action Hierarchy & Progressive Disclosure | 30 | `controls/30-usability-visual-finish-truth-and-quality-closure.md` | BQ-1206–BQ-1210 |
| Input & Decision Efficiency | 30 | `controls/30-usability-visual-finish-truth-and-quality-closure.md` | BQ-1211–BQ-1215 |
| Feedback & Recovery Legibility | 30 | `controls/30-usability-visual-finish-truth-and-quality-closure.md` | BQ-1216–BQ-1220 |
| Perceptual Hierarchy Finish | 30 | `controls/30-usability-visual-finish-truth-and-quality-closure.md` | BQ-1221–BQ-1225 |
| Typographic Spatial Surface Calibration | 30 | `controls/30-usability-visual-finish-truth-and-quality-closure.md` | BQ-1226–BQ-1230 |
| Document Truth Boundary Visibility | 30 | `controls/30-usability-visual-finish-truth-and-quality-closure.md` | BQ-1231–BQ-1235 |
| Evidence Assumption Sample Provenance | 30 | `controls/30-usability-visual-finish-truth-and-quality-closure.md` | BQ-1236–BQ-1240 |
| Document & Operations Responsive Detail | 30 | `controls/30-usability-visual-finish-truth-and-quality-closure.md` | BQ-1241–BQ-1245 |
| Quality Floor Measurement Calibration | 30 | `controls/30-usability-visual-finish-truth-and-quality-closure.md` | BQ-1246–BQ-1250 |


| Operational Context Resolution | 31 | `controls/31-operational-procedure-compilation-authority-and-measurement.md` | BQ-1251–BQ-1255 |
| Role & Accountability Compilation | 31 | `controls/31-operational-procedure-compilation-authority-and-measurement.md` | BQ-1256–BQ-1260 |
| Procedure Authority Classification | 31 | `controls/31-operational-procedure-compilation-authority-and-measurement.md` | BQ-1261–BQ-1265 |
| Executable Procedure Compilation | 31 | `controls/31-operational-procedure-compilation-authority-and-measurement.md` | BQ-1266–BQ-1270 |
| Decision Rights & Approval Boundaries | 31 | `controls/31-operational-procedure-compilation-authority-and-measurement.md` | BQ-1271–BQ-1275 |
| Decision Checkpoint & Stop Sequencing | 31 | `controls/31-operational-procedure-compilation-authority-and-measurement.md` | BQ-1276–BQ-1280 |
| Exception Recovery & Continuity | 31 | `controls/31-operational-procedure-compilation-authority-and-measurement.md` | BQ-1281–BQ-1285 |
| Operational Evidence & Definition of Done | 31 | `controls/31-operational-procedure-compilation-authority-and-measurement.md` | BQ-1286–BQ-1290 |
| KPI Definition & Metric Governance | 31 | `controls/31-operational-procedure-compilation-authority-and-measurement.md` | BQ-1291–BQ-1295 |
| Procedure Validation, Change & Reauthorization | 31 | `controls/31-operational-procedure-compilation-authority-and-measurement.md` | BQ-1296–BQ-1300 |

# Domain 26 Supporting Standards
<!-- id: control-index.domain-26-standards -->

When a Domain 26 capability is active, retrieve only the exact supporting `craft.*` section needed from `CRAFT.md`.

Typical mappings:

- feature depth → `craft.feature-depth`, `craft.feature-purpose-user-job`, `craft.feature-information-actions`
- state completeness → `craft.feature-state-completeness`
- front-end-only truth → `craft.frontend-only-truth`
- feature/component mapping → `craft.feature-component-mapping`
- responsive feature behavior → `craft.responsive-feature-recomposition`
- accessibility → `craft.feature-accessibility`
- icon system/coverage → `craft.icon-system-selection`, `craft.iconography-coverage`, `craft.icon-detail`
- component anatomy/cards/surfaces → `craft.component-anatomy`, `craft.card-specificity`, `craft.surface-elevation`
- affordance/detail → `craft.micro-detail`, `craft.affordance-audit`
- dashboard craft → `craft.dashboard-craft`
- final acceptance → `craft.production-craft-acceptance-gate`, `craft.critical-failures`

# Domain 27 Supporting Standards
<!-- id: control-index.domain-27-standards -->

- artifact contract → `ARTIFACT_CONTRACTS.md` → exact `contracts/*.md`
- feature compilation → `FEATURE_COMPILER.md`, `schemas/feature_spec.schema.json`
- component compilation → `COMPONENT_COMPILER.md`, `schemas/component_spec.schema.json`
- structural fingerprint / genericity → `GENERICITY.md`, `schemas/structural_fingerprint.schema.json`, `evals/generic_template_fingerprints.json`

# Domain 28 Supporting Standards
<!-- id: control-index.domain-28-standards -->

- adversarial reviewers / repair → `CRITICS.md`, `schemas/critique_report.schema.json`
- quality floors → `QUALITY_FLOORS.md`, active artifact contract
- efficacy benchmark → `BENCHMARKS.md`, `benchmarks/*`, benchmark tools
- final acceptance → `schemas/artifact_acceptance.schema.json`, `QA_GATES.md`

# Registry Precedence
<!-- id: control-index.registry-precedence -->

For control-plane addressing and counts, `CONTROL_INDEX.md`, `CONTROL_MANIFEST.md`, and the logical machine registry are authoritative. Legacy count summaries in older 4.0 module snapshots are informational and MUST NOT override the canonical registry.

Stable IDs remain the authoritative addresses. Do not infer IDs from file order.

# Domain 29 Supporting Standards
<!-- id: control-index.domain-29-standards -->

Route mobile/data transformation to `RESPONSIVE_COMPOSITION.md`; documents to `DOCUMENT_CRAFT.md`; accessibility proof to `ACCESSIBILITY_EVIDENCE.md`; mandatory coverage to `COMPLETENESS.md`; product depth to `FEATURE_DEPTH.md`. Re-run genericity after repairs.


# Domain 30 Supporting Standards
<!-- id: control-index.domain-30-standards -->

- task-path usability → `USABILITY_CLOSURE.md`, `schemas/usability_evidence.schema.json`
- rendered final finish → `VISUAL_FINISH.md`, `schemas/visual_finish_evidence.schema.json`
- truth/provenance boundaries → `TRUTH_BOUNDARIES.md`, `schemas/truth_boundary.schema.json`
- document/operations narrow-viewport detail → `RESPONSIVE_DETAIL_CLOSURE.md`, `schemas/responsive_detail_evidence.schema.json`
- score/floor calibration → `QUALITY_MEASUREMENT.md`, `schemas/quality_measurement.schema.json`
- after repairs, rerun genericity, truth, responsive/accessibility, implementation, and active quality floors.

# Domain 31 Supporting Standards
<!-- id: control-index.domain-31-standards -->

**Domain 23/31 specialization rule:** Domain 23 proves baseline operating coverage. Domain 31 compiles the production-detail object for material procedures, decisions, evidence, recovery, handoffs, and KPI definitions. When both are active, satisfy the shared concept once using the stricter Domain 31 structure rather than emitting duplicate SOP/evidence/KPI/handoff objects.

- role/task/context and executable SOP compilation → `OPERATIONAL_PROCEDURE_COMPILER.md`, `schemas/operational_procedure.schema.json`
- authority/provenance/currentness → `PROCEDURE_AUTHORITY.md`, `schemas/procedure_authority.schema.json`
- MAY/MUST/MUST NOT/approval/stop boundaries → `DECISION_RIGHTS.md`, `schemas/decision_rights.schema.json`
- evidence, handoff, exception record, definition of done → `OPERATIONAL_EVIDENCE.md`, `schemas/operational_evidence.schema.json`
- KPI formulas, ownership, target provenance, balancing measures → `KPI_GOVERNANCE.md`, `schemas/kpi_definition.schema.json`
- use `JOBS.md` and exact `operations/*.md` sections as baseline context, not as proof of procedure authority.
- validate compiled procedure JSON with `tools/validate_operational_procedure.py`; execute Domain 31 behavioral fixtures with `tools/test_operations_2.py`.
