<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: QUALITY_MEASUREMENT
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-09
-->

# Quality Measurement Calibration
<!-- id: quality-measurement.root -->

Purpose: ensure BizIQ quality floors are measurable without corrupting longitudinal benchmarks or mistaking evaluator limitations for artifact failures.

# Two-Lane Evaluation Model
<!-- id: quality-measurement.two-lane-model -->

Use two distinct lanes:

1. **Frozen longitudinal benchmark** — preserve the prior scoring formula/judges so revision-to-revision deltas remain comparable.
2. **Floor-capable acceptance audit** — use direct evidence capable of PASS/FAIL at every active production floor.

Do not silently modify the frozen benchmark to make a new revision score better. Do not use a frozen judge to prove a floor it is mathematically incapable of reaching.

# Evaluator Ceiling Test
<!-- id: quality-measurement.ceiling-test -->

Before interpreting a numerical floor failure, calculate the theoretical maximum and minimum of the active scoring formula where practical.

If an evaluator's maximum score is below a required floor, mark that evaluator **NON-DISPOSITIVE FOR THAT FLOOR** and use an independent evidence-capable audit. Preserve its result for longitudinal comparison.

# Floor-Capable Usability Evidence
<!-- id: quality-measurement.usability-evidence -->

Usability acceptance SHOULD combine direct task-path evidence from `USABILITY_CLOSURE.md` with rendered/runtime checks for orientation, action clarity, input efficiency, state preservation, feedback, recovery, keyboard/touch completion, and mobile task continuity.

Absence of dead controls and absence of horizontal overflow are supporting evidence, not sufficient evidence.

# Floor-Capable Visual Evidence
<!-- id: quality-measurement.visual-evidence -->

Visual acceptance SHOULD use rendered critical-view review against `VISUAL_FINISH.md`, including hierarchy, typography, spatial rhythm, component calibration, media treatment, and cross-viewport finish. Pixel statistics alone are insufficient to establish premium visual quality.

# Truth Evidence Calibration
<!-- id: quality-measurement.truth-evidence -->

Truthfulness scoring MUST evaluate both fabricated-claim absence and visible boundary/provenance quality from `TRUTH_BOUNDARIES.md`. Merely including one occurrence of words such as "sample" or "unspecified" cannot automatically prove truthfulness.

# Judge Independence & Score Lock
<!-- id: quality-measurement.independence-lock -->

Blind condition identity, lock scores before unblinding, and preserve raw evidence. A floor-capable audit may be added alongside a frozen benchmark, but the new audit's methodology and thresholds MUST be declared before inspecting condition labels.

# Disagreement Resolution
<!-- id: quality-measurement.disagreement -->

When frozen numerical scoring and direct acceptance evidence disagree:

- report both;
- do not rewrite history;
- explain whether the disagreement is due to artifact behavior, scorer coverage, scorer ceiling, or threshold mismatch;
- use the acceptance evidence for release gating only when its rubric was declared in advance and can actually measure the requirement.

# Acceptance
<!-- id: quality-measurement.acceptance -->

BizIQ may claim a production floor only when the evidence instrument can reach and discriminate around that floor. Benchmark comparability and release acceptance are related but not interchangeable goals.

# Render-State Normalization
<!-- id: quality-measurement.render-state-normalization -->
For screenshot- or pixel-derived benchmark evidence, normalize browser state before capture. At minimum: set the declared viewport, load the artifact from a fresh/known document state, reset scroll to the declared origin (normally `0,0`), clear unintended focus/hover/overlay state, wait for declared rendering stabilization, and then capture. Reused browser pages MUST NOT allow the previous artifact's anchor, scroll, focus, dialog, or transient interaction state to contaminate the next artifact's visual score.

If a benchmark discovers render-state contamination after scores were reported, preserve the legacy result for audit history, correct the protocol, rerender affected conditions symmetrically, and label the corrected series rather than silently rewriting the old score.
