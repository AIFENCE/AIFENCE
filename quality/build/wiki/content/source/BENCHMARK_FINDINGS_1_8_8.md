<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: BENCHMARK_FINDINGS_1_8_8
Module-Version: 2
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-11
-->

# Core 1.8.8 Benchmark-Derived Findings
<!-- id: benchmark-findings-1-8-8.root -->

Core 1.8.8 was qualified against sealed Holdout 9 after its routing behavior was fixed and before any Holdout-9 artifacts were generated. Holdout 9 is now known qualification/regression data and MUST NOT be reused as an untouched future holdout.

## Stable 2.0 qualification result
<!-- id: benchmark-findings-1-8-8.holdout-9 -->

Core 1.8.8 passed **10/10** predeclared Stable 2.0 engineering gates:

- exact artifact routing **40/40 (100%)**, versus 32/40 for Core 1.8.7 on the same unseen corpus;
- pairwise wins versus brief-only control **40/40**;
- mean quality **92.910/100** versus **88.475/100** control;
- paired mean delta **+4.434**, bootstrap 95% CI **+4.419 to +4.450**;
- strict/family-adjusted acceptance **40/40** with every major family at 100%;
- preflight, compact containment, native package integrity, PDF render preflight, slide-fit, CLI execution, and XLSX formula/error audit all **100% PASS**;
- catastrophic implementation failures **0**;
- forbidden internal production terminology **0 occurrences**;
- eager context change **+1.85%** versus Core 1.8.7, within the <=5% release budget;
- official frozen artifact run **119/119 files unchanged** after audit.

## Routing findings
<!-- id: benchmark-findings-1-8-8.routing -->

The two Revision 1.8.8 routing changes generalized on unseen wording. Board/publication/client/executive-ready finished report variants resolved as Fixed-Format Document / PDF, and modifier-bearing multi-artifact lists preserved every requested child. The 40-case adversarial Revision 1.8.8 routing corpus also passes 40/40.

## Benchmark harness invalidation record
<!-- id: benchmark-findings-1-8-8.harness-invalidation -->

The initial Holdout-9 artifact run was invalidated before scores were locked because a reused benchmark generator template hardcoded `P1 workflow` into mobile treatment copy, contradicting AIFENCE's pre-existing emission-naturalization rules. No Core rule, sealed brief, expected graph, or release gate was changed. The entire artifact run was discarded and regenerated from the same sealed corpus. Only the second run is qualification evidence.

## Freeze conclusion
<!-- id: benchmark-findings-1-8-8.freeze -->

Core 1.8.8 is approved as the **AIFENCE Stable 2.0 architecture**. Further control-plane changes require new repeated failure evidence or a new sealed benchmark. Existing holdouts become regression corpora only.
