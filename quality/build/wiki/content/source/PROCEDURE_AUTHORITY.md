<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: PROCEDURE_AUTHORITY
Module-Version: 2
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-09
-->

# Procedure Authority & Accuracy Standard
<!-- id: procedure-authority.root -->

Purpose: prevent a well-written generated procedure from being mistaken for company policy, professional authorization, regulatory instruction, or manufacturer-required procedure.

# Authority Classes
<!-- id: procedure-authority.classes -->

Every material procedure or section must resolve to one of these classes:

| Class | Meaning | May be presented as authoritative? |
|---|---|---|
| `GENERAL_GUIDANCE` | General operating best practice derived from non-authoritative context | No |
| `ORGANIZATION_DRAFT` | Tailored draft based on supplied organization facts but not approved evidence | No; label draft |
| `VERIFIED_ORGANIZATION_PROCEDURE` | Current organization procedure/policy supplied or retrieved with reliable provenance | Yes, within verified scope |
| `EXTERNAL_AUTHORITATIVE_REQUIREMENT` | Current applicable law/regulation/standard/manufacturer/contractual authority verified from an authoritative source | Yes, only within verified scope |
| `MIXED` | Different sections rely on different authority classes | Classify material sections individually |

If classification cannot be supported, default to `GENERAL_GUIDANCE` or `ORGANIZATION_DRAFT`, not a stronger class.

# Provenance Record
<!-- id: procedure-authority.provenance -->

For authoritative procedure content, record as applicable:

```text
Source title / identifier
Issuing authority / owner
Source type
Jurisdiction / organization / facility / product scope
Version / revision
Effective date
Retrieval or supplied date
Applicable section(s)
Interpretation notes
Conflicts / superseded sources
Verification state
```

A URL, document title, or citation by itself does not prove applicability.

# Accuracy Boundary
<!-- id: procedure-authority.accuracy-boundary -->

Separate three concepts:

```text
SOURCE REQUIREMENT — what the authoritative source actually requires
ORGANIZATION CONTROL — how the organization implements the requirement
AIFENCE RECOMMENDATION — a proposed operating design or best practice
```

Never merge them into one unlabeled procedure step.

# Currentness Trigger
<!-- id: procedure-authority.currentness -->

Re-verify authority when:

- the relevant law/regulation/standard/policy may have changed;
- jurisdiction, product, facility, customer contract, system, or business scope changes;
- an old procedure is being reused after a material time gap;
- source version/effective date is unknown;
- an incident reveals the procedure may be inaccurate;
- an approval owner or competent authority requests review.

# High-Consequence Guard
<!-- id: procedure-authority.high-consequence -->

For regulated, licensed, clinical, electrical, hazardous-energy, life-safety, aviation, financial-control, legal, security-sensitive, or similarly consequential work:

- generic AIFENCE steps may frame workflow, evidence, decisions, and escalation;
- they MUST NOT replace required professional judgment, licensed scope, official technical procedure, safety manual, manufacturer instructions, or legally binding controls;
- exact hazardous/technical execution steps require appropriate authoritative input;
- if the authoritative source is missing, produce a controlled draft with explicit verification tasks rather than inventing instructions.

# Approval State
<!-- id: procedure-authority.approval-state -->

Use explicit lifecycle states:

```text
DRAFT
IN REVIEW
APPROVED
EFFECTIVE
SUSPENDED
SUPERSEDED
ARCHIVED
```

Generated content begins as `DRAFT` unless approval evidence is supplied or retrieved. “Production-ready writing” is not the same as “organization-approved procedure.”

# Conflict Rule
<!-- id: procedure-authority.conflict-rule -->

When sources conflict:

1. do not silently choose the convenient source;
2. identify the conflict and affected steps;
3. apply higher-precedence legal/contractual/organization governance only when actually established;
4. escalate unresolved authority conflicts to the responsible owner;
5. keep the affected procedure `UNVERIFIED` or blocked until resolved.

# Machine-Enforced Authority Record
<!-- id: procedure-authority.machine-enforcement -->

`schemas/procedure_authority.schema.json` and `tools/validate_operational_procedure.py` are the machine representation of this standard. Strong authority classes (`VERIFIED_ORGANIZATION_PROCEDURE`, `EXTERNAL_AUTHORITATIVE_REQUIREMENT`) require `verification_state: VERIFIED`, a stable authority record ID, source title, issuer/owner, applicability scope, retrieval/supplied date, applicability basis, and currentness evidence through version, effective date, or an explicit currentness record.

For `MIXED` procedures, top-level classification alone is insufficient. Every material step/section must appear in the procedure `authority_map`. Any map entry using a strong authority class must reference one or more verified `authority_source_ids`. General-guidance and organization-draft sections must remain visibly weaker rather than inheriting authority from nearby verified sections.

Lifecycle claims are also machine-gated. Generated procedures default conceptually to `DRAFT`; `APPROVED` or `EFFECTIVE` requires an approver and approval evidence, and `EFFECTIVE` additionally requires an effective date.
