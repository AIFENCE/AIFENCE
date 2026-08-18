<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: BENCHMARK_FINDINGS_1_8_3
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Core 1.8.3 Holdout 4 Findings
<!-- id: benchmark-findings-1-8-3.root -->

Stable 2.0 qualification against sealed Holdout 4 is **REJECTED**. Holdout 4 is now known validation/regression data and must not be reused as untouched final qualification evidence.

## Qualification outcome
<!-- id: benchmark-findings-1-8-3.outcome -->

Holdout 4 used 40 newly sealed briefs across website, mobile, brand, email, CLI, dashboard, deck, spreadsheet/model, fixed-document, and composite families. Conditions were brief-only control, Core 1.8.2, and Core 1.8.3. Artifacts were frozen by SHA-256 before audit and were not repaired after freeze.

Core 1.8.3 engineering results:

- mean quality: **92.133/100**, clearing the predeclared >=92 gate;
- wins versus brief-only control: **40/40**;
- paired mean improvement versus control: **+0.745 points**, bootstrap 95% CI **+0.495 to +1.012**;
- exact artifact-graph routing: **39/40 (97.5%)**, below the predeclared >=98% gate because a `deck + spreadsheet/model` composite collapsed to spreadsheet-only;
- family-adjusted acceptance: **10/40 (25%)**, below the >=80% gate;
- every-major-family >=75% acceptance: **FAIL**;
- HTML/browser audit: **29/29** treatment HTML surfaces clean at 1440/768/390/320 with zero horizontal overflow, page errors, console errors, resource failures, or dead visible buttons;
- universal executable preflight: **24/24** treatment executable/interface cases PASS;
- CLI direct execution: **5/5** treatment CLI-containing cases PASS for required help/happy/invalid-input checks;
- native-file integrity: all Holdout-4 PPTX/XLSX/PDF files passed their structural integrity checks; treatment XLSX formula-error scans found zero error-token matches;
- eager stable-section context: **30,863.2** token-equivalents versus **30,197.2** for Core 1.8.2, a **+2.206%** regression within the <=5% budget;
- emission naturalization: Core 1.8.3 had **0 forbidden internal-vocabulary occurrences across 40/40 cases**, versus 155 occurrences across 40/40 Core 1.8.2 cases.

Core 1.8.3 therefore passes **7/10** predeclared Stable 2.0 gates and remains **NOT FROZEN**.

## What Core 1.8.3 actually fixed
<!-- id: benchmark-findings-1-8-3.fixed -->

Two Holdout-3 failure classes generalized successfully:

1. **Emission naturalization generalized.** Finished Core 1.8.3 surfaces eliminated the targeted internal compiler/QA vocabulary in all 40 sealed cases.
2. **Universal executable preflight generalized.** All 24 executable/interface treatment cases passed syntax/grammar plus required direct runtime evidence; the prior CLI parser-failure class did not recur.

These gates should be preserved unchanged unless new evidence demonstrates a defect.

## Newly exposed failure cluster: family-insensitive substance validation
<!-- id: benchmark-findings-1-8-3.family-aware-substance -->

The Core 1.8.3 emitted-substance validator itself is too generic. It applies a workflow-shaped `decisions/actions/states/outcomes/evidence-boundaries` contract across artifact families whose production semantics differ materially.

This caused valid family-native structures to fail for reasons such as:

- brand systems being required to look like interactive workflow state machines;
- decks being required to expose generic actions/states/outcomes rather than decision/evidence/implication structure;
- CLI tools being evaluated with the same semantic markers as user-facing workflow surfaces instead of commands/configuration/I-O/errors/recovery;
- fixed documents being rejected for phrases such as `next state` despite natural contextual usage;
- email sequences being penalized by a context-insensitive scaffold phrase rule;
- dashboards/mobile surfaces failing exact-string evidence mapping even when direct executable/browser evidence was clean.

The next revision must replace the universal substance shape with **family-aware emission adapters** while preserving one common naturalization and truth/provenance layer.

## Newly exposed validator defect: OOXML spreadsheet extraction
<!-- id: benchmark-findings-1-8-3.xlsx-extraction -->

The Core 1.8.3 finished-surface extractor does not correctly recover all artifact-tool XLSX string cells. Holdout-4 workbooks were structurally valid and contained visible decision material, but the emission validator reported `no extractable production-facing surface text` for spreadsheet cases.

The next revision must perform namespace-safe OOXML extraction for shared strings, inline strings, and string-valued worksheet cells, and it must verify formula/display surfaces without requiring spreadsheet content to mimic an interactive workflow vocabulary.

## Newly exposed routing defect
<!-- id: benchmark-findings-1-8-3.composite-routing -->

The sealed brief requesting a presentation/deck plus a spreadsheet scenario model resolved only `Spreadsheet / Financial Model`. Composite coordination must recognize strong `deck/presentation + spreadsheet/model` conjunctions without letting the model keyword dominate the deliverable graph.

## Required next revision boundary
<!-- id: benchmark-findings-1-8-3.next -->

The next evidence-driven revision should be limited to:

1. family-aware emitted-substance adapters for web/mobile/dashboard, brand, email/campaign, CLI, deck/presentation, spreadsheet/model, fixed-document/PDF, and composite children;
2. robust OOXML spreadsheet surface extraction;
3. context-sensitive scaffold-language detection rather than globally banning ordinary phrases;
4. exact composite classification for presentation/deck + spreadsheet/model requests;
5. preserving the successful Core 1.8.3 naturalization scan and universal executable preflight unchanged.

Any subsequent Stable 2.0 qualification must use a new sealed **Holdout 5**. Holdouts 1–4 are regression/validation corpora only.
