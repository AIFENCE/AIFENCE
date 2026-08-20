# SPDX-License-Identifier: AGPL-3.0-or-later
"""The AIFENCE fence flow — the three tiers as one logical pipeline.

``POST /v1/fence/submit`` runs a single request through the whole fence in
order, in-process:

1. **Quality** — the quality-control gate scores the artifact.
2. **Guard**   — the enforcement policy engine decides the action's outcome.
3. **Bus**     — the semantic runtime compiles the vetted payload for handoff.

Each stage can stop the flow (quality reject, guard deny/approval), and the
response is one unified receipt sharing the request id. This is the merge made
concrete: not three services beside each other, but one governed flow.
"""
from __future__ import annotations

import functools
import hashlib
from dataclasses import dataclass
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from .core.config import CoreSettings
from .core.metrics import FENCE_OUTCOMES, FENCE_STAGE_CALLS, FENCE_STAGE_LATENCY
from .resilience import BreakerPolicy, CircuitBreaker, TierOutcome
from .security import IdentityDep

router = APIRouter(prefix="/v1/fence", tags=["fence"])

#: Guard outcomes that permit the flow to continue to the bus handoff.
_GUARD_PROCEED = {"allow", "allow_with_limits"}


@dataclass
class FlowBreakers:
    """One circuit breaker per tier, built from application settings."""

    quality: CircuitBreaker
    guard: CircuitBreaker
    bus: CircuitBreaker

    @classmethod
    def from_settings(cls, settings: CoreSettings) -> FlowBreakers:
        fail_open = set(settings.flow_fail_open_tiers)

        def policy(tier: str, timeout: float) -> BreakerPolicy:
            return BreakerPolicy(
                timeout_seconds=timeout,
                failure_threshold=settings.flow_failure_threshold,
                recovery_seconds=settings.flow_recovery_seconds,
                # Guard is never openable; settings validation rejects it too.
                paradigm="fail_open" if tier in fail_open and tier != "guard" else "fail_closed",
            )

        return cls(
            quality=CircuitBreaker("quality", policy("quality", settings.flow_quality_timeout_seconds)),
            guard=CircuitBreaker("guard", policy("guard", settings.flow_guard_timeout_seconds)),
            bus=CircuitBreaker("bus", policy("bus", settings.flow_bus_timeout_seconds)),
        )

    def close(self) -> None:
        for breaker in (self.quality, self.guard, self.bus):
            breaker.close()


class ActionModel(BaseModel):
    type: str = "tool_call"
    operation: str = "read"
    tool: str | None = None
    target: str | None = None
    destructive: bool = False


class SecurityModel(BaseModel):
    environment: str = "production"
    network_destination: str | None = None


class PrincipalModel(BaseModel):
    type: str = "service"
    id: str = "anonymous"


class FenceRequest(BaseModel):
    artifact: str = Field(..., description="AI-generated artifact/work to move through the fence.")
    content_type: str = "text/plain"
    receiver: str = Field("downstream-agent", description="Bus receiver for the semantic handoff.")
    action: ActionModel = Field(default_factory=ActionModel)
    security: SecurityModel = Field(default_factory=SecurityModel)
    principal: PrincipalModel = Field(default_factory=PrincipalModel)
    risk_score: int = Field(10, ge=0, le=100)
    min_quality_score: int = Field(70, ge=0, le=100)
    sources: list[str] | None = Field(
        default=None,
        description="Optional source material; numeric claims absent from it are flagged as unsupported.",
    )


@functools.lru_cache(maxsize=1)
def _policy_engine() -> Any:
    from .guard.policy import PolicyEngine, load_baseline_policy

    return PolicyEngine(load_baseline_policy())


def _run_quality(req: FenceRequest) -> dict[str, Any]:
    from .quality.gate import QualityGate

    decision = QualityGate(min_score=req.min_quality_score).evaluate(
        req.artifact, req.content_type, sources=req.sources
    )
    return {"tier": "quality", **decision.to_dict()}


def _run_guard(
    req: FenceRequest, quality: dict[str, Any] | None, window: Any, identity_key: str
) -> dict[str, Any]:
    """Evaluate the action, including signals drawn from the agent's history.

    The cross-tier findings are appended to whatever the per-request detectors
    produced, so the policy engine treats a trajectory signal exactly like any
    other finding.
    """
    from .behavior import behavioral_findings

    engine = _policy_engine()
    input_document = {
        "action": {
            "type": req.action.type,
            "operation": req.action.operation,
            "tool": req.action.tool,
            "target": req.action.target,
            "destructive": req.action.destructive,
        },
        "security_context": {
            "environment": req.security.environment,
            "network_destination": req.security.network_destination,
        },
        "principal": {"type": req.principal.type, "id": req.principal.id},
    }
    findings = (
        behavioral_findings(operation=req.action.operation, quality=quality, window=window)
        if quality is not None
        else []
    )
    result = engine.evaluate(input_document, findings, req.risk_score)
    return {
        "tier": "guard",
        "outcome": result.outcome,
        "reasons": result.reasons,
        "reason_codes": result.reason_codes,
        "constraints": result.constraints,
        "policy_version": result.policy_version,
        "matched_rule": result.matched_rule,
        "signals": sorted({f.category for f in findings}),
        "explain": {
            "principal": {"type": req.principal.type, "id": req.principal.id},
            "action": {
                "type": req.action.type,
                "operation": req.action.operation,
                "tool": req.action.tool,
                "target": req.action.target,
                "destructive": req.action.destructive,
            },
            "security_context": {
                "environment": req.security.environment,
                "network_destination": req.security.network_destination,
            },
            "risk_score": req.risk_score,
            "policy": {
                "version": result.policy_version,
                "matched_rule": result.matched_rule,
            },
        },
    }


def _run_bus(req: FenceRequest, request: Request, tenant_id: str) -> dict[str, Any]:
    """Durably enqueue the vetted artifact as a real, claimable handoff.

    Uses the composed application's shared session factory so the handoff is
    persisted to the one merged database and a receiver can later poll/claim it —
    a genuine cross-agent delivery, not just an in-memory computation.
    """
    from .bus.bus import SemanticBus
    from .bus.compiler import compile_content
    from .bus.config import get_settings as bus_settings
    from .bus.transport import HandoffEvent, publish_safely

    session_factory = request.app.state.session_factory
    units = compile_content(req.artifact)
    raw_bytes = len(req.artifact.encode("utf-8"))
    digest = hashlib.sha256(req.artifact.encode("utf-8")).hexdigest()
    workspace = f"tenant:{tenant_id}"
    with session_factory() as db:
        message = SemanticBus(db, bus_settings()).handoff(
            receiver=req.receiver,
            content=req.artifact,
            sender="aifence-fence",
            workspace=workspace,
            correlation_id=getattr(request.state, "request_id", None),
        )
        db.commit()
        message_id = message.id
        wire_bytes = message.wire_bytes
        strategy = message.strategy
        workspace = message.workspace
    # Fan out only after the durable commit, so a broker outage can never
    # invent a delivery that was not persisted.
    fanout = publish_safely(
        request.app.state.bus_transport,
        HandoffEvent(
            message_id=message_id,
            receiver=req.receiver,
            sender="aifence-fence",
            workspace=workspace,
            correlation_id=getattr(request.state, "request_id", None),
            wire_bytes=wire_bytes,
            strategy=strategy,
        ),
    )
    return {
        "tier": "bus",
        "receiver": req.receiver,
        "workspace": workspace,
        "message_id": message_id,
        "delivered": True,
        "strategy": strategy,
        "semantic_units": len(units),
        "raw_bytes": raw_bytes,
        "wire_bytes": wire_bytes,
        "content_ref": f"aifence:sha256:{digest}",
        "fanout": fanout,
    }


def _degraded_stage(tier: str, outcome: TierOutcome[Any]) -> dict[str, Any]:
    """Record a tier that was skipped or failed while the flow continued."""
    return {
        "tier": tier,
        "degraded": True,
        "reason": outcome.reason,
        "breaker_state": outcome.state,
        "elapsed_ms": round(outcome.elapsed_ms, 3),
        "detail": f"{tier} tier failed open by policy",
    }


@router.post("/submit", summary="Run an artifact through the full quality→guard→bus fence")
def submit(req: FenceRequest, request: Request, identity: IdentityDep) -> dict[str, Any]:
    # Submitting to the fence performs a policy decision and a durable handoff,
    # so it requires the same credential guard requires for a direct decision.
    identity.require("decisions:write")
    request_id = getattr(request.state, "request_id", None)
    breakers: FlowBreakers = request.app.state.flow_breakers
    stages: dict[str, Any] = {}
    degraded: list[str] = []

    def observe_tier(tier: str, outcome: TierOutcome[Any]) -> None:
        result = "ok" if outcome.ok else (outcome.reason or "degraded")
        FENCE_STAGE_CALLS.labels(tier, result, outcome.state).inc()
        FENCE_STAGE_LATENCY.labels(tier).observe(outcome.elapsed_ms / 1000.0)

    def receipt(final_outcome: str, *, allowed: bool) -> dict[str, Any]:
        """Persist a tamper-evident fence completion event and return its receipt."""
        from .core.db import set_tenant_context
        from .guard.audit import append_event
        from .guard.ids import new_id

        FENCE_OUTCOMES.labels(final_outcome, str(allowed).lower()).inc()
        audit_payload = {
            "request_id": request_id,
            "allowed": allowed,
            "final_outcome": final_outcome,
            "degraded_tiers": list(degraded),
            "artifact_sha256": hashlib.sha256(req.artifact.encode("utf-8")).hexdigest(),
            "quality": {
                "mode": stages.get("quality", {}).get("mode"),
                "profile": stages.get("quality", {}).get("profile"),
                "score": stages.get("quality", {}).get("score"),
                "outcome": stages.get("quality", {}).get("outcome"),
            },
            "guard": {
                "outcome": stages.get("guard", {}).get("outcome"),
                "policy_version": stages.get("guard", {}).get("policy_version"),
                "matched_rule": stages.get("guard", {}).get("matched_rule"),
                "reason_codes": stages.get("guard", {}).get("reason_codes", []),
            },
            "bus": {
                "message_id": stages.get("bus", {}).get("message_id"),
                "receiver": stages.get("bus", {}).get("receiver"),
            },
        }
        guard_app = request.app.state.guard_app
        with request.app.state.session_factory() as session:
            set_tenant_context(session, identity.tenant_id)
            event = append_event(
                session,
                guard_app.state.signing_key,
                event_id=new_id("evt"),
                tenant_id=identity.tenant_id,
                trace_id=request_id or new_id("trc"),
                parent_event_id=None,
                event_type="fence.completed",
                payload=audit_payload,
            )
            session.commit()
            audit = {
                "event_id": event.id,
                "sequence": event.sequence,
                "event_hash": event.event_hash,
                "key_id": event.key_id,
            }
        return {
            "request_id": request_id,
            "tenant_id": identity.tenant_id,
            "allowed": allowed,
            "final_outcome": final_outcome,
            "degraded_tiers": degraded,
            "audit": audit,
            "stages": stages,
        }

    # Each tier runs under its own latency budget and breaker. A fail-closed tier
    # that cannot answer raises TierUnavailable, which surfaces as 503 rather
    # than letting the request through unchecked.
    quality_result = breakers.quality.call(lambda: _run_quality(req))
    observe_tier("quality", quality_result)
    if quality_result.ok and quality_result.value is not None:
        stages["quality"] = quality_result.value
        if not quality_result.value["passed"]:
            return receipt("blocked_by_quality", allowed=False)
    else:
        stages["quality"] = _degraded_stage("quality", quality_result)
        degraded.append("quality")

    # One window per agent identity: cross-tier signals are properties of a
    # trajectory, so they need the agent's recent turns, not just this request.
    agent_key = f"{identity.tenant_id}:{identity.bound_agent_id or identity.key_id}"
    window = request.app.state.agent_windows.get(agent_key)
    quality_result_value = quality_result.value if quality_result.ok else None

    guard_result = breakers.guard.call(
        lambda: _run_guard(req, quality_result_value, window, agent_key)
    )
    observe_tier("guard", guard_result)
    # Guard is always fail-closed, so reaching here means it answered.
    guard_stage = guard_result.value or {}
    stages["guard"] = guard_stage
    if guard_stage.get("outcome") not in _GUARD_PROCEED:
        return receipt("blocked_by_guard", allowed=False)

    # Record the turn only once it has been authorised, so a refused action does
    # not shape the window that judges the next one.
    from .behavior import untrusted_source

    window.record(
        operation=req.action.operation,
        target=req.action.target,
        destination=req.security.network_destination,
        quality=quality_result_value or {},
        observed=set(),
        ingested_untrusted=untrusted_source(
            req.action.operation, req.action.target, bool(req.artifact)
        ),
    )

    bus_result = breakers.bus.call(lambda: _run_bus(req, request, identity.tenant_id))
    observe_tier("bus", bus_result)
    if bus_result.ok and bus_result.value is not None:
        stages["bus"] = bus_result.value
        return receipt("handed_off", allowed=True)
    stages["bus"] = _degraded_stage("bus", bus_result)
    degraded.append("bus")
    # The action was authorized but not delivered; say so rather than implying
    # a handoff that never happened.
    return receipt("authorized_not_delivered", allowed=True)
