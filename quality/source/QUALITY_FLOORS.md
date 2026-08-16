<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: QUALITY_FLOORS
Module-Version: 2
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Quality Floors
<!-- id: quality-floors.root -->

Purpose: prevent a strong aggregate score from hiding a weak release-critical dimension.

# Dimensions
<!-- id: quality-floors.dimensions -->

Use 0–10 evidence-backed scoring for applicable: visual quality, completeness, truthfulness, usability, feature depth, responsiveness, accessibility, implementation correctness, genericity resistance.

A dimension may be N/A only when the artifact contract makes it genuinely inapplicable. UNVERIFIED is not N/A.

# Global Production Floors
<!-- id: quality-floors.global-production -->

- overall evidence-backed target ≥ 92/100;
- no applicable dimension below 9.0;
- truthfulness ≥ 9.5;
- implementation correctness ≥ 9.5;
- no unresolved P0/P1 critic issue;
- no critical failure from active contracts, CREATIVE, CRAFT, security/legal/accessibility controls, or QA gates.

# Premium / Best-in-Class Target
<!-- id: quality-floors.premium-target -->

- overall target ≥ 95/100;
- no applicable dimension below 9.2 except higher contract floors;
- truthfulness and implementation correctness target ≥ 9.6;
- genericity resistance target ≥ 9.2;
- visual quality, usability, responsiveness, accessibility, and feature depth target ≥ 9.3 where applicable.

A 95+ aggregate does not pass if a required floor fails.

# Artifact Profiles
<!-- id: quality-floors.artifact-profiles -->

| Profile ID | VQ | Comp | Truth | Use | Depth | Resp | A11y | Impl | Generic | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `quality-floors.profile.marketing-website` | 9.2 | 9.1 | 9.5 | 9.2 | 8.9 | 9.2 | 9.2 | 9.5 | 9.2 | 95 |
| `quality-floors.profile.local-service` | 9.2 | 9.1 | 9.6 | 9.3 | 8.9 | 9.3 | 9.2 | 9.5 | 9.3 | 95 |
| `quality-floors.profile.saas-web-app` | 9.2 | 9.4 | 9.5 | 9.4 | 9.5 | 9.4 | 9.4 | 9.6 | 9.2 | 95 |
| `quality-floors.profile.dashboard` | 9.2 | 9.4 | 9.5 | 9.4 | 9.5 | 9.4 | 9.4 | 9.6 | 9.2 | 95 |
| `quality-floors.profile.ecommerce` | 9.2 | 9.3 | 9.6 | 9.4 | 9.3 | 9.3 | 9.3 | 9.6 | 9.1 | 95 |
| `quality-floors.profile.regulated-overlay` | — | 9.3 | 9.8 | 9.3 | 9.2 | 9.2 | 9.5 | 9.7 | — | — |
| `quality-floors.profile.document-report` | 9.3 | 9.4 | 9.6 | 9.3 | 9.3 | N/A* | 9.3 | 9.5 | 9.2 | 95 |
| `quality-floors.profile.operations` | 9.0 | 9.5 | 9.6 | 9.4 | 9.5 | 9.2 | 9.3 | 9.7 | 9.0 | 95 |

`*` Responsive is N/A for fixed-format output unless responsive/digital behavior is part of delivery.

When two profiles apply, use the stricter applicable floor per dimension.

# Scoring Integrity
<!-- id: quality-floors.scoring-integrity -->

Scores require evidence. Do not tune to a desired number or invent unsupported decimals. If precise scoring is unavailable, use PASS/FAIL/UNVERIFIED floors instead of false precision.

# Evidence Floors
<!-- id: quality-floors.evidence-floors -->
For P0/P1 product workflows, numerical PASS additionally requires completion ledger, feature-depth closure, responsive viewport evidence when applicable, and accessibility critical-path evidence. A score without the corresponding evidence record is UNVERIFIED.

For substantial interactive artifacts, implementation-correctness and usability floors are **NON-PASS** when any enabled visible control is unaccounted or dead. Responsiveness/usability/implementation-correctness floors are **NON-PASS** when any declared P0/P1 task fails at 320 or 390 px, even if aggregate visual quality and page-level overflow checks are strong. These are non-averagable release gates.

For high-fidelity SaaS/dashboard/portal work, genericity resistance is **NON-PASS** without valid dense-product structural differentiation evidence. A best generic-template similarity of `>=0.61`, fewer than three non-cosmetic structural decisions, insufficient task-to-space linkage, or a failed competitor-swap test blocks the genericity floor regardless of aggregate score.

For complex-consideration B2B marketing work, feature depth is **NON-PASS** without valid decision-depth evidence containing at least two P0/P1 buyer decision paths tied to observable artifact structures. A feature catalog plus generic contact CTA cannot satisfy the depth floor by itself.

For high-fidelity SaaS/dashboard/portal work, visual quality, completeness, accessibility, and feature depth are each **NON-PASS** without valid Revision 1.7.4 dense-product quality evidence. The gate is non-averagable: strong implementation correctness, genericity, or overall score cannot compensate for a missing/failed dense-product visual, completion, accessibility, or workflow-depth section. Payments and analytics additionally require the workflow-specific Level-5 loops in `FEATURE_DEPTH.md`.

# Revision 1.4 Floor-Capable Evidence
<!-- id: quality-floors.measurement-calibration -->
Before using a numerical judge to enforce a floor, apply `QUALITY_MEASUREMENT.md`. If the evaluator's theoretical maximum is below the required floor, its score remains valid for longitudinal comparison but is **NON-DISPOSITIVE** for release acceptance. Usability floor PASS requires `USABILITY_CLOSURE.md` task-path evidence; visual floor PASS requires `VISUAL_FINISH.md` rendered evidence; truth floor PASS requires `TRUTH_BOUNDARIES.md` point-of-use/provenance evidence where material.

# Operations 2.0 Evidence Floor
<!-- id: quality-floors.operations-2-evidence -->

For `quality-floors.profile.operations`, numerical completeness/feature-depth/truth/implementation scores are non-dispositive unless material real-world procedures also pass the applicable Domain 31 evidence gates: exact task/context, truthful authority class, executable steps/decisions, explicit decision rights, exception/recovery, operational evidence and definition of done, reproducible KPI definitions when metrics are material, and procedure lifecycle/currentness checks. An attractive or detailed SOP that cannot establish its authority or execution closure is not production PASS.
