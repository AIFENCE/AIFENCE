<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: BENCHMARK_FINDINGS_1_7
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Revision 1.7 Real-Artifact Benchmark Findings
<!-- id: benchmark-findings-1-7.root -->

The matched six-pair rendered benchmark for Core 1.7 produced a AIFENCE mean of 90.555/100 versus 77.315/100 control, a +13.241 mean paired improvement, and 6/6 pairwise wins. The benchmark also exposed release-floor failures that Revision 1.7.1 treats as permanent regressions rather than one-off artifact fixes.

## Permanent Failure Classes
<!-- id: benchmark-findings-1-7.failures -->

1. **Payments dashboard mobile task loss:** transaction detail/recovery was strong on desktop but disappeared at narrow widths.
2. **SaaS list/detail editor mobile task loss:** the editable detail pane disappeared on mobile, reducing responsiveness and implementation correctness.
3. **Analytics dead controls:** multiple visible navigation/period controls had no observable behavior; payments also retained dead overflow actions.

## Revision 1.7.1 Closure
<!-- id: benchmark-findings-1-7.closure -->

These failures map to existing BQ capabilities—No-dead-control gate, Mobile-first priority check, Dense-UI adaptation, Cross-device continuity, and Responsive Feature Recomposition—whose semantics are strengthened without adding or renumbering BQ IDs. Production/high-fidelity interactive artifacts now require a pre-implementation interaction manifest, exhaustive enabled-control evidence, and direct 320/390 P0/P1 task-preservation evidence.

The canonical regression corpus is `benchmarks/v3_interaction_closure_cases.json`. A high aggregate score cannot compensate for failure of these interaction/mobile closure gates.
