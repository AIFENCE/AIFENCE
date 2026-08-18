# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .audit import append_event
from .ids import new_id
from .models import BudgetReservation, DelegationGrant, MemoryRecord, RuntimeBudget
from .service import AifenceService


def run_tenant_maintenance(
    session: Session,
    service: AifenceService,
    *,
    tenant_id: str,
    batch_size: int = 500,
) -> dict[str, Any]:
    """Run bounded, idempotent tenant maintenance.

    Destructive tenant deletion and KMS crypto-erasure intentionally remain
    externally attested lifecycle jobs; this routine only performs reversible or
    expiry-driven maintenance that can be proven from stored state.
    """
    now = datetime.now(UTC)
    limit = min(max(batch_size, 1), 5000)
    expired_memories = list(
        session.scalars(
            select(MemoryRecord)
            .where(
                MemoryRecord.tenant_id == tenant_id,
                MemoryRecord.status == "active",
                MemoryRecord.expires_at.is_not(None),
                MemoryRecord.expires_at <= now,
            )
            .order_by(MemoryRecord.expires_at.asc(), MemoryRecord.id.asc())
            .limit(limit)
        )
    )
    for record in expired_memories:
        record.status = "expired"

    expired_grants = list(
        session.scalars(
            select(DelegationGrant)
            .where(
                DelegationGrant.tenant_id == tenant_id,
                DelegationGrant.status == "active",
                DelegationGrant.expires_at <= now,
            )
            .order_by(DelegationGrant.expires_at.asc(), DelegationGrant.id.asc())
            .limit(limit)
        )
    )
    for grant in expired_grants:
        grant.status = "expired"
        grant.revoked_at = now

    reservation_statement = (
        select(BudgetReservation)
        .where(
            BudgetReservation.tenant_id == tenant_id,
            BudgetReservation.status == "reserved",
            BudgetReservation.expires_at <= now,
        )
        .order_by(BudgetReservation.expires_at.asc(), BudgetReservation.id.asc())
        .limit(limit)
    )
    if session.bind and session.bind.dialect.name == "postgresql":
        reservation_statement = reservation_statement.with_for_update(skip_locked=True)
    expired_reservations = list(session.scalars(reservation_statement))
    released = 0
    for reservation in expired_reservations:
        budget_statement = select(RuntimeBudget).where(
            RuntimeBudget.tenant_id == tenant_id,
            RuntimeBudget.id == reservation.budget_id,
        )
        if session.bind and session.bind.dialect.name == "postgresql":
            budget_statement = budget_statement.with_for_update()
        budget = session.scalar(budget_statement)
        if budget is not None:
            reserved = {key: Decimal(str(value)) for key, value in budget.reserved.items()}
            for key, value in reservation.amounts.items():
                reserved[key] = max(Decimal("0"), reserved.get(key, Decimal("0")) - Decimal(str(value)))
            budget.reserved = {key: format(value.normalize(), "f") for key, value in reserved.items()}
            budget.version += 1
            budget.updated_at = now
        reservation.status = "expired"
        reservation.settled_at = now
        released += 1

    artifact_result = service.prune_expired_artifacts(
        session, tenant_id=tenant_id, batch_size=limit
    )
    if expired_memories or expired_grants or expired_reservations:
        append_event(
            session,
            service.signing_key,
            event_id=new_id("evt"),
            tenant_id=tenant_id,
            trace_id=new_id("trc"),
            parent_event_id=None,
            event_type="maintenance.completed",
            payload={
                "expired_memories": len(expired_memories),
                "expired_delegations": len(expired_grants),
                "expired_budget_reservations": released,
                "expired_artifacts": artifact_result.get("artifacts_deleted", 0),
            },
        )
        session.commit()
    return {
        "tenant_id": tenant_id,
        "expired_memories": len(expired_memories),
        "expired_delegations": len(expired_grants),
        "expired_budget_reservations": released,
        "artifact_prune": artifact_result,
    }
