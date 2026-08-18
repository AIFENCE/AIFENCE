<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: EVALS
Module-Version: 5
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-09
-->
# AIFENCE Evaluation System
<!-- id: evals.root -->

AIFENCE uses three layers:

1. The logical control regression matrix is the union of `evals/control_regression_matrix.json` and `evals/control_regression_matrix_*.json` shards: **780 conditions** for **260 capabilities**.
2. `evals/end_to_end_cases.json` contains curated cross-module cases for classification, production visual quality, craft, compilation, adversarial review, floors, and benchmark governance.
3. `BENCHMARKS.md` defines real paired efficacy evaluation using public development prompts plus an external private holdout.

# Evaluation Rule
<!-- id: evals.execution-rule -->

Run `python tools/validate_pack.py` first when AIFENCE changes. For behavioral prompt/control changes, review applicable end-to-end cases. For claims that AIFENCE improves artifacts, use the blinded paired benchmark protocol; static validation and self-scoring are insufficient.

# Matrix Sharding Rule
<!-- id: evals.matrix-sharding -->

The base matrix remains stable. New domains use `control_regression_matrix_<domain>.json` shards. The validator treats all shards as one logical matrix and rejects duplicate IDs, gaps, or unbalanced coverage.

# Blind-Eval Separation
<!-- id: evals.blind-separation -->

Condition labels, desired result, and prior scores must be hidden from blind judges. Lock scores before unblinding.

# Failure Promotion
<!-- id: evals.failure-promotion -->

A reusable failure MUST strengthen an end-to-end case, capability regression, artifact contract, critic/floor, genericity fingerprint library, or benchmark corpus. A one-off artifact patch alone is insufficient.

# Revision 1.3 Hardening Suite
<!-- id: evals.revision-1-3-hardening -->
`benchmarks/v2_hardening_cases.json` is a public targeted regression suite derived from measured Revision 1.2 failure classes. It supplements but does not replace the frozen 48-case V2 development corpus or external private holdout.

# Revision 1.4 Quality Closure Regression
<!-- id: evals.revision-1-4-quality-closure -->
Domain 30 adds 10 capabilities and 30 balanced normal/ambiguous/failure regression conditions. Ten E2E cases cover task friction, action hierarchy, state preservation, feedback/recovery, perceptual finish, optical calibration, truth boundaries, generated-proof boundaries, responsive detail, and measurement-ceiling detection. The frozen 48-case longitudinal benchmark remains unchanged.

# Operations 2.0 Evaluation
<!-- id: evals.operations-2 -->

Domain 31 contributes 30 capability regression conditions (10 normal, 10 ambiguous, 10 failure) plus 10 end-to-end cases and a separate 20-case targeted operations corpus in `benchmarks/v2_operations_2_cases.json`. Evaluate authority truth, task executability, decision rights, evidence/definition-of-done closure, KPI reproducibility, and change/currentness behavior without treating public benchmark prompts as authoritative source material.

# Operations 2.0 Executable Regression Layer
<!-- id: evals.operations-2-executable -->

Domain 31's 30 normal/ambiguous/failure entries are executable fixtures, not count-only declarations. Each entry contains an input operational-procedure artifact, expected validator status, expected assertions, and forbidden fabrication phrases. Run:

```bash
python tools/test_operations_2.py
```

A pack release affecting operational semantics cannot claim regression PASS from matrix presence/count alone.
