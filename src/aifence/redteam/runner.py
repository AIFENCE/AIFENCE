# SPDX-License-Identifier: AGPL-3.0-or-later
"""Drives traces through the real quality and guard stack, turn by turn.

The runner deliberately calls the same functions the fence flow calls —
``QualityGate.evaluate``, ``run_detectors``, ``calculate_risk``,
``PolicyEngine.evaluate`` — rather than a simulation of them. A harness that
measures a reimplementation measures nothing.

Turns are executed in order against a per-trace observation window, so a
detector that reasons over an agent's history sees that history exactly as it
would in production.
"""
from __future__ import annotations

from typing import Any, cast

from ..behavior import ObservationWindow, behavioral_findings, untrusted_source
from .corpus import Trace, Turn
from .report import EvaluationReport, TraceResult, TurnResult

#: A hard refusal. On benign work this is a true false positive.
HARD_BLOCK_OUTCOMES = frozenset({"deny", "quarantine_and_terminate"})
#: The action is stopped pending a human or a transform. On an attack this still
#: counts as caught; on benign work it is friction rather than a refusal, so the
#: two are reported separately instead of being averaged into one number.
HOLD_OUTCOMES = frozenset({"require_approval", "redact_or_transform"})
INTERVENING_OUTCOMES = HARD_BLOCK_OUTCOMES | HOLD_OUTCOMES


#: Tools an agent is registered for when a trace does not name its own set.
#: Broad on purpose: the corpus is measuring behavioural detection, not whether
#: an allowlist was configured, and a narrow default would let the tool-allowlist
#: rule take credit for every attack.
DEFAULT_ALLOWED_TOOLS = (
    "orders.read", "customers.export", "warehouse.query", "warehouse.export",
    "http.get", "http.post", "docs.read", "docs.delete", "wiki.write",
    "tickets.read", "billing.read", "crm.read", "storage.read", "storage.delete",
    "catalog.read", "deploys.read", "jobs.read",
)
DEFAULT_ALLOWED_DATA_CLASSES = ("personal_data", "financial", "operational")


def _registered_agent(trace: Trace) -> Any:
    """The agent as the registry would hold it.

    Without this the ``authorization.agent_unregistered`` detector fires on every
    turn of every trace, which scores 100% detection and 100% false positives —
    a perfectly useless measurement.
    """
    from ..guard.models import Agent

    return Agent(
        id=f"agt_{trace.id[:24]}",
        tenant_id="ten_redteam",
        external_id=trace.id,
        name=trace.id,
        version="1.0.0",
        workload_identity=f"spiffe://aifence/agents/{trace.id[:24]}",
        model="provider/model",
        instruction_hash="a" * 64,
        allowed_tools=list(trace.allowed_tools or DEFAULT_ALLOWED_TOOLS),
        allowed_data_classes=list(DEFAULT_ALLOWED_DATA_CLASSES),
        status="active",
    )


def _decision_request(trace: Trace, turn: Turn, index: int) -> Any:
    from ..guard.schemas import DecisionRequest

    return DecisionRequest.model_validate(
        {
            "trace_id": f"trc_{trace.id.replace('-', '_')[:40]}_{index:02d}".ljust(8, "0"),
            "principal": {"type": "service", "id": "agent-operator", "authorization_context": []},
            "agent": {
                "id": f"agt_{trace.id[:24]}",
                "instance_id": "instance-1",
                "version": "1.0.0",
                "workload_identity": f"spiffe://aifence/agents/{trace.id[:24]}",
                "model": "provider/model",
                "instruction_hash": "a" * 64,
            },
            "objective": {
                "declared_goal": trace.description[:200] or "task",
                "approved_scope": list(trace.approved_scope),
                "delegation_depth": 0,
            },
            "action": {
                "type": "tool.call",
                "tool": turn.tool,
                "operation": turn.operation,
                "target": turn.target,
                "arguments": {},
                "destructive": turn.destructive,
                "reversible": not turn.destructive,
                "external_effect": turn.external_effect,
            },
            "security_context": {
                "data_classes": list(turn.data_classes),
                "environment": turn.environment,
                "content": turn.content or turn.artifact,
                "network_destination": turn.network_destination,
            },
        }
    )


def evaluate_trace(
    trace: Trace, *, behavioral: bool = False, policy: str | None = None
) -> TraceResult:
    """Run one trace and record what the fence did at each turn.

    ``policy`` selects an alternative policy document, so the operational cost of
    a profile can be measured against the same corpus.
    """
    from ..guard.detectors import calculate_risk, run_detectors
    from ..guard.policy import PolicyEngine, load_baseline_policy
    from ..quality.gate import QualityGate

    engine = PolicyEngine(load_baseline_policy(policy) if policy else load_baseline_policy())
    gate = QualityGate()
    agent = _registered_agent(trace)
    window = ObservationWindow()
    turns: list[TurnResult] = []

    for index, turn in enumerate(trace.turns, start=1):
        quality = gate.evaluate(
            turn.artifact, turn.content_type, sources=list(turn.sources) or None
        ).to_dict()

        request = _decision_request(trace, turn, index)
        findings = list(run_detectors(request, agent))

        observed: set[str] = set()
        for finding in findings:
            classes = finding.attributes.get("data_classes")
            if isinstance(classes, list):
                observed |= {str(c) for c in classes}

        if behavioral:
            findings.extend(
                behavioral_findings(operation=turn.operation, quality=quality, window=window)
            )

        risk = calculate_risk(request, findings)
        result = engine.evaluate(request.model_dump(), findings, risk)

        quality_blocked = not quality["passed"]
        guard_blocked = result.outcome in HARD_BLOCK_OUTCOMES
        guard_held = result.outcome in HOLD_OUTCOMES
        turns.append(
            TurnResult(
                index=index,
                quality_score=int(cast(int, quality["score"])),
                quality_blocked=quality_blocked,
                guard_outcome=str(result.outcome),
                guard_blocked=guard_blocked,
                guard_held=guard_held,
                risk=int(risk),
                categories=sorted({f.category for f in findings}),
                matched_rule=str(result.matched_rule),
                note=turn.note,
            )
        )
        window.record(
            operation=turn.operation,
            target=turn.target,
            destination=turn.network_destination,
            quality=quality,
            observed=observed,
            ingested_untrusted=untrusted_source(
                turn.operation, turn.target, bool(turn.content or turn.artifact)
            ),
        )

    return TraceResult(trace=trace, turns=tuple(turns))


def evaluate_corpus(
    traces: list[Trace], *, behavioral: bool = False, policy: str | None = None
) -> EvaluationReport:
    """Run every trace and aggregate the detection and false-positive rates."""
    return EvaluationReport(
        results=tuple(evaluate_trace(trace, behavioral=behavioral, policy=policy) for trace in traces),
        behavioral=behavioral,
    )
