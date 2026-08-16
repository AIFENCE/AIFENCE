# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

from typing import Any

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from .db_models import Concept
from .schemas import BusMessageResponse, ConceptResponse, EncodeRequest, TraceContext


def _apply_trace_headers(req: EncodeRequest, traceparent: str | None, tracestate: str | None) -> None:
    if req.trace is not None or traceparent is None:
        return
    try:
        req.trace = TraceContext(traceparent=traceparent.lower(), tracestate=tracestate)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail="invalid W3C trace context") from exc

def concept_response(c: Concept, db: Session | None = None) -> ConceptResponse:
    replacement_code = None
    if c.replacement_id:
        replacement = db.get(Concept, c.replacement_id) if db else None
        replacement_code = replacement.code if replacement else f"C{c.replacement_id:08X}"
    return ConceptResponse(
        code=c.code,
        codebook=c.codebook,
        canonical=c.canonical,
        description=c.description,
        seen_count=c.seen_count,
        confidence=c.confidence,
        version=c.version,
        status=c.status,
        replacement_code=replacement_code,
    )

def bus_response(item: Any) -> BusMessageResponse:
    return BusMessageResponse(
        message_id=item.id,
        packet_id=item.packet_id,
        sender=item.sender,
        receiver=item.receiver,
        workspace=item.workspace,
        run_id=item.run_id,
        correlation_id=item.correlation_id,
        idempotency_key=item.idempotency_key,
        partition_key=item.partition_key,
        ordering_key=item.ordering_key,
        sequence_no=item.sequence_no,
        priority=item.priority,
        status=item.status,
        wire=item.wire,
        strategy=item.strategy,
        estimated_tokens=item.estimated_tokens,
        wire_bytes=item.wire_bytes,
        expires_at=item.expires_at.isoformat() if item.expires_at else None,
        created_at=item.created_at.isoformat(),
    )
