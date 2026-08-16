# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

from datetime import UTC
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from .api_helpers import concept_response
from .calibration import CalibrationStore
from .codebook import Codebook
from .config import get_settings
from .db import get_db
from .db_models import ReceiverKnowledge
from .knowledge import KnowledgeStore
from .latent import pack_latent, unpack_latent
from .patterns import PatternStore
from .protocol_spec import SAGE_PROTOCOL
from .schemas import (
    CalibrationRecordRequest,
    CalibrationResponse,
    Capabilities,
    CounterfactualPatternRequest,
    LatentPacket,
    LatentPackRequest,
    LatentUnpackRequest,
    NegotiateRequest,
    NegotiateResponse,
    PatternCandidateResponse,
    PatternObserveRequest,
    PatternResponse,
    PatternStatusRequest,
)
from .security import current_principal, enforce_agent_scope

router = APIRouter()

settings = get_settings()

@router.post("/patterns/observe", response_model=list[PatternResponse])
def observe_patterns(req: PatternObserveRequest, db: Session = Depends(get_db)) -> list[PatternResponse]:
    """Mine higher-order semantic patterns without sending a packet."""
    from .compiler import compile_content

    store = PatternStore(db, settings)
    codebook = req.codebook or settings.codebook
    promoted = store.observe_units(
        codebook,
        compile_content(req.content)[: settings.max_message_atoms],
        source_ids=req.source_ids,
        trust_score=req.source_trust,
        trust_scope=req.trust_scope,
    )
    db.commit()
    return [PatternResponse.model_validate(store.response(item)) for item in promoted]

@router.get("/patterns", response_model=list[PatternResponse])
def list_patterns(
    codebook: str | None = None,
    status: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> list[PatternResponse]:
    store = PatternStore(db, settings)
    items = store.list(codebook or settings.codebook, status=status)[:limit]
    return [PatternResponse.model_validate(store.response(item)) for item in items]

@router.get("/patterns/candidates", response_model=list[PatternCandidateResponse])
def list_pattern_candidates(
    codebook: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> list[PatternCandidateResponse]:
    items = PatternStore(db, settings).candidates(codebook or settings.codebook)[:limit]
    return [
        PatternCandidateResponse(
            codebook=item.codebook,
            signature=item.signature,
            canonical=item.canonical,
            composition=item.composition,
            relation_structure=item.relation_structure,
            occurrence_count=item.occurrence_count,
            estimated_savings_bytes=item.estimated_savings_bytes,
            semantic_variance=item.semantic_variance,
            trust_scope=item.trust_scope,
            source_diversity=item.source_diversity,
            dominant_source_share=item.dominant_source_share,
            trust_score=item.trust_score,
        )
        for item in items
    ]

@router.get("/patterns/{pattern_id}", response_model=PatternResponse)
def get_pattern(pattern_id: str, db: Session = Depends(get_db)) -> PatternResponse:
    store = PatternStore(db, settings)
    item = store.get(pattern_id)
    if item is None:
        raise HTTPException(404, "pattern not found")
    return PatternResponse.model_validate(store.response(item))

@router.post("/patterns/{pattern_id}/status", response_model=PatternResponse)
def set_pattern_status(
    pattern_id: str, req: PatternStatusRequest, db: Session = Depends(get_db)
) -> PatternResponse:
    store = PatternStore(db, settings)
    try:
        item = store.set_status(pattern_id, req.status)
    except KeyError as exc:
        raise HTTPException(404, "pattern not found") from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    db.commit()
    return PatternResponse.model_validate(store.response(item))

@router.post("/patterns/{pattern_id}/counterfactual", response_model=PatternResponse)
def pattern_counterfactual(pattern_id: str, req: CounterfactualPatternRequest, db: Session = Depends(get_db)) -> PatternResponse:
    store = PatternStore(db, settings)
    try:
        item = store.record_counterfactual(pattern_id, full_success=req.full_success, compressed_success=req.compressed_success, semantic_fidelity=req.semantic_fidelity, receiver=req.receiver, model=req.model, task_family=req.task_family, workspace=req.workspace, validation_id=req.validation_id)
    except KeyError as exc:
        raise HTTPException(404, "pattern not found") from exc
    db.commit()
    return PatternResponse.model_validate(store.response(item))

@router.post("/calibration/record", response_model=CalibrationResponse)
def calibration_record(req: CalibrationRecordRequest, db: Session = Depends(get_db)) -> CalibrationResponse:
    store = CalibrationStore(db, settings.calibration_buckets, settings.calibration_min_samples)
    store.record(
        predicted=req.predicted, observed=req.observed, workspace=req.workspace,
        receiver=req.receiver, model=req.model, task_family=req.task_family,
    )
    report = store.report(
        req.predicted, workspace=req.workspace, receiver=req.receiver,
        model=req.model, task_family=req.task_family,
    )
    db.commit()
    return CalibrationResponse.model_validate(store.response(report))

@router.get("/calibration", response_model=CalibrationResponse)
def calibration_report(
    predicted: float = Query(..., ge=0.0, le=1.0), receiver: str = "*", model: str = "*",
    task_family: str = "*", workspace: str = "default", db: Session = Depends(get_db),
) -> CalibrationResponse:
    store = CalibrationStore(db, settings.calibration_buckets, settings.calibration_min_samples)
    return CalibrationResponse.model_validate(store.response(store.report(
        predicted, workspace=workspace, receiver=receiver, model=model, task_family=task_family
    )))

@router.post("/patterns/{pattern_id}/promote-namespace", response_model=PatternResponse)
def pattern_promote_namespace(pattern_id: str, target: str = Query(...), db: Session = Depends(get_db)) -> PatternResponse:
    store = PatternStore(db, settings)
    try:
        item = store.promote_namespace(pattern_id, target)
    except KeyError as exc:
        raise HTTPException(404, "pattern not found") from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    db.commit()
    return PatternResponse.model_validate(store.response(item))

@router.post("/patterns/gc")
def pattern_gc(codebook: str | None = None, db: Session = Depends(get_db)) -> dict[str, int]:
    result = PatternStore(db, settings).garbage_collect(codebook)
    db.commit()
    return result

@router.post("/latent/pack", response_model=LatentPacket)
def latent_pack(req: LatentPackRequest) -> LatentPacket:
    return pack_latent(req.vector, req.space)

@router.post("/latent/unpack", response_model=list[float])
def latent_unpack(req: LatentUnpackRequest) -> list[float]:
    try:
        return unpack_latent(req.packet)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

@router.post("/negotiate", response_model=NegotiateResponse)
def negotiate(req: NegotiateRequest, db: Session = Depends(get_db)) -> NegotiateResponse:
    if req.receiver is not None:
        req.receiver = enforce_agent_scope(actor=req.receiver, workspace=req.workspace)
    else:
        enforce_agent_scope(actor=None, workspace=req.workspace)
    if SAGE_PROTOCOL not in req.capabilities.protocol_versions:
        raise HTTPException(409, f"peer must support {SAGE_PROTOCOL}")
    protocol = SAGE_PROTOCOL
    cb_name = req.codebook or settings.codebook
    principal = current_principal()
    if principal.kind == "agent" and cb_name != settings.codebook:
        raise HTTPException(403, "agent-scoped credentials may negotiate only the configured codebook")
    codebook = Codebook(db, settings)
    chain = codebook.namespace_chain(cb_name)
    missing = [c for c in codebook.all_chain(cb_name) if c.code not in req.known_codes]
    pattern_store = PatternStore(db, settings, codebook)
    missing_patterns = [
        p for p in pattern_store.list(cb_name, status="active") if p.pattern_id not in req.known_patterns
    ] if req.capabilities.supports_patterns else []
    negotiated = Capabilities(
        protocol_versions=[protocol],
        codebooks=[cb_name],
        max_packet_bytes=min(req.capabilities.max_packet_bytes, settings.max_packet_bytes),
        supports_refs=req.capabilities.supports_refs,
        supports_deltas=req.capabilities.supports_deltas,
        supports_patterns=req.capabilities.supports_patterns,
        latent_spaces=req.capabilities.latent_spaces,
        fallback_modes=req.capabilities.fallback_modes,
    )
    if req.receiver:
        KnowledgeStore(db).update_capabilities(req.receiver, negotiated.model_dump(), req.workspace)
        db.commit()
    return NegotiateResponse(
        protocol_version=protocol,
        codebook=cb_name,
        codebook_chain=chain,
        embedding_space=codebook.embedding_space,
        missing_codes=[concept_response(c, db) for c in missing[:500]],
        missing_patterns=[PatternResponse.model_validate(pattern_store.response(p)) for p in missing_patterns[:500]],
        fingerprint=codebook.fingerprint(cb_name),
        negotiated=negotiated,
    )

@router.get("/receivers/{receiver}")
def receiver_knowledge(
    receiver: str,
    workspace: str = Query(default="default"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    item = db.scalar(
        select(ReceiverKnowledge).where(
            ReceiverKnowledge.workspace == workspace,
            ReceiverKnowledge.receiver == receiver,
        )
    )
    if item is None:
        raise HTTPException(404, "receiver knowledge not found")
    return {
        "receiver": receiver,
        "workspace": workspace,
        "known_codes": KnowledgeStore(db).known_codes(receiver, workspace),
        "known_refs": KnowledgeStore(db).known_refs(receiver, workspace),
        "current_state": item.current_state,
        "capabilities": item.capabilities,
        "updated_at": item.updated_at.replace(tzinfo=item.updated_at.tzinfo or UTC).isoformat(),
    }
