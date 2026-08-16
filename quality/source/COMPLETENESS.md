<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: COMPLETENESS
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->

# Completion Coverage Ledger
<!-- id: completeness.root -->

Purpose: make omissions visible before they become polished but incomplete artifacts.

# Coverage Dimensions
<!-- id: completeness.dimensions -->
Track applicable coverage for: user jobs, entry points, information/data, primary/secondary/contextual actions, happy paths, empty/no-results, loading/partial/stale/offline, errors/recovery, permissions/unavailable, destructive confirmation, validation, success/confirmation, responsive transformations, accessibility evidence, truth/backend semantics, dependencies, content/proof needs, and final acceptance evidence.

# Priority Closure
<!-- id: completeness.priority-closure -->
Every P0/P1 requirement must be PASS or explicitly UNVERIFIED with a release consequence. Optional P2/P3 omissions may be accepted only when the artifact contract still passes. A raw feature count cannot compensate for one missing critical path.

# Cross-Surface Closure
<!-- id: completeness.cross-surface -->
When the same task spans navigation, list/table, detail, form/dialog, confirmation, mobile, or document sections, the ledger follows the user job across those surfaces. “The component exists” is not task completion.

# Completion Evidence
<!-- id: completeness.evidence -->
Each mandatory row identifies requirement/source, implementation location, state/viewport, verification method, result, and recovery issue when failed. Machine-readable ledgers SHOULD use `schemas/completeness_ledger.schema.json`.

# Acceptance
<!-- id: completeness.acceptance -->
Substantial production work fails completeness when a P0/P1 row is missing, silently omitted, falsely marked N/A, or implemented without the required state/viewport/evidence closure.

# Revision 1.4 Completion Additions
<!-- id: completeness.usability-truth-closure -->
P0/P1 completion rows additionally record usability path closure and material truth/provenance status. A feature is not complete merely because its states exist if the user cannot identify the next action/recovery path or if sample/unknown/recommendation content can be mistaken for verified fact.


# Interaction Ledger Parity
<!-- id: completeness.interaction-ledger-parity -->

For substantial interactive artifacts, the interaction-closure manifest's P0/P1 task IDs MUST be a complete mapping of the P0/P1 completion ledger. Missing IDs block completion even if the smaller submitted manifest itself validates. When browser/runtime execution exists, control discovery evidence MUST also reconcile the actual enabled visible control inventory against the manifest so an omitted rendered control cannot silently evade the no-dead-control gate.
# Dense-Product First-Pass Completion Matrix
<!-- id: completeness.dense-product-first-pass -->

For high-fidelity SaaS/dashboard/portal artifacts, every P0/P1 feature MUST close the following applicable columns before acceptance: `entry/orientation`, `information/evidence`, `primary action`, `contextual action`, `normal`, `empty/no-results`, `loading/partial/stale` where data freshness exists, `error/recovery`, `permission/unavailable` where access exists, `success/feedback`, `detail/drill-down`, `responsive 320/390`, `accessibility`, `truth/data semantics`, `dependency`, and `acceptance evidence`.

The completion gate is exhaustive rather than sample-based. An applicable column may be marked N/A only with an explicit reason grounded in the artifact contract/user job. Missing or silently omitted applicable coverage makes the feature and artifact NON-PASS. For dense-product release evidence use `dense_product_quality_evidence.schema.json` in addition to the general completion ledger.

