<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: SEMANTIC_ROUTING
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->

# Semantic Routing & Context Graph
<!-- id: semantic-routing.root -->

Purpose: make request interpretation a structured, evidence-bearing compilation step instead of a substring lookup. This standard operationalizes Domains 02–05 without creating a parallel control plane.

# Token-Aware Industry Resolution
<!-- id: semantic-routing.industry -->

- Industry matching MUST use normalized token/phrase boundaries, aliases, and confidence margins. Arbitrary character-substring matches are prohibited.
- One generic token from a multi-token industry name is insufficient evidence for resolution.
- Known collision classes such as `foundation`/Foundation Models, `homepage`/Home Services, and `report`/Port Operations are regression fixtures.
- A candidate with a weak first/second margin remains `candidate` or `unresolved`; candidate status MUST NOT silently activate the candidate industry's profile risk overlays.
- User-supplied canonical industry identity has precedence, while conflicting subindustry/business-model facts may override individual profile dimensions with provenance.

# Negation-Aware Exposure Resolution
<!-- id: semantic-routing.negation -->

Risk parsing MUST distinguish positive exposure from explicit negation. `no login`, `without payments`, `front-end only`, `no backend`, `does not collect PII`, `no uploads`, and equivalent constructions suppress the negated exposure unless another independent clause reactivates it.

Each exposure records `present`, `absent`, or `unknown` plus source/provenance. `unknown` is not equivalent to present.

# Industry Risk vs Artifact Exposure
<!-- id: semantic-routing.risk-exposure -->

Use a four-stage risk graph:

```text
industry baseline overlay
→ requested feature/data exposure
→ actual implemented exposure
→ applicable legal/security/safety/trust controls
```

Physical-safety industry context does not automatically activate cybersecurity. Regulated industry context may require legal/truth review even when a public artifact has no transactions or sensitive-data collection. Security controls activate when security-relevant exposure exists, except explicit critical-infrastructure baselines.

# Creation-Type Taxonomy
<!-- id: semantic-routing.creation-types -->

Runtime MUST classify at least: website/landing page; SaaS/web app/portal; marketplace/e-commerce; dashboard; native/mobile app; presentation/deck; spreadsheet/financial model; brand identity/logo; email/campaign; marketing creative; CLI/developer tool; fixed-format document/PDF; design system; feature plan; API; brand strategy; SEO/GEO/AEO content; security architecture; legal policies; organization/jobs/SOPs; documentation/repository architecture.

A specific artifact signal outranks generic words such as `report`, `application`, or `platform`.


# Dashboard vs Workspace Boundary
<!-- id: semantic-routing.dashboard-workspace -->

`workspace` alone remains a Web App / SaaS / Portal signal. Resolve a workspace as **Dashboard** when its dominant user job is decision monitoring/review across evidence, status, risk, deadlines, portfolio/renewal health, scorecards, or operational signals and the request does not primarily ask users to create/edit records or construct workflows. Examples include contract-renewal review workspace, portfolio-risk workspace, compliance-review workspace, and revenue-health workspace.

Resolve as **Web App / SaaS / Portal** when the dominant job is record authoring/editing, task/case management, workflow construction, collaboration, or transactional state mutation. When both are material, compile a composite or choose the explicit user-named deliverable rather than silently reclassifying from a generic `workspace` token.

# Composite Artifact Graph
<!-- id: semantic-routing.composite -->

When a request contains multiple independently deliverable artifact families, compile a project graph instead of forcing one creation type. Each node has its own creation type, contract chain, capabilities, QA/evidence obligations, and maturity/fidelity. Shared project context is explicit and limited to relevant dimensions such as brand, industry, audience, truth boundaries, risk, and shared data assumptions.

Example: `customer portal with a marketing homepage` compiles two nodes: SaaS/Web App + Marketing Website.

# Context Graph Contract
<!-- id: semantic-routing.context-graph -->

The runtime context graph records, when known: canonical industry and confidence; subindustry; business model; audiences; user roles; artifact exposure; public/internal status; platform; revenue model; data classes; authentication; transactions; backend status; integration status; jurisdiction; content provenance; implementation maturity; visual fidelity; and reference inspirations.

Every field distinguishes supplied, inferred, negated, and unknown state. Downstream modules consume the graph instead of re-parsing the raw request independently when a resolved field exists.

# Reference Inspiration Abstraction
<!-- id: semantic-routing.reference-abstraction -->

Named product, brand, site, or visual references compile into abstract principles rather than cloning instructions. Extract the requested qualities—information density, hierarchy, restraint, motion character, typography, trust cues, workflow speed, spatial rhythm—and feed those principles into creative direction. Structural fingerprint generation MUST produce an original composition and MUST NOT copy protected logos, trade dress, distinctive layout sequences, or proprietary assets.

# Artifact Inheritance
<!-- id: semantic-routing.contract-inheritance -->

Each artifact node resolves an explicit `contractChain`. Child contracts may specialize or strengthen parents but cannot erase parent truth, accessibility, security, legal, or evidence obligations. Regulated-public-interface is an additive overlay, never a replacement base contract.

# Revision 1.8.6 Renewal-Monitoring & Report+Deck Boundary
<!-- id: semantic-routing.revision-1-8-6 -->

A service/contract/subscription/customer renewal **monitoring workspace** centered on health, deadlines, risk, evidence, review, scorecards, or decisions resolves as **Dashboard** unless record authoring/editing/task-workflow mutation is the dominant job.

A request that explicitly asks for a **fixed analytical report** or fixed-format report **plus** an executive/decision/board deck compiles as a composite containing **Fixed-Format Document / PDF** and **Presentation / Deck**. Generic `report` language without fixed-format intent remains documentation unless another explicit artifact signal wins.

# Revision 1.8.7 Artifact-Graph Phrase Coverage
<!-- id: semantic-routing.revision-1-8-7 -->

Spreadsheet/model routing MUST recognize explicit Excel model phrasing even when domain qualifiers appear between `Excel` and `model`, including staffing, maintenance, replacement, capacity, planning, scenario, budget, and analogous model descriptors.

When three or more explicit artifact deliverables are enumerated in one coordinated list, Runtime MUST preserve every requested child in the artifact graph unless the request explicitly negates or subordinates one item. A brand + email + landing-page request therefore compiles all three children rather than collapsing to a pair.

# Revision 1.8.8 Deliverable Phrase Normalization
<!-- id: semantic-routing.deliverable-phrase-normalization -->

Finished fixed-format deliverables MUST be recognized from bounded publication intent rather than only a literal `PDF` token. Phrases such as `print-ready assessment report`, `board-ready analytical report`, `publication-ready evaluation report`, `executive-ready findings report`, and analogous finished-report/memo constructions resolve as **Fixed-Format Document / PDF**. Generic reporting, report fields, report data, or a report merely mentioned as content MUST NOT manufacture a fixed-format artifact.

# Revision 1.8.8 Modifier-Tolerant Composite Parsing
<!-- id: semantic-routing.modifier-tolerant-composites -->

Explicit coordinated artifact lists preserve every requested child even when harmless modifiers appear immediately before a child artifact noun. Bounded modifiers include public/internal, responsive, interactive, executive, customer/client/member/employee-facing, mobile/web/native, print-ready, production, premium, and high-fidelity. Modifiers describe the child; they do not terminate the list. The parser MUST remain bounded: incidental artifact nouns embedded in explanatory prose MUST NOT become composite children merely because several artifact words occur in the request.
