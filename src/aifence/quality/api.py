# SPDX-License-Identifier: AGPL-3.0-or-later
"""Quality-tier HTTP surface: inspect quality controls and run the quality gate."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, ConfigDict, Field

from ..security import IdentityDep
from .controls import load_controls, registry_summary
from .deep import deep_runtime_status, plan_deep_evaluation
from .gate import ADMISSION_PROFILE, QualityGate

# Authenticated at the router level: the quality tier is part of the fence, not
# a public surface, so every endpoint requires the same identity guard enforces.
router = APIRouter(prefix="/v1/quality", tags=["quality"])


class EvaluateRequest(BaseModel):
    # "schema" shadows a BaseModel attribute, so it is aliased on the wire.
    model_config = ConfigDict(populate_by_name=True)

    artifact: str = Field(..., description="The AI-generated artifact to gate.")
    content_type: str = Field("text/plain", description="MIME type; enables markup- and JSON-specific checks.")
    min_score: int = Field(70, ge=0, le=100, description="Minimum score to accept.")
    schema_: dict[str, Any] | None = Field(
        default=None,
        alias="schema",
        description="Optional JSON Schema the artifact must conform to.",
    )
    sources: list[str] | None = Field(
        default=None,
        description="Optional source material; numeric claims absent from it are reported as unsupported.",
    )


class DeepPlanRequest(BaseModel):
    intent: str = Field(min_length=1, max_length=20000)
    hints: dict[str, Any] = Field(default_factory=dict)


class ControlSummary(BaseModel):
    id: str
    priority: str
    domain: str
    capability_id: str
    requirement: str


@router.get("/registry", summary="Quality control registry summary")
def registry(identity: IdentityDep) -> dict[str, object]:
    return registry_summary()


@router.get("/controls", response_model=list[ControlSummary], summary="List quality controls")
def controls(
    identity: IdentityDep,
    priority: str | None = Query(None, description="Filter by priority, e.g. P0."),
    limit: int = Query(100, ge=1, le=1000),
) -> list[ControlSummary]:
    items = load_controls()
    if priority:
        items = tuple(c for c in items if c.priority.upper() == priority.upper())
    return [
        ControlSummary(
            id=c.id,
            priority=c.priority,
            domain=c.domain,
            capability_id=c.capability_id,
            requirement=c.requirement,
        )
        for c in items[:limit]
    ]




@router.get("/modes", summary="Describe admission and deep Quality modes")
def modes(identity: IdentityDep) -> dict[str, object]:
    return {
        "admission": {
            "mode": "admission",
            "profile": ADMISSION_PROFILE,
            "available": True,
            "semantics": "Bounded deterministic checks executed synchronously inside the fence.",
        },
        "deep": deep_runtime_status(),
    }


@router.post("/deep/plan", summary="Plan a family-native deep Quality 2.0 evaluation")
def deep_plan(request: DeepPlanRequest, identity: IdentityDep) -> dict[str, Any]:
    return plan_deep_evaluation(request.intent, request.hints)


@router.post("/evaluate", summary="Run the quality gate over an artifact")
def evaluate(request: EvaluateRequest, identity: IdentityDep) -> dict[str, object]:
    gate = QualityGate(min_score=request.min_score)
    decision = gate.evaluate(
        request.artifact,
        request.content_type,
        schema=request.schema_,
        sources=request.sources,
    )
    return decision.to_dict()
