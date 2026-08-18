<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: ARTIFACT_CONTRACTS
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->

# Artifact Contract Router
<!-- id: artifact-contracts.root -->

Purpose: convert a broad creation type into an observable production acceptance contract before feature or component design begins.

An artifact contract is not a style template. It defines user jobs, evidence, state coverage, truth boundaries, responsive obligations, and acceptance characteristics appropriate to the deliverable.

# Resolution Rule
<!-- id: artifact-contracts.resolution -->

1. Resolve creation type and delivery mode first.
2. Select the narrowest applicable base contract.
3. Add a second contract only when the artifact genuinely spans two deliverable families.
4. Add `regulated-public-interface` whenever regulated claims, sensitive data, qualified-role boundaries, or regulated decision-making are material.
5. Contract specificity constrains generic production defaults but never overrides higher-precedence safety, legal, security, accessibility, or explicit user requirements.
6. Retrieve only selected contract files; do not preload all contracts.

# Contract Registry
<!-- id: artifact-contracts.registry -->

| Contract | File | Typical triggers |
|---|---|---|
| Marketing Website | `contracts/marketing-website.md` | public company/service/brand websites, landing pages |
| Local Service Website | `contracts/local-service-website.md` | home services, landscaping, contractors, local professional services |
| SaaS / Web App | `contracts/saas-web-app.md` | SaaS, portals, authenticated product UI, workflow applications |
| Dashboard | `contracts/dashboard.md` | analytics, operational monitoring, finance/admin/data workspaces |
| E-Commerce / Marketplace | `contracts/ecommerce-marketplace.md` | product discovery, PDP, cart, checkout, marketplace transactions |
| Regulated Public Interface | `contracts/regulated-public-interface.md` | healthcare, financial, legal, insurance, sensitive/regulated public experiences |
| Document / Report | `contracts/document-report.md` | reports, memos, analyses, strategy documents, formal decision artifacts |
| Operations Workflow | `contracts/operations-workflow.md` | boards, queues, runbooks, SOP interfaces, field/incident/approval workflows |
| Native / Mobile App | `contracts/native-mobile-app.md` | iOS, Android, SwiftUI, Compose, mobile/native apps |
| Presentation / Deck | `contracts/presentation-deck.md` | pitch decks, investor decks, presentations, PPTX/slides |
| Spreadsheet / Financial Model | `contracts/spreadsheet-financial-model.md` | workbooks, budgets, forecasts, financial models |
| Brand Identity / Logo | `contracts/brand-identity.md` | logos, marks, identity systems, visual identity |
| Email / Campaign | `contracts/email-campaign.md` | email campaigns, sequences, lifecycle messaging |
| Marketing Creative | `contracts/marketing-creative.md` | ads, campaign creative, storyboards, channel assets |
| CLI / Developer Tool | `contracts/cli-developer-tool.md` | command-line tools, developer utilities |
| Fixed-Format Document / PDF | `contracts/fixed-format-document.md` | PDFs, print-ready reports, fixed-format documents |

# Contract Inheritance
<!-- id: artifact-contracts.inheritance -->

Contracts compose through explicit inheritance rather than duplicated prose. Runtime returns the resolved `contractChain`; child contracts refine, never weaken, parent obligations.

| Child contract | Parent contract(s) |
|---|---|
| `local-service-website` | `marketing-website` |
| `dashboard` | `saas-web-app` for interactive/stateful behavior; dashboard density rules remain specialized |
| `ecommerce-marketplace` | `marketing-website` + `saas-web-app` where transactions/state are implemented |
| `regulated-public-interface` | overlay on the selected public/interface base contract |
| `native-mobile-app` | base interactive-product obligations from Domain 27/28; no web-specific inheritance |
| `fixed-format-document` | `document-report` |
| `presentation-deck`, `spreadsheet-financial-model`, `brand-identity`, `email-campaign`, `marketing-creative`, `cli-developer-tool` | specialized base contracts; inherit only cross-cutting truth/evidence controls |

Composite projects resolve a contract chain per artifact node and share only explicit project context such as brand, audience, industry, truth boundaries, and risk.

# Compilation Handoff
<!-- id: artifact-contracts.compilation-handoff -->

```text
Artifact Contract
→ FEATURE_COMPILER.md
→ concept / information architecture
→ GENERICITY.md structural fingerprint
→ COMPONENT_COMPILER.md
→ implementation
→ CRITICS.md
→ QUALITY_FLOORS.md
→ final Evidence Gates
```

High-value, repeated, regulated, destructive, conversion-critical, or workflow-critical capabilities require full compilation.

# Revision 1.4 Quality Closure Overlay
<!-- id: artifact-contracts.revision-1-4-closure -->
For substantial production artifacts, active contracts additionally resolve task-path usability, final visual finish, truth/provenance boundaries, and floor-capable evidence. Interactive artifacts, responsive digital documents, and operations workflows activate `RESPONSIVE_DETAIL_CLOSURE.md`; substantial interactive artifacts additionally require interaction-manifest closure for all enabled controls and P0/P1 mobile tasks. These overlays refine acceptance; they do not replace artifact-specific contract semantics.

# Operations 2.0 Contract Overlay
<!-- id: artifact-contracts.operations-2 -->

When `contract.artifact.operations-workflow` is active for a real SOP, runbook, work instruction, checklist, playbook, authority matrix, or governed KPI system, load `OPERATIONAL_PROCEDURE_COMPILER.md` and only the applicable supporting standards. The operations artifact contract governs deliverable behavior; Domain 31 governs real-world procedural executability and authority truth.
