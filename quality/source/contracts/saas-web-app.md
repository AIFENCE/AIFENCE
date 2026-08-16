<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: ARTIFACT_CONTRACT
Contract: SaaS Web App
Module-Version: 2
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# SaaS / Web App Production Contract
<!-- id: contract.artifact.saas-web-app -->

## User Jobs
<!-- id: contract.artifact.saas-web-app.user-jobs -->
Users should complete high-value workflows efficiently, understand system state, recover from failure, and distinguish real functionality from demo/front-end simulation.

## Required Product Model
<!-- id: contract.artifact.saas-web-app.product-model -->
Resolve shell assumptions, entities, primary user jobs/workflows, navigation, search/filter/sort where relevant, CRUD semantics, permissions, data freshness/persistence, key states, help/feedback, and backend dependencies.

## Interaction Contract
<!-- id: contract.artifact.saas-web-app.interaction -->
High-value workflows compile into explicit information/actions/states before components are chosen. Do not use one card grammar for unrelated workflows.

## Responsive Contract
<!-- id: contract.artifact.saas-web-app.responsive -->
Desktop productivity patterns may transform into drawers, bottom navigation, condensed lists, progressive disclosure, sticky task actions, alternate data presentation, or full-screen mobile detail/edit routes. Merely stacking the desktop shell is insufficient, and hiding a task-critical detail/edit/recovery pane without an equivalent path is prohibited.

## Accessibility Contract
<!-- id: contract.artifact.saas-web-app.accessibility -->
Keyboard completion, focus management, accessible names, dialog/disclosure semantics, data semantics, status announcements, and validation communication are required where applicable.

## Truth Contract
<!-- id: contract.artifact.saas-web-app.truth -->
Sample data and simulated auth/payments/persistence/integrations must be clearly distinguished from real backend behavior.

## Evidence
<!-- id: contract.artifact.saas-web-app.evidence -->
Verify representative happy paths plus empty/error states, exhaustive no-dead-control behavior, keyboard-critical flows, responsive recomposition, runtime/broken paths, rendered craft, and direct 320/390 completion of every declared P0/P1 task.


## Mobile Composition Evidence
<!-- id: contract.artifact.saas-web-app.mobile-composition -->
Use `RESPONSIVE_COMPOSITION.md` and `RESPONSIVE_DETAIL_CLOSURE.md`. Validate dense controls/data at 320 and 390 px; toolbars must transform rather than compress, and every P0/P1 task must remain complete. For list/detail/edit workspaces, preserve selection, edit/save/cancel/validation, recovery, and return context through an equivalent mobile surface.

## Completion & Depth Evidence
<!-- id: contract.artifact.saas-web-app.completion-depth -->
Use `COMPLETENESS.md` and `FEATURE_DEPTH.md` for every P0/P1 workflow before acceptance.

## Acceptance Profile
<!-- id: contract.artifact.saas-web-app.acceptance -->
Use `quality-floors.profile.saas-web-app`. Feature depth, usability, accessibility, responsiveness, and implementation correctness are release-blocking.
