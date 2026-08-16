<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: COMPONENT_COMPILER
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Component Design Compiler
<!-- id: component-compiler.root -->

Purpose: translate compiled feature requirements into intentionally designed component systems after feature behavior is known.

# Trigger
<!-- id: component-compiler.trigger -->

Compile important reusable or high-frequency components: navigation, forms, tables/lists, cards, metrics, statuses, search/filter controls, dialogs/drawers, product/service representations, proof modules, workflow objects, and high-value actions.


## Control Behavior Contract
<!-- id: component-compiler.control-behavior-contract -->

Any anatomy that renders as interactive MUST declare its behavior, state change/navigation outcome, feedback, disabled semantics, and responsive availability before implementation. Do not emit visually interactive chrome merely because a familiar component pattern usually contains it. Overflow triggers, period/date selectors, nav tabs, filters, row menus, export buttons, sort controls, and contextual actions require compiled behavior or explicit omission.

For task-critical components, the variant matrix MUST include the narrow-screen equivalent. A desktop-only detail/editor/recovery child cannot simply be removed from the mobile variant when a P0/P1 task depends on it.

# Compilation Schema
<!-- id: component-compiler.schema -->

```text
Component ID
Role / User Job Supported
Source Feature IDs
Content Anatomy
Information Priority
Typography Roles
Iconography
Metadata
Primary / Secondary / Contextual Actions
Surface / Elevation
Borders / Radius
Density
Default / Hover / Focus / Pressed / Selected
Disabled / Loading / Empty / Error / Success / Validation
Truncation / Wrapping / Overflow
Responsive Adaptation
Keyboard Behavior
Accessible Name / Semantics
Motion / Feedback
Invalid Combinations
Variants
Acceptance Criteria
Evidence Plan
```

Machine-readable implementations SHOULD conform to `schemas/component_spec.schema.json`.

# Anatomy Rule
<!-- id: component-compiler.anatomy-rule -->

A component is not complete merely because it has a border, radius, padding, title, and description. Anatomy must follow task and information. Functionally different content SHOULD NOT inherit identical anatomy solely for implementation convenience.

# Variant & State Matrix
<!-- id: component-compiler.variant-state-matrix -->

For components with variants or multiple states, define a matrix that makes invalid combinations explicit and prevents accidental divergence.

# Iconography Rule
<!-- id: component-compiler.iconography -->

Use the resolved professional icon system consistently when icons improve recognition, scanning, status, or affordance. Icon-only actions require accessible names.

# Handoff
<!-- id: component-compiler.handoff -->

Component compilation consumes feature specifications and design direction. It must not silently change feature behavior to fit a convenient component library.

# Narrow-Screen Variant Requirement
<!-- id: component-compiler.narrow-screen-variant -->
Dense controls and data components define explicit 320/390 behavior, including wrapping/disclosure priority, touch targets, overflow policy, focus order, and sticky-layer interaction. “Same component, smaller” is not an accepted mobile variant when task density changes.


# Revision 1.4 Final-Finish Fields
<!-- id: component-compiler.final-finish -->
For important interactive components, resolve action priority, progressive-disclosure rationale, focus/touch efficiency, label clarity, feedback/recovery behavior, optical alignment, typographic role, surface purpose, and narrow-viewport long-content behavior. Reusable anatomy must preserve task clarity rather than merely visual consistency.
