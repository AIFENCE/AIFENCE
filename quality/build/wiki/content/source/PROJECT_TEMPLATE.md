<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: PROJECT_TEMPLATE
Module-Version: 2
Last-Updated: 2026-08-09
-->

# Project
<!-- id: project.root -->

Creation Type:
Industry:
Subindustry:
Creation:
Goal:
Audience:
Business Model:
Primary Users:
Output:
Delivery Mode: Production
Asset Policy: Generate required visual assets locally
Stack:
Jurisdiction:
Data / Safety / Compliance Facts:
Constraints:

# Optional Overrides

Profile Overrides: None

Use only when the actual business model materially differs from the canonical `PROFILE_MATRIX.md` default. Override the affected dimension only; do not replace the canonical industry identity. For Mixed-Model Registry categories, prefer resolving `Subindustry` and `Business Model` before using manual profile overrides.

## Decision & Evidence State

- Known facts:
- Inferred requirements:
- Unknown facts:
- Hard constraints:
- Assumptions requiring validation:
- Primary business goal:
- Primary user goal:
- Non-goals:
- Active control bundles:
- Release-blocking controls:
- Evidence ledger:
- Current `PASS` / `FAIL` / `UNVERIFIED` controls:
- Material changes requiring re-evaluation:

# Control Plane Hooks
<!-- id: project-template.control-plane-hooks -->

When this module is active, use `CONTROL_INDEX.md` to retrieve only the capability sections relevant to the current decision. Applicable capabilities include:

- **Requirement completeness model** — `controls/02-project-intake-and-requirement-resolution.md` (BQ-0041–BQ-0045)
- **Unknown-fact policy** — `controls/02-project-intake-and-requirement-resolution.md` (BQ-0046–BQ-0050)
- **Constraint normalization** — `controls/02-project-intake-and-requirement-resolution.md` (BQ-0051–BQ-0055)
- **Goal hierarchy** — `controls/02-project-intake-and-requirement-resolution.md` (BQ-0056–BQ-0060)
- **Audience resolution** — `controls/02-project-intake-and-requirement-resolution.md` (BQ-0061–BQ-0065)
- **Scope boundary** — `controls/02-project-intake-and-requirement-resolution.md` (BQ-0066–BQ-0070)
- **Assumption register** — `controls/02-project-intake-and-requirement-resolution.md` (BQ-0071–BQ-0075)

These hooks are routing pointers, not permission to preload the listed shards. Evidence Gates control pass/fail claims.
