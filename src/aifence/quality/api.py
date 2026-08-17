# SPDX-License-Identifier: AGPL-3.0-or-later
"""Quality-tier HTTP surface: inspect quality controls and run the quality gate."""
from __future__ import annotations

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from .controls import load_controls, registry_summary
from .gate import QualityGate

router = APIRouter(prefix="/v1/quality", tags=["quality"])


class EvaluateRequest(BaseModel):
    artifact: str = Field(..., description="The AI-generated artifact to gate.")
    content_type: str = Field("text/plain", description="MIME type; enables markup-specific checks.")
    min_score: int = Field(70, ge=0, le=100, description="Minimum score to accept.")


class ControlSummary(BaseModel):
    id: str
    priority: str
    domain: str
    capability_id: str
    requirement: str


@router.get("/registry", summary="Quality control registry summary")
def registry() -> dict[str, object]:
    return registry_summary()


@router.get("/controls", response_model=list[ControlSummary], summary="List quality controls")
def controls(
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


@router.post("/evaluate", summary="Run the quality gate over an artifact")
def evaluate(request: EvaluateRequest) -> dict[str, object]:
    gate = QualityGate(min_score=request.min_score)
    decision = gate.evaluate(request.artifact, request.content_type)
    return decision.to_dict()
