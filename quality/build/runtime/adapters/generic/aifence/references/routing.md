<!-- GENERATED from source/README.md by tooling/build.mjs. Do not hand edit. -->

# Routing reference

# Retrieval Rules
<!-- id: readme.retrieval-rules -->

## Rule 1 — Resolve Industry First

For industry-specific work, resolve the canonical identity before using industry-mapped modules.

### Duplicate Subindustry Resolution Guard
<!-- id: readme.duplicate-subindustry-resolution -->

When a subindustry label appears under multiple parents, MUST NOT select the first match or broadest umbrella.

Resolve using:

1. exact offering/domain term;
2. narrowest direct canonical parent;
3. audience, transaction model, service area, operating model, and deliverable;
4. independent profile overrides after canonical identity;
5. local service / B2C behavior when appropriate without erasing domain identity;
6. strongest contextual evidence when ambiguity remains.

## Rule 2 — Read Exact Headings

For industry-indexed modules, retrieve the exact industry heading and stop at the next top-level heading.

## Rule 3 — Resolve Job Before SOP

Resolve industry → role → MANIFEST operations shard → exact SOP stable ID/section.

## Rule 3A — Section-Level Retrieval Protocol

Search by stable ID when available. Retrieve only the matching section plus the minimum adjacent context required to apply it correctly.

## Rule 4 — Load Universal Standards by Need

Load only when applicable:

- `CREATIVE.md` — substantial visual differentiation/quality.
- `CRAFT.md` — substantial production feature/component craft.
- `ASSETS.md` — custom images/illustrations/media.
- `STRUCTURE.md` — maintainable systems.
- `TERMINOLOGY.md` — naming/copy/UI text.
- `SEO_GEO_AEO.md` — public discoverability.
- `SECURITY.md` — auth/permissions/sensitive data/APIs/payments.
- `LEGAL.md` — policies/privacy/consumer/payment/legal obligations.

# Creation-Type Router
<!-- id: readme.creation-type-router -->

Use `SEMANTIC_ROUTING.md` before this table when creation type, industry, negation, risk exposure, or composite scope is ambiguous. Hybrid/composite creations compile one artifact node per independently deliverable family; do not force the whole project into one type.

| Creation Type | Primary Modules |
|---|---|
| Website / Landing Page | INDUSTRIES, ARTIFACT_CONTRACTS, FEATURES, DESIGN, CREATIVE, CRAFT, FEATURE_COMPILER, GENERICITY, COMPONENT_COMPILER, CRITICS, QUALITY_FLOORS, HALO, SEO_GEO_AEO, TERMINOLOGY, STRUCTURE, ASSETS when Domain 11/media is active |
| Web App / SaaS / Portal | INDUSTRIES, ARTIFACT_CONTRACTS, FEATURES, FEATURE_COMPILER, DESIGN, CREATIVE, CRAFT, GENERICITY, COMPONENT_COMPILER, CRITICS, QUALITY_FLOORS, STRUCTURE, TERMINOLOGY |
| Marketplace / E-Commerce | INDUSTRIES, ARTIFACT_CONTRACTS, FEATURES, FEATURE_COMPILER, DESIGN, CREATIVE, CRAFT, GENERICITY, COMPONENT_COMPILER, CRITICS, QUALITY_FLOORS, ASSETS, SEO_GEO_AEO, TERMINOLOGY |
| Dashboard | ARTIFACT_CONTRACTS, FEATURES, FEATURE_COMPILER, DESIGN, CREATIVE, CRAFT, GENERICITY, COMPONENT_COMPILER, CRITICS, QUALITY_FLOORS, STRUCTURE, TERMINOLOGY |
| Native / Mobile App | INDUSTRIES, ARTIFACT_CONTRACTS, FEATURES, FEATURE_COMPILER, DESIGN, CREATIVE, CRAFT, GENERICITY, COMPONENT_COMPILER, CRITICS, QUALITY_FLOORS, STRUCTURE, TERMINOLOGY |
| Presentation / Deck | ARTIFACT_CONTRACTS, DOCUMENT_CRAFT, DESIGN, CREATIVE, CRAFT, ASSETS, CRITICS, QUALITY_FLOORS, TERMINOLOGY |
| Spreadsheet / Financial Model | ARTIFACT_CONTRACTS, STRUCTURE, TERMINOLOGY, TRUTH_BOUNDARIES, CRITICS, QUALITY_FLOORS |
| Brand Identity / Logo | INDUSTRIES, ARTIFACT_CONTRACTS, HALO, DESIGN, CREATIVE, CRAFT, ASSETS, GENERICITY, CRITICS, QUALITY_FLOORS, TERMINOLOGY |
| Email / Campaign | INDUSTRIES, ARTIFACT_CONTRACTS, HALO, CREATIVE, CRAFT, TERMINOLOGY, LEGAL when triggered |
| Marketing Creative | INDUSTRIES, ARTIFACT_CONTRACTS, DESIGN, CREATIVE, CRAFT, ASSETS, GENERICITY, CRITICS, QUALITY_FLOORS, TERMINOLOGY |
| CLI / Developer Tool | ARTIFACT_CONTRACTS, STRUCTURE, TERMINOLOGY, SECURITY when triggered |
| Fixed-Format Document / PDF | ARTIFACT_CONTRACTS, DOCUMENT_CRAFT, STRUCTURE, TERMINOLOGY, CRITICS, QUALITY_FLOORS |
| Design System | DESIGN, CREATIVE, CRAFT, STRUCTURE, TERMINOLOGY |
| Feature Plan | ARTIFACT_CONTRACTS, FEATURES, FEATURE_COMPILER, CRAFT, QUALITY_FLOORS, STRUCTURE |
| API | STRUCTURE, TERMINOLOGY; SECURITY when triggered |
| Brand Strategy | HALO, TERMINOLOGY, DESIGN/CREATIVE when needed |
| SEO/GEO/AEO Content | SEO_GEO_AEO, TERMINOLOGY, industry context |
| Security Architecture | SECURITY, STRUCTURE, TERMINOLOGY; LEGAL when applicable |
| Legal Policies | LEGAL, TERMINOLOGY, SECURITY when referenced |
| Org / Jobs / SOPs | INDUSTRIES, JOBS, exact operations section |
| Documentation / Repository Architecture | STRUCTURE, TERMINOLOGY, DOCUMENT_CRAFT, SECURITY when applicable |

`SEMANTIC_ROUTING.md`, `RETRIEVAL_INTELLIGENCE.md`, `TRUTH_BOUNDARIES.md`, `COMPLETENESS.md`, and `EVIDENCE_ADAPTER.md` are cross-cutting orchestration standards and are not permission to preload their entire contents. Runtime retrieves their required stable sections. Risk modules are activated from the exposure/risk graph rather than industry labels alone.

# Routing by Task
<!-- id: readme.routing-by-task -->

For substantial production artifacts, resolve the artifact contract before detailed creation. Production visual/product work activates Domains 26–28 through `CONTROL_INDEX.md` as applicable.

Domain 27 compiles artifact/feature/component/fingerprint intent before implementation. Domain 28 performs adversarial post-implementation review, recovery, floors, and benchmark governance. Domain 29 hardens measured benchmark gaps in mobile composition, documents, accessibility evidence, completeness, and feature depth while preserving genericity resistance. Domain 30 routes the applicable closure standards directly: `USABILITY_CLOSURE.md`, `VISUAL_FINISH.md`, `TRUTH_BOUNDARIES.md`, `RESPONSIVE_DETAIL_CLOSURE.md`, and `QUALITY_MEASUREMENT.md`. High-fidelity concepts keep this quality-closure path even when implementation maturity is explicitly non-production.

Purely non-visual/non-interactive work may still use an artifact contract and Domain 28 evidence controls, while visual craft remains inactive when irrelevant.

# Context Efficiency Protocol
<!-- id: readme.context-efficiency-protocol -->

Preferred sequence:

```text
README
→ user request / PROJECT
→ creation + delivery mode
→ industry/profile only if needed
→ risk triggers
→ CONTROL_INDEX bundle/capability
→ artifact contract
→ feature compilation
→ creative concepts + structural fingerprint
→ component compilation
→ implementation
→ render/test
→ adversarial critics + repair
→ quality floors
→ validate
```

Never load every module, every control shard, every industry, or every SOP.