---
name: biziq
description: Use BizIQ for production-quality websites, apps, dashboards, ecommerce, documents, operating procedures, design systems, feature plans, APIs, brand/SEO/security/legal work, and substantial artifact modifications. Routes requests through BizIQ Core with production completeness, truth boundaries, craft, responsive/accessibility evidence, adversarial QA, and Operations 2.0 when applicable.
---
# BizIQ Production Skill

Generated for BizIQ Core **{{CORE_REVISION}}** / Runtime **{{RUNTIME_VERSION}}**. Canonical standards remain in `source/`; this Skill is a derived activation layer.

Use BizIQ as a **router and control plane**, not as a giant prompt to preload.

## Activation

Activate for new production artifacts or substantial modifications where quality, completeness, implementation fidelity, truthfulness, operational rigor, or governed QA materially matters.

Do not activate merely to explain what BizIQ is unless the user asks for BizIQ analysis.

## Preferred workflow

1. **Ask the BizIQ Runtime for a plan.** Prefer the `biziq_plan` MCP tool when available. Otherwise run `biziq plan "<request>" --json` through the bundled launcher.
2. Treat BizIQ Core `README.md` as authoritative. Do not preload the repository.
3. Resolve creation type, production/delivery mode, industry only when material, independent profiles, risk overlays, artifact contract, active domains, and unresolved facts.
4. Retrieve only the exact sections required for the current step. Prefer stable IDs and `biziq_get_sections`/`biziq_get_control` over whole-file loading.
5. Compile important features/components before implementation when routed. For material SOP/runbook work, use Operations 2.0 and preserve authority/provenance boundaries.
6. Produce the complete requested artifact. Do not silently downgrade to MVP, mockup, prototype, placeholder-only, or brevity mode unless explicitly requested.
7. Apply truth boundaries: never invent business proof, credentials, legal/regulatory requirements, organization thresholds, authoritative procedure status, backend behavior, or real-world evidence.
8. Validate substantial work. Repair avoidable failures before delivery.

## Runtime commands

- MCP preferred: `biziq_plan`, `biziq_get_sections`, `biziq_get_control`, `biziq_get_artifact_contract`, `biziq_compile_*`, `biziq_validate`.
- CLI fallback: `biziq status`, `biziq plan`, `biziq get`, `biziq validate`, `biziq doctor`.
- If `biziq` is not on PATH, use `scripts/biziq-runtime.mjs` from this skill.

## Progressive references

Read only when needed:
- `references/routing.md` — exact runtime/fallback routing behavior.
- `references/truth.md` — truth, sample-data, authority, and unknown-fact boundaries.
- `references/qa.md` — final validation and evidence expectations.
- `references/operations.md` — Operations 2.0 activation and authority rules.

## Failure behavior

If Runtime/MCP is unavailable, do not invent its output. Follow the compact fallback in `references/routing.md`, locate BizIQ Core `README.md`, and continue with the smallest necessary retrieval. If Core cannot be located, state that BizIQ cannot be authoritatively applied rather than pretending the pack was loaded.
