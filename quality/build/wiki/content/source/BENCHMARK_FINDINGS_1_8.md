<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: BENCHMARK_FINDINGS_1_8
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Benchmark Findings — Core 1.8 Generalization

**Status:** Engineering candidate; Stable 2.0 freeze rejected.

Core 1.8 was developed after observing repeated failure clusters on a 36-case corpus that was unseen during Core 1.7.x development. Because that corpus informed Core 1.8, it is now a development-validation/regression set rather than an untouched holdout.

## Measured outcomes

- Artifact-graph routing: 36/36 exact, versus 20/36 in Core 1.7.4.
- Corrected adversarial router corpus: 480/480.
- Mean eager stable-section context: 29,127 token-equivalents, 48.61% below Core 1.7.4.
- Artifact mean: 91.968/100; 36/36 pairwise wins versus brief-only control; mean paired improvement +4.258 (bootstrap 95% interval +3.828 to +4.656).
- Universal >=9.0-all-dimensions pass: 17/36.
- Family-adjusted release acceptance: 21/36 (58.3%).
- Family-quality validator: 17/28 applicable family artifacts pass.

## Remaining repeated failure clusters

Public-web, mobile, email, brand, and some CLI artifacts still miss first-pass feature/depth thresholds; brand also misses completeness/truth-boundary depth. One composite artifact fails 320px overflow and therefore independent child QA. These are release-blocking evidence under Core 1.8's fail-closed family contract.

## Governance consequence

Do not claim external or publication-grade validation. The blinded scoring passes were generated in the same environment and are not independent judges. Do not freeze the architecture as Stable 2.0 on this corpus. Any next revision must use these findings only as repeated failure classes, and its generalization claim must be tested on a newly sealed holdout.
