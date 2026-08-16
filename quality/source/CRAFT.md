<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: CRAFT
Module-Version: 1
Last-Updated: 2026-08-09
-->

# Feature & Component Craft Standards
<!-- id: craft.root -->

Purpose: raise substantial websites, dashboards, SaaS products, portals, ecommerce experiences, and application interfaces from strong macro composition to premium feature-level and component-level execution.

This module is a native BizIQ domain standard used by Domain 26 of the standard control plane. It complements `CREATIVE.md`, `DESIGN.md`, `FEATURES.md`, `STRUCTURE.md`, and accessibility/engineering controls; it does not replace them.

Use `CONTROL_INDEX.md` to resolve the exact Domain 26 capability sections required for the current task. Do not preload this entire module when one exact `craft.*` section is sufficient.

# Craft Quality Principle
<!-- id: craft.quality-principle -->

A high-quality interface must succeed at both levels:

1. **Feature craftsmanship** — important capabilities feel intentionally product-designed.
2. **Component craftsmanship** — visible elements feel intentionally finished.

The target sequence is:

```text
Requirement
→ User Job
→ Feature Purpose
→ Information + Actions
→ Interaction Model
→ States
→ Visual Treatment
→ Component Anatomy
→ Iconography
→ Micro-Detail
→ Responsive Recomposition
→ Implementation
→ Rendered Evidence
```

Do not jump directly from a feature noun to a generic component.

# Feature Depth Standard
<!-- id: craft.feature-depth -->

A substantial feature MUST be specified deeply enough that implementation does not depend on generic assumptions.

For high-value features, resolve as applicable:

- purpose;
- user job;
- priority;
- entry point;
- information shown;
- primary action;
- secondary actions;
- contextual actions;
- interaction model;
- default state;
- loading state;
- empty state;
- filtered-empty/no-results state;
- partial-data state;
- error state;
- success state;
- disabled/unavailable state;
- destructive behavior;
- validation and recovery;
- responsive behavior;
- keyboard behavior;
- accessibility semantics;
- visual/component treatment;
- iconography where useful;
- contextual help where useful;
- data/truth semantics;
- front-end-only simulation behavior;
- dependencies;
- observable acceptance criteria.

A feature name alone is not sufficient.

Terms such as `dashboard`, `search`, `filters`, `analytics`, `services`, `gallery`, `booking`, `checkout`, `profile`, `notifications`, `contact form`, `FAQ`, `map`, `reports`, `transactions`, `customers`, and `settings` MUST NOT be treated as self-defining.

# Feature Quality Ladder
<!-- id: craft.feature-quality-ladder -->

Use this internal quality model:

- **Level 1 — Mentioned:** feature name only. Not acceptable for important production features.
- **Level 2 — Functional:** basic happy-path behavior. Still shallow for high-value features.
- **Level 3 — Product-defined:** purpose, user job, information, actions, interaction, states, mobile, accessibility, and feedback. Production baseline.
- **Level 4 — Refined:** Level 3 plus progressive disclosure, contextual actions, iconography, density, truncation, keyboard efficiency, motion, cross-feature relationships, microcopy, responsive recomposition, and evidence-backed acceptance. Premium target.

High-value production features SHOULD target Level 4.

# Feature Purpose & User Job
<!-- id: craft.feature-purpose-user-job -->

Every high-value feature should answer:

- Why does this exist?
- What outcome is the user trying to achieve?
- What uncertainty, task, or decision does it resolve?
- What should be easier after using it?

Examples:

`FAQ` should resolve meaningful objections or recurring questions rather than fill a template slot.

`Search` should help a user locate a meaningful target quickly enough to continue a real task.

`Services` should help a visitor understand fit, scope, differentiation, and next action rather than repeat generic service cards.

# Feature Information & Action Contract
<!-- id: craft.feature-information-actions -->

Important features SHOULD explicitly resolve:

- required information;
- optional/supporting information;
- primary action;
- secondary actions;
- contextual actions;
- information priority;
- destructive or irreversible actions;
- progressive disclosure.

Avoid permanently exposing every possible action.

Actions that are contextual SHOULD appear when context makes them useful.

# Feature Interaction Model
<!-- id: craft.feature-interaction-model -->

Select interaction patterns based on the task rather than habit.

Possible patterns include:

- table;
- list;
- card;
- tabs;
- segmented controls;
- filter bar;
- command/search palette;
- drawer;
- modal;
- disclosure;
- accordion;
- inline editing;
- drill-down;
- direct manipulation;
- wizard;
- contextual menu;
- timeline;
- comparison;
- gallery;
- map;
- structured detail view.

Do not default every feature to cards.

# Feature State Completeness
<!-- id: craft.feature-state-completeness -->

Determine applicable states rather than designing only the happy path.

Potential states include:

- initial;
- default;
- hover;
- focus;
- pressed;
- selected;
- loading;
- partial;
- empty;
- filtered-empty;
- no-results;
- error;
- validation-error;
- success;
- disabled;
- unavailable;
- offline;
- permission-denied;
- destructive-confirmation.

Different causes should not be collapsed into one generic empty state when the recovery action differs.

# Front-End-Only Feature Truth
<!-- id: craft.frontend-only-truth -->

For front-end-only work, explicitly resolve which features:

- operate fully locally;
- simulate backend behavior;
- use sample/demo data;
- use temporary browser persistence;
- are intentionally unavailable;
- would require a real backend or integration in production.

Do not imply real authentication, payment processing, persistence, email delivery, API calls, uploads, or account creation when those systems do not exist.

Sample data SHOULD be clearly identified where users could reasonably mistake it for real operational data.

# Feature-to-Component Mapping
<!-- id: craft.feature-component-mapping -->

Before implementation, map substantial features to the UI primitives required to express them correctly.

Example:

```text
Transaction management
→ search
→ filter controls
→ data table/list
→ status indicator
→ row/context action
→ detail drawer/page
→ empty/no-result state
→ pagination or progressive loading
→ export action when applicable
```

Do not compress an entire workflow into one universal card because it is convenient.

# Feature Visual Treatment
<!-- id: craft.feature-visual-treatment -->

Important features SHOULD define visual intent appropriate to their task and domain.

Examples:

A payment workspace may be compact, high-information, numerically aligned, status-driven, and table/list-first.

A landscaping service section may be image-supported, editorial, craft-oriented, and materially differentiated rather than rendered as SaaS-style icon cards.

Function and art direction should reinforce one another.

# Responsive Feature Recomposition
<!-- id: craft.responsive-feature-recomposition -->

Responsive behavior MUST be resolved at feature level for substantial interfaces.

Evaluate:

- changed priority;
- reordered information;
- hidden secondary data;
- table-to-list/card transformation;
- sticky actions;
- filter disclosure;
- modal vs drawer treatment;
- chart behavior;
- navigation changes;
- touch targets;
- mobile density;
- horizontal overflow strategy.

Do not merely stack desktop components vertically.

# Feature Accessibility Contract
<!-- id: craft.feature-accessibility -->

For important interactive features, resolve:

- semantic element choices;
- keyboard completion;
- focus order;
- accessible names;
- status announcements;
- error communication;
- non-color-only meaning;
- dialog/disclosure semantics;
- table/list semantics;
- target sizing;
- input labels;
- disabled/unavailable explanation where relevant.

Accessibility is part of feature design, not a final repair step.

# Icon System Selection Standard
<!-- id: craft.icon-system-selection -->

Substantial production interfaces MUST explicitly decide whether an icon system materially improves the experience.

When useful, select one coherent professional icon family that fits:

- visual character;
- stroke/fill style;
- corner character;
- optical weight;
- symbol coverage;
- accessibility;
- implementation cost;
- performance budget.

Appropriate systems may include Font Awesome, Phosphor, Lucide, Tabler, Heroicons, Material Symbols, or a project-specific SVG system.

Do not force one library universally.

# Iconography Coverage Standard
<!-- id: craft.iconography-coverage -->

Evaluate icon usage for:

- primary/secondary navigation;
- mobile navigation;
- search;
- filter;
- sort;
- download/export;
- edit/delete;
- disclosure;
- overflow;
- pagination;
- status;
- alert;
- notification;
- metric labels;
- contact methods;
- external links;
- upload;
- password visibility;
- form affordances;
- empty states;
- social links;
- contextual actions.

Do not leave everything text-only by habit.

Do not make everything icon-only.

Use icon + text when that provides the clearest combination.

# Icon Detail Standard
<!-- id: craft.icon-detail -->

Maintain consistent:

- stroke/fill treatment;
- optical size;
- visual weight;
- baseline alignment;
- container treatment;
- label spacing;
- hover/focus/active state;
- selected state;
- disabled state.

Icon-only controls MUST have accessible names.

Avoid mixing visually incompatible families.

# Component Anatomy Standard
<!-- id: craft.component-anatomy -->

Major reusable elements MUST be treated as designed components rather than styled rectangles.

Evaluate as applicable:

- information hierarchy;
- content anatomy;
- internal spacing;
- typography roles;
- icon placement;
- metadata;
- supporting labels;
- dividers;
- borders;
- surface contrast;
- radius;
- elevation;
- contextual actions;
- status treatment;
- hover;
- focus;
- pressed;
- selected;
- disabled;
- loading;
- empty;
- truncation;
- wrapping;
- responsive adaptation.

Important components SHOULD contain meaningful refinement beyond `border + radius + padding` where the visual language supports it.

# Card Anatomy & Specificity
<!-- id: craft.card-specificity -->

Cards MUST NOT default across an experience to:

```text
icon
heading
two-line paragraph
```

inside equal rounded rectangles.

Card structure should reflect the information or task.

Possible anatomy includes:

- category/eyebrow;
- media;
- icon;
- title;
- description;
- numerical value;
- metadata;
- status;
- progress;
- divider;
- contextual action;
- directional affordance;
- footer;
- inset region;
- timestamp.

Reject cards that could be copied unchanged into an unrelated product.

# Surface & Elevation System
<!-- id: craft.surface-elevation -->

Define surface hierarchy rather than independently styling containers.

Possible levels include:

- page;
- secondary surface;
- raised surface;
- interactive surface;
- selected surface;
- inset surface;
- overlay;
- modal;
- tooltip.

Use consistent relationships among:

- background;
- border;
- elevation;
- shadow;
- radius;
- active state;
- dark-mode equivalent where applicable.

Avoid turning every object into a floating rounded card.

# Section Finish Standard
<!-- id: craft.section-finish -->

Every major page section SHOULD have an intentional relationship to the sections around it.

Evaluate:

- spacing shift;
- surface change;
- divider/rule;
- overlap;
- inset;
- breakout;
- typography shift;
- media scale;
- density change;
- asymmetric alignment;
- foreground/background relationship;
- edge treatment.

Do not separate every section only with identical vertical padding.

# Micro-Detail Density Standard
<!-- id: craft.micro-detail -->

Evaluate where useful:

- chevrons;
- external-link indicators;
- active nav markers;
- status glyphs;
- separators;
- contextual metadata;
- badges;
- avatars;
- notification dots;
- keyboard shortcut hints;
- trend indicators;
- row hover actions;
- selected states;
- overflow actions;
- helper text;
- timestamps;
- progress markers.

Additional detail MUST improve clarity, hierarchy, affordance, domain expression, or task completion.

Do not add decorative noise to simulate sophistication.

# Interaction Affordance Audit
<!-- id: craft.affordance-audit -->

Every visible interactive element should communicate actionability before activation.

Evaluate:

- familiar control shape;
- text treatment;
- iconography;
- border/surface;
- disclosure cue;
- hover;
- focus;
- selected state;
- cursor where relevant;
- motion/feedback.

If interactive content is materially indistinguishable from static content, refine it.

# Dashboard Craft Standard
<!-- id: craft.dashboard-craft -->

Operational dashboards SHOULD evaluate:

- numerical alignment;
- tabular numerals;
- icon-supported navigation where useful;
- status icon + label pairing;
- row hover behavior;
- contextual row actions;
- sorting indicators;
- filter hierarchy;
- overflow menus;
- sticky headers where useful;
- selection states;
- drill-down affordances;
- meaningful trend representation;
- tooltips where clarification is needed;
- empty/loading/error states;
- responsive data transformation;
- keyboard efficiency.

Dashboards should feel operational rather than like marketing pages made of metric cards.

# Visual Finishing Pass
<!-- id: craft.finishing-pass -->

Before delivery, inspect:

- icon alignment;
- icon-family consistency;
- border consistency;
- radii;
- elevation;
- spacing;
- text wrapping;
- table density;
- numeric alignment;
- badge shape;
- dividers;
- heading alignment;
- button hierarchy;
- hover/focus quality;
- image crops;
- metadata;
- navigation polish;
- empty states;
- menu surfaces;
- tooltip treatment;
- section transitions;
- mobile density.

Ask:

**Does every visible part feel intentionally finished?**

# Generic Rounded Rectangle Guard
<!-- id: craft.rounded-rectangle-guard -->

Major interface regions composed primarily of generic rounded rectangles without sufficient functional or visual differentiation MUST fail premium production acceptance.

Rounded containers are allowed.

Universal rounded-card grammar is not.

# Production Craft Acceptance Gate
<!-- id: craft.production-craft-acceptance-gate -->

For substantial production visual interfaces, all applicable checks below must pass.

## 1. Feature Depth

High-value features have purpose, user job, information, actions, interaction model, states, responsive/accessibility behavior, data/truth semantics, dependencies, and observable acceptance criteria proportional to importance.

## 2. Component Anatomy

Important components have task-specific hierarchy and anatomy rather than generic container treatment.

## 3. Iconography

When iconography materially improves the experience, one coherent system is selected and used intentionally. Icon-only controls remain accessible.

## 4. Interaction Affordance

Important actions are discoverable before activation and have appropriate hover/focus/active/disabled feedback.

## 5. State Completeness

Applicable loading, empty, filtered-empty/no-results, error, success, disabled/unavailable, and destructive states are resolved for high-value workflows.

## 6. Dashboard / Dense UI Craft

When applicable, tables, lists, numerical information, statuses, filters, contextual actions, and drill-down behavior are designed for scanning and operation rather than flattened into generic cards.

## 7. Responsive Recomposition

Important features change composition or priority when needed rather than merely stacking desktop UI.

## 8. Surface & Micro-Detail

Surface hierarchy, borders, radii, elevation, metadata, icon alignment, dividers, and contextual affordances form a coherent system.

## 9. Genericity Rejection

Fail when the experience is dominated by interchangeable rounded rectangles, repeated equal-card anatomy, or components that could be transplanted into unrelated products without meaningful change.

## 10. Rendered Evidence

When rendering tools exist, judge these requirements from actual desktop/mobile pixels and critical states. Correct material weaknesses and re-render.

# Craft Critical Failures
<!-- id: craft.critical-failures -->

Do not finalize substantial production interfaces with:

- high-value features defined only by a noun;
- important missing interaction states;
- generic repeated card anatomy across functionally different content;
- major regions dominated by interchangeable rounded rectangles;
- accidental or visibly inconsistent iconography;
- unclear action affordances;
- desktop-only feature composition merely stacked on mobile;
- fake backend behavior in front-end-only work;
- visually polished components that do not support their intended user job;
- technically working features that remain behaviorally shallow.

# Compiled Quality Loop
<!-- id: craft.compiled-quality-loop -->

For substantial production interfaces, craft is downstream of compiled product intent:

```text
ARTIFACT_CONTRACTS
→ FEATURE_COMPILER
→ concept exploration
→ GENERICITY structural fingerprint
→ COMPONENT_COMPILER
→ implementation
→ CRITICS
→ QUALITY_FLOORS
```

Visual craft must not compensate for shallow product behavior, and product completeness must not excuse generic or under-finished execution.

# Final Craft Standard
<!-- id: craft.final-standard -->

Every major feature should feel intentionally product-designed.

Every important visible component should feel intentionally finished.

Neither visual polish without product depth nor product behavior without visual craft is sufficient.

# Revision 1.4 Final Closure Loop
<!-- id: craft.revision-1-4-final-closure -->
After compiled feature/component implementation and Revision 1.3 hardening, close the artifact through `USABILITY_CLOSURE.md` → `VISUAL_FINISH.md` → `TRUTH_BOUNDARIES.md` → responsive-detail evidence where applicable → `QUALITY_MEASUREMENT.md` → active quality floors. Re-run genericity after any material visual or responsive repair.
