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


def _run_guard(req: FenceRequest) -> dict[str, Any]:
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
    result = engine.evaluate(input_document, [], req.risk_score)
    return {
        "tier": "guard",
        "outcome": result.outcome,
        "reasons": result.reasons,
        "constraints": result.constraints,
        "policy_version": result.policy_version,
        "matched_rule": result.matched_rule,
    }


def _run_bus(req: FenceRequest, request: Request) -> dict[str, Any]:
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
    with session_factory() as db:
        message = SemanticBus(db, bus_settings()).handoff(
            receiver=req.receiver,
            content=req.artifact,
            sender="aifence-fence",
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

    def receipt(final_outcome: str, *, allowed: bool) -> dict[str, Any]:
        return {
            "request_id": request_id,
            "tenant_id": identity.tenant_id,
            "allowed": allowed,
            "final_outcome": final_outcome,
            "degraded_tiers": degraded,
            "stages": stages,
        }

    # Each tier runs under its own latency budget and breaker. A fail-closed tier
    # that cannot answer raises TierUnavailable, which surfaces as 503 rather
    # than letting the request through unchecked.
    quality_result = breakers.quality.call(lambda: _run_quality(req))
    if quality_result.ok and quality_result.value is not None:
        stages["quality"] = quality_result.value
        if not quality_result.value["passed"]:
            return receipt("blocked_by_quality", allowed=False)
    else:
        stages["quality"] = _degraded_stage("quality", quality_result)
        degraded.append("quality")

    guard_result = breakers.guard.call(lambda: _run_guard(req))
    # Guard is always fail-closed, so reaching here means it answered.
    guard_stage = guard_result.value or {}
    stages["guard"] = guard_stage
    if guard_stage.get("outcome") not in _GUARD_PROCEED:
        return receipt("blocked_by_guard", allowed=False)

    bus_result = breakers.bus.call(lambda: _run_bus(req, request))
    if bus_result.ok and bus_result.value is not None:
        stages["bus"] = bus_result.value
        return receipt("handed_off", allowed=True)
    stages["bus"] = _degraded_stage("bus", bus_result)
    degraded.append("bus")
    # The action was authorized but not delivered; say so rather than implying
    # a handoff that never happened.
    return receipt("authorized_not_delivered", allowed=True)
