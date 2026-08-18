<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: FEATURE_COMPILER
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Feature Specification Compiler
<!-- id: feature-compiler.root -->

Purpose: compile high-value features into an implementation-ready product contract **before** detailed visual/component design.

# Trigger
<!-- id: feature-compiler.trigger -->

Full compilation is mandatory when a feature is a primary user job/conversion path, primary-navigation capability, frequent workflow, data mutation, permission/payment/security/privacy/compliance-sensitive behavior, destructive action, decision-critical flow, major source of edge states, or materially transformed on mobile.

# Compilation Schema
<!-- id: feature-compiler.schema -->

Compile applicable fields:

```text
Feature ID
Name
Purpose
User Job
Priority
Entry Point
Preconditions
Information / Data
Primary Action
Secondary Actions
Contextual Actions
Interaction Model
Default / Loading / Partial
Empty / Filtered-Empty / No-Results
Error / Recovery
Success / Confirmation
Disabled / Unavailable
Permission / Offline
Destructive Confirmation
Validation
Responsive Strategy
Keyboard Behavior
Accessibility Semantics
Visual Treatment
Iconography
Contextual Help
Truth / Sample / Backend Semantics
Dependencies
Analytics / Audit Need when applicable
Acceptance Criteria
Evidence Plan
Buyer Decision / Evaluation Question when B2B complex-consideration
Evidence / Proof Needed for that Decision
Fit / Qualification Signal
Objection / Risk Handling
Downstream State / Expectation
```

Machine-readable implementations SHOULD conform to `schemas/feature_spec.schema.json`.

# Procedure
<!-- id: feature-compiler.procedure -->

1. Read the selected artifact contract.
2. Identify high-value features from user jobs rather than page/component names.
3. Split overly broad nouns into real workflows.
4. Resolve information and actions before choosing a component pattern.
5. Resolve applicable states and recovery.
6. Resolve truth/back-end semantics.
7. Resolve responsive/accessibility behavior.
8. Define observable acceptance criteria.
9. Only then hand the feature to concept/component design.

# Self-Defining Noun Guard
<!-- id: feature-compiler.self-defining-guard -->

`dashboard`, `search`, `filters`, `analytics`, `services`, `gallery`, `booking`, `checkout`, `profile`, `notifications`, `FAQ`, `map`, `transactions`, `customers`, `settings`, and `reports` are not complete feature definitions.

# Acceptance
<!-- id: feature-compiler.acceptance -->

A high-value feature fails compilation when implementation still requires invention of purpose, data, action hierarchy, state behavior, responsive transformation, accessibility behavior, truth semantics, or completion criteria.

# Revision 1.3 Depth Handoff
<!-- id: feature-compiler.depth-handoff -->
P0/P1 features additionally produce `FEATURE_DEPTH.md` closure evidence and `COMPLETENESS.md` coverage rows. Responsive strategies must reference the mobile priority/data transformation model from `RESPONSIVE_COMPOSITION.md`.


# Revision 1.4 Usability Closure Fields
<!-- id: feature-compiler.usability-closure -->
For P0/P1 features, additionally compile: Entry/Orientation Cue; Required Decisions; Required Inputs; Primary Action; Secondary/Contextual/Destructive Actions; State Preservation; Success Feedback; Error/Recovery; Keyboard/Touch Completion; Avoidable Friction Risks; Truth/Provenance Boundary. Feature closure is incomplete when behavior exists but the primary task path remains ambiguous or unnecessarily costly.


# Interaction-Closure Handoff
<!-- id: feature-compiler.interaction-handoff -->

For substantial interactive artifacts, assign a stable local task ID to every compiled P0/P1 user job/workflow and hand those IDs to the interaction-closure manifest. The manifest task set MUST cover every P0/P1 completion-ledger entry; responsive QA may not omit a task merely because its desktop surface is difficult to adapt. Feature-level controls/actions that render enabled MUST also hand off an expected observable behavior to component/interaction compilation.

# B2B Decision-Depth Handoff
<!-- id: feature-compiler.b2b-decision-handoff -->

When the context graph resolves B2B/enterprise/procurement or another complex-consideration buyer journey, compile at least two decision paths and hand them to `FEATURE_DEPTH.md` decision-depth evidence before acceptance. Feature nouns alone do not count as buyer decision support.
