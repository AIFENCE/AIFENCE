<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: CRITICS
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Adversarial Critique & Repair System
<!-- id: critics.root -->

Purpose: make validation adversarial. Critics try to disprove completion from artifact/evidence rather than confirm builder intention.

# Independence Rule
<!-- id: critics.independence -->

When practical, each critic evaluates the rendered/runtime artifact without builder rationale, desired score, condition label, or prior critic score. Critics may use the artifact contract and compiled feature/component specifications because those define acceptance.

# Critic Set
<!-- id: critics.set -->

## Visual Quality Critic
<!-- id: critics.visual -->
Try to find weak hierarchy, awkward spacing, repetitive composition, unfinished typography, poor crops, inconsistent surfaces/radii, weak icon alignment, low detail quality, excess symmetry, dead visual zones, and under-designed transitions.

## Feature Depth Critic
<!-- id: critics.feature-depth -->
Try to find feature nouns masquerading as specifications, missing information/actions/states, dead ends, unclear recovery, overexposed contextual actions, missing dependencies, or workflows that do not accomplish the user job.

## Accessibility & Responsive Critic
<!-- id: critics.accessibility-responsive -->
Try to find keyboard/focus/accessibility-name/contrast/target-size/dialog/reflow failures, desktop-only assumptions, tables that simply shrink, and mobile layouts that merely stack.

Specifically compare the declared P0/P1 task ledger between desktop, 390, and 320. Treat a hidden transaction inspector, edit/detail pane, recovery action, contextual menu, or completion action without an equivalent narrow-screen path as a P1 mobile task-loss defect even when the page has no horizontal overflow.

## Truth & Implementation Critic
<!-- id: critics.truth-implementation -->
Try to find fabricated facts/proof, unlabeled sample data, fake backend semantics, dead controls, broken paths/assets, runtime errors, misleading persistence/payment/auth claims, or missing validation.

For interactive work, enumerate and exercise **all enabled visible controls**, not a convenience sample. Treat inert navigation/period controls, overflow triggers, “More” actions, filters, row menus, exports, and action buttons as release-blocking implementation defects unless they are explicitly disabled with truthful reason or removed.

## Genericity Critic
<!-- id: critics.genericity -->
Try to find universal rounded-card grammar, interchangeable sections, category-agnostic anatomy, repeated icon-heading-copy units, common template sequences, weak domain specificity, and competitor-swap structure. For SaaS/dashboards specifically test whether the result collapses to a generic sidebar/KPI/chart/table or queue/right-panel pattern, whether at least four meaningful information grammars are present where justified, whether primary task topology shapes the composition, and whether at least two structural choices would fail if the product were relabeled for an unrelated competitor.

# Issue Schema
<!-- id: critics.issue-schema -->

```text
Issue ID
Critic
Dimension
Severity: P0 / P1 / P2 / P3
Evidence
Why It Matters
Affected Feature / Component / Viewport
Required Fix
Revalidation Method
Status
```

Use `schemas/critique_report.schema.json`.

# Severity
<!-- id: critics.severity -->

- P0: truth, safety, critical accessibility, destructive behavior, severe runtime/corruption, or release-invalidating contract breach.
- P1: primary user-job failure, major feature/state gap, major mobile failure, severe genericity, dead primary control.
- P2: material usability, hierarchy, density, component-craft, or visual-polish weakness.
- P3: minor polish not materially blocking production.

# Iterative Render Critique Loop
<!-- id: critics.iterative-loop -->

```text
IMPLEMENT
→ RENDER critical desktop/mobile/states
→ run independent critics
→ consolidate issues
→ prioritize repair
→ fix P0/P1, then material P2
→ re-render affected views
→ re-run affected critics
→ evaluate QUALITY_FLOORS
→ repeat while release-blocking failures remain
```

At least one rendered critique pass follows the first implementation render when rendering exists. Do not loop cosmetically after material floors pass.

# Repair Prioritization
<!-- id: critics.repair-prioritization -->

Repair order: truth/safety/legal/security/critical accessibility → primary task/data correctness → responsive/keyboard completion → feature completeness/recovery → genericity/IA → component anatomy/affordance/density → decorative polish.

# No-Render Fallback
<!-- id: critics.no-render-fallback -->

When rendering is unavailable, perform source/spec checks but mark render-dependent visual/responsive evidence UNVERIFIED. Do not award rendered-quality PASS from source alone.

# Revision 1.3 Specialized Critics
<!-- id: critics.revision-1-3-specialists -->
When applicable, add a **Mobile Composition Critic**, **Document Craft Critic**, **Accessibility Evidence Critic**, and **Completeness Critic**. After any repair, rerun the Genericity Critic and affected quality floors so a local fix cannot regress structural differentiation.


# Revision 1.4 Specialized Critics
<!-- id: critics.revision-1-4-specialists -->
When applicable, add:

- **Task Friction Critic** — attempts the P0/P1 path and finds ambiguous next actions, avoidable decisions, hidden prerequisites, state loss, weak feedback, and recovery dead ends.
- **Visual Finish Critic** — looks for flat hierarchy, optical spacing/alignment defects, weak typographic roles, inconsistent surfaces, unfinished media/state treatment, and cross-viewport polish gaps.
- **Truth Boundary Critic** — finds supplied/verified/sample/assumption/unknown/interpretation/recommendation content whose visual treatment could mislead a reasonable user.
- **Responsive Detail Critic** — stress-tests dense document/operations structures, long content, sticky layers, and label/value preservation after macro overflow has already passed.
- **Measurement Calibration Critic** — checks whether the scoring instrument can actually reach/discriminate around the active floor before treating a score as release-dispositive.

- **B2B Decision-Depth Critic** — for complex-consideration B2B marketing, checks that at least two important buyer decisions are supported by evidence/fit/risk/action/downstream-state paths in the rendered artifact rather than only feature presentation.

After repair, rerun the existing Genericity Critic and affected Revision 1.3 hardening gates.
