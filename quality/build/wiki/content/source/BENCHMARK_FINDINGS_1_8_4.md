<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: BENCHMARK_FINDINGS_1_8_4
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Core 1.8.4 Benchmark Findings — Sealed Holdout 5

**Qualification decision:** NOT APPROVED for Stable 2.0 freeze.

Core 1.8.4 was qualified on Sealed Holdout 5, a 40-brief corpus created and hashed before artifact generation. Conditions were brief-only control, Core 1.8.3, and Core 1.8.4. The 144-file artifact tree was frozen before audit and remained byte-identical after qualification; no post-freeze artifact repair was allowed.

## Holdout 5 Result
<!-- id: benchmark-findings-1-8-4.holdout-5-result -->

Core 1.8.4 achieved:

- mean engineering quality: **92.362/100**;
- wins versus brief-only control: **40/40**;
- paired mean improvement: **+2.717 points** with bootstrap 95% interval **+2.023 to +3.564**;
- exact artifact routing: **39/40 (97.5%)**;
- family-native emission validation: **35/40**;
- family-adjusted release acceptance: **34/40 (85.0%)**;
- universal executable/interface preflight: **18/19**;
- native PPTX/XLSX/PDF integrity: **14/14** Core 1.8.4 native files;
- forbidden internal production vocabulary: **0 occurrences across 40/40 Core 1.8.4 cases**;
- eager stable-section context regression: **+4.58%** versus Core 1.8.3, within the predeclared <=5% budget;
- artifact freeze verification: **144/144 files unchanged**.

Core 1.8.4 passes **6/10** predeclared Stable 2.0 gates. Stable 2.0 remains rejected.

## What Generalized
<!-- id: benchmark-findings-1-8-4.generalized -->

The Core 1.8.4 family-aware emission architecture resolves the validator defect exposed by Holdout 4. Brand, deck, spreadsheet/model, CLI, email, mobile, dashboard, website, and other artifact families can now prove production substance with family-native semantics rather than one universal workflow-shaped state machine.

The namespace-safe XLSX/OOXML adapter also generalized successfully. All five spreadsheet/model cases passed family-native emitted-surface validation, and the generated native workbooks exposed inputs, formula/derived surfaces, scenarios, provenance markers, decision surfaces, and editable/derived boundaries to the validator.

The exact Holdout-4 deck + spreadsheet composite routing defect did not recur: the airport retrofit request resolved as **Presentation / Deck + Spreadsheet / Financial Model**.

The successful Core 1.8.3 naturalization and universal syntax/grammar systems also remained intact. No Core 1.8.4 treatment artifact leaked forbidden BizIQ/compiler vocabulary, and no catastrophic parser/runtime/native-file failure occurred.

## Remaining Failure Clusters
<!-- id: benchmark-findings-1-8-4.remaining-clusters -->

Four narrow failure clusters remain:

1. **Dashboard versus workspace boundary.** A sealed “contract renewal workspace” case was predeclared as Dashboard but resolved as Web App / SaaS / Portal. Under the fixed oracle this leaves exact routing at 97.5%, narrowly below the >=98% Stable threshold.
2. **Composite compact containment.** The marine-sensor brand + website composite overflows horizontally at 320/390 on both child HTML surfaces. The failure is frozen and unrepaired, reducing compact containment and universal interface preflight below 100%.
3. **Fixed-document materialization depth.** Four fixed reports emit too few distinct findings/conclusions and implications/actions even though their requested topics are present. This is a substantive first-pass depth problem, not a family-adapter bug.
4. **Deck + model project continuity.** The airport retrofit deck/model composite routes correctly but its emitted project-level surfaces do not materialize enough cross-artifact continuity and evidence/provenance boundary language to pass the composite family adapter.

## Next Revision Boundary
<!-- id: benchmark-findings-1-8-4.next-revision -->

The evidence supports a narrow **Core 1.8.5 — Fixed-Document Depth, Composite Continuity & Compact Containment**. It should preserve family-aware emission adapters, namespace-safe XLSX extraction, naturalization, universal executable grammar preflight, and the current retrieval architecture. Changes should be limited to:

- fixed-document findings/conclusions and implications/actions depth;
- project-level provenance and cross-artifact continuity for composites;
- child-level compact containment before freeze;
- clarification of Dashboard versus Web App/Workspace classification without broad router retuning.

Any subsequent Stable 2.0 qualification must use a new sealed Holdout 6. Holdout 5 is now known validation/regression data and must not be represented as an untouched qualification corpus again.

## Method Boundary
<!-- id: benchmark-findings-1-8-4.method-boundary -->

Holdout 5 is same-environment deterministic engineering qualification with blinded condition identities and score locking. It is not independent human or third-party-model judging. Numeric rubric results therefore support regression and release engineering decisions but do not constitute third-party efficacy validation.
