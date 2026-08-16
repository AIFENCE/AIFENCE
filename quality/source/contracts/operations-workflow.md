<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: ARTIFACT_CONTRACT
Contract: Operations Workflow
Module-Version: 3
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-09
-->
# Operations Workflow Production Contract
<!-- id: contract.artifact.operations-workflow -->

## User Jobs
<!-- id: contract.artifact.operations-workflow.user-jobs -->
Operators should know what needs attention, who owns it, current status, required evidence, exceptions, handoff conditions, and allowed next actions.

## Workflow Contract
<!-- id: contract.artifact.operations-workflow.workflow -->
Resolve trigger, queue/prioritization, owners, states/transitions, required information/evidence, primary/contextual actions, approvals/handoffs, exceptions/escalations, destructive/reversible actions, completion conditions, audit/history, and supplied/sample metrics.

## Failure & Exception Contract
<!-- id: contract.artifact.operations-workflow.failure -->
Blocked, missing-evidence, permission, offline/unavailable, error, rejected, escalated, overdue, and partial states must be represented when applicable.

## Dense UI & Responsive Contract
<!-- id: contract.artifact.operations-workflow.responsive -->
Boards, queues, tables, timelines, detail panes, and mobile task views should change density and action placement intentionally while preserving ownership/status/evidence.

## Evidence
<!-- id: contract.artifact.operations-workflow.evidence -->
Exercise representative transitions, exception/recovery, ownership/handoff, mobile task completion, keyboard-critical paths, and truth of simulated integrations/data.


## Narrow-Screen Task Contract
<!-- id: contract.artifact.operations-workflow.narrow-screen-task -->
Use `RESPONSIVE_COMPOSITION.md` to preserve owner/status/evidence/next action and exception recovery at 320/390 px without toolbar or sticky-layer collisions.


## Operational Procedure Compiler Contract
<!-- id: contract.artifact.operations-workflow.procedure-compiler -->
For a real-world SOP/work instruction/runbook, resolve the exact role, task, trigger, context, and risk, then compile through `OPERATIONAL_PROCEDURE_COMPILER.md`. Generic profile cadence is baseline context, not a finished procedure. P0/P1 or high-consequence procedures should reach L5 auditable closed-loop depth where applicable.

## Authority & Decision Rights Contract
<!-- id: contract.artifact.operations-workflow.authority -->
Classify procedure authority with `PROCEDURE_AUTHORITY.md`. Make MUST/MAY/MUST NOT/APPROVAL REQUIRED/STOP & ESCALATE boundaries explicit through `DECISION_RIGHTS.md`. Do not invent approval thresholds, credentials, policy, regulatory requirements, or system permissions.

## Evidence, Completion & KPI Contract
<!-- id: contract.artifact.operations-workflow.operational-evidence -->
Use `OPERATIONAL_EVIDENCE.md` for material step/decision records, exception evidence, handoff acceptance, and observable definition of done. Use `KPI_GOVERNANCE.md` for reproducible metric definitions and target provenance; KPI names or invented targets do not satisfy production completeness.

## Acceptance Profile
<!-- id: contract.artifact.operations-workflow.acceptance -->
Use `quality-floors.profile.operations`. Completeness, feature depth, usability, implementation correctness, and state coverage are strict floors.
