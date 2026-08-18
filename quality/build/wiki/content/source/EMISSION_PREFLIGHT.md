<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: EMISSION_PREFLIGHT
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Emission Naturalization, Family-Aware Substance, Continuity & Universal Executable Preflight
<!-- id: emission-preflight.root -->

Core 1.8.5 preserves Core 1.8.4 family-aware emission, finished-surface naturalization, namespace-safe XLSX extraction, and universal executable gates while strengthening the fixed-document and composite depth failures exposed by Stable-2.0 Holdout 5. The gate runs after generation and before artifact freeze, packaging, scoring, or delivery. It is fail-closed and adds no BQ IDs.

# Finished-Surface Naturalization Scan
<!-- id: emission-preflight.naturalization-scan -->

Acceptance MUST scan the actual production-facing surfaces, not only an evidence summary. User-visible HTML/text, deck and document text, spreadsheet labels, campaign copy, brand guidance, and directly observed CLI/runtime output MUST NOT expose internal AIFENCE/compiler/QA vocabulary unless the user explicitly requested process documentation. Forbidden language includes control priorities (`P0`, `P1`), closure/gate names, `truth boundary`, `feature depth`, `genericity`, `artifact contract`, `evidence plan`, `acceptance ledger`, and equivalent orchestration labels.

A violation is release-blocking. Repair rewrites the emitted copy into natural domain language and reruns the scan; it does not suppress the finding.

# Legacy Emitted Material Substance Shape
<!-- id: emission-preflight.substance -->

Core 1.8.3 used a universal decision/action/state/outcome substance shape. It remains documented for compatibility and regression history, but Core 1.8.4 production acceptance MUST use the family-aware adapter below. A structurally correct artifact is still NON-PASS when finished surfaces consist mainly of framework language.

# Family-Aware Emission Adapters
<!-- id: emission-preflight.family-adapters -->

Direct substance evidence MUST use the native semantics of the emitted artifact instead of forcing every family into an interactive workflow state machine. Common requirements remain concrete domain terms, direct finished-surface markers, and at least one evidence/provenance boundary. Family-native requirements are:

- **Website:** visitor decisions, proof points, actions, uncertainties/objections, and continuation paths.
- **Web app:** user jobs, actions, states, recovery paths, and outcomes.
- **Dashboard:** decision questions, evidence views, actions, states, and recovery/handoff.
- **Mobile:** user jobs, actions, states, recovery paths, and outcomes.
- **Brand:** identity rules, typography, color, composition, imagery/iconography, at least three applications, and misuse constraints.
- **Email/campaign:** audience states, message jobs, CTAs, sequence transitions, measurement events, and compliance/truth boundaries.
- **CLI:** commands, help surfaces, configuration rules, stdout/stderr contracts, exit semantics, and recovery guidance.
- **Presentation/deck:** storyline beats, evidence points, implications, decisions/requests, and audience takeaways.
- **Spreadsheet/model:** editable inputs, calculations/outputs, scenarios, decision surfaces, provenance markers, and editable/derived boundaries.
- **Fixed document:** questions/issues, evidence points, findings/conclusions, implications/actions, and provenance markers.
- **Marketing creative:** message layers, proof elements, CTAs, visual rules, and channel context.
- **Composite:** shared-context rules, cross-artifact continuity, child acceptance references, plus independent family-native validation of every child.

Evidence items themselves MUST be concrete. Generic category labels do not become valid merely because they appear in the family schema.


# Fixed-Document Findings & Implications Depth
<!-- id: emission-preflight.fixed-document-depth -->

A substantial fixed-format report, memo, brief, or PDF MUST materialize more than topic coverage. Before acceptance its finished surface MUST contain at least three materially distinct findings/conclusions, at least three corresponding implications/actions, at least four evidence points, at least two provenance/source-boundary markers, and at least two reader-facing takeaways or decisions. Findings MUST resolve the document's stated questions/issues rather than restating headings. Implications MUST say what changes, what should be decided, or what must happen next. Repeated paraphrases count once.

The document compiler SHOULD map `issue/question → evidence → finding/conclusion → implication/action → reader takeaway` for each material section while preserving source/assumption boundaries. A report with four topics but only one substantive conclusion is NON-PASS.

# Composite Project Continuity
<!-- id: emission-preflight.composite-continuity -->

Composite acceptance MUST prove that child artifacts form one coherent project without collapsing their family-native contracts. Project-level evidence MUST include at least three shared-context rules, three cross-artifact continuity/handoff statements, two child acceptance references, two explicit shared identifiers or assumptions, and two project-level provenance/truth boundaries. Shared anchors MUST be visible on more than one child surface when they are intended to coordinate those children.

Examples include a deck and model sharing the same scenario names and assumptions; a brand and website sharing approved naming/visual rules; or a mobile/admin pair sharing entity IDs and state definitions. A merely adjacent bundle of individually valid files is NON-PASS.

# Responsive Composite Pre-Freeze Containment Compiler
<!-- id: emission-preflight.compact-containment -->

For every responsive child in a composite project, compact containment is a generation-stage prerequisite rather than only a post-hoc QA check. Before freeze, compile and verify width-safe layout primitives: flex/grid children use `min-width: 0` where shrinkage is required; media and long controls remain within the containing block; unbreakable tokens/URLs can wrap; fixed/min widths cannot exceed compact viewports; tables/data regions transform or scroll intentionally; and child shells do not inherit desktop-only widths from sibling artifacts.

Direct 320px and 390px evidence MUST show zero horizontal overflow, zero task-critical clipping, and preserved critical paths for every responsive child. Any failing child blocks project freeze; a passing sibling cannot offset it.

# Namespace-Safe XLSX Surface Adapter
<!-- id: emission-preflight.xlsx-adapter -->

Spreadsheet acceptance MUST recover visible surface text from OOXML without assuming a single string encoding. Extraction MUST support shared strings, inline strings, string-valued worksheet cells, formulas/derived labels where useful, workbook/table labels, and namespace-qualified XML produced by supported spreadsheet generators. A structurally valid workbook with visible labels MUST NOT fail merely because strings are not represented as simple `<t>` nodes.

The adapter validates spreadsheet-native semantics; it does not require a workbook to mimic an interactive application's actions/states vocabulary.

# Context-Sensitive Scaffold Detection
<!-- id: emission-preflight.scaffold-context -->

Scaffold phrases are evaluated in family context rather than globally banned. Ordinary language such as `next state`, `relevant evidence`, or `decision path` MAY be legitimate in some documents, emails, or analytical surfaces. A scaffold finding becomes release-blocking when generic phrases dominate, when evidence records themselves rely on generic placeholders, or when direct family-specific marker coverage is too weak.

Production-facing internal AIFENCE/compiler/QA vocabulary remains globally forbidden under the Finished-Surface Naturalization Scan.

# Universal Executable Grammar Preflight
<!-- id: emission-preflight.universal-executable -->

Every emitted executable artifact MUST pass a language-appropriate parser/compiler check before acceptance. This includes browser JavaScript, CLI JavaScript/Node entrypoints, Python, shell scripts, and other supported executable text formats. Syntax checking is performed against the emitted files themselves.

Artifacts whose contract implies direct execution (for example browser interfaces with scripted controls or CLI/developer tools) additionally require direct runtime evidence: the artifact must initialize, required happy/error paths must execute with expected exit behavior, and observed runtime errors must be empty. Missing runtime evidence is UNVERIFIED/NON-PASS when runtime execution is required.

Browser-specific `GENERATION_PREFLIGHT.md` remains valid; Core 1.8.3 generalizes the same fail-closed principle to every generated executable family.

# Direct Evidence Contract
<!-- id: emission-preflight.evidence -->

Core 1.8.4 acceptance uses `schemas/family_emission_evidence.schema.json` with `tools/validate_family_emission_evidence.py`; the Core 1.8.3 `validate_emission_preflight.py` remains available as a compatibility/regression validator for the prior universal shape. The family-aware validator extracts emitted text/HTML/Markdown/JSON/CSV, namespace-safe OOXML (`.pptx`, `.xlsx`, `.docx`), and PDF surfaces where extraction support is available, and can merge direct runtime output for CLI surfaces. `tools/validate_universal_executable_preflight.py` remains the executable grammar/runtime gate.

Executable preflight recursively checks supported emitted code and, when `--require-runtime` is used, requires schema-valid direct runtime evidence. Generated evidence records include artifact hashes and parser/runtime results.

# Semantic-Equivalence Materialization
<!-- id: emission-preflight.semantic-equivalence -->

Materialization acceptance SHOULD compare emitted concepts semantically rather than requiring brittle verbatim phrase identity. Exact phrase matches remain strongest. Conservative token/stem equivalence and narrowly defined synonym groups MAY satisfy a concept only when the emitted surface preserves the material meaning. For short two- or three-token concepts, every material concept token must match exactly or through an approved synonym group. Generic topical similarity does not count.

# Render-Aware Fixed-Document Preflight
<!-- id: emission-preflight.fixed-document-render -->

Every substantial fixed-format PDF MUST be rendered before freeze and inspected on the actual page surface. Direct evidence MUST cover all pages and record clipping, visible text/table collisions, readability, logical reading order, table reading order, navigable links where applicable, contrast/readability, zoom/reflow or magnification behavior, and alt-text presence or an explicit not-applicable determination. PDF text geometry MUST show zero material overlapping word boxes and zero words beyond page bounds. A content-deep document with collided cells, clipped text, or unverified reading order is NON-PASS.

Use `schemas/fixed_document_render_evidence.schema.json` with `tools/validate_fixed_document_render_evidence.py`.

# Presentation Slide-Fit & Render Preflight
<!-- id: emission-preflight.presentation-slide-fit -->

Every substantial presentation/deck MUST be rendered before freeze and checked slide-by-slide. Direct evidence MUST prove that each title fits its intended title region, title and subtitle regions do not overlap, body text and visuals do not collide, no visible element clips beyond the slide bounds, and the rendered slide remains readable. Long titles MUST be reflowed, shortened without losing meaning, or resized within the approved type scale; they MUST NOT simply overflow into subtitle/body regions.

Use `schemas/presentation_slide_fit_evidence.schema.json` with `tools/validate_presentation_slide_fit_evidence.py`. Any failed slide blocks presentation acceptance.

# Acceptance
<!-- id: emission-preflight.acceptance -->

Final acceptance is blocked when any of the following is true:

1. forbidden internal vocabulary appears on a production-facing surface;
2. required family-native semantic markers or common domain/provenance markers are absent from the emitted artifact;
3. generic scaffold language dominates or substitutes for concrete family material;
4. any supported emitted executable fails syntax/grammar checking;
5. runtime-required executable work lacks direct runtime evidence or has unexpected runtime failures.

These failures are non-averagable with aggregate quality scores.

# Recovery
<!-- id: emission-preflight.recovery -->

Repair the emitted artifact, not the evaluator. Rewrite leaked orchestration labels into domain language, materialize missing concrete substance, correct parser/runtime defects, rerun direct preflight, and only then freeze/package/deliver. Preserve already-passing routing, retrieval, truth, responsive, and family-depth evidence.
