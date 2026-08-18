<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: BENCHMARK_FINDINGS_1_3
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-09
-->

# Revision 1.3 Benchmark Findings → Revision 1.4 Closure
<!-- id: benchmark-findings-1-3.root -->

Revision 1.3 scored **93.34** on the frozen 48 public Benchmark V2 cases versus **89.60** for Revision 1.2, winning **48/48** matched cases. On a rotated 24-case holdout, Revision 1.3 scored **93.44** versus **79.93** control, winning **24/24** pairs.

Targeted Revision 1.3 improvements worked: completeness rose 8.80→9.68, feature depth 8.78→9.54, responsiveness 7.95→9.12, and accessibility 8.80→9.21 while genericity resistance remained extremely strong at 9.86.

Remaining measured gaps:

- frozen usability remained ~8.60;
- visual quality remained ~8.94;
- truthfulness showed a small 9.34→9.30 regression, concentrated in documents where explicit sample/unknown boundary wording was reduced;
- some document/operations cases showed small frozen responsive-score regressions despite passing page-level overflow and new 320/390/768 evidence.

## Measurement finding
<!-- id: benchmark-findings-1-3.usability-ceiling -->

The frozen usability judge is **not capable of proving the 9.0 production floor**. Its three component formulas have maxima of approximately 9.15, 8.75, and 8.60, and the frozen combined score takes their median, producing a theoretical maximum of 8.75. Therefore the frozen score remains useful for longitudinal comparison but cannot be release-dispositive for the 9.0 usability floor.

Revision 1.4 preserves the frozen judge and adds a separately declared floor-capable task-path evidence system.

## Revision 1.4 response
<!-- id: benchmark-findings-1-3.response -->

1. `USABILITY_CLOSURE.md` — task friction, action hierarchy, state continuity, input efficiency, feedback, recovery.
2. `VISUAL_FINISH.md` — perceptual hierarchy, optical spacing/typography/surface/media calibration.
3. `TRUTH_BOUNDARIES.md` — visible supplied/verified/sample/assumption/unknown/interpretation/recommendation provenance.
4. `RESPONSIVE_DETAIL_CLOSURE.md` — task-level document/operations narrow-viewport evidence beyond page overflow.
5. `QUALITY_MEASUREMENT.md` — frozen longitudinal vs floor-capable acceptance lanes and scorer-ceiling detection.
6. Domain 30 — 10 capabilities / 50 controls / 30 regression conditions.
7. A separate 20-case Revision 1.4 quality-closure suite, while preserving the frozen 48 public cases.
