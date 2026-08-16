<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: EVIDENCE_ADAPTER
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->

# Executable Evidence Adapter Contract
<!-- id: evidence-adapter.root -->

Purpose: define a model/tool-neutral interface through which browser-, runtime-, spreadsheet-, slide-, document-, and CLI-capable agents can return machine-verifiable QA evidence instead of self-attested completion.

# Evidence Record
<!-- id: evidence-adapter.record -->

Each record identifies artifact node, evidence type, tool/adapter, timestamp when available, target state/viewport/platform, result, observations, produced files or hashes, and whether the evidence is direct, inferred, or unavailable. Evidence never upgrades an unexecuted check to PASS.

# Browser Evidence Profile
<!-- id: evidence-adapter.browser -->

Where browser execution exists, capture applicable: viewport screenshots; overflow/clipping; console/runtime errors; broken resources; primary controls and links; keyboard critical path; focus visibility; dialog/menu/dropdown states; loading/empty/error/success states; accessibility scan output; performance metrics; and responsive transformation at contract-defined widths.

For substantial interactive artifacts, browser evidence MUST also include two structured closure records:

- `interactive control closure` — exhaustive accounting of enabled visible controls against the pre-implementation interaction manifest. Direct PASS requires the runtime-discovered enabled-control inventory to exactly reconcile with the manifest, every enabled control to be exercised, and `deadControlIds` to be empty. An enabled rendered control omitted from the manifest is a failure, not an exemption.
- `mobile task preservation` — task-level results for every manifest-declared P0/P1 task at every required narrow viewport, including 320 and 390 px by default. Direct PASS requires entry, completion, state/context preservation, and applicable recovery to succeed.

The manifest is validated by `schemas/interaction_closure_manifest.schema.json`. `tools/validate_execution_evidence.py --interaction-manifest <file>` cross-checks evidence against it; omitting declared controls/tasks cannot produce PASS.

# Non-Web Evidence Profiles
<!-- id: evidence-adapter.non-web -->

- Spreadsheet: formula errors, recalculation, cross-sheet references, scenario changes, workbook open integrity, print/freeze/format checks.
- Presentation: slide overflow, font fallback, image quality, export rendering, contrast, notes/links where required.
- PDF/document: page rendering, clipping, table breaks, links, tags/reading order when accessible PDF is required.
- CLI: exit codes, stdout/stderr, help, invalid inputs, missing configuration, destructive confirmation, platform smoke tests.
- Native app: device/viewport states, permission flows, keyboard/safe-area behavior, lifecycle interruption/recovery when tool support exists.

# Acceptance Rule
<!-- id: evidence-adapter.acceptance -->

A quality gate that requires executable evidence may PASS only from direct evidence or an explicitly approved equivalent. `unavailable` is not failure by itself, but it must remain visible and may block production acceptance when the artifact contract marks that evidence class release-critical.

# Executable Validation Interface
<!-- id: evidence-adapter.validator -->

Use `tools/validate_execution_evidence.py <evidence.json> [--plan runtime-plan.json] [--interaction-manifest interaction.json]` to validate evidence records against `schemas/execution_evidence.schema.json`, verify release-critical plan coverage, and cross-check exhaustive enabled-control/mobile-task closure when a manifest is supplied. A `PASS` record with non-direct provenance is invalid. A required plan check without a direct PASS remains `UNVERIFIED` and blocks evidence-backed production acceptance.
# Dense-Product First-Pass Quality Evidence
<!-- id: evidence-adapter.dense-product-first-pass -->

When Runtime declares `denseProductQualityClosure`, collect direct evidence for the four non-averagable sections in `schemas/dense_product_quality_evidence.schema.json`. Generation preflight and interaction closure remain prerequisites. A dense-product quality record may reuse the same direct browser observations, screenshots, keyboard traces, state transitions, and task evidence, but each required section must independently satisfy its acceptance semantics.

