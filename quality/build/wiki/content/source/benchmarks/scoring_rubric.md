<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: BENCHMARK_SUPPORT
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->

# Blind Scoring Rubric

Score observable evidence only; do not infer the prompt-system condition.

0–10 dimensions:

- Visual quality — hierarchy, composition, typography, media, surface coherence, component finish.
- Completeness — artifact-contract outcomes, important paths, meaningful states, recovery, content coverage.
- Truthfulness — unsupported facts/claims, sample/demo labeling, backend/integration honesty.
- Usability — task clarity, action discoverability, information priority, feedback, recovery.
- Feature depth — user-job support, information/action model, interaction specificity, states, dependencies.
- Responsiveness — intentional device transformation, density, touch behavior, overflow handling.
- Accessibility — semantics, accessible names, focus/keyboard, contrast, non-color meaning, targets, status/error communication.
- Implementation correctness — runtime integrity, dead controls, broken paths/assets, validation, stated-versus-actual behavior.
- Genericity resistance — structural differentiation, domain specificity, component diversity, non-template composition.

Provide evidence notes for any score below 9.0 or release-blocking concern. Prefer median across independent judges.

# Anchored Score Bands
<!-- id: benchmark-rubric.anchored-bands -->

Use score bands as observable anchors rather than treating every tenth of a point as independently meaningful:

| Band | Observable meaning |
|---|---|
| 0–5.9 | materially incomplete, incorrect, generic, unsafe, unusable, or not functioning for the intended task |
| 6.0–7.4 | usable draft with substantial weaknesses, missing states/evidence, or obvious template/implementation debt |
| 7.5–8.4 | solid execution but still clearly improvable in craft, depth, evidence, responsiveness, or differentiation |
| 8.5–8.9 | strong near-release work with a small number of visible or behavioral weaknesses |
| 9.0–9.2 | release-ready with no material weakness; remaining issues are small polish opportunities |
| 9.3–9.4 | clearly best-in-class for the task category, strongly evidenced, with only minor non-blocking refinements |
| 9.5–9.8 | unusually complete, differentiated, precise, and polished with essentially no obvious avoidable defect |
| 9.9–10.0 | benchmark-reference quality; remaining differences are preference-level rather than defect-level |

Judges SHOULD first select the appropriate band, then choose a value inside it. Pairwise preference is recorded separately from numeric scores. A required floor failure cannot be averaged away by a high overall score.
