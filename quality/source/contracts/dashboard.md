<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: ARTIFACT_CONTRACT
Contract: Dashboard
Module-Version: 2
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Dashboard Production Contract
<!-- id: contract.artifact.dashboard -->

## User Jobs
<!-- id: contract.artifact.dashboard.user-jobs -->
A dashboard must help a user monitor, compare, investigate, prioritize, and act. It is not a collection of decorative metric cards.

## Information & Data Contract
<!-- id: contract.artifact.dashboard.data -->
Resolve decisions/monitoring tasks, metric definitions/time context, numeric alignment, tables/lists versus summaries, statuses, search/filter/sort/date controls, drill-down/detail, contextual actions, selection/bulk behavior when useful, export when meaningful, and freshness/sample-data semantics.

## Dense UI Contract
<!-- id: contract.artifact.dashboard.density -->
Prefer scan-efficient lists/tables, aligned numbers, restrained surfaces, progressive disclosure, contextual actions, and clear state encoding. Do not flatten operational data into universal cards.

## State Contract
<!-- id: contract.artifact.dashboard.states -->
Loading, partial, no data, filtered-empty/no-results, stale, error, selected, permission/unavailable, and success states must be considered where applicable.

## Responsive Contract
<!-- id: contract.artifact.dashboard.responsive -->
Determine column priority, table transformation, horizontal-overflow policy, compact filters, mobile navigation, chart adaptation, sticky actions, and touch behavior. Preserve every P0/P1 monitor → investigate → act/recover path; task-critical drill-down/detail or recovery surfaces may transform but may not disappear at 320/390.

## Evidence
<!-- id: contract.artifact.dashboard.evidence -->
Inspect rendered desktop/mobile, populated and empty/error states, filter/search behavior, row actions, numeric alignment, overflow, keyboard usability, runtime integrity, exhaustive enabled-control behavior, and the declared P0/P1 task ledger at both 320 and 390 px.


## Mobile Investigation Contract
<!-- id: contract.artifact.dashboard.mobile-investigation -->
At 320/390 px preserve monitor → investigate → act/recover end-to-end. Search/filter/date/view/period/overflow controls must use a deliberate compressed interaction model and remain behaviorally live. Tables/charts require a task-preserving narrow-screen transformation. A desktop transaction/detail/recovery inspector must become an equivalent mobile route, sheet, drawer, or disclosure rather than being hidden.

## Completion & Accessibility Evidence
<!-- id: contract.artifact.dashboard.completion-accessibility -->
Use `COMPLETENESS.md`, `FEATURE_DEPTH.md`, and `ACCESSIBILITY_EVIDENCE.md` for critical monitoring/investigation/action paths.

## Acceptance Profile
<!-- id: contract.artifact.dashboard.acceptance -->
Use `quality-floors.profile.dashboard`. Feature depth, usability, responsiveness, implementation correctness, and genericity resistance are strict floors.
