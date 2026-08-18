<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: BENCHMARKS
Module-Version: 3
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# AIFENCE Benchmark Protocol
<!-- id: benchmarks.root -->

Purpose: measure whether AIFENCE improves real artifacts rather than merely adding rules or optimizing against its own evaluator.

# Benchmark V2
<!-- id: benchmarks.v2 -->

The public development set contains **48 representative requests**. A paired A/B run creates **96 artifacts**.

A serious release benchmark SHOULD also use a separately maintained private holdout of at least **24 requests** (48 paired artifacts), producing at least **144 artifacts** across public development + private holdout.

Private holdout prompts should not be committed to the public AIFENCE repository.

# Conditions
<!-- id: benchmarks.conditions -->

- Control: same model/tool stack with AIFENCE disabled; use only the request and unavoidable platform instructions.
- AIFENCE: same model/tool stack, same request, same external facts/assets when practical, AIFENCE enabled.
- Keep model family, generation mode, tool access, resource budget, and request facts matched.
- Randomize condition order.
- Do not intentionally degrade the control.

# Blinding
<!-- id: benchmarks.blinding -->

1. assign opaque artifact IDs;
2. store condition mapping separately;
3. hide condition, prompt-system identity, desired result, and prior scores from evaluators;
4. score/lock results before unblinding;
5. preserve the unblinding key and run seed.

`tools/prepare_benchmark.py` creates the randomized paired manifest and separate key.

# Evaluation
<!-- id: benchmarks.evaluation -->

Score the nine `QUALITY_FLOORS.md` dimensions. Prefer multiple independent model judges and/or qualified human judges, median score per artifact/dimension, automated runtime/accessibility/browser checks as evidence inputs, direct pairwise preference in addition to scalar scores, and written failure reasons for material losses.

# Automated Evidence
<!-- id: benchmarks.automated-evidence -->

Where applicable collect console/runtime errors, broken links/assets, dead controls, overflow, viewport renders, keyboard completion, accessibility findings, performance evidence, backend/simulation truth, required-state captures, and structural-fingerprint similarity.

# Anti-Overfit
<!-- id: benchmarks.anti-overfit -->

Maintain a private holdout outside the public repository; rotate part after major improvements; track category/contract/dimension results; investigate development improvements that regress on holdout; and do not add a rule solely to win one public item unless it generalizes to a real failure class.

# Release Interpretation
<!-- id: benchmarks.release-interpretation -->

Meaningful improvement should show positive paired median delta, no material regression in truthfulness/accessibility/implementation/safety, improvement on private holdout, fewer release-blocking failures, and evidence across multiple artifact families.

A benchmark score is evidence, not proof of universal model superiority.

# Revision 1.3 Hardening Suite
<!-- id: benchmarks.hardening-suite -->

`benchmarks/v2_hardening_cases.json` contains 20 public regression prompts targeting the measured Revision 1.2 weaknesses. It supplements the frozen 48-case V2 development set. Do not merge the hardening prompts into the frozen set when reporting longitudinal V2 scores. Use a rotated external private holdout for the next efficacy run.

# Revision 1.4 Measurement Calibration
<!-- id: benchmarks.revision-1-4-measurement -->
The 48 public Benchmark V2 development cases remain frozen for longitudinal comparisons. `benchmarks/v2_hardening_cases.json` remains the Revision 1.3 targeted suite. `benchmarks/v2_quality_closure_cases.json` is a separate Revision 1.4 development/hardening suite and MUST NOT be merged into the frozen 48 when reporting historical V2 scores.

A key Revision 1.3 finding is that the frozen usability judge is not floor-capable: its component formulas mathematically cap the median usability score below the 9.0 global floor. Preserve that judge unchanged for longitudinal scoring, but use `QUALITY_MEASUREMENT.md` plus `USABILITY_CLOSURE.md` for release-floor evidence. Declare any new floor-capable rubric before unblinding condition identity.

# Browser Render-State Normalization
<!-- id: benchmarks.render-state-normalization -->
Browser-rendered benchmarks MUST normalize viewport, scroll origin, focus/hover/overlay state, and render settling before each screenshot. Reusing a browser page is allowed only when state is explicitly reset between artifacts. A visual judge must not score a random mid-page viewport caused by a previous artifact's interaction. Protocol corrections must be applied symmetrically to compared revisions/conditions and documented as a new normalized series while retaining legacy score history.

# Runtime 1.0.5 / Core 1.6 Fidelity Closure Suite
<!-- id: benchmarks.runtime-1-0-5-fidelity -->

`benchmarks/v2_runtime_fidelity_cases.json` contains 12 public paired-benchmark prompts targeting the newest Runtime/Core integration failure modes: Domain 29/30 module routing, asset routing, high-fidelity concept semantics, financial-regulated risk expansion, initialization-with-inline-execution, responsive detail, and floor-capable quality evidence. It is a **separate extension suite** and MUST NOT be merged into the frozen 48-case longitudinal Benchmark V2 score.

A release may report this suite as **prepared** or **executed** only according to available evidence. Do not publish efficacy scores until matched control/AIFENCE artifacts have been generated under identical model/tool conditions, opaque IDs have been scored by condition-blind judges, scores have been locked before unblinding, and an external private holdout has also been evaluated. Runtime regression PASS is not a substitute for visual efficacy evidence.

# Revision 1.5 Operations 2.0 Targeted Corpus
<!-- id: benchmarks.operations-2 -->

`benchmarks/v2_operations_2_cases.json` contains 20 public regression prompts for operational executability, authority truth, decision rights, evidence/definition-of-done, KPI governance, and procedure lifecycle/currentness. It supplements the frozen 48-case longitudinal set and MUST NOT replace or modify it.

For claims about regulatory, legal, clinical, safety, manufacturer, or organization-specific accuracy, benchmark prompts are not sources of authority. The generated condition must retrieve or be supplied authoritative evidence when the task requires it, or preserve the affected content as draft/general guidance/UNVERIFIED.

# Revision 1.7 Semantic Routing & Retrieval Suite
<!-- id: benchmarks.semantic-routing-1-7 -->

`benchmarks/v2_semantic_routing_cases.json` contains 30 public routing/contract cases covering substring collisions, explicit negation, expanded artifact types, composite artifacts, public/internal semantics, risk/exposure separation, reference-inspired wording, and high-/low-fidelity concepts. These are deterministic routing regressions and a benchmark corpus; they do not by themselves establish visual efficacy.

`tools/benchmark_pipeline.py` manages the auditable lifecycle: paired generation jobs, artifact capture and hashes, condition-blind judging manifests, score-hash locking, unblinding, bootstrap confidence intervals, effect size, per-dimension/family/split deltas, floor-failure rates, pairwise preference counts, and inter-judge spread. Conditions and scores MUST remain separated until the score lock is recorded.
