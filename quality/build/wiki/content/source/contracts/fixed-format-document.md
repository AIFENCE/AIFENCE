<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: ARTIFACT_CONTRACT
Contract: Fixed-Format Document / PDF
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Fixed-Format Document / PDF Production Contract
<!-- id: contract.artifact.fixed-format-document -->

## Reader & Purpose
Resolve reader, use context, decision/information goal, required sections, evidence sources, and whether the document is print, screen, or both.


## Findings, Implications & Reader Decisions
A substantial report MUST resolve material questions/issues into at least three distinct findings or conclusions and at least three implications/actions, supported by at least four evidence points and two provenance/source-boundary markers. Include reader-facing takeaways or decisions. Repeated summary prose does not count as additional findings.

## Page System
Use intentional page size, margins, grids, typography, running elements, tables, figures, captions, callouts, and section starts. Avoid accidental orphaned headings and card-heavy web layouts transplanted to print.

## Truth & Citation Contract
Separate supplied facts, sourced facts, calculations, assumptions, recommendations, and sample content. Citations and references must be real and traceable when required.

## Accessibility & Output Integrity
When accessible PDF is required, preserve reading order, tagged structure, alt text, contrast, and navigable headings/links. Verify pagination, clipping, table breaks, image resolution, and font embedding. Direct acceptance also requires logical reading-order/table-order evidence, readable contrast, zoom or magnification verification, navigable links where applicable, and alt-text evidence or an explicit not-applicable determination.

## Evidence
Render every page and inspect page boundaries, overflow, text/table collisions, tables/figures, links, headings, footers, references, and final PDF integrity. Run the Core 1.8.6 PDF text-geometry/render-accessibility preflight before freeze.
