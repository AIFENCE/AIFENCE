<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: ACCESSIBILITY_EVIDENCE
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->

# Accessibility Evidence System
<!-- id: accessibility-evidence.root -->

Purpose: replace inferred accessibility quality with observable completion evidence.

# Evidence Matrix
<!-- id: accessibility-evidence.matrix -->
For each critical path record: semantic structure; accessible names/labels; keyboard reachability; visible focus; logical focus order; dialog/drawer focus entry/return; validation/error association; status/live feedback; non-color meaning; contrast/readability; target size/spacing; zoom/reflow; responsive order; table/list semantics; and reduced-motion behavior when motion is material.

# Keyboard Critical-Path Test
<!-- id: accessibility-evidence.keyboard-path -->
A critical path PASS requires completion using keyboard input alone when the platform supports keyboard interaction. Inspect focus visibility, order, traps, offscreen focus, destructive-action safeguards, and post-action focus placement.

# Dynamic Feedback Test
<!-- id: accessibility-evidence.dynamic-feedback -->
Errors, saves, filtering/no-results, async loading/completion, offline/retry, cart/checkout changes, and other material state changes require programmatically determinable feedback where applicable. Visible text alone is insufficient when assistive technology would not receive the update.

# Evidence Precedence
<!-- id: accessibility-evidence.precedence -->
Automated checks may find defects but cannot prove accessibility alone. Direct keyboard/zoom/reflow/state evidence outranks static source inference. Missing required evidence is UNVERIFIED.

# Accessibility Acceptance
<!-- id: accessibility-evidence.acceptance -->
No critical path may PASS accessibility with unlabeled controls, keyboard-incomplete primary actions, invisible focus, trapped focus, material color-only state, unassociated errors, or unresolved zoom/reflow failure.

# Revision 1.4 Usability Link
<!-- id: accessibility-evidence.usability-link -->
Accessibility evidence and usability evidence overlap but are not interchangeable. Keyboard completion, focus return, error association, status feedback, touch-target behavior, and reflow evidence SHOULD be reused by `USABILITY_CLOSURE.md` where applicable rather than duplicated or inferred.
# Dense-Product First-Pass Accessibility Closure
<!-- id: accessibility-evidence.dense-product-first-pass -->

For every P0/P1 dense-product workflow, direct evidence MUST demonstrate:

- all enabled controls in the path have accessible names and meaningful roles;
- keyboard-only completion where the platform supports keyboard interaction;
- visible focus for exercised controls plus logical order and focus return after drawers/dialogs/detail transitions;
- programmatically determinable feedback for save, filter, retry, failure, loading/completion, or other material dynamic state;
- status/selection/error meaning is not color-only;
- interactive targets and adjacent spacing are usable at 320/390 and text remains readable without horizontal page scrolling;
- table/list/detail relationships remain semantically understandable after narrow-screen transformation;
- errors are associated with the affected input/action and recovery remains reachable.

Static HTML semantics or an automated checker without critical-path execution cannot satisfy this gate. Use the accessibility section of `dense_product_quality_evidence.schema.json`; missing direct evidence remains UNVERIFIED.


# Fixed-Document Direct Accessibility Evidence
<!-- id: accessibility-evidence.fixed-document -->

Fixed-format documents require direct reading-order and table-order inspection plus readable contrast, navigable links when present, heading/structure evidence, zoom or magnification verification, and alt-text evidence or an explicit not-applicable determination. Text extraction alone cannot prove document accessibility. Rendered collision/clipping defects are accessibility failures as well as visual-quality failures.
