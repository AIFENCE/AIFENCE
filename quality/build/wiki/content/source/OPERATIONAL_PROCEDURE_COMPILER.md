<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: OPERATIONAL_PROCEDURE_COMPILER
Module-Version: 2
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-09
-->

# Operational Procedure Compiler
<!-- id: operational-procedure-compiler.root -->

Purpose: convert AIFENCE's industry, operating-profile, role, task, authority, risk, and organization context into a **task-executable, controlled, evidence-bearing operating procedure** without fabricating company policy or external authority.

Existing `JOBS.md` role definitions and `operations/*.md` SOP sections are **baseline operating context**. They are not automatically an approved organization procedure, licensed work instruction, manufacturer procedure, regulatory instruction, or jurisdiction-specific mandate.

# Compiler Entry Conditions
<!-- id: operational-procedure-compiler.entry -->

Use this compiler when the user asks for or materially depends on:

- operating procedures, SOPs, work instructions, runbooks, checklists, playbooks, job execution standards, or shift procedures;
- role responsibilities that imply decisions, approvals, records, KPIs, or handoffs;
- an operational workflow whose real-world execution matters;
- regulated, licensed, safety-critical, financial-control, privacy/security, quality, or customer-impacting operations;
- transformation of a generic `operations/*.md` role baseline into an actual process.

Do not invoke it merely to list job titles when no procedural detail is requested.

# Context Resolution
<!-- id: operational-procedure-compiler.context -->

Before compiling steps, resolve only what is material:

```text
Canonical industry / subindustry
Business model and operating environment
Organization/site/team context
Role and qualification boundary
Procedure/task name
Business/user outcome
Trigger / event / cadence
Risk class and consequence of error
Systems / tools / equipment
Required inputs / records
Applicable organization policies supplied by the user
Applicable external authorities actually verified
Jurisdiction / facility / product / system scope when relevant
Dependencies / upstream and downstream owners
```

Unknown material facts remain `UNKNOWN` or become explicit placeholders. Do not fill them with plausible-sounding operational detail.

# Role Specification
<!-- id: operational-procedure-compiler.role-spec -->

When a role must be operationally defined, compile:

```text
Role ID / title
Purpose
Primary accountabilities
Scope boundary
Required competencies / credentials (only when supplied or verified)
Inputs received
Outputs produced
Systems / tools used
Decisions owned
Decisions recommended but not approved
Approval limits
MUST actions
MAY actions
MUST NOT actions
STOP & ESCALATE conditions
Consult / inform interfaces
KPI ownership
Required records
Cadence / coverage expectations
Handoff responsibilities
Explicit exclusions
```

A title alone does not create authority, certification, licensure, system access, or approval rights.

# Procedure Compilation Schema
<!-- id: operational-procedure-compiler.schema -->

Compile each material procedure with the following fields. Omit a field only when genuinely inapplicable; do not silently omit an unknown.

```text
Procedure ID
Procedure Name
Purpose / intended outcome
Authority Class
Authority / source references
Scope and exclusions
Responsible role
Approver / escalation owner
Trigger
Entry conditions / prerequisites
Required inputs
Tools / systems / equipment
Safety / security / quality prerequisites
Step sequence
Decision points
Verification / quality checkpoints
Required measurements or observations
Required records / evidence
Customer/user communication points
Approval points
Exception paths
STOP & ESCALATE conditions
Recovery / rollback / containment
Output
Handoff
Definition of Done
KPI / SLA links
Record retention / audit link when applicable
Review / reauthorization trigger
Open unknowns / assumptions
Validation plan
```

# Step Grammar
<!-- id: operational-procedure-compiler.step-grammar -->

A material step SHOULD answer:

1. **Actor** — who performs it.
2. **Action** — observable action, not vague intent.
3. **Input** — what is needed.
4. **Method/System** — where/how the action occurs when material.
5. **Decision/Check** — acceptance condition or branching logic.
6. **Evidence** — what record proves completion when evidence matters.
7. **Failure path** — what happens if the condition is not met.
8. **Boundary** — approval, authorization, safety, or scope limit when applicable.

Avoid weak steps such as “review the issue,” “ensure compliance,” “handle exceptions,” or “follow policy” when the actual decision/check/evidence can be specified from available facts.

# Depth Ladder
<!-- id: operational-procedure-compiler.depth-ladder -->

```text
L1 — Mentioned
Role/task exists by name only.

L2 — Structured
Purpose, cadence, and broad activity sequence exist.

L3 — Executable
Trigger, prerequisites, actor, ordered actions, decisions, outputs, and completion condition are explicit.

L4 — Controlled
L3 + authority boundaries, approvals, exceptions, stop-work/escalation, recovery, required records, and quality/risk checkpoints.

L5 — Auditable Closed Loop
L4 + provenance, definition of done, KPI/measurement ownership, evidence traceability, lifecycle/change control, and validation coverage.
```

For substantial production operations, P0/P1/high-consequence procedures target **L5**. Low-risk routine procedures may target L4 when audit/metric lifecycle is genuinely unnecessary.

# Decision-Point Standard
<!-- id: operational-procedure-compiler.decision-points -->

Every consequential branch must state:

```text
Condition / signal
Decision owner
Allowed choices
Decision criteria
Required evidence
Approval if required
Resulting next state / next step
Escalation when criteria cannot be resolved
```

Do not hide decisions inside prose such as “as appropriate” or “if needed” when the criteria can be made explicit.

# Procedure Composition
<!-- id: operational-procedure-compiler.composition -->

Use `PROCEDURE_AUTHORITY.md` before authoritative claims, `DECISION_RIGHTS.md` for actor boundaries, `OPERATIONAL_EVIDENCE.md` for evidence/definition-of-done, and `KPI_GOVERNANCE.md` for measurement.

Recommended compilation flow:

```text
Industry + business model
→ exact role/task context
→ authority classification
→ role/accountability specification
→ trigger / prerequisites / inputs
→ executable steps
→ decision rights + approval points
→ quality/safety/security checkpoints
→ exception / stop / recovery paths
→ evidence and records
→ output / handoff / definition of done
→ KPI definitions
→ validation and change-control state
```

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

# Canonical Machine Artifact
<!-- id: operational-procedure-compiler.canonical-machine-artifact -->

For machine-readable delivery, `schemas/operational_procedure.schema.json` is the canonical structural model and composes the authority, decision-rights, evidence, role-accountability, and KPI schemas. Unknowns are explicit fields, not omitted structure. The semantic validator then checks cross-object relationships that JSON Schema alone cannot safely prove: unique IDs, evidence/source reference resolution, MIXED authority coverage, strong-source verification, lifecycle evidence, KPI target provenance, and high-consequence closure.

Validation sequence:

```text
JSON Schema
→ cross-object semantic validation
→ authority/currentness validation
→ decision/evidence/KPI closure
→ executable Domain 31 regression fixtures
→ PASS / FAIL / UNVERIFIED semantics
```
