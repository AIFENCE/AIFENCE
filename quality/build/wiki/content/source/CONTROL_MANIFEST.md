<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: CONTROL_MANIFEST
Module-Version: 4
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-09
-->

# Control Plane Address Manifest
<!-- id: control-manifest.root -->

`MANIFEST.md` remains canonical for industry, operations-shard, job, and SOP addresses. This file is canonical for current control-plane counts and shard addressing.

# Control Plane Summary
<!-- id: control-manifest.summary -->

```text
Domains: 31
Capabilities: 260
Controls: 1,300
Stable control range: BQ-0001 through BQ-1300
Regression conditions: 780
```

# Registry Storage
<!-- id: control-manifest.registry -->

- `control_registry.csv` — BQ-0001–BQ-1000
- `control_registry/26-feature-component-craft.csv`
- `control_registry/27-artifact-contracts-and-specification-compilation.csv`
- `control_registry/28-adversarial-critique-repair-quality-floors-and-benchmarking.csv`
- `control_registry/29-benchmark-driven-quality-hardening.csv`
- `control_registry/30-usability-visual-finish-truth-and-quality-closure.csv`
- `control_registry/31-operational-procedure-compilation-authority-and-measurement.csv`
- router: `CONTROL_INDEX.md`
- domain shards: `controls/01-*.md` through `controls/31-*.md`

# Compilation Modules
<!-- id: control-manifest.compilation -->

`ARTIFACT_CONTRACTS.md`, `contracts/*.md`, `FEATURE_COMPILER.md`, `COMPONENT_COMPILER.md`, `GENERICITY.md`, and `schemas/*.json`.

# Evaluation & Closure Modules
<!-- id: control-manifest.evaluation -->

`CRITICS.md`, `QUALITY_FLOORS.md`, `RESPONSIVE_COMPOSITION.md`, `ACCESSIBILITY_EVIDENCE.md`, `COMPLETENESS.md`, `FEATURE_DEPTH.md`, `USABILITY_CLOSURE.md`, `VISUAL_FINISH.md`, `TRUTH_BOUNDARIES.md`, `RESPONSIVE_DETAIL_CLOSURE.md`, `QUALITY_MEASUREMENT.md`, `BENCHMARKS.md`, `EVALS.md`, and evaluation tools under `tools/`.

# Operations 2.0 Modules
<!-- id: control-manifest.operations-2 -->

`OPERATIONAL_PROCEDURE_COMPILER.md`, `PROCEDURE_AUTHORITY.md`, `DECISION_RIGHTS.md`, `OPERATIONAL_EVIDENCE.md`, `KPI_GOVERNANCE.md`, their composed schemas, Domain 31, `tools/validate_operational_procedure.py`, and `tools/test_operations_2.py`. Existing `operations/*.md` files remain profile-context shards. Domain 23 provides baseline coverage; Domain 31 specializes production-detail execution without duplicate parallel objects.

# Addressing Rule
<!-- id: control-manifest.addressing -->

Use stable IDs and `CONTROL_INDEX.md`/logical machine registries. Do not use file order, legacy count summaries, or inferred ranges.
