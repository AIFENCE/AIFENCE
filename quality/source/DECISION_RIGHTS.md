<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: DECISION_RIGHTS
Module-Version: 2
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-09
-->

# Operational Decision Rights Standard
<!-- id: decision-rights.root -->

Purpose: make operational authority explicit enough that a procedure tells people not only **what to do**, but what they are allowed, required, prohibited, or required to escalate.

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

# Decision Rights Record
<!-- id: decision-rights.record -->

A material decision record should contain:

```text
Decision / action
Trigger / threshold
Performer
Decision owner
MUST / MAY / MUST NOT status
Approval owner and limit
Required evidence
Consulted role(s)
Informed role(s)
Escalation path
Time constraint / SLA if supplied
Segregation-of-duties rule if applicable
Fallback when owner unavailable
```

# Authority Boundaries
<!-- id: decision-rights.boundaries -->

Never infer:

- spending or pricing authority;
- hiring/firing authority;
- legal acceptance authority;
- clinical authority;
- financial posting/approval authority;
- production deployment authority;
- security incident authority;
- customer compensation/refund limits;
- warranty commitments;
- access rights or administrative privileges;
- licensure/certification scope.

If an exact threshold/limit is unknown, use a named placeholder or escalation rule rather than fabricating a number.

# Segregation of Duties
<!-- id: decision-rights.sod -->

Where fraud, safety, financial, security, privacy, compliance, or quality risk justifies separation, identify incompatible actions such as:

```text
request ↔ approve
create vendor ↔ approve payment
prepare entry ↔ approve/post entry
develop change ↔ independently approve high-risk change
perform inspection ↔ independently release critical output
initiate access ↔ approve privileged access
```

Do not require segregation when it is not justified by the actual risk/context; small organizations may use compensating review controls when appropriate and verified.

# Stop-Work / Stop-Processing Standard
<!-- id: decision-rights.stop-work -->

Define stop conditions for material uncertainty involving safety, legality, security, privacy, data integrity, unauthorized scope, missing required approval, failed verification, or unavailable critical evidence.

A stop condition must state:

- who stops the work;
- what is preserved/contained;
- who is notified;
- what evidence is recorded;
- what condition permits restart;
- who authorizes restart when approval is required.

# Delegation and Temporary Coverage
<!-- id: decision-rights.delegation -->

Delegation must preserve competence, conflict-of-interest, approval-limit, and segregation requirements. Temporary coverage does not automatically inherit all authority of the absent role.

# Machine-Enforced Conditional Requirements
<!-- id: decision-rights.machine-enforcement -->

Decision-right records are closed-schema objects in `schemas/decision_rights.schema.json`. `APPROVAL_REQUIRED` must identify the approval owner and either a verified approval limit with provenance or `approval_limit_state: ORGANIZATION_SPECIFIC_NOT_SUPPLIED`. `STOP_AND_ESCALATE` must identify containment, notification targets, escalation path, restart condition, and restart authorization state.

A numeric or monetary approval limit is invalid without explicit provenance. Unknown authority remains unknown; escalation is preferable to fabricated precision.
