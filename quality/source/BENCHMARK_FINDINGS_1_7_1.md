<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: BENCHMARK_FINDINGS_1_7_1
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Revision 1.7.1 Real-Artifact Benchmark Findings
<!-- id: benchmark-findings-1-7-1.root -->

The controlled six-pair rerun raised the BizIQ treatment mean from 90.555 to 92.518 and moved strict 9.0-every-dimension passes from 2/6 to 3/6. Payments cleared the strict floor after interaction/mobile closure. The remaining misses were structurally different: SaaS genericity resistance 8.9, analytics genericity resistance 8.8, and B2B feature depth 8.9.

## Revision 1.7.2 Permanent Regressions
<!-- id: benchmark-findings-1-7-1.regressions -->

1. Dense SaaS may not claim genericity PASS from a generic list/detail shell plus cosmetic differentiation.
2. Analytics may not claim genericity PASS from a generic KPI/chart/table composition merely because controls are functional.
3. Complex-consideration B2B marketing may not claim feature-depth PASS from feature presentation without buyer decision/evidence/risk/action/downstream paths.

The canonical corpus is `benchmarks/v3_quality_floor_closure_cases.json`.
