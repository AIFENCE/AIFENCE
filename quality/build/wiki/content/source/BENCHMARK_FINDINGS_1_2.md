<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: BENCHMARK_FINDINGS
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-09
-->

# Revision 1.2 Benchmark Findings → Revision 1.3 Hardening
<!-- id: benchmark-findings.revision-1-2 -->

The real browser-rendered V2 run established a 72-pair combined AIFENCE mean of 89.67/100 versus 79.92 control, with AIFENCE winning 72/72 pairs. The strongest dimension was genericity resistance (9.80), which Revision 1.3 intentionally preserves.

Measured remaining AIFENCE means were approximately: responsiveness 7.97, feature depth 8.77, completeness 8.79, accessibility 8.80, and visual quality 8.88. Documents were the weakest artifact family: roughly 6.86 feature depth and 7.15 completeness under the original general-purpose judge. Dense SaaS/dashboard/edge interfaces repeatedly scored about 6.55 responsiveness because narrow-screen controls/data were still compressed rather than fully transformed.

# Revision 1.3 Response
<!-- id: benchmark-findings.revision-1-3-response -->

- `RESPONSIVE_COMPOSITION.md` converts mobile quality into a viewport/task transformation contract at 320/390/768 + desktop.
- `DOCUMENT_CRAFT.md` gives documents a decision/evidence depth model and document-type-specific editorial grammar.
- `ACCESSIBILITY_EVIDENCE.md` requires critical-path keyboard/focus/status/reflow evidence rather than source inference.
- `COMPLETENESS.md` makes P0/P1 omissions explicit through a coverage ledger.
- `FEATURE_DEPTH.md` requires Level-5 closure for important product/workflow features.
- Domain 29 (`BQ-1151`–`BQ-1200`) makes these requirements enforceable through Contract → Procedure → Evidence Gate → Recovery → Regression.
- `GENERICITY.md` is preserved byte-for-byte from Revision 1.2; targeted repairs must re-run genericity evaluation.

# Evaluation Discipline
<!-- id: benchmark-findings.evaluation-discipline -->

Do not rewrite or replace the frozen 48-case public V2 development set merely to improve scores. Use `benchmarks/v2_hardening_cases.json` for targeted regression and a rotated external private holdout for efficacy reruns.
