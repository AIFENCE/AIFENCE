<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: FAMILY_DEPTH_CLOSURE
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Family Depth Closure
<!-- id: family-depth-closure.root -->

Core 1.8.1 converts the repeated Holdout-1 first-pass failures in public websites, mobile apps, brand systems, email campaigns, CLI tools, and responsive composite projects into executable family-specific closure. It supplements existing artifact contracts, `NONWEB_FIRST_PASS.md`, truth boundaries, accessibility, implementation preflight, and evidence rules without adding BQ IDs or weakening previously passing families.

# Website Decision Depth
<!-- id: family-depth-closure.website -->

A substantial high-fidelity public website MUST compile at least two materially different visitor decision paths: one primary conversion/commitment path and one evaluation, qualification, proof, support, or secondary-action path. Each path MUST expose the visitor decision, relevant evidence/proof, material objection or uncertainty, next action, continuation/downstream state, concrete artifact surface, truth boundary, and narrow-screen equivalent. A polished `hero -> features -> testimonials -> CTA` sequence is insufficient by itself.

The page architecture MUST be derived from decisions and proof needs rather than repeated generic section grammar. Proof should precede or accompany commitment where it materially changes the decision. Secondary paths may not be omitted merely to simplify the first pass.

# Mobile Workflow Depth
<!-- id: family-depth-closure.mobile -->

A substantial native/mobile artifact MUST compile at least one P0 and one P1 workflow through entry/orientation, action, state/feedback, material error or interruption, recovery/retry, continuation, compact-device surface, and larger-device/adaptive surface. Mobile-specific navigation, permission/offline/interruption semantics, state restoration, touch-target/readability, and focus/keyboard behavior where applicable MUST be explicit rather than inherited from a desktop mental model.

# Brand System Completeness
<!-- id: family-depth-closure.brand -->

A production/high-fidelity brand identity MUST be a usable visual-language system, not a logo moodboard. At minimum it MUST define roles and usage rules for identity mark/wordmark, typography, color, composition/layout, iconography, and imagery. Motion/interaction principles are required when the intended applications are interactive. Each core system element MUST include purpose, rules, at least one do/don't boundary, and an observable application. At least three materially different application contexts MUST demonstrate the system. Sample claims, photography, endorsements, awards, and other proof-bearing content remain subject to truth/provenance boundaries.

# Campaign Sequence Depth
<!-- id: family-depth-closure.email -->

A substantial email/campaign artifact MUST compile the sequence as a stateful lifecycle rather than a set of individually polished messages. A sequence MUST contain at least three meaningful stages unless the user explicitly requests fewer, and each stage MUST identify audience state/segment, message job, evidence/proof boundary, CTA/action, expected event or measurement, fallback/recovery, and next state. Branching or segmentation MUST be explicit when different audience states materially change the message or action.

# CLI Product Depth
<!-- id: family-depth-closure.cli -->

A substantial CLI/developer tool MUST expose a coherent product surface: discoverable root/help behavior, at least one primary job command or mode, input/config precedence, deterministic success output, deterministic error output, exit-code semantics, recovery guidance, and safety/dry-run/confirmation behavior where destructive or consequential operations exist. Tests/fixtures MUST cover help, happy path, invalid input, and material recovery. A single successful command invocation is insufficient first-pass depth.

# Composite Narrow-Screen Containment
<!-- id: family-depth-closure.composite -->

Composite projects MUST preserve each child artifact's independent contract and QA while sharing only explicit project context. When any child is web/mobile/responsive, the composite acceptance record MUST include direct 320px and 390px containment evidence for that child: no horizontal overflow, no clipped task-critical content, no hidden P0/P1 path, and no cross-artifact shell/layout assumption that breaks the child. A passing sibling artifact may not offset a failing child.

Before the child is frozen, its compact composition MUST also compile width-safe primitives rather than relying on a later screenshot repair: shrinkable flex/grid descendants use `min-width: 0`; images/media/inputs cannot exceed their containing block; long URLs/tokens wrap; fixed and minimum widths are bounded; tables/data regions have an explicit compact strategy; and project shells/tokens may not impose desktop-only child widths. The 320/390 evidence is therefore both a generation prerequisite and a final acceptance gate.

# Executable Acceptance
<!-- id: family-depth-closure.acceptance -->

Use `schemas/family_depth_evidence.schema.json` and `tools/validate_family_depth_evidence.py`. Evidence is direct and fail-closed. Required family records, critical-dimension floors, or responsive containment evidence may not be inferred from source intent. Any failed required check blocks family-depth PASS until the smallest upstream cause is corrected and re-executed.

# Recovery
<!-- id: family-depth-closure.recovery -->

Repair the upstream decision/workflow/system/sequence/product/composite structure rather than padding the artifact with decorative sections or hidden content. Preserve already-passing routing, retrieval budgets, truth boundaries, and family contracts. Re-run only affected direct evidence plus any dependent critical path.
