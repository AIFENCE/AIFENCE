<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: TRUTH_BOUNDARIES
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-09
-->

# Truth Boundary & Provenance Standard
<!-- id: truth-boundaries.root -->

Purpose: prevent polished output from making unknown, simulated, generated, illustrative, or inferred content look like verified real-world fact.

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

# Document Provenance Ledger
<!-- id: truth-boundaries.document-provenance -->

Substantial reports, memos, analyses, due-diligence documents, and regulated documents SHOULD distinguish:

```text
Statement / finding
Status: Supplied | Verified | Assumption | Unknown | Interpretation | Recommendation
Source / evidence reference
Confidence / limitation when material
Downstream decision affected
Verification owner / next step when unresolved
```

The document may remain readable and elegant; provenance does not require turning every sentence into a database row. Use ledgers, footnotes, evidence callouts, source notes, or section-level provenance appropriate to the document type.

# Sample & Simulated Product Semantics
<!-- id: truth-boundaries.sample-simulation -->

Sample data MUST be visibly labeled in contexts where users could infer real customers, performance, revenue, incidents, stock, results, or operational activity. Front-end-only flows MUST state when persistence, submission, authentication, payment, notifications, or backend processing are simulated or unavailable.

# Generated Media Boundary
<!-- id: truth-boundaries.generated-media -->

Generated imagery may establish mood, context, or concept but MUST NOT be presented as verified completed work, a real customer, a factual property, a real employee, or documentary evidence unless it actually is.

# Recommendation Boundary
<!-- id: truth-boundaries.recommendation-boundary -->

Recommendations MUST remain distinguishable from evidence. In high-risk or decision documents, show the evidence/assumption chain supporting the recommendation and identify unresolved facts that could change it.

# Regulated & High-Risk Escalation
<!-- id: truth-boundaries.regulated-escalation -->

For medical, legal, financial, safety, government, insurance, security, or other materially regulated contexts, unknown credentials, eligibility, outcomes, rates, guarantees, authority, coverage, security posture, or professional relationships MUST remain explicitly unknown rather than implied by polished presentation.

# Acceptance
<!-- id: truth-boundaries.acceptance -->

Truthfulness PASS requires both absence of fabricated claims and **visible status/provenance where ambiguity would be material**. An artifact that is technically non-fabricated but visually implies unavailable proof fails this standard.
