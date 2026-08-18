<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: BENCHMARK_FINDINGS
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Fresh Core 1.7.2 Benchmark Finding: Generation Compiler Preflight
<!-- id: benchmark-findings-1-7-2.root -->

A completely fresh six-pair rendered benchmark reproduced the Core 1.7.2 structural-genericity and B2B decision-depth improvements, but all six freshly generated dense-product artifacts contained the same JavaScript parser defect: an element ID named `export` was used as an implicit global in `export.onclick = ...`. Controls and AIFENCE treatments therefore rendered visually but their scripts did not execute.

Revision 1.7.3 converts this failure into a fail-closed generation boundary:

- real parser syntax check before rendered acceptance;
- direct runtime initialization/load evidence when JavaScript is present;
- zero uncaught page errors, artifact-attributable error-console failures, or failed required local resources;
- explicit DOM bindings instead of implicit element-global assumptions;
- parser/runtime failure remains blocking regardless of visual score;
- permanent regression fixtures in Core and generated Runtime tests.

A fresh six-pair no-repair replication was then executed against Runtime 1.1.3 / Core 1.7.3 using the same six briefs. All 12 artifacts were generated into a clean benchmark directory and 0/12 were byte-identical to prior benchmark artifacts.

Measured result:

- Brief-only control mean: **76.481/100**.
- AIFENCE 1.7.3 treatment mean: **91.444/100**.
- Mean paired improvement: **+14.963 points**; AIFENCE won **6/6** pairs.
- Bootstrap 95% interval for mean paired delta: **+12.407 to +17.500**.
- All **6/6 AIFENCE artifacts passed generation preflight**.
- Fresh AIFENCE payments, SaaS, and analytics each passed the targeted 320/390 interaction workflow audit.
- The three brief-only product controls reproduced the parser failure and failed preflight.
- Strict >=9.0-every-dimension remained **3/6** because dense-product visual quality/completeness/accessibility and payments/analytics feature depth still had sub-9 scores; the parser/dead-JS failure itself was eliminated in the AIFENCE treatment.

This remains a single-session/single-judge engineering benchmark rather than independent third-party validation.
