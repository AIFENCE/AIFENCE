<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: STRUCTURE
Module-Version: 1
Last-Updated: 2026-08-09
-->

# Structure, Organization & Maintainability High-Quality Standards
<!-- id: structure.structure-organization-and-maintainability-high-quality-standards -->

Version: 2026-08-09  
Status: Architecture, organization, readability, and maintainability standard  
Scope: Websites, web applications, SaaS products, repositories, codebases, design systems, content systems, documentation, APIs, assets, configuration, data models, analytics, and operational knowledge

---

# 1. Purpose
<!-- id: structure.1-purpose -->

This standard defines how systems should be structured so they remain:

- consistent
- organized
- readable
- maintainable
- scalable
- predictable
- discoverable
- testable
- reusable
- auditable
- easy to onboard into
- safe to modify

Good structure reduces:

- duplication
- ambiguity
- hidden dependencies
- accidental coupling
- inconsistent naming
- maintenance cost
- onboarding time
- change risk
- documentation drift
- design drift
- ownership confusion

Structure is a long-term quality system, not a one-time cleanup activity.

---

# 2. Standards Language
<!-- id: structure.2-standards-language -->

Use these terms consistently:

- MUST = required
- MUST NOT = prohibited
- SHOULD = expected unless there is a documented reason not to
- SHOULD NOT = generally avoid
- MAY = optional enhancement

---

# 3. Core Structural Principle
<!-- id: structure.3-core-structural-principle -->

Every important item SHOULD have:

- one clear purpose
- one expected location
- one canonical name
- one owner
- one lifecycle
- one source of truth

If contributors cannot predict where something belongs, the structure needs improvement.

---

# 4. Predictability Standard
<!-- id: structure.4-predictability-standard -->

A good structure SHOULD be understandable without memorizing exceptions.

A contributor SHOULD be able to answer:

- Where does this belong?
- Where is this configured?
- Where is this feature implemented?
- Where is this documented?
- Who owns it?
- What depends on it?
- What can be changed safely?

Predictability is more valuable than cleverness.

---

# 5. Simplicity Standard
<!-- id: structure.5-simplicity-standard -->

Choose the simplest structure that supports:

- current requirements
- foreseeable growth
- clear ownership
- safe change

Do not introduce architectural complexity merely because it might be useful someday.

---

# 6. Consistency Standard
<!-- id: structure.6-consistency-standard -->

Patterns SHOULD remain consistent across similar domains.

Examples:

- routes
- feature folders
- test placement
- component APIs
- documentation format
- configuration
- error handling
- naming
- design tokens

Consistency reduces cognitive load.

---

# 7. Exception Standard
<!-- id: structure.7-exception-standard -->

Exceptions to established structure SHOULD be:

- rare
- intentional
- documented
- justified
- reviewable

Do not normalize exceptions by silently repeating them.

---

# 8. Hierarchy Standard
<!-- id: structure.8-hierarchy-standard -->

Use hierarchy only when it communicates a meaningful relationship.

A hierarchy SHOULD represent:

- containment
- product domain
- ownership
- audience
- lifecycle
- technical layer
- content taxonomy
- permissions

Do not nest directories simply to make a repository look organized.

---

# 9. Depth Standard
<!-- id: structure.9-depth-standard -->

Keep hierarchy as shallow as practical.

Most project areas SHOULD stay within roughly 2–5 meaningful levels.

Avoid:

```text
src/modules/platform/features/account/settings/preferences/forms/components/internal/
```

unless every level carries clear architectural meaning.

---

# 10. Breadth Standard
<!-- id: structure.10-breadth-standard -->

Avoid giant flat directories containing unrelated files.

When a directory grows substantially, split it by:

- feature
- domain
- responsibility
- lifecycle
- ownership

Do not group files alphabetically as a substitute for architecture.

---

# 11. Domain-First Standard
<!-- id: structure.11-domain-first-standard -->

Complex products SHOULD generally organize around business or product domains.

Prefer:

```text
features/
  authentication/
  billing/
  reporting/
  onboarding/
```

over a repository where every feature is fragmented across unrelated global folders.

---

# 12. Feature-First Standard
<!-- id: structure.12-feature-first-standard -->

Feature-specific implementation SHOULD live near the feature.

Example:

```text
features/
  billing/
    components/
    api/
    hooks/
    schemas/
    tests/
    types/
```

This improves locality and discoverability.

---

# 13. Type-First Structure Standard
<!-- id: structure.13-type-first-structure-standard -->

Type-based organization MAY be appropriate for:

- small projects
- shared libraries
- design systems
- documentation repositories

Example:

```text
components/
hooks/
utils/
styles/
```

Reevaluate when the project becomes domain-heavy.

---

# 14. Hybrid Structure Standard
<!-- id: structure.14-hybrid-structure-standard -->

Large systems MAY use a hybrid structure.

Example:

```text
src/
  app/
  features/
  shared/
  infrastructure/
```

The distinction between these areas MUST be documented.

---

# 15. Shared-Code Standard
<!-- id: structure.15-shared-code-standard -->

Only move code into shared/common modules after real reuse exists.

Shared code SHOULD:

- serve multiple domains
- have a stable abstraction
- have clear ownership
- avoid hidden domain assumptions
- be tested

`shared`, `common`, and `utils` MUST NOT become dumping grounds.

---

# 16. Utility Standard
<!-- id: structure.16-utility-standard -->

A utility SHOULD be:

- small
- generic
- independently testable
- clearly named
- side-effect free where practical

Avoid:

```text
utils.ts
helpers.ts
misc.ts
```

when they become large collections.

---

# 17. Module Standard
<!-- id: structure.17-module-standard -->

A module SHOULD represent one coherent capability.

A module SHOULD have:

- clear responsibility
- deliberate public interface
- private implementation
- predictable dependencies
- tests
- documentation where necessary

---

# 18. Boundary Standard
<!-- id: structure.18-boundary-standard -->

Architectural boundaries SHOULD be explicit.

Common boundaries:

- UI
- application/use-case logic
- domain logic
- data access
- infrastructure
- external integrations
- configuration

---

# 19. Dependency Direction Standard
<!-- id: structure.19-dependency-direction-standard -->

Dependencies SHOULD flow in a predictable direction.

Example:

```text
UI
↓
Application
↓
Domain
↓
Infrastructure / Adapters
```

Avoid arbitrary cross-layer imports.

---

# 20. Circular Dependency Standard
<!-- id: structure.20-circular-dependency-standard -->

Circular dependencies SHOULD be treated as architecture warnings.

Resolve them by:

- extracting abstractions
- reversing ownership
- introducing interfaces
- separating responsibilities
- moving orchestration upward

---

# 21. Encapsulation Standard
<!-- id: structure.21-encapsulation-standard -->

Internal implementation details SHOULD remain private to the owning module.

Expose only the minimum public API needed by consumers.

---

# 22. Public Interface Standard
<!-- id: structure.22-public-interface-standard -->

Reusable domains and libraries SHOULD expose a deliberate public interface.

Prefer:

```text
billing/index.ts
```

instead of importing private implementation paths directly.

---

# 23. Deep Import Standard
<!-- id: structure.23-deep-import-standard -->

Avoid deep imports into another feature's internals.

Bad:

```text
features/billing/internal/helpers/calculateTax
```

Prefer a stable public export.

---

# 24. Single Responsibility Standard
<!-- id: structure.24-single-responsibility-standard -->

A file, component, module, service, or document SHOULD have one primary responsibility.

If the name needs repeated `And`, consider splitting it.

---

# 25. Cohesion Standard
<!-- id: structure.25-cohesion-standard -->

Things that change together SHOULD generally live together.

Things that change for unrelated reasons SHOULD generally be separated.

---

# 26. Coupling Standard
<!-- id: structure.26-coupling-standard -->

Minimize coupling between:

- features
- modules
- services
- UI components
- data models
- configuration
- external vendors

Prefer explicit contracts over implicit shared state.

---

# 27. Canonical Source Standard
<!-- id: structure.27-canonical-source-standard -->

Each important value SHOULD have one canonical source.

Examples:

- product names
- pricing
- plan definitions
- routes
- roles
- permissions
- feature flags
- design tokens
- API endpoints
- analytics event names

Do not duplicate canonical values across multiple systems without synchronization.

---

# 28. Duplication Standard
<!-- id: structure.28-duplication-standard -->

Avoid duplicating:

- business rules
- validation rules
- configuration
- constants
- legal links
- design tokens
- terminology
- schemas

Duplication MAY remain when abstraction would make the system less clear.

---

# 29. DRY Judgment Standard
<!-- id: structure.29-dry-judgment-standard -->

Do not apply DRY mechanically.

Two similar implementations MAY remain separate when:

- their concepts differ
- their owners differ
- their change patterns differ
- abstraction creates unwanted coupling
- the duplicated logic is trivial

---

# 30. Abstraction Standard
<!-- id: structure.30-abstraction-standard -->

Create an abstraction only when it makes the system easier to understand or safer to change.

Avoid premature abstractions based on hypothetical reuse.

---

# 31. Naming Standard
<!-- id: structure.31-naming-standard -->

Names SHOULD reveal purpose.

Good:

- `calculateInvoiceTotal`
- `SubscriptionCard`
- `BillingSettings`
- `formatCurrency`

Avoid:

- `helper`
- `thing`
- `misc`
- `data2`
- `newComponent`
- `temp`

---

# 32. Naming Convention Standard
<!-- id: structure.32-naming-convention-standard -->

Each project MUST define naming conventions for:

- files
- directories
- components
- functions
- variables
- classes
- constants
- routes
- API resources
- database fields
- analytics events

---

# 33. Folder Naming Standard
<!-- id: structure.33-folder-naming-standard -->

Folder names SHOULD:

- follow one casing convention
- use predictable separators
- represent a clear responsibility
- avoid unclear abbreviations
- avoid temporary labels

---

# 34. File Naming Standard
<!-- id: structure.34-file-naming-standard -->

Use one file naming convention consistently.

Common choices:

- `kebab-case`
- `camelCase`
- `PascalCase` for components

Do not mix conventions arbitrarily.

---

# 35. Component Naming Standard
<!-- id: structure.35-component-naming-standard -->

Components SHOULD describe what they represent.

Prefer:

- `InvoiceTable`
- `AccountSwitcher`
- `UserAvatar`

Avoid:

- `Box`
- `Thing`
- `Component2`

unless the component is intentionally primitive.

---

# 36. Boolean Naming Standard
<!-- id: structure.36-boolean-naming-standard -->

Booleans SHOULD read naturally.

Prefer:

- `isLoading`
- `hasPermission`
- `canEdit`
- `shouldRetry`

Avoid ambiguous names such as:

- `status`
- `flag`
- `enabledThing`

---

# 37. Collection Naming Standard
<!-- id: structure.37-collection-naming-standard -->

Collections SHOULD use plural nouns.

Examples:

- `users`
- `invoices`
- `projects`

---

# 38. Function Naming Standard
<!-- id: structure.38-function-naming-standard -->

Functions SHOULD use verbs that describe the action.

Examples:

- `createUser`
- `loadInvoice`
- `validateEmail`
- `formatDate`

---

# 39. Class Naming Standard
<!-- id: structure.39-class-naming-standard -->

Classes SHOULD use nouns describing the concept represented.

Avoid generic suffixes unless meaningful.

---

# 40. Constant Naming Standard
<!-- id: structure.40-constant-naming-standard -->

Global constants SHOULD follow one documented convention.

Avoid hiding mutable state behind names that imply constancy.

---

# 41. Route Naming Standard
<!-- id: structure.41-route-naming-standard -->

Routes SHOULD be:

- stable
- readable
- predictable
- resource-oriented where appropriate

Avoid unnecessary route aliases.

---

# 42. API Naming Standard
<!-- id: structure.42-api-naming-standard -->

API resource names SHOULD align with domain terminology.

Do not use one term in the product and a different unexplained term in the API.

---

# 43. Database Naming Standard
<!-- id: structure.43-database-naming-standard -->

Database naming SHOULD be consistent across:

- tables
- columns
- indexes
- foreign keys
- constraints
- migrations

Document singular/plural conventions.

---

# 44. Terminology Alignment Standard
<!-- id: structure.44-terminology-alignment-standard -->

The same concept SHOULD use the same canonical terminology across:

- UI
- code
- API
- database
- analytics
- documentation
- support

Differences SHOULD be intentional and documented.

---

# 45. Root Directory Standard
<!-- id: structure.45-root-directory-standard -->

A repository root SHOULD remain easy to scan.

Typical root:

```text
/
  src/
  tests/
  docs/
  scripts/
  config/
  public/
  README.md
  package.json
```

Only include directories that have clear roles.

---

# 46. Source Directory Standard
<!-- id: structure.46-source-directory-standard -->

Application source SHOULD live under one predictable root such as:

```text
src/
```

Avoid source files scattered across the repository.

---

# 47. Test Directory Standard
<!-- id: structure.47-test-directory-standard -->

Choose one consistent test placement model:

- colocated tests
- centralized tests
- hybrid by test type

Document the convention.

---

# 48. Documentation Directory Standard
<!-- id: structure.48-documentation-directory-standard -->

Long-form internal documentation SHOULD have a predictable home such as:

```text
docs/
```

Do not rely exclusively on chat history or tickets as documentation.

---

# 49. Script Directory Standard
<!-- id: structure.49-script-directory-standard -->

Operational and development scripts SHOULD live in a dedicated location.

Example:

```text
scripts/
```

Each script SHOULD document:

- purpose
- arguments
- side effects
- required environment

---

# 50. Configuration Directory Standard
<!-- id: structure.50-configuration-directory-standard -->

Centralized configuration SHOULD live in a predictable location.

Avoid hidden configuration spread across unrelated modules.

---

# 51. Public Asset Standard
<!-- id: structure.51-public-asset-standard -->

Public/static assets SHOULD have a dedicated location.

Use meaningful subdirectories:

```text
public/
  images/
  icons/
  fonts/
```

---

# 52. Asset Naming Standard
<!-- id: structure.52-asset-naming-standard -->

Asset filenames SHOULD be descriptive.

Prefer:

`pricing-dashboard.webp`

Avoid:

`IMG_39482-final2.png`

---

# 53. Asset Ownership Standard
<!-- id: structure.53-asset-ownership-standard -->

Important assets SHOULD have:

- source file
- optimized output
- owner
- usage context

Avoid orphaned design exports with unknown origin.

---

# 54. Design System Directory Standard
<!-- id: structure.54-design-system-directory-standard -->

A design system SHOULD separate:

- foundations
- tokens
- primitives
- components
- patterns
- templates
- documentation

Example:

```text
design-system/
  tokens/
  foundations/
  components/
  patterns/
  templates/
```

---

# 55. Token Standard
<!-- id: structure.55-token-standard -->

Design values SHOULD come from tokens.

Tokenize:

- color
- spacing
- typography
- radius
- elevation
- motion
- breakpoints
- z-index
- semantic states

Avoid one-off values without reason.

---

# 56. Token Naming Standard
<!-- id: structure.56-token-naming-standard -->

Tokens SHOULD describe semantic purpose where possible.

Prefer:

```text
color.text.muted
color.action.primary
```

over:

```text
gray500
blue600
```

for application usage.

---

# 57. Primitive Component Standard
<!-- id: structure.57-primitive-component-standard -->

Primitive components SHOULD be:

- generic
- accessible
- predictable
- composable
- minimally opinionated

Examples:

- Button
- Input
- Dialog
- Tabs
- Tooltip

---

# 58. Composite Component Standard
<!-- id: structure.58-composite-component-standard -->

Composite components SHOULD represent reusable product patterns.

Examples:

- PricingCard
- UserPicker
- InvoiceSummary

Do not over-generalize domain components.

---

# 59. Pattern Standard
<!-- id: structure.59-pattern-standard -->

Document recurring UX patterns separately from primitive components.

Examples:

- onboarding flow
- destructive confirmation
- search/filter
- multi-step form
- permission request

---

# 60. Template Standard
<!-- id: structure.60-template-standard -->

Templates SHOULD assemble patterns for repeatable page types.

Examples:

- dashboard
- article
- product detail
- checkout
- settings

---

# 61. UI State Standard
<!-- id: structure.61-ui-state-standard -->

Reusable components SHOULD define:

- default
- hover
- focus
- active
- disabled
- loading
- error
- empty
- success

where applicable.

---

# 62. Responsive Structure Standard
<!-- id: structure.62-responsive-structure-standard -->

Responsive behavior SHOULD be defined as part of the component or layout system.

Do not treat mobile as a later override layer.

---

# 63. CSS Structure Standard
<!-- id: structure.63-css-structure-standard -->

CSS SHOULD follow one clear strategy.

Examples:

- component-scoped styles
- utility-first
- CSS modules
- design-system classes

Avoid combining several competing methodologies without governance.

---

# 64. CSS Layer Standard
<!-- id: structure.64-css-layer-standard -->

Where appropriate, organize styles into:

```text
reset
tokens
base
components
utilities
overrides
```

Keep overrides small.

---

# 65. Override Standard
<!-- id: structure.65-override-standard -->

Frequent overrides indicate structural problems.

Fix the underlying component or token before accumulating override files.

---

# 66. Z-Index Standard
<!-- id: structure.66-z-index-standard -->

Maintain a documented z-index scale.

Avoid arbitrary values such as:

`999999`

---

# 67. Responsive Breakpoint Standard
<!-- id: structure.67-responsive-breakpoint-standard -->

Use a small, documented breakpoint system.

Avoid component-specific magic breakpoints unless content requires them.

---

# 68. Content Structure Standard
<!-- id: structure.68-content-structure-standard -->

Content SHOULD use predictable levels:

```text
Section
  Topic
    Subtopic
```

Do not create a heading hierarchy based only on visual appearance.

---

# 69. Heading Standard
<!-- id: structure.69-heading-standard -->

Heading levels SHOULD represent semantic hierarchy.

Use:

- H1 for page subject
- H2 for major sections
- H3 for subsections

Avoid skipping levels without reason.

---

# 70. Page Template Standard
<!-- id: structure.70-page-template-standard -->

Common page types SHOULD have reusable structures.

Examples:

- landing page
- category page
- detail page
- article
- comparison
- help article

---

# 71. Content Block Standard
<!-- id: structure.71-content-block-standard -->

Reusable content blocks SHOULD have a clear purpose.

Examples:

- hero
- proof
- feature list
- testimonial
- comparison
- FAQ
- CTA

Do not create dozens of nearly identical block types.

---

# 72. Content Model Standard
<!-- id: structure.72-content-model-standard -->

Structured content SHOULD separate:

- data
- presentation
- relationships
- metadata

Avoid storing entire rendered layouts as opaque text when structured content would be easier to maintain.

---

# 73. CMS Model Standard
<!-- id: structure.73-cms-model-standard -->

CMS models SHOULD reflect stable content concepts.

Avoid creating a unique CMS content type for every page.

---

# 74. Taxonomy Standard
<!-- id: structure.74-taxonomy-standard -->

Taxonomies SHOULD have:

- clear definitions
- controlled naming
- limited overlap
- ownership
- documented parent/child relationships

---

# 75. Metadata Standard
<!-- id: structure.75-metadata-standard -->

Metadata SHOULD be consistent.

Examples:

- title
- description
- author
- publish date
- update date
- category
- tags
- status

---

# 76. Documentation Standard
<!-- id: structure.76-documentation-standard -->

Important systems SHOULD document:

- purpose
- architecture
- interfaces
- setup
- dependencies
- common operations
- failure modes
- ownership

---

# 77. README Standard
<!-- id: structure.77-readme-standard -->

Every meaningful repository or package SHOULD have a README.

Minimum content:

- purpose
- setup
- development commands
- build
- test
- deployment
- ownership/contact

---

# 78. Architecture Documentation Standard
<!-- id: structure.78-architecture-documentation-standard -->

Architecture documentation SHOULD explain:

- major components
- boundaries
- dependency direction
- data flow
- integrations
- major decisions

---

# 79. Architecture Decision Record Standard
<!-- id: structure.79-architecture-decision-record-standard -->

Important architectural decisions SHOULD be recorded.

ADR structure:

```text
Context
Decision
Alternatives
Consequences
Status
Date
```

---

# 80. Documentation Locality Standard
<!-- id: structure.80-documentation-locality-standard -->

Documentation SHOULD live near the thing it explains when possible.

Examples:

- package README beside package
- schema docs beside schema
- component examples beside component

---

# 81. Documentation Drift Standard
<!-- id: structure.81-documentation-drift-standard -->

Documentation MUST be updated when behavior materially changes.

Outdated documentation SHOULD be treated as a defect.

---

# 82. Code Comment Standard
<!-- id: structure.82-code-comment-standard -->

Comments SHOULD explain:

- why
- constraints
- unusual behavior
- external limitations

Do not comment obvious syntax.

---

# 83. TODO Standard
<!-- id: structure.83-todo-standard -->

TODOs SHOULD include:

- reason
- owner or ticket
- expected resolution path

Avoid anonymous permanent TODOs.

---

# 84. Example Standard
<!-- id: structure.84-example-standard -->

Complex public interfaces SHOULD include usage examples.

Examples SHOULD reflect current supported usage.

---

# 85. Onboarding Standard
<!-- id: structure.85-onboarding-standard -->

A new contributor SHOULD be able to:

1. clone/access the project
2. install dependencies
3. run locally
4. run tests
5. locate major domains
6. understand contribution rules

without relying on tribal knowledge.

---

# 86. Setup Automation Standard
<!-- id: structure.86-setup-automation-standard -->

Automate repetitive setup where practical.

Examples:

- dependency installation
- local environment bootstrap
- seed data
- lint/test commands

---

# 87. Environment Standard
<!-- id: structure.87-environment-standard -->

Environments SHOULD be clearly defined.

Typical:

- local
- development
- staging
- production

Avoid environment-specific behavior hidden in code.

---

# 88. Environment Variable Standard
<!-- id: structure.88-environment-variable-standard -->

Environment variables SHOULD:

- have descriptive names
- be documented
- have sample values where safe
- be validated at startup

---

# 89. Secret Standard
<!-- id: structure.89-secret-standard -->

Secrets MUST NOT be committed to source control.

Use a secret-management system appropriate to the environment.

---

# 90. Configuration Validation Standard
<!-- id: structure.90-configuration-validation-standard -->

Configuration SHOULD fail early when invalid.

Avoid silently falling back to unsafe or unexpected defaults.

---

# 91. Feature Flag Standard
<!-- id: structure.91-feature-flag-standard -->

Feature flags SHOULD have:

- owner
- purpose
- created date
- removal condition

Expired flags SHOULD be removed.

---

# 92. Dependency Standard
<!-- id: structure.92-dependency-standard -->

Dependencies SHOULD be added only when their value outweighs:

- maintenance
- bundle size
- security
- licensing
- upgrade cost

---

# 93. Dependency Ownership Standard
<!-- id: structure.93-dependency-ownership-standard -->

Important dependencies SHOULD have an owner or responsible team.

---

# 94. Dependency Upgrade Standard
<!-- id: structure.94-dependency-upgrade-standard -->

Upgrade dependencies intentionally.

Review:

- breaking changes
- security
- performance
- bundle impact
- deprecated APIs

---

# 95. Lockfile Standard
<!-- id: structure.95-lockfile-standard -->

Projects using dependency managers SHOULD commit the appropriate lockfile.

---

# 96. Version Pinning Standard
<!-- id: structure.96-version-pinning-standard -->

Critical dependencies SHOULD use predictable versioning.

Avoid production references to floating `latest`.

---

# 97. External Integration Standard
<!-- id: structure.97-external-integration-standard -->

Each integration SHOULD have:

- adapter/boundary
- configuration
- timeout
- error handling
- retry policy
- observability
- owner

---

# 98. Vendor Isolation Standard
<!-- id: structure.98-vendor-isolation-standard -->

External vendor-specific logic SHOULD be isolated.

Avoid spreading vendor SDK calls throughout domain code.

---

# 99. API Client Standard
<!-- id: structure.99-api-client-standard -->

API clients SHOULD centralize:

- base URL
- authentication
- retry
- timeout
- error normalization
- telemetry

---

# 100. Error Handling Standard
<!-- id: structure.100-error-handling-standard -->

Errors SHOULD have predictable structure.

Differentiate:

- validation errors
- authorization errors
- not-found errors
- external dependency errors
- internal failures

---

# 101. Error Ownership Standard
<!-- id: structure.101-error-ownership-standard -->

Errors SHOULD be handled at the layer with enough context to act correctly.

Do not catch errors only to hide them.

---

# 102. Logging Standard
<!-- id: structure.102-logging-standard -->

Logs SHOULD be:

- structured
- searchable
- meaningful
- appropriately leveled
- privacy-aware

---

# 103. Log Naming Standard
<!-- id: structure.103-log-naming-standard -->

Use stable event names.

Example:

```text
invoice.payment_failed
user.login_succeeded
```

---

# 104. Observability Standard
<!-- id: structure.104-observability-standard -->

Production systems SHOULD expose:

- logs
- metrics
- traces where appropriate
- health signals
- alerts

---

# 105. Analytics Event Standard
<!-- id: structure.105-analytics-event-standard -->

Analytics events SHOULD use one naming system.

Example:

```text
object_action
```

Such as:

```text
account_created
subscription_canceled
```

---

# 106. Analytics Schema Standard
<!-- id: structure.106-analytics-schema-standard -->

Analytics events SHOULD document:

- trigger
- properties
- owner
- source
- purpose

---

# 107. Data Model Standard
<!-- id: structure.107-data-model-standard -->

Data models SHOULD represent stable domain concepts.

Avoid tables or objects that mix unrelated responsibilities.

---

# 108. Schema Ownership Standard
<!-- id: structure.108-schema-ownership-standard -->

Each major schema SHOULD have an owner.

---

# 109. Migration Standard
<!-- id: structure.109-migration-standard -->

Database migrations SHOULD be:

- ordered
- immutable after deployment
- reviewed
- reversible where practical
- tested

---

# 110. Identifier Standard
<!-- id: structure.110-identifier-standard -->

Identifiers SHOULD use one strategy appropriate to the system.

Avoid exposing sequential internal IDs when unnecessary.

---

# 111. Timestamp Standard
<!-- id: structure.111-timestamp-standard -->

Timestamps SHOULD use a canonical timezone, typically UTC internally.

Display conversion belongs at presentation boundaries.

---

# 112. Soft Delete Standard
<!-- id: structure.112-soft-delete-standard -->

Use soft deletion only when business, recovery, audit, or legal needs require it.

Do not make everything soft-deleted by default.

---

# 113. Archive vs Delete Standard
<!-- id: structure.113-archive-vs-delete-standard -->

The data model SHOULD distinguish:

- active
- archived
- deleted

when these states have different semantics.

---

# 114. Validation Standard
<!-- id: structure.114-validation-standard -->

Validation SHOULD exist at appropriate boundaries.

Examples:

- UI
- API
- domain
- database

Do not rely on client-side validation alone.

---

# 115. Schema Reuse Standard
<!-- id: structure.115-schema-reuse-standard -->

Share schemas where they genuinely represent the same contract.

Do not force UI and persistence models to be identical.

---

# 116. Test Strategy Standard
<!-- id: structure.116-test-strategy-standard -->

Testing SHOULD include the right mix of:

- unit tests
- integration tests
- end-to-end tests
- accessibility tests
- visual tests where appropriate

---

# 117. Test Locality Standard
<!-- id: structure.117-test-locality-standard -->

Tests SHOULD be easy to find from the code they verify.

---

# 118. Test Naming Standard
<!-- id: structure.118-test-naming-standard -->

Tests SHOULD describe observable behavior.

Prefer:

`returns 403 when user lacks billing permission`

over:

`test billing auth`

---

# 119. Test Independence Standard
<!-- id: structure.119-test-independence-standard -->

Tests SHOULD avoid unnecessary shared mutable state.

---

# 120. Fixture Standard
<!-- id: structure.120-fixture-standard -->

Test fixtures SHOULD be:

- minimal
- readable
- reusable where appropriate
- clearly named

Avoid enormous universal fixtures.

---

# 121. Mocking Standard
<!-- id: structure.121-mocking-standard -->

Mock boundaries, not implementation details.

Excessive mocking often indicates excessive coupling.

---

# 122. CI Structure Standard
<!-- id: structure.122-ci-structure-standard -->

CI pipelines SHOULD be organized into understandable stages.

Typical:

```text
install
lint
typecheck
test
build
security
deploy
```

---

# 123. Fast Feedback Standard
<!-- id: structure.123-fast-feedback-standard -->

Run fast checks before expensive checks.

---

# 124. Quality Gate Standard
<!-- id: structure.124-quality-gate-standard -->

Important branches SHOULD require:

- passing tests
- lint
- type checks where applicable
- review
- build success

---

# 125. Code Review Standard
<!-- id: structure.125-code-review-standard -->

Reviews SHOULD evaluate:

- correctness
- readability
- structure
- maintainability
- security
- tests
- documentation
- naming

---

# 126. Review Size Standard
<!-- id: structure.126-review-size-standard -->

Prefer small, focused changes.

Large unrelated changes SHOULD be split when possible.

---

# 127. Commit Standard
<!-- id: structure.127-commit-standard -->

Commits SHOULD represent coherent changes.

Avoid mixing:

- formatting
- refactors
- features
- unrelated fixes

in one commit without reason.

---

# 128. Commit Message Standard
<!-- id: structure.128-commit-message-standard -->

Commit messages SHOULD explain the change clearly.

---

# 129. Branch Standard
<!-- id: structure.129-branch-standard -->

Use a predictable branch naming convention.

Example:

```text
feature/
fix/
chore/
docs/
```

---

# 130. Pull Request Standard
<!-- id: structure.130-pull-request-standard -->

Pull requests SHOULD explain:

- what changed
- why
- screenshots when visual
- testing
- risk
- follow-up work

---

# 131. Refactor Standard
<!-- id: structure.131-refactor-standard -->

Refactoring SHOULD improve structure without changing intended behavior.

Keep refactors focused.

---

# 132. Dead Code Standard
<!-- id: structure.132-dead-code-standard -->

Unused code SHOULD be removed.

Do not keep commented-out implementations indefinitely.

Version control is the archive.

---

# 133. Deprecated Code Standard
<!-- id: structure.133-deprecated-code-standard -->

Deprecated APIs SHOULD have:

- replacement
- migration path
- timeline
- owner

---

# 134. Technical Debt Standard
<!-- id: structure.134-technical-debt-standard -->

Technical debt SHOULD be visible and classified.

Potential categories:

- architecture
- dependencies
- testing
- performance
- accessibility
- documentation
- security

---

# 135. Debt Prioritization Standard
<!-- id: structure.135-debt-prioritization-standard -->

Prioritize debt based on:

- user impact
- change frequency
- operational risk
- developer friction
- security
- cost of delay

---

# 136. Ownership Standard
<!-- id: structure.136-ownership-standard -->

Important domains SHOULD have explicit owners.

Ownership SHOULD cover:

- code
- data
- design
- documentation
- operations

---

# 137. CODEOWNERS Standard
<!-- id: structure.137-codeowners-standard -->

Repositories MAY use automated ownership rules for high-risk areas.

---

# 138. Maintainer Standard
<!-- id: structure.138-maintainer-standard -->

Each shared package SHOULD have a clear maintainer.

---

# 139. Bus Factor Standard
<!-- id: structure.139-bus-factor-standard -->

Critical knowledge SHOULD NOT exist with only one person.

Document and cross-train high-risk areas.

---

# 140. Change Control Standard
<!-- id: structure.140-change-control-standard -->

Structural changes SHOULD include:

- rationale
- migration plan
- affected areas
- owners
- rollback strategy where needed

---

# 141. Migration Plan Standard
<!-- id: structure.141-migration-plan-standard -->

Large restructures SHOULD be incremental.

Prefer:

1. define target
2. migrate one domain
3. validate
4. migrate remaining areas
5. remove old structure

---

# 142. Big-Bang Rewrite Standard
<!-- id: structure.142-big-bang-rewrite-standard -->

Avoid full rewrites when incremental migration can achieve the same result.

---

# 143. Backward Compatibility Standard
<!-- id: structure.143-backward-compatibility-standard -->

Public interfaces SHOULD maintain compatibility when practical.

Breaking changes SHOULD be versioned and documented.

---

# 144. Versioning Standard
<!-- id: structure.144-versioning-standard -->

Use a clear versioning policy for:

- APIs
- packages
- schemas
- design systems
- documentation

---

# 145. Release Structure Standard
<!-- id: structure.145-release-structure-standard -->

Releases SHOULD have:

- version
- date
- summary
- notable changes
- breaking changes
- migration notes

---

# 146. Changelog Standard
<!-- id: structure.146-changelog-standard -->

Maintain a changelog for public or shared systems where useful.

---

# 147. Deprecation Standard
<!-- id: structure.147-deprecation-standard -->

Deprecation SHOULD communicate:

- deprecated element
- replacement
- deadline
- impact

---

# 148. Archive Standard
<!-- id: structure.148-archive-standard -->

Archived projects SHOULD be clearly marked.

Include:

- archive date
- reason
- replacement
- read-only status

---

# 149. Repository Standard
<!-- id: structure.149-repository-standard -->

A repository SHOULD represent a coherent unit of ownership and release.

Do not split repositories merely by technical layer without operational benefit.

---

# 150. Monorepo Standard
<!-- id: structure.150-monorepo-standard -->

Monorepos SHOULD define:

- package boundaries
- dependency rules
- ownership
- build caching
- release strategy

---

# 151. Multi-Repo Standard
<!-- id: structure.151-multi-repo-standard -->

Multi-repo systems SHOULD document:

- service map
- API ownership
- shared libraries
- release dependencies
- local setup

---

# 152. Service Boundary Standard
<!-- id: structure.152-service-boundary-standard -->

A service SHOULD own a meaningful business or technical capability.

Do not create microservices simply to split files.

---

# 153. Microservice Standard
<!-- id: structure.153-microservice-standard -->

A microservice SHOULD have independent:

- ownership
- deployment
- observability
- data responsibility
- interface

---

# 154. Monolith Standard
<!-- id: structure.154-monolith-standard -->

A monolith MAY be well structured.

Prefer a modular monolith over premature distributed complexity.

---

# 155. Package Standard
<!-- id: structure.155-package-standard -->

Packages SHOULD have:

- clear responsibility
- public API
- version
- tests
- README
- owner

---

# 156. Dependency Graph Standard
<!-- id: structure.156-dependency-graph-standard -->

Large systems SHOULD make dependency relationships inspectable.

---

# 157. Import Rule Standard
<!-- id: structure.157-import-rule-standard -->

Automated lint rules SHOULD enforce important dependency boundaries where feasible.

---

# 158. Layer Violation Standard
<!-- id: structure.158-layer-violation-standard -->

Imports that bypass architecture SHOULD be treated as violations, not normal shortcuts.

---

# 159. Readability Standard
<!-- id: structure.159-readability-standard -->

Code and documents SHOULD optimize for the next reader.

Prefer clarity over terseness.

---

# 160. Function Size Standard
<!-- id: structure.160-function-size-standard -->

Functions SHOULD remain small enough to understand without excessive scrolling.

Split by responsibility, not arbitrary line limits.

---

# 161. File Size Standard
<!-- id: structure.161-file-size-standard -->

Large files SHOULD trigger review.

A large file is not automatically wrong, but may indicate mixed responsibilities.

---

# 162. Complexity Standard
<!-- id: structure.162-complexity-standard -->

High cyclomatic or cognitive complexity SHOULD trigger refactoring review.

---

# 163. Nesting Standard
<!-- id: structure.163-nesting-standard -->

Deep conditional nesting SHOULD be reduced where practical.

Prefer:

- early returns
- extracted functions
- explicit state machines

---

# 164. Condition Standard
<!-- id: structure.164-condition-standard -->

Complex business conditions SHOULD be named.

Prefer:

```text
canUserManageBilling
```

over repeated long boolean expressions.

---

# 165. State Machine Standard
<!-- id: structure.165-state-machine-standard -->

Complex workflows SHOULD use explicit state models.

Examples:

- checkout
- onboarding
- approval
- subscription lifecycle

---

# 166. Magic Value Standard
<!-- id: structure.166-magic-value-standard -->

Avoid unexplained magic numbers and strings.

Use named constants or configuration.

---

# 167. Commented Code Standard
<!-- id: structure.167-commented-code-standard -->

Commented-out code SHOULD be removed.

---

# 168. Formatting Standard
<!-- id: structure.168-formatting-standard -->

Use automated formatting where possible.

Formatting discussions SHOULD NOT consume code-review time.

---

# 169. Linting Standard
<!-- id: structure.169-linting-standard -->

Use linting to enforce:

- syntax
- conventions
- unsafe patterns
- architecture rules where practical

---

# 170. Type Safety Standard
<!-- id: structure.170-type-safety-standard -->

Where supported, use type systems to make contracts explicit.

Avoid bypassing type safety without documented reason.

---

# 171. Interface Standard
<!-- id: structure.171-interface-standard -->

Interfaces SHOULD express stable contracts, not every internal detail.

---

# 172. Generic Standard
<!-- id: structure.172-generic-standard -->

Generics SHOULD improve reuse without obscuring intent.

Do not create highly abstract generic APIs for trivial reuse.

---

# 173. Read Path Standard
<!-- id: structure.173-read-path-standard -->

Critical user and developer workflows SHOULD have a clear "read path."

A reader should know where to start.

Examples:

- README
- route
- feature entry
- use case
- domain model

---

# 174. Execution Path Standard
<!-- id: structure.174-execution-path-standard -->

Complex flows SHOULD make orchestration obvious.

Avoid business logic hidden across unrelated event handlers.

---

# 175. Command / Query Standard
<!-- id: structure.175-command-query-standard -->

Where useful, distinguish operations that:

- change state
- read state

This improves traceability.

---

# 176. Side Effect Standard
<!-- id: structure.176-side-effect-standard -->

Side effects SHOULD occur at clear boundaries.

Avoid hidden network, storage, or logging effects in seemingly pure helpers.

---

# 177. Global State Standard
<!-- id: structure.177-global-state-standard -->

Global state SHOULD be minimized.

Use global state only for genuinely global concerns.

---

# 178. Local State Standard
<!-- id: structure.178-local-state-standard -->

Keep state as close as possible to where it is used.

---

# 179. Cache Standard
<!-- id: structure.179-cache-standard -->

Caches SHOULD have:

- purpose
- ownership
- invalidation rules
- TTL
- monitoring

---

# 180. Async Standard
<!-- id: structure.180-async-standard -->

Asynchronous flows SHOULD expose:

- loading
- success
- failure
- retry
- cancellation where appropriate

---

# 181. Retry Standard
<!-- id: structure.181-retry-standard -->

Retries SHOULD be bounded.

Avoid infinite retry loops.

---

# 182. Timeout Standard
<!-- id: structure.182-timeout-standard -->

External calls SHOULD have explicit timeouts.

---

# 183. Idempotency Standard
<!-- id: structure.183-idempotency-standard -->

Operations that may be retried SHOULD be idempotent where practical.

---

# 184. Permission Structure Standard
<!-- id: structure.184-permission-structure-standard -->

Permissions SHOULD use a documented model.

Examples:

- role-based
- attribute-based
- resource-based

---

# 185. Role Standard
<!-- id: structure.185-role-standard -->

Roles SHOULD group permissions with clear meaning.

Avoid roles with overlapping unclear responsibilities.

---

# 186. Policy Standard
<!-- id: structure.186-policy-standard -->

Authorization policy SHOULD live in a predictable layer.

Avoid permission checks scattered inconsistently through UI code.

---

# 187. Security Boundary Standard
<!-- id: structure.187-security-boundary-standard -->

Authentication and authorization boundaries SHOULD be explicit.

---

# 188. Accessibility Structure Standard
<!-- id: structure.188-accessibility-structure-standard -->

Accessibility SHOULD be structural.

Use:

- semantic HTML
- logical heading order
- predictable focus
- accessible labels
- consistent navigation

---

# 189. Performance Structure Standard
<!-- id: structure.189-performance-structure-standard -->

Performance SHOULD be considered in architecture.

Avoid structures that require loading entire systems for small tasks.

---

# 190. Lazy Loading Standard
<!-- id: structure.190-lazy-loading-standard -->

Heavy features SHOULD be loaded when needed.

Examples:

- charts
- maps
- editors
- 3D
- large admin modules

---

# 191. Bundle Boundary Standard
<!-- id: structure.191-bundle-boundary-standard -->

Bundle boundaries SHOULD roughly align with user journeys or feature domains.

---

# 192. Image Organization Standard
<!-- id: structure.192-image-organization-standard -->

Images SHOULD be organized by:

- feature
- page
- asset type

Avoid a single giant images directory.

---

# 193. Font Standard
<!-- id: structure.193-font-standard -->

Fonts SHOULD be centrally managed.

Do not load unrelated font families from multiple components.

---

# 194. Icon Standard
<!-- id: structure.194-icon-standard -->

Use one primary icon system.

Avoid mixing several icon families with inconsistent visual language.

---

# 195. Localization Structure Standard
<!-- id: structure.195-localization-structure-standard -->

Localization files SHOULD be organized by:

- locale
- namespace/domain
- feature

Avoid one huge translation file.

---

# 196. Translation Key Standard
<!-- id: structure.196-translation-key-standard -->

Translation keys SHOULD be semantic and stable.

Avoid using full English sentences as permanent identifiers in large systems unless that is the chosen i18n model.

---

# 197. Content Ownership Standard
<!-- id: structure.197-content-ownership-standard -->

Content categories SHOULD have owners.

Examples:

- marketing
- support
- legal
- product
- documentation

---

# 198. Content Lifecycle Standard
<!-- id: structure.198-content-lifecycle-standard -->

Content SHOULD have lifecycle states.

Example:

```text
Draft
Review
Approved
Published
Archived
```

---

# 199. Review Cadence Standard
<!-- id: structure.199-review-cadence-standard -->

Time-sensitive documentation and content SHOULD define review cadence.

---

# 200. Searchability Standard
<!-- id: structure.200-searchability-standard -->

Structure SHOULD support search.

Names, headings, metadata, and file paths SHOULD contain meaningful terms.

---

# 201. Discoverability Standard
<!-- id: structure.201-discoverability-standard -->

Important information SHOULD be reachable through:

- navigation
- index pages
- search
- links
- README files

Do not rely on hidden tribal knowledge.

---

# 202. Index Standard
<!-- id: structure.202-index-standard -->

Large documentation areas SHOULD have index pages.

---

# 203. Cross-Link Standard
<!-- id: structure.203-cross-link-standard -->

Related documentation SHOULD link to each other.

---

# 204. Broken Link Standard
<!-- id: structure.204-broken-link-standard -->

Internal links SHOULD be validated automatically where practical.

---

# 205. Source of Truth Standard
<!-- id: structure.205-source-of-truth-standard -->

The project SHOULD explicitly identify the authoritative location for:

- product requirements
- design
- code
- API contracts
- data schemas
- legal text
- documentation

---

# 206. Duplicate Documentation Standard
<!-- id: structure.206-duplicate-documentation-standard -->

Avoid maintaining the same authoritative documentation in multiple locations.

Use links or generated copies instead.

---

# 207. Generated Documentation Standard
<!-- id: structure.207-generated-documentation-standard -->

Generated documentation SHOULD be reproducible from source.

---

# 208. API Documentation Standard
<!-- id: structure.208-api-documentation-standard -->

API docs SHOULD be generated from or validated against actual API contracts where possible.

---

# 209. Schema Documentation Standard
<!-- id: structure.209-schema-documentation-standard -->

Data schemas SHOULD be documented alongside:

- field definitions
- constraints
- ownership
- lifecycle

---

# 210. Design Documentation Standard
<!-- id: structure.210-design-documentation-standard -->

Design components SHOULD document:

- purpose
- anatomy
- states
- variants
- accessibility
- usage
- anti-patterns

---

# 211. Pattern Library Standard
<!-- id: structure.211-pattern-library-standard -->

Recurring implementation patterns SHOULD be documented.

Examples:

- table filtering
- pagination
- error handling
- forms
- permissions
- notifications

---

# 212. Reference Implementation Standard
<!-- id: structure.212-reference-implementation-standard -->

Important patterns SHOULD have a reference implementation.

---

# 213. Starter Template Standard
<!-- id: structure.213-starter-template-standard -->

New modules or services MAY use templates to preserve consistency.

Templates SHOULD be easy to update.

---

# 214. Scaffolding Standard
<!-- id: structure.214-scaffolding-standard -->

Automated scaffolding SHOULD create only useful files.

Avoid generating large amounts of boilerplate nobody understands.

---

# 215. Generator Ownership Standard
<!-- id: structure.215-generator-ownership-standard -->

Code generators SHOULD have:

- owner
- templates
- tests
- versioning

---

# 216. Architecture Fitness Standard
<!-- id: structure.216-architecture-fitness-standard -->

Automated checks SHOULD validate structural rules where practical.

Examples:

- import boundaries
- circular dependencies
- forbidden folders
- naming
- package dependency rules

---

# 217. Complexity Budget Standard
<!-- id: structure.217-complexity-budget-standard -->

Large systems SHOULD set practical limits for:

- dependency depth
- bundle size
- component complexity
- page weight
- test runtime

---

# 218. Module Growth Standard
<!-- id: structure.218-module-growth-standard -->

Modules SHOULD be reviewed when they become disproportionately large.

Potential responses:

- split subdomains
- extract services
- separate read/write paths
- isolate integrations

---

# 219. Ownership Growth Standard
<!-- id: structure.219-ownership-growth-standard -->

A domain SHOULD not outgrow the team responsible for understanding it.

---

# 220. Maintenance Window Standard
<!-- id: structure.220-maintenance-window-standard -->

Allocate regular maintenance work.

Do not rely only on emergency refactoring.

---

# 221. Cleanup Standard
<!-- id: structure.221-cleanup-standard -->

Periodic cleanup SHOULD include:

- dead files
- unused dependencies
- stale flags
- obsolete docs
- deprecated APIs
- abandoned experiments

---

# 222. Archival Standard
<!-- id: structure.222-archival-standard -->

Old content and code SHOULD be archived or removed intentionally.

Do not leave ambiguous abandoned artifacts in active structures.

---

# 223. Experimental Code Standard
<!-- id: structure.223-experimental-code-standard -->

Experiments SHOULD be clearly separated from production paths.

Example:

```text
experiments/
```

with owners and expiration dates.

---

# 224. Prototype Standard
<!-- id: structure.224-prototype-standard -->

Prototypes SHOULD NOT silently become production architecture.

Productionize intentionally.

---

# 225. Temporary Standard
<!-- id: structure.225-temporary-standard -->

Temporary files and workarounds SHOULD have removal plans.

Avoid naming production artifacts:

- temp
- new
- old
- final
- final2

---

# 226. Migration File Standard
<!-- id: structure.226-migration-file-standard -->

Migration-specific code SHOULD be isolated and removable after completion.

---

# 227. Compatibility Layer Standard
<!-- id: structure.227-compatibility-layer-standard -->

Compatibility code SHOULD be documented and scheduled for removal when obsolete.

---

# 228. Feature Retirement Standard
<!-- id: structure.228-feature-retirement-standard -->

Retiring a feature SHOULD include:

1. stop new usage
2. migrate users/data
3. remove entry points
4. remove code
5. remove docs
6. remove analytics
7. remove flags/config

---

# 229. Structure Review Standard
<!-- id: structure.229-structure-review-standard -->

Structural reviews SHOULD ask:

- Is this where a new contributor would look?
- Does the name reveal purpose?
- Does this domain have a clear boundary?
- Is the owner obvious?
- Is there duplication?
- Can this be tested independently?
- Can it be removed safely?
- Is the documentation current?

---

# 230. Readability Review Standard
<!-- id: structure.230-readability-review-standard -->

Before merging, reviewers SHOULD ask:

- Can I understand the intent without reconstructing hidden context?
- Are names precise?
- Are functions focused?
- Are dependencies obvious?
- Is the control flow straightforward?

---

# 231. Maintainability Review Standard
<!-- id: structure.231-maintainability-review-standard -->

Evaluate whether a future change would require editing many unrelated files.

If yes, inspect for excessive coupling.

---

# 232. Scalability Review Standard
<!-- id: structure.232-scalability-review-standard -->

Scalability includes more than traffic.

Evaluate scalability of:

- code organization
- team ownership
- data
- releases
- documentation
- design system
- support

---

# 233. Team Scalability Standard
<!-- id: structure.233-team-scalability-standard -->

Structure SHOULD allow teams to work independently with minimal collisions.

---

# 234. Ownership Boundary Standard
<!-- id: structure.234-ownership-boundary-standard -->

Ownership boundaries SHOULD align with meaningful architecture where possible.

---

# 235. Cross-Team Contract Standard
<!-- id: structure.235-cross-team-contract-standard -->

Cross-team dependencies SHOULD use documented contracts.

---

# 236. Handoff Standard
<!-- id: structure.236-handoff-standard -->

Handoffs SHOULD include:

- owner
- interface
- expectations
- failure path
- escalation

---

# 237. Project Structure Example — Small Website
<!-- id: structure.237-project-structure-example-small-website -->

```text
/
  src/
    pages/
    components/
    layouts/
    styles/
    content/
  public/
    images/
    icons/
  tests/
  docs/
  README.md
```

---

# 238. Project Structure Example — SaaS Application
<!-- id: structure.238-project-structure-example-saas-application -->

```text
/
  src/
    app/
      routing/
      providers/
      shell/

    features/
      authentication/
      billing/
      onboarding/
      reporting/
      settings/

    shared/
      components/
      hooks/
      utilities/
      types/

    infrastructure/
      api/
      analytics/
      storage/
      integrations/

  tests/
    e2e/

  docs/
    architecture/
    product/
    operations/

  public/
  scripts/
  config/
  README.md
```

---

# 239. Feature Structure Example
<!-- id: structure.239-feature-structure-example -->

```text
features/
  billing/
    components/
    hooks/
    api/
    schemas/
    types/
    tests/
    index.ts
```

Only include folders that are actually needed.

---

# 240. Design System Structure Example
<!-- id: structure.240-design-system-structure-example -->

```text
design-system/
  tokens/
    color
    spacing
    typography
    radius
    motion

  foundations/
    accessibility
    grid
    typography

  components/
    button
    input
    dialog
    tabs

  patterns/
    forms
    navigation
    tables
    onboarding

  templates/
    dashboard
    settings
    detail-page

  docs/
```

---

# 241. Documentation Structure Example
<!-- id: structure.241-documentation-structure-example -->

```text
docs/
  getting-started/
  architecture/
  product/
  api/
  design-system/
  operations/
  security/
  decisions/
```

---

# 242. Content Repository Structure Example
<!-- id: structure.242-content-repository-structure-example -->

```text
content/
  pages/
  articles/
  industries/
  glossary/
  policies/
  media/
  metadata/
```

---

# 243. API Structure Example
<!-- id: structure.243-api-structure-example -->

```text
api/
  routes/
  controllers/
  services/
  domain/
  repositories/
  schemas/
  middleware/
  tests/
```

The exact layering MAY differ, but responsibility boundaries SHOULD remain clear.

---

# 244. Repository Root Checklist
<!-- id: structure.244-repository-root-checklist -->

- [ ] README exists
- [ ] source has one predictable location
- [ ] tests have a defined location
- [ ] docs have a defined location
- [ ] scripts have a defined location
- [ ] configuration is discoverable
- [ ] generated output is separated
- [ ] temporary files are excluded

---

# 245. Folder Structure Checklist
<!-- id: structure.245-folder-structure-checklist -->

- [ ] folders have clear responsibilities
- [ ] hierarchy is not unnecessarily deep
- [ ] large folders are grouped meaningfully
- [ ] shared folders are not dumping grounds
- [ ] naming follows one convention
- [ ] ownership is clear
- [ ] deprecated folders are removed

---

# 246. Code Structure Checklist
<!-- id: structure.246-code-structure-checklist -->

- [ ] feature boundaries are clear
- [ ] dependency direction is predictable
- [ ] no circular dependencies
- [ ] public APIs are explicit
- [ ] deep imports are limited
- [ ] utilities are focused
- [ ] business rules are centralized
- [ ] side effects occur at boundaries
- [ ] state ownership is clear

---

# 247. Design Structure Checklist
<!-- id: structure.247-design-structure-checklist -->

- [ ] tokens are centralized
- [ ] primitives are reusable
- [ ] patterns are documented
- [ ] states are complete
- [ ] accessibility is built in
- [ ] one icon system is used
- [ ] visual overrides are limited
- [ ] responsive behavior is defined
- [ ] components have owners

---

# 248. Documentation Checklist
<!-- id: structure.248-documentation-checklist -->

- [ ] README is current
- [ ] architecture is documented
- [ ] key decisions have ADRs
- [ ] public APIs have examples
- [ ] setup instructions work
- [ ] ownership is listed
- [ ] obsolete documentation is removed
- [ ] cross-links are valid

---

# 249. Maintainability Checklist
<!-- id: structure.249-maintainability-checklist -->

- [ ] important values have one source of truth
- [ ] naming is predictable
- [ ] duplicated business logic is minimized
- [ ] feature flags have expiry plans
- [ ] deprecated code has migration plans
- [ ] dependencies are intentional
- [ ] technical debt is tracked
- [ ] dead code is removed

---

# 250. Readability Checklist
<!-- id: structure.250-readability-checklist -->

- [ ] names reveal intent
- [ ] functions are focused
- [ ] files are understandable
- [ ] control flow is straightforward
- [ ] comments explain why
- [ ] magic values are named
- [ ] complex conditions are extracted
- [ ] formatting is automated

---

# 251. Scalability Checklist
<!-- id: structure.251-scalability-checklist -->

- [ ] domains can grow independently
- [ ] ownership can scale across teams
- [ ] dependency boundaries are enforceable
- [ ] shared packages have maintainers
- [ ] documentation scales with the architecture
- [ ] CI remains understandable
- [ ] build/test performance is monitored

---

# 252. Change Safety Checklist
<!-- id: structure.252-change-safety-checklist -->

Before significant changes:

- [ ] affected domain identified
- [ ] dependencies identified
- [ ] tests updated
- [ ] documentation updated
- [ ] migration plan defined
- [ ] rollback considered
- [ ] analytics impact reviewed
- [ ] compatibility reviewed

---

# 253. 100-Point Structure Quality Score
<!-- id: structure.253-100-point-structure-quality-score -->

Use this as an internal QA framework.

## Organization — 20 points

- predictable hierarchy: 5
- clear domain grouping: 5
- shallow meaningful nesting: 3
- no dumping-ground folders: 4
- canonical locations: 3

## Readability — 20 points

- naming quality: 5
- focused files/modules: 4
- straightforward control flow: 4
- clear interfaces: 4
- useful documentation/comments: 3

## Maintainability — 20 points

- low duplication: 4
- low coupling: 5
- stable boundaries: 5
- dependency discipline: 3
- technical debt visibility: 3

## Consistency — 15 points

- naming conventions: 3
- structure conventions: 3
- design-system consistency: 3
- API/data consistency: 3
- documentation consistency: 3

## Scalability — 10 points

- team ownership scales: 3
- modules can grow independently: 3
- build/test structure scales: 2
- documentation scales: 2

## Change Safety — 10 points

- tests: 3
- versioning/migrations: 2
- observability: 2
- change control: 2
- deprecation process: 1

## Governance — 5 points

- ownership: 2
- architecture decisions recorded: 1
- review process: 1
- cleanup cadence: 1

---

# 254. Quality Thresholds
<!-- id: structure.254-quality-thresholds -->

Internal recommendation:

- 90–100 = excellent structural quality
- 80–89 = strong
- 70–79 = usable but needs consolidation
- 60–69 = increasingly fragile
- below 60 = restructuring recommended

Critical failures override the numeric score.

---

# 255. Critical Structural Failures
<!-- id: structure.255-critical-structural-failures -->

Treat these as high-priority issues:

- no clear source of truth
- circular architecture
- hidden global state controlling core behavior
- undocumented critical dependencies
- no owner for critical domains
- duplicated business rules causing contradictory behavior
- shared/common folders containing unrelated code
- structural conventions changing feature by feature
- no reliable test location or strategy
- production behavior depending on undocumented manual steps
- old and new architectures running indefinitely without migration ownership
- documentation materially contradicting implementation

---

# 256. Structure Strategy Priority Order
<!-- id: structure.256-structure-strategy-priority-order -->

When creating or improving structure:

1. Define product/domain boundaries.
2. Define canonical terminology.
3. Define ownership.
4. Define dependency direction.
5. Define predictable file/folder conventions.
6. Centralize configuration and source-of-truth values.
7. Build shared abstractions only after real reuse exists.
8. Add automated lint/test/architecture checks.
9. Document important architecture and decisions.
10. Establish recurring cleanup and review.

---

# 257. Final Standard
<!-- id: structure.257-final-standard -->

The best structure is not the structure with the most folders, abstractions, layers, or patterns.

The best structure is the one where a competent contributor can quickly understand:

- what exists
- where it belongs
- how it relates
- who owns it
- how it changes
- how it is tested
- how it is documented
- how it can be removed

A maintainable system should make the correct place for new work obvious.

Consistency should reduce decisions.

Organization should reduce searching.

Readability should reduce interpretation.

Boundaries should reduce accidental coupling.

Documentation should reduce tribal knowledge.

Automation should reduce drift.

Structure should make future change easier, not merely make today's repository look tidy.

# Control Plane Hooks
<!-- id: structure.control-plane-hooks -->

When this module is active, use `CONTROL_INDEX.md` to retrieve only the capability sections relevant to the current decision. Applicable capabilities include:

- **Primary-task mapping** — `controls/08-ux-strategy-and-information-architecture.md` (BQ-0281–BQ-0285)
- **Journey-state model** — `controls/08-ux-strategy-and-information-architecture.md` (BQ-0286–BQ-0290)
- **Information-scent standard** — `controls/08-ux-strategy-and-information-architecture.md` (BQ-0291–BQ-0295)
- **Content-priority hierarchy** — `controls/08-ux-strategy-and-information-architecture.md` (BQ-0296–BQ-0300)
- **Navigation complexity budget** — `controls/08-ux-strategy-and-information-architecture.md` (BQ-0301–BQ-0305)
- **Edge-state architecture** — `controls/08-ux-strategy-and-information-architecture.md` (BQ-0306–BQ-0310)
- **Cross-page continuity** — `controls/08-ux-strategy-and-information-architecture.md` (BQ-0311–BQ-0315)
- **Mobile navigation states** — `controls/13-responsive-mobile-and-cross-device-design.md` (BQ-0501–BQ-0505)
- **Cross-device continuity** — `controls/13-responsive-mobile-and-cross-device-design.md` (BQ-0516–BQ-0520)
- **Message-hierarchy map** — `controls/15-content-copy-and-terminology.md` (BQ-0561–BQ-0565)
- **Semantic-component mapping** — `controls/17-front-end-engineering-and-component-implementation.md` (BQ-0641–BQ-0645)
- **Data-model-first planning** — `controls/18-application-logic-data-and-integrations.md` (BQ-0681–BQ-0685)
- **Answerability design** — `controls/20-seo-geo-aeo-and-discoverability.md` (BQ-0776–BQ-0780)
- **Internal-link intent** — `controls/20-seo-geo-aeo-and-discoverability.md` (BQ-0791–BQ-0795)
- **Config-vs-content separation** — `controls/24-packaging-delivery-and-repository-integration.md` (BQ-0936–BQ-0940)

These hooks are routing pointers, not permission to preload the listed shards. Evidence Gates control pass/fail claims.
