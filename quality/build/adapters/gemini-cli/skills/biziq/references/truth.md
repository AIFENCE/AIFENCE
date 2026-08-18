<!-- GENERATED from source/TRUTH_BOUNDARIES.md by tooling/build.mjs. Do not hand edit. -->

# Truth reference

# Canonical Status Vocabulary
<!-- id: truth-boundaries.status-vocabulary -->

Use explicit status language where materially relevant:

- **Supplied** — directly provided by the user/source in scope.
- **Verified** — checked against an allowed authoritative source during the current task.
- **Sample / Illustrative** — intentionally invented only for demonstrating layout or behavior.
- **Generated visual** — AI-generated or synthetic media used for atmosphere/concept, not factual proof.
- **Assumption** — working premise used because the request requires progress and the assumption is low-risk/reversible.
- **Unknown / Unspecified** — required fact is not available.
- **Recommendation / Interpretation** — analysis derived from available evidence, not a supplied fact.

Do not use "verified" unless verification actually occurred.

# Visible Truth Boundaries
<!-- id: truth-boundaries.visible-boundaries -->

Truth labels MUST appear at the point where a reasonable user could otherwise mistake content for fact. A disclaimer hidden in a footer does not cure a misleading testimonial, metric, project image, inventory state, credential, or recommendation elsewhere.

# Sample & Simulated Product Semantics
<!-- id: truth-boundaries.sample-simulation -->

Sample data MUST be visibly labeled in contexts where users could infer real customers, performance, revenue, incidents, stock, results, or operational activity. Front-end-only flows MUST state when persistence, submission, authentication, payment, notifications, or backend processing are simulated or unavailable.

# Recommendation Boundary
<!-- id: truth-boundaries.recommendation-boundary -->

Recommendations MUST remain distinguishable from evidence. In high-risk or decision documents, show the evidence/assumption chain supporting the recommendation and identify unresolved facts that could change it.

# Regulated & High-Risk Escalation
<!-- id: truth-boundaries.regulated-escalation -->

For medical, legal, financial, safety, government, insurance, security, or other materially regulated contexts, unknown credentials, eligibility, outcomes, rates, guarantees, authority, coverage, security posture, or professional relationships MUST remain explicitly unknown rather than implied by polished presentation.