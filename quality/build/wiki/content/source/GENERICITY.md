<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: GENERICITY
Module-Version: 2
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Structural Fingerprint & Genericity Engine
<!-- id: genericity.root -->

Purpose: make “template-like” output observable enough to reject before final implementation and again after rendered critique.

# Candidate Fingerprint
<!-- id: genericity.candidate-fingerprint -->

For each substantial concept, record as applicable: artifact family, shell/navigation model, opening composition, section/workflow sequence, dominant layout motifs, card/container ratio, component-type diversity, alignment bias, surface/elevation changes, CTA positions, media roles, density transitions, table/list usage, proof grammar, state patterns, mobile transformations, interaction/disclosure patterns, and distinctive domain-specific elements.

Use `schemas/structural_fingerprint.schema.json`.

# Common-Template Comparison
<!-- id: genericity.template-comparison -->

Compare candidates against `evals/generic_template_fingerprints.json`.

```text
0.00–0.45  low genericity risk
0.46–0.60  moderate; inspect
0.61–0.72  high; refine unless strongly justified
> 0.72     reject for premium production unless common structure is contract-required and differentiation evidence is compelling
```

The library represents common defaults, not prohibited styles. Category conventions may remain when useful, but high similarity requires meaningful differentiation elsewhere.

# Repetition Heuristics
<!-- id: genericity.repetition-heuristics -->

Raise risk for repeated centered heading + equal card grid, icon-heading-copy cards, rounded metric cards for unrelated information, identical CTA bands, interchangeable splits, one radius/elevation treatment everywhere, marketing-card grammar inside operational products, or desktop simply stacked on mobile.

For dense products additionally raise risk when the whole experience is only `sidebar + topbar + KPI cards + chart cards + table card`, or only `queue/list + generic right detail panel`, with no task-specific spatial or interaction logic. A familiar shell is allowed; the work inside it must still carry a project-specific information topology.

# Domain Specificity
<!-- id: genericity.domain-specificity -->

Genericity decreases only through meaningful domain evidence, user-job structure, information density, task-specific component anatomy, distinct section purpose, content-specific media, or interaction behavior. Cosmetic randomization alone is not differentiation.

# Dense Product Structural Differentiation
<!-- id: genericity.dense-product-differentiation -->

High-fidelity SaaS, dashboards, portals, and dense application interfaces require **structural differentiation evidence** before genericity resistance may PASS.

The evidence MUST demonstrate all of the following:

1. **Task-derived structure:** at least three non-cosmetic structural decisions; at least two must derive from a user job, workflow, domain/data model, or proof/decision model rather than brand decoration.
2. **Grammar diversity:** materially different information jobs use materially appropriate grammars. Dense products target at least four meaningful grammar families across the primary experience (for example table/list, timeline, inspector, comparison, chart, inline audit/event stream, status matrix, command surface, map, dependency graph, or structured form). Do not count color/radius variants as new grammars.
3. **Task-to-space linkage:** primary tasks explicitly map to the regions/surfaces that support orientation, inspection, decision, action, and recovery. Shell/navigation alone does not count as a differentiator.
4. **Competitor-swap resistance:** replacing the product/domain with a generic competitor should break at least two structural decisions. If the same composition could be relabeled for an unrelated SaaS product with no meaningful redesign, differentiation is insufficient.
5. **Template similarity:** run the structural fingerprint against the generic library. A best match at or above `0.61` is non-pass for premium/high-fidelity dense products until repaired; `0.46–0.60` requires explicit rendered differentiation evidence.
6. **Rendered confirmation:** at least three observed rendered characteristics must show that the differentiated structure survived implementation.

Use `schemas/genericity_evidence.schema.json` and `tools/validate_genericity_evidence.py`.

# Dense Product Recovery Patterns
<!-- id: genericity.dense-product-recovery -->

When dense-product genericity fails, repair the information topology rather than adding decorative novelty. Prefer transformations such as:

- make the primary workflow itself the composition instead of placing it inside a generic card;
- use persistent context, inline decision history, comparisons, causality, dependencies, or exception/recovery surfaces when the job needs them;
- give different information types different containment/elevation rules;
- let hierarchy and spatial continuity express relationships that would otherwise become unrelated cards;
- create one memorable task-specific interaction or visual/data moment beyond the shell;
- preserve accessibility, mobile task completion, truth, and implementation correctness during differentiation repair.

# Two-Stage Gate
<!-- id: genericity.two-stage-gate -->

1. Pre-implementation: fingerprint serious concepts and compile structural differentiation evidence; reject high-risk default compositions.
2. Post-render: Genericity Critic evaluates actual pixels/structure and reconciles them with the differentiation evidence. Material drift reopens Recovery.

# Tooling
<!-- id: genericity.tooling -->

`tools/fingerprint_similarity.py` provides a deterministic weighted-overlap heuristic. `tools/validate_genericity_evidence.py` enforces the dense-product closure manifest. These tools support judgment; they do not replace rendered critique.
