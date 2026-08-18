<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: NONWEB_FIRST_PASS
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Non-Web First-Pass Quality Closure
<!-- id: nonweb-first-pass.root -->

This module converts the repeated Core 1.7.4 generalization-holdout failures in mobile, presentations, spreadsheets/models, fixed-format documents, brand/email creative, and CLI output into family-specific executable acceptance requirements. It supplements, and never weakens, the active artifact contract, truth boundaries, accessibility obligations, implementation preflight, or evidence rules.

# Family Contracts
<!-- id: nonweb-first-pass.family-contracts -->

A substantial high-fidelity artifact in an applicable family MUST produce direct evidence for the family profile below before acceptance using `schemas/artifact_family_quality_evidence.schema.json` and `tools/validate_artifact_family_quality_evidence.py`. Missing evidence is **UNVERIFIED**, not PASS.

| Family | Required first-pass closure |
|---|---|
| Native / Mobile App | compact and large device states; P0/P1 critical-path depth; safe-area/target/readability checks; keyboard/focus where applicable; interruption/offline/error recovery; state continuity; direct interaction evidence |
| Presentation / Deck | required narrative/decision structure; legible typography; contrast; reading order; evidence/provenance boundaries; decision or next-state depth; slide-bound/export rendering; non-generic story grammar |
| Spreadsheet / Financial Model | formula integrity; recalculation; scenario mutation; editable-vs-derived distinction; decision surface; validation; labels/number formats; screen/print legibility; provenance/assumption boundaries |
| Fixed-Format Document / PDF | page rendering/clipping; heading hierarchy; text extraction/reading order; links; tables/page breaks; provenance/limitations; document accessibility when claimed; decision/action depth where applicable |
| Brand Identity / Logo | symbol/wordmark/type/color roles; usage grammar; anti-cliche differentiation; accessible contrast; multiple application contexts; provenance of sample claims/assets |
| Email / Campaign | sequence/state progression; responsive/mobile rendering; links/CTA semantics; accessible image alternatives when images are used; truth/proof boundaries; recovery/fallback where a CTA or state transition can fail |
| Marketing Creative | campaign grammar across placements; differentiated visual/semantic hook; legibility and contrast; truth/proof boundaries; placement adaptation; accessible alternatives where applicable |
| CLI / Developer Tool | help; happy path; invalid input; deterministic exit codes; stdout/stderr discipline; reproducible behavior; failure recovery; fixtures/tests; truthful capability boundary |
| Composite | each child artifact passes its own family contract; shared project context is explicit; independent QA is preserved; cross-artifact claims/terminology/identity remain consistent |

# Family Acceptance Thresholds
<!-- id: nonweb-first-pass.acceptance-thresholds -->

Cross-family benchmark scoring retains the universal 0–10 rubric and reports the strict `>= 9.0 in every dimension` result for comparability. Release acceptance additionally uses artifact-family criticality:

- **All families:** overall score >= 90/100; truthfulness and implementation correctness >= 9.0; catastrophic truth, security, accessibility, file-integrity, or execution failures block release regardless of aggregate score.
- **Interactive web/mobile/product:** completeness, usability, responsiveness, accessibility, and feature depth are release-critical at >= 9.0.
- **Presentation / Spreadsheet / Fixed Document / Brand / Email / Marketing Creative / CLI:** completeness, accessibility, and feature depth are release-critical at >= 9.0 when applicable; non-critical rubric dimensions may not fall below 8.5.
- A dimension may be marked not-applicable only when the active artifact contract supplies an explicit reason. Omission is not N/A.

# Evidence Rules
<!-- id: nonweb-first-pass.evidence-rules -->

Evidence MUST identify the artifact, family, checked surface/path/state, method, and observed result. File-open success alone is insufficient for semantic quality. Render-only evidence is insufficient for formulas, executable CLI behavior, interaction, or accessibility semantics. Source inference alone is insufficient when direct execution/render/document evidence is available.

# Recovery
<!-- id: nonweb-first-pass.recovery -->

On failure, repair the smallest upstream family-contract cause and re-run the affected evidence. Do not hide content, remove required states, flatten a composite into one artifact, or weaken the acceptance threshold to manufacture a pass. Repeated benchmark failures become reusable family regressions rather than one-off artifact patches.
