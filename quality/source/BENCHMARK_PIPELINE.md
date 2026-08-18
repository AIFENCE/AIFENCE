<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: BENCHMARK_PIPELINE
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->

# End-to-End Benchmark Pipeline
<!-- id: benchmark-pipeline.root -->

Purpose: turn benchmark preparation and scoring into an auditable lifecycle rather than disconnected utilities.

# Lifecycle
<!-- id: benchmark-pipeline.lifecycle -->

```text
case corpus
→ control/AIFENCE generation manifest
→ artifact capture + hashes
→ render normalization
→ automated evidence bundle
→ condition-blind judge package
→ score lock
→ unblind
→ paired statistical analysis
→ findings + regression promotion
```

The pipeline MUST NOT fabricate generations, judge scores, or evidence. Missing stages remain explicitly incomplete.

# Statistical Report
<!-- id: benchmark-pipeline.statistics -->

For complete paired runs report: pair count; mean and median deltas; nonparametric bootstrap confidence interval for the paired mean and median; per-dimension win/loss/tie rates; overall pairwise preference; floor-failure rate; artifact-family deltas; development vs holdout deltas; effect size; and inter-judge agreement when multiple judges score the same artifact.

# Quality Score Anchors
<!-- id: benchmark-pipeline.anchors -->

Scores are anchored behaviorally. `9.0` means release-ready with no material weakness and only small polish opportunities; `9.3` means clearly best-in-class for the task class with strong evidence and only minor non-blocking refinements; `9.5` means unusually complete, differentiated, and precise with essentially no obvious avoidable defect; `10.0` is reserved for benchmark-reference quality where further improvement would be preference-level rather than defect-level. Judges should prefer anchored bands and paired preference over false precision.

# Regression Fuzzing
<!-- id: benchmark-pipeline.fuzzing -->

Classifier/routing regression must include deterministic adversarial cases for token collisions, negation, singular/plural variants, ambiguous industries, mixed artifacts, public/internal distinction, front-end-only semantics, contradictory requirements, prototype/high-fidelity combinations, and reference-inspired wording. Real failures become permanent fixtures.

# Control Activation Coverage
<!-- id: benchmark-pipeline.control-coverage -->

The pack generates a coverage inventory mapping every control/capability to its shard, activation evidence when observed, regression references, benchmark references, and reachability status. Unreachable, never-tested, or permanently co-activated capabilities are review findings rather than silently accepted growth.

# Semantic Duplication & Conflict Lint
<!-- id: benchmark-pipeline.semantic-lint -->

A deterministic semantic lint performs normalized similarity checks for duplicated requirements and heuristic scans for MUST/MUST NOT conflicts that target highly similar requirement text. Findings are review candidates; the linter does not automatically rewrite canonical controls.
