<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: MATERIALIZATION_CLOSURE
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Domain-Specific Materialization & Artifact Naturalization
<!-- id: materialization-closure.root -->

Core 1.8.2 closes the repeated Stable-2.0 Holdout-2 failure cluster in which an artifact could satisfy the shape of a compiler/evidence contract while remaining shallow, generic, or visibly written in internal BizIQ/QA vocabulary. This module is fail-closed for substantial high-fidelity artifacts and supplements, rather than replaces, family depth, truth boundaries, completeness, accessibility, and artifact contracts.

# Naturalization Boundary
<!-- id: materialization-closure.naturalization -->

Production-facing copy, labels, headings, controls, diagrams, slides, worksheets, CLI help, and customer-visible annotations MUST be written in the vocabulary of the user, business, workflow, and artifact. Internal orchestration terms are implementation metadata, not user-facing content. Unless the user explicitly asks for BizIQ process documentation, production artifacts MUST NOT expose labels such as `P0`, `P1`, `decision depth closure`, `truth boundary`, `feature depth`, `quality gate`, `genericity`, `artifact contract`, `evidence plan`, `compiler`, `QA gate`, `acceptance ledger`, or equivalent internal control language.

Internal requirements MUST be translated into natural artifact language. For example, an internal requirement for a secondary decision path becomes a concrete comparison, qualification, preparation, support, or evaluation journey appropriate to the domain; it does not become a section titled "Secondary Decision Path".

# Concrete Domain Materialization
<!-- id: materialization-closure.domain-materialization -->

Every substantial P0/P1 requirement MUST materialize into domain-specific content, data, state, action, rule, proof need, recovery, or decision support. Generic placeholders such as `service one`, `feature A`, `proof block`, `learn more`, `workflow step`, or `relevant evidence` do not satisfy materialization unless the artifact is explicitly a wireframe/low-fidelity concept.

A materialization record MUST connect:

`user job / decision -> domain-specific need -> concrete artifact surface -> user-facing language/data -> action or state -> evidence/truth boundary -> continuation or outcome`.

At least one field in each record MUST be specific enough that a competitor in a materially different industry could not reuse it unchanged without becoming inaccurate or nonsensical.

# Website & Mobile Materialization
<!-- id: materialization-closure.web-mobile -->

Public websites and mobile products MUST derive first-pass depth from real visitor/user questions, qualification criteria, preparation needs, comparison dimensions, service/product constraints, state transitions, recovery conditions, and downstream outcomes. The first pass MUST include enough concrete material to make primary and secondary journeys usable without relying on generic architecture labels.

For service/marketing websites, this normally includes domain-specific offering detail, who/what is a fit, preparation or process expectations, material constraints/unknowns, proof requirements, objections or evaluation criteria, and a concrete next-state after conversion. For mobile products, workflow states MUST expose domain-relevant objects, values, decisions, interruptions, and recovery—not merely generic cards labeled `Task`, `Status`, or `Step`.

# Brand & Campaign Materialization
<!-- id: materialization-closure.brand-campaign -->

Brand systems MUST define actual rules, not category inventories. Typography, color, composition, iconography, imagery, and identity records MUST include a concrete role, observable rule, misuse boundary, and application behavior. Sample claims or proof-bearing examples MUST remain clearly sample/unknown unless supplied or sourced.

Email/campaign artifacts MUST materialize audience state, reason-for-message, useful proof or explanation, concrete CTA semantics, expected downstream event, fallback/recovery, and next lifecycle state. Subject/body/CTA content must be audience- and domain-specific enough that the sequence could not be transplanted unchanged into an unrelated product.

# Non-Web Reading & Decision Surfaces
<!-- id: materialization-closure.nonweb-reading -->

Presentations, spreadsheets/models, and fixed-format documents MUST materialize their intended reading/decision job rather than exposing the evaluation scaffold. Decks require concrete decision questions, evidence, implications, and next-state material; spreadsheets require explicit assumptions, editable inputs, derived outputs, scenarios, decision surfaces, and source/provenance boundaries; fixed documents require concrete findings/requirements/actions plus readable hierarchy, tables/figures where useful, and accessible reading order.

Accessibility is part of materialization: meaning may not depend on internal labels, visual position alone, color alone, or inaccessible exported structure.

# CLI Interface Naturalization
<!-- id: materialization-closure.cli -->

CLI output is a user interface. Commands, help, errors, stdout/stderr, exit semantics, examples, configuration names, and recovery guidance MUST use task/domain vocabulary. Internal compiler terminology MUST not leak into normal help/output. At least one happy-path and one error/recovery path MUST show concrete, ergonomic output with stable labels, actionable guidance, and deterministic semantics.

# Executable Acceptance
<!-- id: materialization-closure.acceptance -->

Use `schemas/materialization_evidence.schema.json` and `tools/validate_materialization_evidence.py`. Evidence is direct and fail-closed. The validator checks minimum domain-materialization records, concrete specificity, distinct jobs/surfaces, naturalized user-facing language, absence of prohibited internal vocabulary, family-specific materialization, and catastrophic failures. Missing or generic evidence is UNVERIFIED/NON-PASS.

# Recovery
<!-- id: materialization-closure.recovery -->

Repair the upstream domain materialization, not the score. Replace generic labels/content with concrete user/business/workflow material; add missing states/actions/proof needs; and translate internal requirements into natural artifact language. Preserve already-passing routing, retrieval budgets, truth boundaries, and interaction/file-integrity evidence.
