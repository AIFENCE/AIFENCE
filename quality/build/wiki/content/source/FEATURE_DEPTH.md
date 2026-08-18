<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: FEATURE_DEPTH
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->

# Feature Depth Closure
<!-- id: feature-depth.root -->

Purpose: ensure important capabilities behave like finished product features rather than visible nouns.

# Depth Ladder
<!-- id: feature-depth.ladder -->
0 Mentioned; 1 visible shell; 2 basic happy-path function; 3 product-defined information/actions; 4 state/recovery/responsive/accessibility complete; 5 decision/workflow integrated with dependencies, evidence, and acceptance. Production P0/P1 app/workflow features target Level 5. Documents use the equivalent `DOCUMENT_CRAFT.md` decision-depth model.

# State Closure
<!-- id: feature-depth.state-closure -->
Resolve only applicable states, but do so explicitly. Empty and filtered-empty are distinct when they imply different recovery; loading and stale/offline are distinct when freshness affects decisions; permission/unavailable is distinct from error; destructive actions require confirmation/recovery semantics.

# Action Closure
<!-- id: feature-depth.action-closure -->
Primary action, secondary actions, contextual actions, bulk actions, and destructive actions need hierarchy, availability rules, feedback, and post-action state. A visible button without resulting product state does not count as depth.

# Dependency Closure
<!-- id: feature-depth.dependency-closure -->
Identify data source/persistence, permissions, integrations, upstream/downstream feature dependencies, and front-end-only simulation boundaries. Unavailable dependencies must alter behavior/truth claims rather than being ignored.

# Depth Evidence
<!-- id: feature-depth.evidence -->
For each P0/P1 feature, record the user job, level reached, missing dimensions, critical states exercised, responsive transformation, accessibility evidence, dependencies, and acceptance result. Use `schemas/feature_depth_evidence.schema.json` when structured.

# Revision 1.4 Depth-to-Usability Closure
<!-- id: feature-depth.usability-closure -->
Level-5 depth requires not only more information/actions/states but a coherent priority model. Penalize feature depth that increases cognitive load through duplicated actions, uncontrolled metadata, or state abundance without clear orientation. Deep features should make complex work more legible, not merely expose more controls.
# B2B Decision-Journey Depth
<!-- id: feature-depth.b2b-decision-journey -->

For complex-consideration B2B marketing artifacts, feature depth is not satisfied by a polished feature catalog plus a contact CTA. The artifact must help a buyer **make and advance a decision**.

Compile at least two P0/P1 decision paths when the audience/business model involves enterprise, procurement, technical evaluation, implementation risk, or multi-stakeholder purchase. Each path must connect:

`buyer decision → relevant information/evidence → fit or qualification signal → objection/risk handling → next action → downstream state/expectation`

At least one path SHOULD address evaluation/fit and at least one SHOULD address adoption, implementation, security/integration, procurement, or another material buying risk when applicable. Proof may be verified evidence, supplied proof, transparent sample/demo evidence, or an explicit unknown boundary; do not fabricate customer outcomes.

Feature-depth PASS requires the paths to be represented in the actual artifact through appropriate interactions/content structures, not merely written in a planning note. Use `schemas/decision_depth_evidence.schema.json` and `tools/validate_decision_depth_evidence.py`.

# B2B Depth Recovery
<!-- id: feature-depth.b2b-depth-recovery -->

When B2B depth fails, repair the buyer journey rather than adding more feature cards. Typical repairs include fit/qualification tools, role-specific paths, technical/integration evaluation, comparison/selection aids, implementation sequence, risk/objection handling, ROI/value-model boundaries, procurement/security readiness, or a more explicit handoff/next-step state. Preserve truth boundaries and avoid invented proof.
# Payments & Analytics Level-5 Depth Closure
<!-- id: feature-depth.payments-analytics-level-5 -->

For payments/transaction operations artifacts, P0/P1 Level-5 depth requires an end-to-end operational loop containing: `find/filter/segment → inspect transaction → understand status/risk/context → take or simulate an allowed action → observe result/feedback → recover/continue`. The artifact must expose enough status/history/evidence to make the action intelligible; a transaction table plus detail drawer is not sufficient by itself.

For analytics/decision dashboards, P0/P1 Level-5 depth requires: `decision/question → evidence/source context → comparison/segmentation → interpretation/guardrail → inspect/drill-down → next action/handoff → continued state`. Metric cards, charts, and a table without this reasoning/action loop remain below Level 5 even when polished.

For both families, evidence MUST identify at least three P0/P1 features at Level 5, including one investigation/inspection feature, one decision/action or recovery feature, and one continuity/comparison feature. Responsive and accessibility closure are part of Level 5, not separate optional bonuses. Use `dense_product_quality_evidence.schema.json` for this benchmark-derived gate.

