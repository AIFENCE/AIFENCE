<!-- GENERATED from source/OPERATIONAL_PROCEDURE_COMPILER.md, source/PROCEDURE_AUTHORITY.md, source/DECISION_RIGHTS.md, source/KPI_GOVERNANCE.md by tooling/build.mjs. Do not hand edit. -->

# Operations reference

# Compiler Entry Conditions
<!-- id: operational-procedure-compiler.entry -->

Use this compiler when the user asks for or materially depends on:

- operating procedures, SOPs, work instructions, runbooks, checklists, playbooks, job execution standards, or shift procedures;
- role responsibilities that imply decisions, approvals, records, KPIs, or handoffs;
- an operational workflow whose real-world execution matters;
- regulated, licensed, safety-critical, financial-control, privacy/security, quality, or customer-impacting operations;
- transformation of a generic `operations/*.md` role baseline into an actual process.

Do not invoke it merely to list job titles when no procedural detail is requested.

# Real-World Accuracy Gate
<!-- id: operational-procedure-compiler.accuracy-gate -->

A procedure MUST NOT be represented as operationally authoritative merely because it is detailed.

Before calling a procedure **verified**, **approved**, **regulatory**, **manufacturer-required**, **licensed**, **certified**, or equivalent:

- identify the exact source and authority;
- confirm scope/jurisdiction/product/facility applicability when material;
- confirm version/effective date or currentness when material;
- distinguish source requirement from AIFENCE interpretation;
- identify unresolved conflicts or missing evidence;
- preserve mandatory wording only to the extent copyright/source-use rules permit;
- mark the result `UNVERIFIED` if authoritative evidence is unavailable.

When current authoritative research tools exist and accuracy depends on current law, regulation, standard, policy, or manufacturer instruction, retrieve the current authoritative source instead of relying on memory.

# Compilation Acceptance
<!-- id: operational-procedure-compiler.acceptance -->

A compiled operational procedure passes only when:

- the correct role/task/context is resolved;
- authority status is explicit and truthful;
- P0/P1 steps are executable rather than generic;
- consequential decisions have criteria and owners;
- approvals and prohibited actions are explicit;
- relevant exceptions, stop conditions, recovery, and handoffs are present;
- definition of done is observable;
- evidence requirements are mapped to material steps;
- KPI definitions do not invent targets or formulas;
- current authoritative claims have adequate provenance;
- no source uncertainty is disguised as certainty.

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

# Mandatory Rights Vocabulary
<!-- id: decision-rights.vocabulary -->

For consequential work, classify actions and decisions using:

```text
MUST — required when trigger/condition applies
MAY — permitted within stated scope
MUST NOT — prohibited
APPROVAL REQUIRED — performer may prepare/recommend but not authorize
STOP & ESCALATE — work cannot safely/legitimately continue
CONSULT — named expertise must be involved before decision
INFORM — stakeholder receives required communication after/before event
```

Avoid vague phrases like “use judgment” unless the role truly has delegated discretion and the decision criteria/boundary are known.

# No Invented Targets
<!-- id: kpi-governance.no-invented-targets -->

Do not fabricate targets, SLAs, tolerances, benchmarks, staffing ratios, utilization targets, defect limits, financial thresholds, or regulatory limits.

When a useful target is unknown:

- label it `ORGANIZATION-SPECIFIC — NOT SUPPLIED`;
- optionally provide a method for establishing the target;
- do not turn an industry norm, model guess, or arbitrary percentage into policy.

# Formula Integrity
<!-- id: kpi-governance.formula-integrity -->

A KPI name without a calculation definition is incomplete when reproducibility matters.

Example pattern:

```text
First-Time Fix Rate
= eligible service jobs resolved without a qualifying repeat visit
  / all eligible completed service jobs
  × 100
```

The procedure must still define “eligible,” “resolved,” the repeat window, exclusions, and data source before the metric is considered production-ready.