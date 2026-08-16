<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: DOCUMENT_CRAFT
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-09
-->

# Document Decision Depth & Editorial Craft
<!-- id: document-craft.root -->

Purpose: evaluate documents by decision/evidence depth rather than app-style interaction depth.

# Document Depth Model
<!-- id: document-craft.depth-model -->
A substantial decision document resolves, as applicable: question/decision, scope, known facts, evidence, assumptions/unknowns, analytical method, findings, implications, alternatives, risks, recommendation, owner/action/timing, verification, and traceability. Missing interactive states do not penalize a fixed document; missing decision/evidence links do.

# Evidence Chain
<!-- id: document-craft.evidence-chain -->
Important conclusions SHOULD be traceable through `claim/finding → evidence or supplied fact → interpretation → implication → recommendation/action`. Unknown evidence stays unknown. Recommendations without visible rationale fail high-depth acceptance.

# Document-Type Completeness
<!-- id: document-craft.type-completeness -->
Use document-specific structures rather than a universal report shell. Examples: experiment reports require hypothesis/method/result/limitations; postmortems require impact/timeline/detection/contributing factors/recovery/actions; PRDs require problems/scope/requirements/states/dependencies/acceptance; legal memos require issue/rule/analysis/conclusion with supplied authority boundaries; system design requires requirements/architecture/flows/tradeoffs/failure modes/acceptance.

# Editorial Composition
<!-- id: document-craft.editorial-composition -->
Use typography, page rhythm, tables, diagrams, evidence callouts, comparison, decision matrices, timelines, risk matrices, and action tables according to information purpose. Avoid repeating rounded cards for every finding. Long-form reading must preserve hierarchy and scanning without turning the document into a dashboard.

# Document Accessibility Evidence
<!-- id: document-craft.accessibility -->
For structured digital/fixed documents, verify logical heading order, meaningful link text, table semantics/headers where supported, figure captions/alternatives when applicable, reading order, contrast, zoom/readability, and exported pagination/clipping.

# Document Acceptance
<!-- id: document-craft.acceptance -->
High-value documents pass feature/depth scoring through decision completeness, evidence traceability, analytical specificity, risk/alternative treatment, and actionable closure—not through arbitrary UI feature counts.

# Revision 1.4 Truth & Responsive Closure
<!-- id: document-craft.truth-responsive-closure -->
Decision documents MUST keep supplied/verified evidence, assumptions, unknowns, interpretations, and recommendations visually distinguishable when the distinction can affect a decision. Responsive digital documents additionally apply `RESPONSIVE_DETAIL_CLOSURE.md` to action tables, matrices, timelines, citations, long identifiers, callouts, and navigation. A visually elegant memo fails if its provenance or narrow-screen relationships become ambiguous.
