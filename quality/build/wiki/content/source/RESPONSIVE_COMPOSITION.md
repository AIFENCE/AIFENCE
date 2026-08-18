<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: RESPONSIVE_COMPOSITION
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-09
-->

# Responsive Composition Hardening
<!-- id: responsive-composition.root -->

Purpose: eliminate desktop-compression masquerading as responsive design.

# Viewport Evidence Matrix
<!-- id: responsive-composition.viewport-matrix -->
For substantial product UI, validate at minimum 320, 390, 768, and a representative desktop width. A viewport passes only when the primary task remains complete without uncontrolled page-level horizontal overflow, clipped primary actions, overlapping sticky/fixed UI, or unreadable information density.

# Mobile Priority Map
<!-- id: responsive-composition.priority-map -->
Before CSS implementation, classify information/actions as P0 task-critical, P1 frequent, P2 supporting, or P3 deferrable. Mobile transformation must preserve P0/P1 access while progressively disclosing lower-priority detail. Hiding is not a valid transformation when it removes required task context.

# Dense Control Compression
<!-- id: responsive-composition.control-compression -->
Search, filters, date ranges, view switches, bulk actions, and primary CTAs MUST NOT compete in one narrow toolbar. Resolve them into an intentional mobile model such as primary action + search + filter sheet, segmented disclosure, bottom sheet, overflow menu, or task-specific drawer. Touch targets, labels, focus order, and current filter state remain evident.

# Data Transformation
<!-- id: responsive-composition.data-transformation -->
Tables and dense lists require an explicit narrow-screen strategy: priority columns + row detail, semantic horizontal scrolling with persistent context, stacked labeled values, responsive comparison mode, or alternate detail view. Merely setting a large `min-width` is insufficient when the critical task cannot be completed comfortably.

# Sticky Collision Guard
<!-- id: responsive-composition.sticky-collision-guard -->
Fixed bottom navigation, sticky headers, drawers, cookie/consent UI, primary actions, and virtual keyboards must not occlude one another or critical content. Reserve safe-area space and test focus/scroll behavior.

# Responsive Acceptance
<!-- id: responsive-composition.acceptance -->
PASS requires rendered geometry evidence at the viewport matrix, preserved task completion, intentional control/data transformation, and no material overflow/clipping. Source media queries alone are not evidence.

# Revision 1.4 Detail Closure
<!-- id: responsive-composition.detail-closure -->
After macro recomposition passes, apply `RESPONSIVE_DETAIL_CLOSURE.md` to responsive documents and operations artifacts. Page-level overflow alone cannot prove success; verify task-level label/value relationships, long-content behavior, sticky/overlay collisions, and preservation of owner/status/evidence/action context at 320, 390, 768, and desktop as applicable.
