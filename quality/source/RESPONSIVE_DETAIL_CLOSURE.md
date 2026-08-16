<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: RESPONSIVE_DETAIL_CLOSURE
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->

# Responsive Detail Closure — Documents & Operations
<!-- id: responsive-detail.root -->

Purpose: close narrow-viewport defects that remain after macro responsive recomposition has already passed.


## P0/P1 Task-Preservation Invariant
<!-- id: responsive-detail.task-preservation-invariant -->

For interactive artifacts, responsive transformation MUST preserve capability, not merely content. Build a task ledger before responsive implementation and map every P0/P1 desktop task to a 320/390 equivalent. The narrow-screen path MUST preserve task entry, required information, primary/secondary actions, relevant state, validation/feedback, recovery, and a predictable return/orientation path.

A desktop split pane, side drawer, inspector, transaction detail, editable properties pane, recovery surface, or contextual-action rail may become a full-screen route, bottom sheet, modal/drawer, inline disclosure, or staged mobile flow. It MUST NOT be hidden or removed when that surface is required to complete a declared P0/P1 task. CSS such as `display:none`, conditional omission, or breakpoint-only removal is a release failure unless an equivalent task path is directly evidenced.

## Dense List/Detail and Edit Transformation
<!-- id: responsive-detail.list-detail-edit -->

For list/detail, queue/detail, table/inspector, dashboard/drill-down, or editor/property-pane patterns:

- preserve the selected entity and list/filter/sort context when entering mobile detail;
- preserve inspect → act/recover and edit → validate → save/cancel flows;
- provide an explicit return path that restores orientation/focus where applicable;
- preserve unsaved/recoverable state across mobile disclosures when technically applicable;
- keep task-critical overflow/menu actions reachable rather than deleting them at the breakpoint;
- if a desktop secondary pane is task-critical, provide a mobile replacement surface with equivalent semantics.

## Mobile Task Evidence Ledger
<!-- id: responsive-detail.mobile-task-ledger -->

For every declared P0/P1 task, evidence at both 320 and 390 px MUST identify: task ID; entry affordance; equivalent mobile surface; completion affordance; preserved state/context; recovery status; observed result. Missing task rows are not PASS. A page-wide no-overflow check cannot substitute for this ledger.

# Document Detail Recomposition
<!-- id: responsive-detail.documents -->

For responsive digital documents, explicitly test and transform:

- decision/action tables;
- timelines;
- risk matrices;
- comparison tables;
- evidence callouts and side notes;
- long URLs, identifiers, citations, and code-like tokens;
- figures/captions;
- footnotes/endnotes;
- table of contents and in-page anchors;
- multi-column editorial treatments.

At narrow widths, preserve the semantic relationship between labels and values. Do not merely hide columns or allow unreadable scale reduction.

# Operations Detail Recomposition
<!-- id: responsive-detail.operations -->

Operational workflows MUST preserve status, owner, evidence, exception, dependency, and primary action context at 320/390px. Transform kanban/swimlane, queue, exception, audit, and handoff structures into an interaction model suited to narrow screens rather than horizontal clipping.

# Long-Content Stress Test
<!-- id: responsive-detail.long-content -->

Use representative worst-case content during QA: long translated labels, long names, multi-word statuses, high digit counts, identifiers, validation text, evidence notes, and expanded helper copy. Truncated text MUST retain a discoverable full-value path when the omitted content matters to the task.

# Sticky / Fixed / Overlay Collision Audit
<!-- id: responsive-detail.collision-audit -->

At 320, 390, 768, and desktop where applicable, verify that sticky navigation, bottom bars, drawers, dialogs, cookie/consent layers, floating actions, and virtual keyboards do not cover focus, validation, content, or primary actions.

# Responsive Detail Evidence
<!-- id: responsive-detail.evidence -->

Record viewport-specific evidence for each critical dense structure:

```text
Viewport
Structure
Task-critical fields/actions preserved
Overflow behavior
Wrap/truncation behavior
Sticky/overlay collision
Keyboard/focus visibility
Transformation used
PASS / FAIL / UNVERIFIED
```

# Acceptance
<!-- id: responsive-detail.acceptance -->

A page-level `scrollWidth == viewportWidth` check is insufficient. Responsive-detail PASS requires task-level evidence for the dense document/operations structures and interactive P0/P1 workflows actually present. For interactive artifacts, every declared P0/P1 task must PASS at both 320 and 390 px; any hidden-without-equivalent task-critical surface blocks responsive/usability/implementation acceptance.
