<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: OPERATIONAL_EVIDENCE
Module-Version: 2
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-09
-->

# Operational Evidence, Records & Definition-of-Done Standard
<!-- id: operational-evidence.root -->

Purpose: connect procedure execution to observable completion, auditability, recovery, and handoff without generating unnecessary bureaucracy.

# Evidence Classes
<!-- id: operational-evidence.classes -->

Use the minimum evidence justified by consequence and traceability needs:

```text
Execution evidence — proves the action occurred
Decision evidence — records consequential choice/approval and rationale when needed
Quality evidence — proves acceptance/check criteria were met
Exception evidence — records deviation, containment, escalation, or waiver
Handoff evidence — proves ownership/status transfer
Outcome evidence — shows the intended result or downstream acceptance
```

# Evidence Record
<!-- id: operational-evidence.record -->

For material evidence, define as applicable:

```text
Evidence ID / record type
Procedure / step / decision linked
Required content
System of record / repository
Responsible recorder
Timestamp / effective period
Approval / reviewer
Source data or attachment
Retention rule / owner when supplied or authoritative
Access / confidentiality classification when relevant
Correction / amendment rule
Downstream consumer
```

Do not invent retention periods, legal recordkeeping durations, or system names.

# Definition of Done
<!-- id: operational-evidence.definition-of-done -->

A procedure is not complete because its final action was attempted. Definition of Done should specify observable closure, such as:

```text
required actions completed
acceptance checks passed
required approvals captured
records updated
customer/user communication completed when required
exceptions resolved or formally handed off
downstream owner accepted handoff
system/equipment/process left in defined state
follow-up owner/date established for deferred items
```

# Exception & Recovery Ledger
<!-- id: operational-evidence.exception-ledger -->

Material exceptions should record:

```text
what deviated
when detected
impact / risk
containment
owner
approval / waiver if applicable
recovery action
root cause status when needed
follow-up due date
closure evidence
```

# Handoff Contract
<!-- id: operational-evidence.handoff -->

Every material handoff SHOULD state:

```text
work / issue
current state
business/user impact
actions completed
required evidence / records
open exception or risk
next required action
receiving owner
deadline / commitment if supplied
approval needed
definition of acceptance
```

A handoff is complete only when the receiving responsibility is explicit; “sent an email” is not automatically ownership transfer.

# Auditability Without Bureaucracy
<!-- id: operational-evidence.proportionality -->

Evidence rigor must be proportional to risk, reversibility, legal/contractual obligation, customer impact, financial impact, and cost of reconstruction. Do not add approval chains or records that provide no meaningful control value.

# Machine Evidence Integrity
<!-- id: operational-evidence.machine-integrity -->

Evidence records use stable `evidence_id` values and are referenced by material steps, decisions, exceptions, handoffs, and Definition-of-Done criteria. References must resolve to an evidence record in the same procedure package. If a retention rule is specified, `retention_provenance` is required; AIFENCE may not invent legal/contractual retention periods.
