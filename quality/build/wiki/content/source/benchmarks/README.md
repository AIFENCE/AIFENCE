<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: BENCHMARK_SUPPORT
Module-Version: 2
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->

# Benchmark V2 Public Development Set

`v2_development_cases.json` contains 48 public development prompts (96 paired artifacts).

Do not commit private holdout prompts here. Keep them outside the public repository and pass them to `tools/prepare_benchmark.py --private-holdout /path/to/private.json`.

Use `BENCHMARKS.md` for the normative protocol and `benchmarks/scoring_rubric.md` for judge guidance.

## Runtime 1.0.5 fidelity extension

`v2_runtime_fidelity_cases.json` contains 12 public extension prompts for Runtime/Core routing fidelity and quality-closure behavior. Keep it separate from the frozen 48-case V2 longitudinal development set. It may be prepared with the normal blind-pair tooling, but no efficacy claim is valid until matched artifacts and condition-blind scores exist.

## Revision 1.7 semantic routing suite

`v2_semantic_routing_cases.json` contains 30 public semantic-routing and contract-resolution cases. Use `tools/benchmark_pipeline.py prepare` to create explicit paired generation jobs and a private blind key. Keep this suite separate from the frozen 48-case longitudinal V2 set.
