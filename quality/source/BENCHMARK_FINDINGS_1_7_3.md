<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: BENCHMARK_FINDINGS_1_7_3
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->

# Core 1.7.3 Fresh Six-Pair Findings

A completely fresh six-pair no-repair benchmark against Runtime 1.1.3 / Core 1.7.3 generated six brief-only controls and six BizIQ treatments from the same frozen briefs. The BizIQ treatment mean was **91.444/100** versus **76.481/100** control, with BizIQ winning **6/6** pairs. Revision 1.7.3 successfully eliminated the fresh JavaScript parser/runtime failure from all six BizIQ artifacts.

The remaining strict-floor result was **3/6**. All three dense-product treatments remained below 9.0 in one or more first-pass quality dimensions despite correct runtime execution:

- Payments: visual quality 8.7, completeness 8.7, feature depth 8.9, accessibility 8.7.
- SaaS: visual quality 8.7, completeness 8.9, accessibility 8.8.
- Analytics: visual quality 8.7, completeness 8.7, feature depth 8.8, accessibility 8.7.

Revision 1.7.4 converts these residuals into the executable dense-product first-pass quality closure. The benchmark-derived requirement is not to add cosmetic polish after generation, but to generate visually finished, coverage-complete, accessible, workflow-deep dense products before acceptance.
