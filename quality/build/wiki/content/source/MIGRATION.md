<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: MIGRATION
Module-Version: 5
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-09
-->

# Migration — AIFENCE 3.1.0 → 4.0.0
<!-- id: migration.4-0-0 -->

AIFENCE 4.0.0 introduced the normative lazy control plane. Existing domain modules remain authoritative for domain content while `CONTROL_INDEX.md` and `controls/*.md` provide execution contracts, Evidence Gates, Recovery behavior, and regression coverage.

## Required behavior

- Load README first.
- Route through CONTROL_INDEX after task classification.
- Treat Evidence Gates as completion gates.
- Use UNVERIFIED when evidence cannot be obtained.
- Preserve decision state and re-evaluate affected controls after material changes.
- Run `tools/validate_pack.py` when AIFENCE itself changes.

## Compatibility

Existing industry/design/feature/halo/job/SOP IDs remain stable.

# Control-Plane Revision 1.1 — Native Feature & Component Craft
<!-- id: migration.control-plane-1-1 -->

This revision promotes Feature & Component Craft into the canonical AIFENCE control plane as **Domain 26**.

## Architecture

```text
Domains: 26
Capabilities: 210
Controls: 1,050
Control IDs: BQ-0001 through BQ-1050
Regression conditions: 630
```

Existing BQ-0001 through BQ-1000 are unchanged. New controls use BQ-1001 through BQ-1050.

## Native additions

- `CRAFT.md`
- `controls/26-feature-component-craft.md`
- `control_registry/26-feature-component-craft.csv`
- `evals/control_regression_matrix_26.json`
- Domain 26 routes in `CONTROL_INDEX.md`
- craft-aware release gates in `QA_GATES.md`
- integrated validation in `tools/validate_pack.py`

## Registry architecture

`control_registry.csv` remains the stable base registry. Domain-specific CSV files under `control_registry/` are native registry shards. The validator and CONTROL_INDEX treat them as one logical registry.

## Regression architecture

`evals/control_regression_matrix.json` remains the stable base matrix. Domain-specific matrix shards are logically merged and validated as one regression system.

## Legacy extension retirement

If an earlier craft-extension package was applied, the following are deprecated and no longer authoritative:

- `CRAFT_CONTROL_INDEX.md`
- `control_registry_extension.csv`
- `tools/validate_craft_extension.py`
- `evals/craft_end_to_end_cases.json`

Compatibility stubs may remain, but all active routing uses `CONTROL_INDEX.md` and `tools/validate_pack.py`.

# Control-Plane Revision 1.2 — Compiled Artifact & Adversarial Quality Architecture
<!-- id: migration.control-plane-1-2 -->

Revision 1.2 implements the post-benchmark architecture:

```text
Request
→ artifact contract
→ feature compiler
→ concept exploration
→ structural fingerprint / genericity rejection
→ component compiler
→ implementation
→ runtime/render
→ independent adversarial critics
→ prioritized repair
→ re-render / re-evaluate
→ artifact-specific quality floors
→ final Evidence Gates
```

New domains:

- Domain 27 — Artifact Contracts & Specification Compilation — BQ-1051–BQ-1100.
- Domain 28 — Adversarial Critique, Repair, Quality Floors & Benchmarking — BQ-1101–BQ-1150.

Current logical control plane at Revision 1.2:

```text
28 domains
230 capabilities
1,150 controls
690 capability regression conditions
```

BQ-0001 through BQ-1050 remain unchanged.

Benchmark V2 has 48 public development prompts (96 paired artifacts); private holdout prompts remain external to the public repository.

# Control-Plane Revision 1.3 — Benchmark-Driven Quality Hardening
<!-- id: migration.control-plane-1-3 -->
Revision 1.3 adds Domain 29 (BQ-1151–BQ-1200) and five targeted standards for responsive composition, document decision/editorial craft, accessibility evidence, completion coverage, and feature-depth closure. The Revision 1.2 genericity engine and fingerprint library are preserved. Current plane: 29 domains, 240 capabilities, 1,200 controls, 720 regression conditions.

# Control-Plane Revision 1.4 — Quality Closure & Measurement Calibration
<!-- id: migration.control-plane-1-4 -->
Revision 1.4 adds Domain 30 (`BQ-1201`–`BQ-1250`) for usability task-friction closure, rendered visual finish, explicit truth/provenance boundaries, responsive document/operations detail, and quality-floor measurement calibration. Current plane: 30 domains, 250 capabilities, 1,250 controls, 750 regression conditions. Revision 1.2 genericity remains unchanged and Revision 1.3 hardening remains active.

# Control-Plane Revision 1.5 — Operations 2.0
<!-- id: migration.control-plane-1-5 -->

Revision 1.5 adds Domain 31 (`BQ-1251`–`BQ-1300`) and an operational compilation layer without renumbering existing controls. Existing `JOBS.md` and `operations/*.md` remain canonical role/profile baselines, but material real-world procedures now compile through `OPERATIONAL_PROCEDURE_COMPILER.md`, authority/provenance, decision-rights, operational-evidence, and KPI-governance standards.

Current logical control plane:

```text
31 domains
260 capabilities
1,300 controls
780 capability regression conditions
```

Revision 1.5 specifically addresses the gap between a well-structured generic SOP and an executable, authority-aware, auditable operating procedure.

# Control-Plane Revision 1.6 — Operations Integrity & Machine Enforcement
<!-- id: migration.control-plane-1-6 -->

Revision 1.6 does **not** add controls or domains. It preserves all BQ-0001–BQ-1300 IDs and the 31-domain / 260-capability / 1,300-control architecture while closing implementation-integrity gaps found after the Operations 2.0 benchmark.

Changes: canonicalized `MANIFEST.md` control metadata delegation; harmonized Domain 23 metric target provenance with Domain 31; defined Domain 23 baseline vs Domain 31 specialization ownership; made operational schemas closed/composed with lifecycle, authority-map, decision-right, evidence, role, KPI, exception, handoff, and Definition-of-Done objects; strengthened strong-authority/currentness and KPI/approval conditionals; unified schema + semantic validation; converted all 30 Domain 31 regression conditions into executable fixtures; and added a dedicated executable regression runner.

# Control-Plane Revision 1.7 — Semantic Routing & Retrieval Intelligence
<!-- id: migration.revision-1-7 -->

Revision 1.7 does not renumber BQ controls. Consumers should migrate from whole-module Runtime loading to `phases[].retrievalActions` / `activeCapabilities`, treat `activeModules` as compatibility/debug metadata, consume structured `contextGraph`, `riskGraph`, and `artifactGraph`, support composite contract chains, and use executable evidence records for evidence-required PASS decisions. Existing clients that only inspect creation type, domains, modules, contracts, and QA remain readable because those fields are retained.
