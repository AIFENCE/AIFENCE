# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .db_models import (
    BusMessage,
    MessageAudit,
    ReceiverKnowledge,
    ReceiverKnowledgeItem,
    ReferenceGrant,
    SharedState,
    StateCheckpoint,
)


def _refs_from_wire(wire: dict[str, Any]) -> set[str]:
    refs = wire.get("R") or wire.get("refs") or []
    return {str(item) for item in refs if isinstance(item, str)}


def _states_from_wire(wire: dict[str, Any]) -> set[str]:
    states: set[str] = set()
    base = wire.get("base") or wire.get("b")
    if isinstance(base, str):
        states.add(base)
    meta = wire.get("meta") or wire.get("m") or {}
    if isinstance(meta, dict) and isinstance(meta.get("state"), str):
        states.add(meta["state"])
    return states


def reference_roots(db: Session, *, retain_audit: bool = True) -> set[str]:
    now = datetime.now(UTC)
    roots: set[str] = set()
    for grant in db.scalars(select(ReferenceGrant).where(ReferenceGrant.invalidated_at.is_(None))):
        if grant.expires_at is None or grant.expires_at.replace(tzinfo=grant.expires_at.tzinfo or UTC) > now:
            roots.add(grant.ref_id)
    for item in db.scalars(select(BusMessage).where(BusMessage.status != "acked")):
        roots |= _refs_from_wire(item.wire or {})
    if retain_audit:
        for audit in db.scalars(select(MessageAudit)):
            roots |= _refs_from_wire(audit.packet or {})
    roots.update(
        db.scalars(
            select(ReceiverKnowledgeItem.value).where(ReceiverKnowledgeItem.kind == "ref", ReceiverKnowledgeItem.stale_at.is_(None))
        )
    )
    return roots


def state_roots(db: Session, *, retain_audit: bool = True) -> set[str]:
    roots = set(db.scalars(select(StateCheckpoint.state_id)))
    roots.update(value for value in db.scalars(select(ReceiverKnowledge.current_state)) if value)
    for item in db.scalars(select(BusMessage).where(BusMessage.status != "acked")):
        roots |= _states_from_wire(item.wire or {})
    if retain_audit:
        for audit in db.scalars(select(MessageAudit)):
            roots |= _states_from_wire(audit.packet or {})
    return roots


def reachable_states(db: Session, *, retain_audit: bool = True) -> set[str]:
    reachable: set[str] = set()
    pending = list(state_roots(db, retain_audit=retain_audit))
    while pending:
        state_id = pending.pop()
        if state_id in reachable:
            continue
        state = db.get(SharedState, state_id)
        if state is None:
            continue
        reachable.add(state_id)
        if state.parent_id and state.parent_id not in reachable:
            pending.append(state.parent_id)
    return reachable
