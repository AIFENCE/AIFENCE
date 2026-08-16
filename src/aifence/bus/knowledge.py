# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .db_models import ReceiverKnowledge, ReceiverKnowledgeItem
from .schemas import Packet


class KnowledgeStore:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, receiver: str | None, workspace: str = "default") -> ReceiverKnowledge | None:
        if not receiver:
            return None
        return self.db.scalar(
            select(ReceiverKnowledge).where(
                ReceiverKnowledge.workspace == workspace,
                ReceiverKnowledge.receiver == receiver,
            )
        )

    def ensure(self, receiver: str, workspace: str = "default") -> ReceiverKnowledge:
        item = self.get(receiver, workspace)
        if item is not None:
            return item
        for _ in range(2):
            try:
                with self.db.begin_nested():
                    self.db.add(ReceiverKnowledge(workspace=workspace, receiver=receiver))
            except IntegrityError:
                pass  # concurrent writer won the unique-constraint race
            item = self.get(receiver, workspace)
            if item is not None:
                return item
            # Lost race and the winner had not committed yet; retry once so the
            # insert blocks on the unique index until the winner's commit lands.
        raise RuntimeError(f"receiver knowledge unavailable for {workspace}/{receiver}")

    def _values(self, receiver: str | None, workspace: str, kind: str) -> list[str]:
        if not receiver:
            return []
        return list(
            self.db.scalars(
                select(ReceiverKnowledgeItem.value).where(
                    ReceiverKnowledgeItem.workspace == workspace,
                    ReceiverKnowledgeItem.receiver == receiver,
                    ReceiverKnowledgeItem.kind == kind,
                    ReceiverKnowledgeItem.stale_at.is_(None),
                )
            )
        )

    def known_codes(self, receiver: str | None, workspace: str = "default") -> list[str]:
        return self._values(receiver, workspace, "code")

    def known_refs(self, receiver: str | None, workspace: str = "default") -> list[str]:
        return self._values(receiver, workspace, "ref")

    def _add_value(self, receiver: str, workspace: str, kind: str, value: str, confidence: float = 1.0) -> None:
        exists = self.db.scalar(
            select(ReceiverKnowledgeItem.id).where(
                ReceiverKnowledgeItem.workspace == workspace,
                ReceiverKnowledgeItem.receiver == receiver,
                ReceiverKnowledgeItem.kind == kind,
                ReceiverKnowledgeItem.value == value,
            )
        )
        if exists is not None:
            item = self.db.get(ReceiverKnowledgeItem, exists)
            if item is not None:
                item.confidence = max(item.confidence, confidence)
                item.stale_at = None
            return
        try:
            with self.db.begin_nested():
                self.db.add(ReceiverKnowledgeItem(workspace=workspace, receiver=receiver, kind=kind, value=value, confidence=confidence))
            return
        except IntegrityError:
            pass  # concurrent writer inserted the same item first
        item = self.db.scalar(
            select(ReceiverKnowledgeItem).where(
                ReceiverKnowledgeItem.workspace == workspace,
                ReceiverKnowledgeItem.receiver == receiver,
                ReceiverKnowledgeItem.kind == kind,
                ReceiverKnowledgeItem.value == value,
            )
        )
        if item is not None:
            item.confidence = max(item.confidence, confidence)
            item.stale_at = None

    def update_capabilities(self, receiver: str, capabilities: dict[str, Any], workspace: str = "default") -> ReceiverKnowledge:
        item = self.ensure(receiver, workspace)
        item.capabilities = capabilities
        return item

    def acknowledge(self, receiver: str, packet: Packet, workspace: str = "default") -> ReceiverKnowledge:
        item = self.ensure(receiver, workspace)
        for atom in packet.atoms:
            if atom.code:
                self._add_value(receiver, workspace, "code", atom.code, atom.confidence)
        for ref in packet.refs:
            self._add_value(receiver, workspace, "ref", ref, packet.prov.confidence)
        target_state = packet.meta.get("state")
        if isinstance(target_state, str):
            item.current_state = target_state
        elif packet.base and packet.delta == []:
            item.current_state = packet.base
        return item


    def items(self, receiver: str | None, workspace: str = "default", kind: str | None = None) -> list[dict[str, Any]]:
        if not receiver:
            return []
        stmt = select(ReceiverKnowledgeItem).where(ReceiverKnowledgeItem.workspace == workspace, ReceiverKnowledgeItem.receiver == receiver)
        if kind:
            stmt = stmt.where(ReceiverKnowledgeItem.kind == kind)
        return [{"kind": item.kind, "value": item.value, "confidence": item.confidence, "stale": item.stale_at is not None} for item in self.db.scalars(stmt)]

    def mark_stale(self, receiver: str, kind: str, value: str, workspace: str = "default") -> bool:
        item = self.db.scalar(select(ReceiverKnowledgeItem).where(ReceiverKnowledgeItem.workspace == workspace, ReceiverKnowledgeItem.receiver == receiver, ReceiverKnowledgeItem.kind == kind, ReceiverKnowledgeItem.value == value))
        if item is None:
            return False
        item.stale_at = datetime.now(UTC)
        return True

    def fingerprint(self, receiver: str | None, workspace: str = "default") -> str:
        item = self.get(receiver, workspace)
        if item is None:
            return "unknown"
        payload = {
            "codes": self.known_codes(receiver, workspace),
            "refs": self.known_refs(receiver, workspace),
            "state": item.current_state,
            "caps": item.capabilities or {},
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()[:24]
