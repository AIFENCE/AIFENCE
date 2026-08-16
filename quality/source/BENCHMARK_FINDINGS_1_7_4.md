<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: BENCHMARK_FINDINGS_1_7_4
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->

# Core 1.7.4 Fresh Six-Pair Findings

A completely fresh six-pair no-repair replication was executed against Runtime 1.1.4 / Core 1.7.4 using the same frozen briefs as the Core 1.7.3 replication. Six brief-only controls and six BizIQ treatments were generated into a clean benchmark directory. Artifact hashes showed **0/12 byte-identical matches** against the Core 1.7.3 benchmark.

## Result

- Control mean: **83.000/100**.
- BizIQ 1.7.4 mean: **93.519/100**.
- Mean paired improvement: **+10.519 points**.
- Pairwise wins: **6/6**.
- Bootstrap 95% interval for the mean paired improvement: **+9.889 to +11.167**.
- Strict floor result: **6/6 BizIQ artifacts had every applicable scored dimension >=9.0**.

The three dense-product treatments that missed strict floors in the Core 1.7.3 fresh benchmark now all pass:

- Payments: **93.111/100**, minimum dimension **9.2**.
- SaaS: **93.444/100**, minimum dimension **9.2**.
- Analytics: **93.111/100**, minimum dimension **9.2**.

All 12 artifacts passed generation syntax/runtime preflight and rendered without horizontal page overflow at 1440, 768, 390, and 320 px. The three BizIQ dense-product treatments also passed direct 320/390 critical-task execution with keyboard-open/focus-return evidence, and each passed `validate_dense_product_quality_evidence.py` without post-generation artifact repair.

## Interpretation

Revision 1.7.4 closes the benchmarked first-pass dense-product visual-quality, completeness, accessibility, and payments/analytics feature-depth failure class in this six-case replication. The result remains a single-session benchmark with one condition-blind judge who also generated the artifacts; it is engineering evidence rather than independent third-party validation. Future publication-grade claims should use multiple independent judges and a private holdout corpus.
