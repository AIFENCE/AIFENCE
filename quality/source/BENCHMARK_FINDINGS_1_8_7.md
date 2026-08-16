<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: BENCHMARK_FINDINGS
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Core 1.8.7 Benchmark-Derived Findings
<!-- id: benchmark-findings-1-8-7.root -->

Core 1.8.7 was qualified on sealed Holdout 8 after the revision behavior was fixed. Holdout 8 is now known validation data and MUST NOT be reused as an untouched Stable-2.0 holdout.

## Confirmed improvements

- Exact artifact-graph routing improved from 35/40 under Core 1.8.6 to 38/40 under Core 1.8.7 on the sealed corpus.
- Qualified `Excel ... model` phrasings such as workforce-capacity and preventive-maintenance replacement models resolved as Spreadsheet / Financial Model.
- The new presentation slide-fit contract activated on fresh presentation work; five treatment decks passed direct slide-fit evidence, including two deliberately long-title title slides that rendered with clean title/subtitle separation.
- Fresh treatment HTML surfaces passed 124 viewport checks across 1440/768/390/320 with zero observed overflow, page errors, console errors, or dead controls.
- Four treatment CLI artifacts passed direct help/happy/invalid-input execution; ten treatment native XLSX/PPTX packages passed structural package integrity; five treatment fixed PDFs passed the Core 1.8.6 render-aware geometry/accessibility validator.
- Eager retrieval context remained effectively flat versus 1.8.6 (+0.24% on this corpus).

## Stable 2.0 qualification result

Stable 2.0 remains **REJECTED**. Holdout 8 passed 9/10 predeclared engineering gates. The failing gate was exact artifact-graph routing: 38/40 (95%) versus the required >=98%.

The two sealed routing misses were:

1. `print-ready assessment report` fell through to generic Documentation instead of Fixed-Format Document / PDF;
2. an explicit three-child `brand identity + onboarding email campaign + public landing page` list still dropped the email child because the modifier between coordinated artifact nouns exceeded the compact-list preservation heuristic.

These cases MUST remain frozen regression evidence. A subsequent revision should generalize fixed-report phrase normalization and explicit multi-child list parsing without special-casing Holdout-8 strings.

## Methodological boundary

Holdout-8 artifact scoring is same-environment engineering scoring calibrated against direct runtime/render/native-file evidence. It is not independent human or third-party model judging. The sealed corpus and artifact hashes prevent post-result case/artifact edits, but Stable-2.0 external-validation claims require independent judges.
