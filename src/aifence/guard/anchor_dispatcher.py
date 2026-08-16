# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import or_, select, text
from sqlalchemy.orm import Session, sessionmaker

from .audit_anchor import build_anchor_backend
from .crypto import hash_object
from .db import set_tenant_context
from .ids import new_id
from .models import AuditAnchor, AuditAnchorClaim

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AnchorRunResult:
    claimed: int = 0
    verified: int = 0
    retried: int = 0
    failed: int = 0
    anchor_ids: tuple[str, ...] = ()


class AuditAnchorWorker:
    """Fenced, idempotent publisher for independent audit evidence destinations."""

    def __init__(self, *, session_factory: sessionmaker[Session], service: Any,
                 worker_id: str | None = None) -> None:
        self.session_factory = session_factory
        self.service = service
        self.settings = service.settings
        self.worker_id = worker_id or f"anchor-{os.getpid()}-{new_id('wrk')}"
        self._closed = False

    async def close(self) -> None:
        self._closed = True

    async def run_forever(self) -> None:
        while not self._closed:
            result = await self.run_once(limit=self.settings.anchor_batch_size)
            if result.claimed == 0:
                await asyncio.sleep(self.settings.anchor_poll_milliseconds / 1000)

    async def run_once(self, *, limit: int | None = None) -> AnchorRunResult:
        claims = self._claim(min(limit or self.settings.anchor_batch_size,
                                 self.settings.anchor_batch_size))
        states = await asyncio.gather(*(
            asyncio.to_thread(self._deliver, anchor_id, tenant_id, fence)
            for anchor_id, tenant_id, fence in claims
        )) if claims else []
        return AnchorRunResult(
            claimed=len(claims),
            verified=sum(state == "verified" for state in states),
            retried=sum(state == "retry" for state in states),
            failed=sum(state == "failed" for state in states),
            anchor_ids=tuple(claim[0] for claim in claims),
        )

    def _claim(self, limit: int) -> list[tuple[str, str, int]]:
        now = datetime.now(UTC)
        expires = now + timedelta(seconds=self.settings.anchor_lease_seconds)
        with self.session_factory() as session:
            if session.get_bind().dialect.name == "postgresql":
                rows = session.execute(
                    text(
                        "SELECT anchor_id, tenant_id, fencing_token FROM "
                        "agentdance_claim_audit_anchors(:worker_id, :batch_size, :lease_seconds)"
                    ),
                    {
                        "worker_id": self.worker_id,
                        "batch_size": limit,
                        "lease_seconds": self.settings.anchor_lease_seconds,
                    },
                ).all()
                result: list[tuple[str, str, int]] = []
                for row in rows:
                    anchor_id, tenant_id, fence = str(row[0]), str(row[1]), int(row[2])
                    set_tenant_context(session, tenant_id)
                    claim = session.get(AuditAnchorClaim, anchor_id)
                    anchor = session.scalar(
                        select(AuditAnchor).where(
                            AuditAnchor.tenant_id == tenant_id, AuditAnchor.id == anchor_id
                        )
                    )
                    if claim is None or anchor is None:
                        if claim is not None:
                            claim.status = "dead_lettered"
                            claim.processed_at = now
                        continue
                    anchor.status = "delivering"
                    anchor.lease_owner = self.worker_id
                    anchor.lease_expires_at = expires
                    anchor.fencing_token = fence
                    anchor.attempts = claim.attempts
                    result.append((anchor_id, tenant_id, fence))
                session.commit()
                return result

            statement = select(AuditAnchorClaim).where(
                or_(
                    AuditAnchorClaim.status.in_(["pending", "retry"]),
                    (AuditAnchorClaim.status == "leased")
                    & (AuditAnchorClaim.lease_expires_at <= now),
                ),
                AuditAnchorClaim.available_at <= now,
                AuditAnchorClaim.attempts < AuditAnchorClaim.max_attempts,
            ).order_by(
                AuditAnchorClaim.priority.asc(),
                AuditAnchorClaim.available_at.asc(),
                AuditAnchorClaim.created_at.asc(),
                AuditAnchorClaim.anchor_id.asc(),
            ).limit(limit)
            result = []
            for claim in session.scalars(statement):
                # Preserve one in-flight chain element per tenant/destination.
                earlier = session.scalar(select(AuditAnchorClaim.anchor_id).where(
                    AuditAnchorClaim.tenant_id == claim.tenant_id,
                    AuditAnchorClaim.destination == claim.destination,
                    AuditAnchorClaim.status.in_(["pending", "retry", "leased"]),
                    AuditAnchorClaim.created_at < claim.created_at,
                ).limit(1))
                if earlier:
                    continue
                claim.status = "leased"
                claim.lease_owner = self.worker_id
                claim.lease_expires_at = expires
                claim.fencing_token += 1
                claim.attempts += 1
                set_tenant_context(session, claim.tenant_id)
                anchor = session.scalar(select(AuditAnchor).where(
                    AuditAnchor.tenant_id == claim.tenant_id,
                    AuditAnchor.id == claim.anchor_id,
                ))
                if anchor is None:
                    claim.status = "dead_lettered"
                    claim.processed_at = now
                    continue
                anchor.status = "delivering"
                anchor.lease_owner = self.worker_id
                anchor.lease_expires_at = expires
                anchor.fencing_token = claim.fencing_token
                anchor.attempts = claim.attempts
                result.append((claim.anchor_id, claim.tenant_id, claim.fencing_token))
            session.commit()
            return result

    def _deliver(self, anchor_id: str, tenant_id: str, fence: int) -> str:
        try:
            with self.session_factory() as session:
                set_tenant_context(session, tenant_id)
                anchor = self._locked_anchor(session, anchor_id, tenant_id, fence)
                envelope = dict(anchor.envelope)
                destination = anchor.destination
            backend = build_anchor_backend(self.settings, destination)
            receipt = backend.publish(envelope)
            if not backend.verify(envelope, receipt):
                raise RuntimeError("remote audit anchor read-back verification failed")
            with self.session_factory() as session:
                set_tenant_context(session, tenant_id)
                anchor = self._locked_anchor(session, anchor_id, tenant_id, fence)
                claim = session.get(AuditAnchorClaim, anchor_id)
                if claim is None or claim.fencing_token != fence or claim.lease_owner != self.worker_id:
                    raise RuntimeError("audit anchor completion fence is stale")
                combined = {"envelope": envelope, "backend": receipt}
                now = datetime.now(UTC)
                anchor.receipt = combined; anchor.receipt_hash = hash_object(combined)
                anchor.status = "verified"; anchor.verified_at = now; anchor.anchored_at = now
                anchor.lease_owner = None; anchor.lease_expires_at = None; anchor.last_error = None
                claim.status = "processed"; claim.processed_at = now
                claim.lease_owner = None; claim.lease_expires_at = None
                session.commit()
            return "verified"
        except Exception as exc:
            logger.exception("audit anchor delivery failed", extra={"anchor_id": anchor_id})
            with self.session_factory() as session:
                set_tenant_context(session, tenant_id)
                try:
                    anchor = self._locked_anchor(session, anchor_id, tenant_id, fence)
                except RuntimeError:
                    return "failed"
                claim = session.get(AuditAnchorClaim, anchor_id)
                if claim is None or claim.fencing_token != fence:
                    return "failed"
                anchor.last_error = f"{type(exc).__name__}: {exc}"[:4096]
                anchor.lease_owner = None; anchor.lease_expires_at = None
                claim.lease_owner = None; claim.lease_expires_at = None
                if claim.attempts < claim.max_attempts:
                    available = datetime.now(UTC) + timedelta(seconds=min(600, 2 ** min(claim.attempts, 9)))
                    anchor.status = "pending"; anchor.available_at = available
                    claim.status = "retry"; claim.available_at = available
                    state = "retry"
                else:
                    anchor.status = "failed"; claim.status = "dead_lettered"
                    claim.processed_at = datetime.now(UTC); state = "failed"
                session.commit()
                return state

    def _locked_anchor(self, session: Session, anchor_id: str, tenant_id: str,
                       fence: int) -> AuditAnchor:
        statement = select(AuditAnchor).where(
            AuditAnchor.tenant_id == tenant_id, AuditAnchor.id == anchor_id)
        if session.bind and session.bind.dialect.name == "postgresql":
            statement = statement.with_for_update()
        anchor = session.scalar(statement)
        if anchor is None:
            raise RuntimeError("audit anchor disappeared")
        if anchor.lease_owner != self.worker_id or anchor.fencing_token != fence:
            raise RuntimeError("audit anchor lease is stale")
        return anchor
