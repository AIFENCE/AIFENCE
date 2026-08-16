# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from .codec import SageCodec
from .config import Settings
from .db_models import BusMessage, MessageAudit, OrderingCounter
from .resilience import QuotaManager
from .schemas import Budget, EncodeRequest, Packet, Provenance


def _utcnow() -> datetime:
    return datetime.now(UTC)


class SemanticBus:
    """Durable, vendor-neutral delivery for compact SAGE packets.

    Framework adapters map their local agent identities to the stable receiver strings
    used here. Claims are leases, so a crashed consumer does not strand a message.
    """

    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings
        self.codec = SageCodec(db, settings)
        self.quotas = QuotaManager(db, settings)

    def _next_sequence(self, workspace: str, ordering_key: str) -> int:
        now = _utcnow()
        dialect = self.db.bind.dialect.name if self.db.bind is not None else ""
        if dialect == "sqlite":
            from sqlalchemy.dialects.sqlite import insert as sqlite_insert

            sqlite_stmt = sqlite_insert(OrderingCounter).values(
                workspace=workspace, ordering_key=ordering_key, sequence_no=1, updated_at=now
            )
            sqlite_upsert = sqlite_stmt.on_conflict_do_update(
                index_elements=[OrderingCounter.workspace, OrderingCounter.ordering_key],
                set_={"sequence_no": OrderingCounter.sequence_no + 1, "updated_at": now},
            ).returning(OrderingCounter.sequence_no)
            return int(self.db.execute(sqlite_upsert).scalar_one())
        if dialect == "postgresql":
            from sqlalchemy.dialects.postgresql import insert as pg_insert

            pg_stmt = pg_insert(OrderingCounter).values(
                workspace=workspace, ordering_key=ordering_key, sequence_no=1, updated_at=now
            )
            pg_upsert = pg_stmt.on_conflict_do_update(
                index_elements=[OrderingCounter.workspace, OrderingCounter.ordering_key],
                set_={"sequence_no": OrderingCounter.sequence_no + 1, "updated_at": now},
            ).returning(OrderingCounter.sequence_no)
            return int(self.db.execute(pg_upsert).scalar_one())
        counter = self.db.scalar(
            select(OrderingCounter)
            .where(OrderingCounter.workspace == workspace, OrderingCounter.ordering_key == ordering_key)
            .with_for_update()
        )
        if counter is None:
            counter = OrderingCounter(workspace=workspace, ordering_key=ordering_key, sequence_no=1)
            self.db.add(counter)
            self.db.flush()
            return 1
        counter.sequence_no += 1
        self.db.flush()
        return int(counter.sequence_no)

    def handoff(
        self,
        *,
        receiver: str,
        content: Any,
        sender: str | None = None,
        act: str = "handoff",
        workspace: str = "default",
        run_id: str | None = None,
        correlation_id: str | None = None,
        priority: int = 0,
        ttl_seconds: int | None = None,
        budget_tokens: int | None = None,
        source_ids: list[str] | None = None,
        idempotency_key: str | None = None,
        partition_key: str | None = None,
        ordering_key: str | None = None,
    ) -> BusMessage:
        receiver = receiver.strip()
        if not receiver:
            raise ValueError("receiver is required")
        if idempotency_key:
            existing = self.db.scalar(select(BusMessage).where(BusMessage.workspace == workspace, BusMessage.idempotency_key == idempotency_key))
            if existing is not None:
                if existing.receiver != receiver or existing.sender != sender:
                    raise ValueError("idempotency key reused for a different handoff")
                return existing
        self.quotas.enforce_handoff(workspace, sender)
        result = self.codec.encode(
            EncodeRequest(
                content=content,
                sender=sender,
                receiver=receiver,
                act=act,
                workspace=workspace,
                run_id=run_id,
                budget=Budget(max_tokens=budget_tokens) if budget_tokens else None,
                provenance=Provenance(source_ids=source_ids or [], producer=sender),
            )
        )
        now = _utcnow()
        effective_ttl = ttl_seconds if ttl_seconds is not None else self.settings.default_bus_ttl_seconds
        expires_at = now + timedelta(seconds=effective_ttl) if effective_ttl else None
        partition_seed = partition_key or ordering_key or receiver
        partition = hashlib.sha256(partition_seed.encode("utf-8")).hexdigest()[:8]
        partition_index = int(partition, 16) % self.settings.bus_partition_count
        effective_partition = f"p{partition_index:04d}"
        sequence_no = self._next_sequence(workspace, ordering_key) if ordering_key else None
        item = BusMessage(
            id="M" + uuid.uuid4().hex,
            packet_id=result.packet.id or "",
            sender=sender,
            receiver=receiver,
            workspace=workspace,
            run_id=run_id,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
            partition_key=effective_partition,
            ordering_key=ordering_key,
            sequence_no=sequence_no,
            priority=priority,
            status="pending",
            wire=self.codec.compact(result.packet),
            strategy=result.strategy,
            estimated_tokens=result.estimated_tokens,
            wire_bytes=result.output_bytes_msgpack,
            expires_at=expires_at,
        )
        self.db.add(item)
        self.db.flush()
        return item


    def forward_refs(
        self,
        *,
        receiver: str,
        refs: list[str],
        sender: str | None = None,
        workspace: str = "default",
        run_id: str | None = None,
        correlation_id: str | None = None,
        priority: int = 0,
        ttl_seconds: int | None = None,
        source_ids: list[str] | None = None,
        idempotency_key: str | None = None,
        partition_key: str | None = None,
        ordering_key: str | None = None,
    ) -> BusMessage:
        if not refs:
            raise ValueError("at least one ref is required")
        if idempotency_key:
            existing = self.db.scalar(select(BusMessage).where(BusMessage.workspace == workspace, BusMessage.idempotency_key == idempotency_key))
            if existing is not None:
                if existing.receiver != receiver or existing.sender != sender:
                    raise ValueError("idempotency key reused for a different handoff")
                return existing
        self.quotas.enforce_handoff(workspace, sender)
        ref_bytes_avoided = 0
        for ref_id in refs:
            ref_item = self.codec.refs.get(ref_id, actor=sender, workspace=workspace)
            if ref_item is None:
                raise KeyError(ref_id)
            ref_bytes_avoided += ref_item.byte_size
            grant = self.codec.refs.grant_metadata(ref_id, actor=sender, workspace=workspace)
            if grant.owner != sender:
                raise PermissionError("only the explicit reference owner can forward it")
            self.codec.refs.grant(
                ref_id, workspace=workspace, owner=grant.owner, acl=list(set(grant.acl) | {receiver}),
                allowed_paths=grant.allowed_paths, tier=grant.tier, provenance=grant.provenance, sensitivity=grant.sensitivity,
            )
        packet = Packet(
            id=self.codec._packet_id(), cb=self.settings.codebook, sender=sender, receiver=receiver, act="handoff",
            refs=refs, prov=Provenance(source_ids=source_ids or [], producer=sender), meta={"strategy": "zero_copy"},
        )
        if self.settings.packet_signing_private_key is not None:
            from .signing import sign_wire
            unsigned = self.codec.compact(packet)
            unsigned.pop("g", None)
            packet.signature = sign_wire(unsigned, self.settings.packet_signing_private_key.get_secret_value(), key_id=self.settings.packet_signing_key_id)
        _, packed = self.codec._wire(packet)
        now = _utcnow()
        effective_ttl = ttl_seconds if ttl_seconds is not None else self.settings.default_bus_ttl_seconds
        expires_at = now + timedelta(seconds=effective_ttl) if effective_ttl else None
        wire = self.codec.compact(packet)
        partition_seed = partition_key or ordering_key or receiver
        partition = hashlib.sha256(partition_seed.encode("utf-8")).hexdigest()[:8]
        effective_partition = f"p{int(partition, 16) % self.settings.bus_partition_count:04d}"
        sequence_no = self._next_sequence(workspace, ordering_key) if ordering_key else None
        item = BusMessage(
            id="M" + uuid.uuid4().hex, packet_id=packet.id or "", sender=sender, receiver=receiver, workspace=workspace,
            run_id=run_id, correlation_id=correlation_id, idempotency_key=idempotency_key, partition_key=effective_partition,
            ordering_key=ordering_key, sequence_no=sequence_no, priority=priority, status="pending", wire=wire,
            strategy="zero_copy", estimated_tokens=max(1, len(str(wire)) // 4), wire_bytes=len(packed), expires_at=expires_at,
        )
        self.db.add(item)
        self.db.add(MessageAudit(
            packet_id=packet.id or "", run_id=run_id, sender=sender, receiver=receiver, workspace=workspace, strategy="zero_copy",
            cache_hit=False, input_bytes=0, output_bytes=len(packed), estimated_tokens=item.estimated_tokens, budget_tokens=None,
            atom_count=0, ref_count=len(refs), packet=packet.model_dump(exclude_none=True),
            decisions=[{"action": "zero_copy_forward", "refs": refs}], provenance=packet.prov.model_dump(), ref_bytes_avoided=ref_bytes_avoided,
        ))
        self.db.flush()
        return item

    def _eligible(self, receiver: str, workspace: str, now: datetime, partition: str | None = None) -> Any:
        lease_cutoff = now - timedelta(seconds=self.settings.bus_claim_lease_seconds)
        deliverable_status = or_(
            BusMessage.status == "pending",
            and_(
                BusMessage.status == "claimed",
                BusMessage.claimed_at.is_not(None),
                BusMessage.claimed_at <= lease_cutoff,
            ),
        )
        conditions = [
            BusMessage.workspace == workspace,
            BusMessage.receiver == receiver,
            deliverable_status,
            or_(BusMessage.expires_at.is_(None), BusMessage.expires_at > now),
        ]
        if partition is not None:
            conditions.append(BusMessage.partition_key == partition)
        return and_(*conditions)

    def pull(
        self,
        *,
        receiver: str,
        workspace: str = "default",
        limit: int = 20,
        claim: bool = True,
        budget_tokens: int | None = None,
        partition: str | None = None,
    ) -> list[BusMessage]:
        now = _utcnow()
        stmt = (
            select(BusMessage)
            .where(self._eligible(receiver, workspace, now, partition))
            .order_by(BusMessage.priority.desc(), BusMessage.ordering_key, BusMessage.sequence_no, BusMessage.created_at, BusMessage.id)
            .limit(max(1, min(limit, 100)))
        )
        if claim:
            stmt = stmt.with_for_update(skip_locked=True)
        items = list(self.db.scalars(stmt))
        if budget_tokens is not None:
            if budget_tokens <= 0:
                return []
            selected: list[BusMessage] = []
            used = 0
            for item in items:
                cost = max(1, int(item.estimated_tokens or 1))
                if used + cost <= budget_tokens:
                    selected.append(item)
                    used += cost
            items = selected
        if claim:
            for item in items:
                item.status = "claimed"
                item.claimed_at = now
            self.db.flush()
        return items

    def ack(self, message_id: str, *, receiver: str, workspace: str = "default") -> BusMessage:
        item = self.db.get(BusMessage, message_id)
        if item is None or item.workspace != workspace:
            raise KeyError(message_id)
        if item.receiver != receiver:
            raise PermissionError("message belongs to another receiver")
        if item.status == "acked":
            return item
        if item.expires_at is not None:
            expires = item.expires_at
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=UTC)
            if expires <= _utcnow():
                raise ValueError("cannot acknowledge an expired message")
        item.status = "acked"
        item.acked_at = _utcnow()
        packet = self.codec.expand(item.wire)
        self.codec.decode(packet, False, receiver=receiver, workspace=workspace, acknowledge=True)
        self.db.flush()
        return item

    def nack(self, message_id: str, *, receiver: str, workspace: str = "default") -> BusMessage:
        item = self.db.get(BusMessage, message_id)
        if item is None or item.workspace != workspace:
            raise KeyError(message_id)
        if item.receiver != receiver:
            raise PermissionError("message belongs to another receiver")
        if item.status == "acked":
            raise ValueError("cannot nack an acknowledged message")
        item.status = "pending"
        item.claimed_at = None
        self.db.flush()
        return item

    def backpressure(self, *, workspace: str = "default") -> dict[str, Any]:
        status = self.quotas.backpressure(workspace)
        return {"state": status.state, "pending": status.pending, "limit": status.limit, "ratio": status.ratio}

    def pending_count(self, *, receiver: str, workspace: str = "default") -> int:
        now = _utcnow()
        stmt = select(func.count(BusMessage.id)).where(self._eligible(receiver, workspace, now))
        return int(self.db.scalar(stmt) or 0)
