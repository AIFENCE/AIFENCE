# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from .a2a_adapter import (
    agent_card,
    agent_card_extension,
    pack_data_part,
    pack_message,
    unpack_data_part,
    unpack_message,
)
from .api_helpers import _apply_trace_headers, bus_response
from .bus import SemanticBus
from .codec import SageCodec
from .config import get_settings
from .conformance import run_tck
from .db import get_db
from .db_models import MessageAudit
from .inspector import Inspector
from .integrations import config_for, profiles
from .patterns import PatternStore
from .protocol_spec import (
    SAGE_PROTOCOL,
    SAGE_SUPPORTED_PROTOCOLS,
    SAGE_WIRE_VERSION,
    canonical_digest,
    validate_wire_v2,
    wire_schema,
)
from .resilience import BackpressureError, QuotaExceededError
from .schemas import (
    A2AMessagePackRequest,
    A2AMessageUnpackRequest,
    A2APackRequest,
    A2AUnpackRequest,
    BusAckRequest,
    BusBatchAckRequest,
    BusContextItem,
    BusMessageResponse,
    DecodeRequest,
    DecodeResponse,
    EncodeRequest,
    EncodeResponse,
    ExplainResponse,
    FeedbackRequest,
    HandoffRequest,
    InspectorResponse,
    IntegrationConfigResponse,
    IntegrationProfile,
    ReceiveRequest,
    ReplayResponse,
    SendRequest,
    TransportReceiveRequest,
    TransportResponse,
)
from .security import current_principal, enforce_agent_scope

router = APIRouter()

settings = get_settings()

@router.post("/bus/handoff", response_model=BusMessageResponse)
def bus_handoff(req: HandoffRequest, db: Session = Depends(get_db)) -> BusMessageResponse:
    """Compress and durably enqueue a framework-neutral agent-to-agent handoff."""
    sender = enforce_agent_scope(actor=req.sender, workspace=req.workspace)
    try:
        bus = SemanticBus(db, settings)
        if req.refs:
            item = bus.forward_refs(
                receiver=req.receiver, refs=req.refs, sender=sender, workspace=req.workspace, run_id=req.run_id,
                correlation_id=req.correlation_id, priority=req.priority, ttl_seconds=req.ttl_seconds, source_ids=req.source_ids,
                idempotency_key=req.idempotency_key, partition_key=req.partition_key, ordering_key=req.ordering_key,
            )
        else:
            if req.content is None:
                raise ValueError("content or refs is required")
            item = bus.handoff(
                receiver=req.receiver, content=req.content, sender=sender, act=req.act, workspace=req.workspace,
                run_id=req.run_id, correlation_id=req.correlation_id, priority=req.priority, ttl_seconds=req.ttl_seconds,
                budget_tokens=req.budget_tokens, source_ids=req.source_ids, idempotency_key=req.idempotency_key,
                partition_key=req.partition_key, ordering_key=req.ordering_key,
            )
    except BackpressureError as exc:
        raise HTTPException(503 if exc.state == "unavailable" else 429, str(exc), headers={"Retry-After": "1"}) from exc
    except QuotaExceededError as exc:
        raise HTTPException(429, str(exc), headers={"Retry-After": "1"}) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    db.commit()
    return bus_response(item)

@router.get("/bus/pull/{receiver}", response_model=list[BusMessageResponse])
def bus_pull(
    receiver: str,
    workspace: str = Query(default="default"),
    limit: int = Query(default=20, ge=1, le=100),
    claim: bool = Query(default=True),
    budget_tokens: int | None = Query(default=None, ge=1),
    partition: str | None = Query(default=None, pattern=r"^p[0-9]{4}$"),
    db: Session = Depends(get_db),
) -> list[BusMessageResponse]:
    enforce_agent_scope(actor=receiver, workspace=workspace)
    items = SemanticBus(db, settings).pull(
        receiver=receiver, workspace=workspace, limit=limit, claim=claim, budget_tokens=budget_tokens, partition=partition
    )
    if claim:
        db.commit()
    return [bus_response(item) for item in items]

@router.get("/bus/context/{receiver}", response_model=list[BusContextItem])
def bus_context(
    receiver: str,
    workspace: str = Query(default="default"),
    limit: int = Query(default=20, ge=1, le=100),
    budget_tokens: int | None = Query(default=None, ge=1),
    partition: str | None = Query(default=None, pattern=r"^p[0-9]{4}$"),
    db: Session = Depends(get_db),
) -> list[BusContextItem]:
    scoped_receiver = enforce_agent_scope(actor=receiver, workspace=workspace)
    assert scoped_receiver is not None
    bus = SemanticBus(db, settings)
    items = bus.pull(
        receiver=scoped_receiver,
        workspace=workspace,
        limit=limit,
        claim=True,
        budget_tokens=budget_tokens,
        partition=partition,
    )
    result: list[BusContextItem] = []
    for item in items:
        decoded = bus.codec.decode(
            bus.codec.expand(item.wire),
            False,
            receiver=scoped_receiver,
            workspace=workspace,
            acknowledge=False,
        )
        result.append(
            BusContextItem(
                message_id=item.id,
                packet_id=item.packet_id,
                sender=item.sender,
                receiver=item.receiver,
                workspace=item.workspace,
                run_id=item.run_id,
                correlation_id=item.correlation_id,
                act=decoded.act,
                concepts=decoded.concepts,
                literals=decoded.literals,
                references=decoded.references,
                provenance=decoded.provenance,
                base_state=decoded.base_state,
                delta=decoded.delta,
                resolved_state=decoded.resolved_state,
                strategy=item.strategy,
                estimated_tokens=item.estimated_tokens,
                wire_bytes=item.wire_bytes,
            )
        )
    db.commit()
    return result

@router.post("/bus/ack-batch", response_model=list[BusMessageResponse])
def bus_ack_batch(
    req: BusBatchAckRequest, db: Session = Depends(get_db)
) -> list[BusMessageResponse]:
    receiver = enforce_agent_scope(actor=req.receiver, workspace=req.workspace)
    assert receiver is not None
    bus = SemanticBus(db, settings)
    items = []
    try:
        for message_id in dict.fromkeys(req.message_ids):
            items.append(bus.ack(message_id, receiver=receiver, workspace=req.workspace))
    except PermissionError as exc:
        db.rollback()
        raise HTTPException(403, str(exc)) from exc
    except KeyError as exc:
        db.rollback()
        raise HTTPException(404, "message not found") from exc
    except ValueError as exc:
        db.rollback()
        raise HTTPException(409, str(exc)) from exc
    db.commit()
    return [bus_response(item) for item in items]

@router.post("/bus/{message_id}/ack", response_model=BusMessageResponse)
def bus_ack(
    message_id: str, req: BusAckRequest, db: Session = Depends(get_db)
) -> BusMessageResponse:
    enforce_agent_scope(actor=req.receiver, workspace=req.workspace)
    try:
        item = SemanticBus(db, settings).ack(
            message_id, receiver=req.receiver, workspace=req.workspace
        )
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(404, "message not found") from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    db.commit()
    return bus_response(item)

@router.post("/bus/{message_id}/nack", response_model=BusMessageResponse)
def bus_nack(
    message_id: str, req: BusAckRequest, db: Session = Depends(get_db)
) -> BusMessageResponse:
    enforce_agent_scope(actor=req.receiver, workspace=req.workspace)
    try:
        item = SemanticBus(db, settings).nack(
            message_id, receiver=req.receiver, workspace=req.workspace
        )
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(404, "message not found") from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    db.commit()
    return bus_response(item)

@router.post("/a2a/pack")
def a2a_pack(req: A2APackRequest) -> dict[str, Any]:
    return pack_data_part(req.wire)

@router.post("/a2a/unpack")
def a2a_unpack(req: A2AUnpackRequest) -> dict[str, Any]:
    try:
        return {"wire": unpack_data_part(req.part)}
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

@router.post("/a2a/message/pack")
def a2a_message_pack(req: A2AMessagePackRequest) -> dict[str, Any]:
    try:
        return pack_message(
            req.wire,
            message_id=req.message_id,
            role=req.role,
            context_id=req.context_id,
            task_id=req.task_id,
            metadata=req.metadata or None,
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

@router.post("/a2a/message/unpack")
def a2a_message_unpack(req: A2AMessageUnpackRequest) -> dict[str, Any]:
    try:
        return {"wire": unpack_message(req.message)}
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

@router.get("/a2a/extension")
def a2a_extension() -> dict[str, Any]:
    return agent_card_extension()

@router.get("/a2a/agent-card")
def a2a_agent_card(
    url: str = Query(..., description="Public A2A 1.0 endpoint URL"),
    name: str = Query(default="SAGE-enabled agent"),
    description: str = Query(default="Agent supporting SAGE semantic payloads"),
    version: str = Query(default="1.0.0"),
    protocol_binding: str = Query(default="HTTP+JSON"),
) -> dict[str, Any]:
    if settings.env == "production" and not url.lower().startswith("https://"):
        raise HTTPException(422, "production A2A interface URLs must use HTTPS")
    return agent_card(
        name=name,
        description=description,
        url=url,
        version=version,
        protocol_binding=protocol_binding,
    )

@router.get("/protocol")
def protocol_info() -> dict[str, Any]:
    return {
        "protocol": SAGE_PROTOCOL,
        "wire_version": SAGE_WIRE_VERSION,
        "supported_protocols": list(SAGE_SUPPORTED_PROTOCOLS),
        "canonical_digest": "sha256(canonical-msgpack)",
        "frozen_line": "0.2.x",
    }

@router.get("/protocol/wire-schema")
def protocol_wire_schema() -> dict[str, Any]:
    return wire_schema()

@router.post("/protocol/validate")
def protocol_validate(wire: dict[str, Any]) -> dict[str, Any]:
    try:
        validate_wire_v2(wire)
    except (ValidationError, ValueError, TypeError) as exc:
        raise HTTPException(422, str(exc)) from exc
    return {"valid": True, "protocol": SAGE_PROTOCOL, "digest": canonical_digest(wire)}

@router.get("/protocol/tck")
def protocol_tck() -> dict[str, Any]:
    return run_tck().as_dict()

@router.get("/integrations", response_model=list[IntegrationProfile])
def list_integrations() -> list[IntegrationProfile]:
    return profiles()

@router.get("/integrations/{platform}", response_model=IntegrationConfigResponse)
def integration_config(
    platform: str,
    base_url: str = Query(..., min_length=8),
    agent_id: str = Query(..., min_length=1),
) -> IntegrationConfigResponse:
    try:
        return config_for(platform, base_url, agent_id)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc

@router.post("/send", response_model=EncodeResponse)
def send(
    req: SendRequest, db: Session = Depends(get_db),
    traceparent: str | None = Header(default=None), tracestate: str | None = Header(default=None),
) -> EncodeResponse:
    """Primary SAGE transport: receiver-aware, budget-constrained communication."""
    req.sender = enforce_agent_scope(actor=req.sender, workspace=req.workspace)
    _apply_trace_headers(req, traceparent, tracestate)
    try:
        return SageCodec(db, settings).encode(req)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        status = 413 if str(exc).startswith("payload exceeds") else 422
        raise HTTPException(status_code=status, detail=str(exc)) from exc

@router.post("/transport/send", response_model=TransportResponse)
def transport_send(
    req: SendRequest, db: Session = Depends(get_db),
    traceparent: str | None = Header(default=None), tracestate: str | None = Header(default=None),
) -> TransportResponse:
    req.sender = enforce_agent_scope(actor=req.sender, workspace=req.workspace)
    _apply_trace_headers(req, traceparent, tracestate)
    codec = SageCodec(db, settings)
    try:
        result = codec.encode(req)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        status = 413 if str(exc).startswith("payload exceeds") else 422
        raise HTTPException(status_code=status, detail=str(exc)) from exc
    return TransportResponse(
        packet_id=result.packet.id or "",
        wire=codec.compact(result.packet),
        strategy=result.strategy,
        estimated_tokens=result.estimated_tokens,
        output_bytes=result.output_bytes_msgpack,
        cache_hit=result.cache_hit,
    )

@router.post("/transport/receive", response_model=DecodeResponse)
def transport_receive(req: TransportReceiveRequest, db: Session = Depends(get_db)) -> DecodeResponse:
    req.receiver = enforce_agent_scope(actor=req.receiver, workspace=req.workspace)
    codec = SageCodec(db, settings)
    packet = codec.expand(req.wire)
    return codec.decode(
        packet,
        req.resolve_refs,
        receiver=req.receiver,
        workspace=req.workspace,
        acknowledge=req.acknowledge,
    )

@router.post("/receive", response_model=DecodeResponse)
def receive(req: ReceiveRequest, db: Session = Depends(get_db)) -> DecodeResponse:
    req.receiver = enforce_agent_scope(actor=req.receiver, workspace=req.workspace)
    return SageCodec(db, settings).decode(
        req.packet,
        req.resolve_refs,
        receiver=req.receiver,
        workspace=req.workspace,
        acknowledge=req.acknowledge,
    )

@router.post("/encode", response_model=EncodeResponse)
def encode(req: EncodeRequest, db: Session = Depends(get_db)) -> EncodeResponse:
    try:
        return SageCodec(db, settings).encode(req)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        status = 413 if str(exc).startswith("payload exceeds") else 422
        raise HTTPException(status_code=status, detail=str(exc)) from exc

@router.post("/decode", response_model=DecodeResponse)
def decode(req: DecodeRequest, db: Session = Depends(get_db)) -> DecodeResponse:
    return SageCodec(db, settings).decode(
        req.packet,
        req.resolve_refs,
        receiver=req.receiver,
        workspace=req.workspace,
    )

@router.get("/explain/{packet_id}", response_model=ExplainResponse)
def explain(packet_id: str, db: Session = Depends(get_db)) -> ExplainResponse:
    item = db.scalar(select(MessageAudit).where(MessageAudit.packet_id == packet_id))
    if item is None:
        raise HTTPException(404, "packet not found")
    return ExplainResponse(
        packet_id=item.packet_id,
        strategy=item.strategy,
        decisions=item.decisions,
        provenance=item.provenance,
        cache_hit=item.cache_hit,
        input_bytes=item.input_bytes,
        output_bytes=item.output_bytes,
        estimated_tokens=item.estimated_tokens,
        budget_tokens=item.budget_tokens,
    )

@router.get("/inspect/{packet_id}", response_model=InspectorResponse)
def inspect_packet(packet_id: str, db: Session = Depends(get_db)) -> InspectorResponse:
    principal = current_principal()
    workspace = principal.workspace if principal.kind == "agent" else None
    actor = principal.agent if principal.kind == "agent" else None
    try:
        return InspectorResponse.model_validate(Inspector(db).packet(packet_id, workspace=workspace, actor=actor))
    except KeyError as exc:
        raise HTTPException(404, "packet not found") from exc

@router.get("/inspect/run/{run_id}")
def inspect_run(run_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    principal = current_principal()
    workspace = principal.workspace if principal.kind == "agent" else None
    actor = principal.agent if principal.kind == "agent" else None
    try:
        return Inspector(db).run(run_id, workspace=workspace, actor=actor)
    except KeyError as exc:
        raise HTTPException(404, "run not found") from exc

@router.post("/feedback/{packet_id}")
def feedback(packet_id: str, req: FeedbackRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    item = db.scalar(select(MessageAudit).where(MessageAudit.packet_id == packet_id))
    if item is None:
        raise HTTPException(404, "packet not found")
    item.task_success = req.task_success
    patterns = PatternStore(db, settings).record_feedback(item.decisions, req.task_success)
    db.commit()
    return {
        "packet_id": packet_id,
        "task_success": req.task_success,
        "patterns_updated": [PatternStore(db, settings).response(pattern) for pattern in patterns],
    }

@router.get("/runs/{run_id}/replay", response_model=ReplayResponse)
def replay(run_id: str, db: Session = Depends(get_db)) -> ReplayResponse:
    items = list(
        db.scalars(
            select(MessageAudit).where(MessageAudit.run_id == run_id).order_by(MessageAudit.created_at, MessageAudit.id)
        )
    )
    return ReplayResponse(
        run_id=run_id,
        packets=[
            {
                "packet_id": item.packet_id,
                "sender": item.sender,
                "receiver": item.receiver,
                "strategy": item.strategy,
                "packet": item.packet,
                "decisions": item.decisions,
                "task_success": item.task_success,
                "created_at": item.created_at.isoformat(),
            }
            for item in items
        ],
    )
