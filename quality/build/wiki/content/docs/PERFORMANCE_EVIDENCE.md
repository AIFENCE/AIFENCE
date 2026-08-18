<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: PERFORMANCE_EVIDENCE
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-11
-->

# BizIQ 2.0 Performance & Evidence
<!-- id: performance-evidence.root -->

BizIQ Stable 2.0 is the frozen Core 1.8.8 architecture with Runtime packaging 2.0.0. This page separates **internal Stable qualification**, **external-value engineering evidence**, and the remaining **independent-judging boundary** so public performance claims stay traceable and appropriately scoped.

## Headline results
<!-- id: performance-evidence.headline -->

The strongest current product-value evidence is **External Value Benchmark 1**, a fresh 30-brief benchmark across 10 artifact families comparing three conditions under one locked engineering protocol:

| Condition | Mean engineering value | Production acceptance | Catastrophic failures |
|---|---:|---:|---:|
| Brief-only / default | **65.200 / 100** | 0 / 30 | 0 |
| Strong handcrafted production prompt | **85.867 / 100** | 4 / 30 | 0 |
| **BizIQ Stable 2.0** | **96.800 / 100** | **30 / 30** | **0** |

Paired results:

- **BizIQ vs default:** +31.600 points, **30/30 wins**, bootstrap 95% CI **+29.067 to +34.400**.
- **BizIQ vs strong expert prompt:** +10.933 points, **30/30 wins**, bootstrap 95% CI **+9.333 to +12.533**.
- **Expert prompt vs default:** +20.667 points, **30/30 wins**.

BizIQ reached **100% production acceptance in every tested family** under the locked engineering acceptance rule.

## Engineering value dimensions
<!-- id: performance-evidence.dimensions -->

The external-value score uses five equally weighted 20-point categories. These categories emphasize observable production behavior rather than aesthetic preference alone.

| Dimension | Default | Expert prompt | **BizIQ 2.0** |
|---|---:|---:|---:|
| Production completeness | 12.40 | 17.73 | **19.60** |
| Operational usability | 10.13 | 15.60 | **20.00** |
| Implementation resilience | 18.80 | **19.60** | **19.60** |
| Accessibility / render quality | 15.07 | 17.20 | **19.60** |
| Domain / evidence depth | 8.80 | 15.73 | **18.00** |

The expert baseline is intentionally strong. Its implementation-resilience score is already near the ceiling, while BizIQ's largest additional gains come from materialization depth, recovery and continuation behavior, provenance, decision usefulness, family-native completeness, and cross-artifact continuity.

## External Value Benchmark 1 protocol
<!-- id: performance-evidence.external-value-protocol -->

External Value Benchmark 1 uses **30 previously unseen briefs across 10 artifact families**. Each brief is produced under three conditions:

1. brief-only/default generation;
2. one frozen strong handcrafted production prompt;
3. BizIQ Stable 2.0 / Core 1.8.8.

The scoring protocol and family-native subchecks are fixed before scoring. Artifacts are frozen before audit. Engineering acceptance is based on direct artifact evidence such as browser execution, compact-width containment, CLI execution, native PPTX/XLSX/PDF integrity, formula checks, render geometry, accessibility evidence, domain materialization, provenance, and composite continuity where applicable.

The official scored run contained **114 frozen original artifact files**, all of which remained byte-identical after audit. Direct evidence included:

- 57 HTML surfaces / 228 viewport executions across 1440, 768, 390, and 320 px;
- zero horizontal-overflow, page-error, console-error, or dead-control failures;
- 12 CLI implementations exercising help, success, and invalid-input behavior;
- 12 PPTX decks with native/render checks;
- 12 XLSX workbooks with zero standard formula-error tokens;
- 12 PDFs with zero detected text-overlap and edge-clipping failures;
- zero catastrophic failures across the 90 scored condition/case combinations.

A pre-score benchmark-harness run was invalidated because the original protocol did not enumerate every family-level subcheck explicitly. No score from that run was used. The protocol was completed, the benchmark resealed, the artifact tree discarded, and all three conditions regenerated before scoring.

Final benchmark seal: `155d6d9f752789a7d270aac0a4b408a9679f50295a001f76c7b3a8f4970b945e`.

Frozen artifact-tree hash: `f1701c3952fc308f368489b3479ceeddd68ca4ea3e597a89796237051536fe34`.

## Stable 2.0 internal qualification
<!-- id: performance-evidence.stable-qualification -->

Stable 2.0 was frozen only after **Sealed Holdout 9** passed all **10/10 predeclared engineering gates** on a separate 40-brief corpus:

- exact artifact-graph routing: **40/40 (100%)**;
- pairwise wins versus brief-only control: **40/40 (100%)**;
- mean engineering quality: **92.910/100** versus **88.475/100** control;
- mean paired improvement: **+4.434 points**, bootstrap 95% CI **+4.419 to +4.450**;
- family-adjusted acceptance: **40/40 (100%)**;
- every major family acceptance: **100%**;
- universal/interface/native preflight: **100%**;
- compact 320/390 containment: **100%**;
- catastrophic parser/runtime/native failures: **0**;
- eager-context regression versus Core 1.8.7: **+1.85%**, inside the <=5% budget;
- frozen artifact verification: **119/119 files byte-identical after audit**.

See `ARCHITECTURE_FREEZE_STATUS.md` and `BENCHMARK_FINDINGS_1_8_8.md` for the canonical Stable 2.0 qualification record.

## Architecture under test
<!-- id: performance-evidence.architecture -->

The frozen Stable 2.0 architecture consists of:

- **Core 1.8.8**;
- **Runtime 2.0.0**;
- **31 control domains**;
- **260 capabilities**;
- **1,300 controls**;
- semantic routing and bounded retrieval;
- artifact-family production and acceptance contracts;
- naturalization, executable/native preflight, render-aware document validation, compact containment, and composite continuity requirements.

Stable 2.0 is architecture-frozen. New controls or broad control-plane expansion require a repeated regression class or new sealed evidence demonstrating measurable benefit.

## What the evidence supports
<!-- id: performance-evidence.claim-boundary -->

The current evidence supports the claim that, **inside the locked same-environment engineering benchmark**, BizIQ 2.0 materially outperformed both brief-only generation and the frozen strong handcrafted production prompt while maintaining zero catastrophic failures and 100% engineering acceptance across the tested families.

It does **not** establish universal superiority across all models, tasks, users, domains, or future versions. The engineering scores are not independent third-party ratings and should not be presented as such.

The next credibility layer is independent blinded preference judging using the already-frozen benchmark artifacts. That test should evaluate whether BizIQ's engineering advantage also translates into preference by judges who do not know which condition produced each artifact.

## Public reporting rules
<!-- id: performance-evidence.reporting-rules -->

When citing BizIQ performance publicly:

- identify the benchmark and condition being compared;
- distinguish **engineering value score** from subjective visual preference;
- include the strong expert-prompt baseline when making product-value comparisons;
- preserve the same-environment / non-third-party methodological boundary;
- do not combine scores from different sealed holdouts into one synthetic score;
- do not imply independent blind judging has completed until judge scorecards are locked and unblinded;
- keep Core 1.8.8 frozen while external-value evidence is being accumulated.
