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
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/v1/fence", tags=["fence"])

#: Guard outcomes that permit the flow to continue to the bus handoff.
_GUARD_PROCEED = {"allow", "allow_with_limits"}


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


@functools.lru_cache(maxsize=1)
def _policy_engine() -> Any:
    from .guard.policy import PolicyEngine, load_baseline_policy

    return PolicyEngine(load_baseline_policy())


def _run_quality(req: FenceRequest) -> dict[str, Any]:
    from .quality.gate import QualityGate

    decision = QualityGate(min_score=req.min_quality_score).evaluate(req.artifact, req.content_type)
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
    }


@router.post("/submit", summary="Run an artifact through the full quality→guard→bus fence")
def submit(req: FenceRequest, request: Request) -> dict[str, Any]:
    request_id = getattr(request.state, "request_id", None)
    stages: dict[str, Any] = {}

    quality = _run_quality(req)
    stages["quality"] = quality
    if not quality["passed"]:
        return {
            "request_id": request_id,
            "allowed": False,
            "final_outcome": "blocked_by_quality",
            "stages": stages,
        }

    guard = _run_guard(req)
    stages["guard"] = guard
    if guard["outcome"] not in _GUARD_PROCEED:
        return {
            "request_id": request_id,
            "allowed": False,
            "final_outcome": "blocked_by_guard",
            "stages": stages,
        }

    stages["bus"] = _run_bus(req, request)
    return {
        "request_id": request_id,
        "allowed": True,
        "final_outcome": "handed_off",
        "stages": stages,
    }
