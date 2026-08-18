<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: VISUAL_FINISH
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->

# Visual Finish & Perceptual Quality Standard
<!-- id: visual-finish.root -->

Purpose: close the "last-mile" visual gap after structure and genericity are already strong. This standard focuses on perceptual hierarchy, optical calibration, editorial rhythm, component precision, and cross-viewport finish.

# Hierarchy Before Decoration
<!-- id: visual-finish.hierarchy -->

A polished artifact MUST communicate priority through more than container size. Validate contrast of scale, weight, spacing, position, grouping, and emphasis across primary message, supporting context, metadata, controls, and evidence.

Reject:

- every section carrying equal visual weight;
- repeated heading/body/button cadence with no editorial modulation;
- strong decoration around weak information hierarchy;
- primary and secondary actions with indistinguishable emphasis;
- dense metadata competing with task-critical content.

# Spatial Rhythm Calibration
<!-- id: visual-finish.spatial-rhythm -->

Use a coherent spacing system, then perform an optical pass. Mathematical spacing alone is insufficient when typography, borders, icons, and media create uneven perceived gaps.

Review:

- section-to-section rhythm;
- heading-to-body and label-to-value spacing;
- card/content inset consistency;
- alignment across adjacent components;
- dense-table row height and scanning rhythm;
- terminal spacing before footer/sticky controls;
- mobile compression without visual crowding.

# Typographic Finish
<!-- id: visual-finish.typography -->

Typography MUST expose role, not merely size. Verify line length, line-height, weight contrast, numeric alignment, metadata tone, label clarity, heading wraps, orphan-like fragments, and long-content behavior.

For dense products, numeric/tabular content SHOULD use stable alignment. For documents, body measure and heading rhythm SHOULD support long-form reading rather than dashboard density.

# Surface & Component Calibration
<!-- id: visual-finish.surface-calibration -->

Borders, radii, shadows, fills, separators, and elevation MUST communicate hierarchy/state consistently. Do not add elevation merely to make a surface look "premium." Different surface treatments need a semantic reason such as containment, selection, overlay, warning, evidence, or focus.

Review icon baseline alignment, badge padding, input/button height compatibility, disclosure affordances, dividers, chart labels, table headers, and empty/error-state composition.

# Media & Evidence Finish
<!-- id: visual-finish.media-finish -->

Media crops, illustrations, charts, diagrams, and proof-bearing visuals MUST align with surrounding hierarchy and responsive focal behavior. Do not use one polished hero beside visibly lower-fidelity filler media.

# Cross-Viewport Finish Sweep
<!-- id: visual-finish.cross-viewport -->

Perform a final perceptual sweep at representative desktop, tablet, 390px, and 320px views when responsive delivery applies. The goal is not identical composition; the goal is equivalent hierarchy, legibility, and intentionality.

# Visual Defect Ledger
<!-- id: visual-finish.defect-ledger -->

Record material defects before final acceptance:

```text
Defect ID
Viewport / page / component
Hierarchy / typography / spacing / surface / media / alignment / state
Observed defect
Severity
Repair
Re-render evidence
Regression dimensions checked
```

# Acceptance
<!-- id: visual-finish.acceptance -->

Visual-quality PASS requires rendered evidence showing coherent hierarchy, calibrated rhythm, polished typography, consistent surfaces, aligned controls/icons, and no material unfinished region across applicable critical views. Genericity resistance MUST be rechecked after visual repairs.
# Dense-Product First-Pass Finish
<!-- id: visual-finish.dense-product-first-pass -->

For high-fidelity SaaS/dashboard/portal work, visual quality MUST be established in the initial generation before acceptance rather than delegated to a later cosmetic polish pass. Direct rendered evidence at desktop plus 390px and 320px critical views must show all of the following:

- one clearly dominant task/orientation region and an intentional secondary evidence/action hierarchy;
- at least three semantically distinct surface roles (for example workspace, evidence, selected/detail, exception/recovery) rather than uniform cards;
- calibrated dense-row/field/control rhythm with aligned icon/text/control baselines and no visibly accidental gaps;
- stable typography roles for page/task title, section/region labels, data values, metadata, annotations, and state/error text;
- coherent control geometry and affordance hierarchy across filters, primary actions, contextual actions, and destructive/recovery actions;
- intentionally designed empty/no-results, error/recovery, selected/detail, and feedback states when applicable;
- no material unfinished region, placeholder-looking filler, abrupt density discontinuity, or mobile composition that looks like a collapsed desktop afterthought.

A first-pass artifact with clean code and strong structure is still visual NON-PASS when rendered evidence fails these finish requirements. Use the visual section of `dense_product_quality_evidence.schema.json`; do not infer PASS from source CSS tokens alone.

