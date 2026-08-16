# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import Settings
from .db_models import BusMessage, IdempotencyRecord, QuotaCounter


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _window_start(now: datetime, seconds: int) -> datetime:
    epoch = int(now.timestamp())
    return datetime.fromtimestamp(epoch - (epoch % seconds), tz=UTC)


def request_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode()
    return hashlib.sha256(raw).hexdigest()


def _scoped_resource(resource: str, subject: str | None) -> str:
    if not subject:
        return resource
    digest = hashlib.sha256(subject.encode()).hexdigest()[:16]
    return f"{resource}:{digest}"


class QuotaExceededError(RuntimeError):
    pass


class BackpressureError(RuntimeError):
    def __init__(self, state: str) -> None:
        self.state = state
        super().__init__(f"workspace queue is {state}")


@dataclass(frozen=True)
class BackpressureStatus:
    state: str
    pending: int
    limit: int
    ratio: float


class IdempotencyStore:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings

    def get(self, workspace: str, operation: str, key: str, payload: Any) -> dict[str, Any] | None:
        now = _utcnow()
        item = self.db.scalar(
            select(IdempotencyRecord).where(
                IdempotencyRecord.workspace == workspace,
                IdempotencyRecord.operation == operation,
                IdempotencyRecord.key == key,
            )
        )
        if item is None:
            return None
        if item.expires_at is not None and item.expires_at <= now:
            self.db.delete(item)
            self.db.flush()
            return None
        digest = request_hash(payload)
        if item.request_hash != digest:
            raise ValueError("idempotency key reused with different request")
        return dict(item.response or {})

    def put(self, workspace: str, operation: str, key: str, payload: Any, response: dict[str, Any]) -> None:
        expires = _utcnow() + timedelta(seconds=self.settings.idempotency_ttl_seconds)
        item = IdempotencyRecord(
            workspace=workspace,
            operation=operation,
            key=key,
            request_hash=request_hash(payload),
            response=response,
            expires_at=expires,
        )
        self.db.add(item)
        try:
            self.db.flush()
        except IntegrityError:
            self.db.rollback()
            existing = self.get(workspace, operation, key, payload)
            if existing is None:
                raise


class QuotaManager:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings

    def _limit(self, resource: str) -> int:
        base = resource.split(":", 1)[0]
        limits = {
            "handoff": self.settings.quota_handoffs_per_window,
            "handoff_agent": self.settings.quota_handoffs_per_agent_window,
            "ref_bytes": self.settings.quota_ref_bytes_per_window,
            "pattern_observation": self.settings.quota_pattern_observations_per_window,
        }
        if base not in limits:
            raise KeyError(resource)
        return limits[base]

    def consume(self, workspace: str, resource: str, amount: int = 1, *, subject: str | None = None) -> int:
        if amount < 0:
            raise ValueError("quota amount must be nonnegative")
        resource = _scoped_resource(resource, subject)
        now = _utcnow()
        start = _window_start(now, self.settings.quota_window_seconds)
        values = {"workspace": workspace, "resource": resource, "window_start": start, "used": amount, "updated_at": now}
        dialect = self.db.bind.dialect.name if self.db.bind is not None else ""
        if dialect == "sqlite":
            from sqlalchemy.dialects.sqlite import insert as sqlite_insert

            sqlite_stmt = sqlite_insert(QuotaCounter).values(**values).on_conflict_do_update(
                index_elements=[QuotaCounter.workspace, QuotaCounter.resource, QuotaCounter.window_start],
                set_={"used": QuotaCounter.used + amount, "updated_at": now},
            ).returning(QuotaCounter.used)
            used = int(self.db.execute(sqlite_stmt).scalar_one())
        elif dialect == "postgresql":
            from sqlalchemy.dialects.postgresql import insert as pg_insert

            pg_stmt = pg_insert(QuotaCounter).values(**values).on_conflict_do_update(
                index_elements=[QuotaCounter.workspace, QuotaCounter.resource, QuotaCounter.window_start],
                set_={"used": QuotaCounter.used + amount, "updated_at": now},
            ).returning(QuotaCounter.used)
            used = int(self.db.execute(pg_stmt).scalar_one())
        else:
            item = self.db.scalar(
                select(QuotaCounter)
                .where(
                    QuotaCounter.workspace == workspace,
                    QuotaCounter.resource == resource,
                    QuotaCounter.window_start == start,
                )
                .with_for_update()
            )
            if item is None:
                item = QuotaCounter(**values)
                self.db.add(item)
                self.db.flush()
            else:
                item.used += amount
                item.updated_at = now
                self.db.flush()
            used = int(item.used)
        limit = self._limit(resource)
        if used > limit:
            self.db.execute(
                update(QuotaCounter)
                .where(
                    QuotaCounter.workspace == workspace,
                    QuotaCounter.resource == resource,
                    QuotaCounter.window_start == start,
                )
                .values(used=QuotaCounter.used - amount, updated_at=now)
            )
            self.db.flush()
            raise QuotaExceededError(f"quota exceeded for {resource}")
        return used

    def backpressure(self, workspace: str) -> BackpressureStatus:
        pending = int(
            self.db.scalar(
                select(func.count(BusMessage.id)).where(
                    BusMessage.workspace == workspace,
                    BusMessage.status.in_(["pending", "claimed"]),
                )
            )
            or 0
        )
        limit = self.settings.max_pending_messages_per_workspace
        ratio = pending / max(1, limit)
        if ratio >= 1.0:
            state = "unavailable"
        elif ratio >= self.settings.backpressure_throttled_ratio:
            state = "throttled"
        elif ratio >= self.settings.backpressure_degraded_ratio:
            state = "degraded"
        else:
            state = "normal"
        return BackpressureStatus(state=state, pending=pending, limit=limit, ratio=ratio)

    def enforce_handoff(self, workspace: str, sender: str | None = None) -> BackpressureStatus:
        status = self.backpressure(workspace)
        if status.state == "unavailable":
            raise BackpressureError("unavailable")
        if status.state == "throttled":
            raise BackpressureError("throttled")
        with self.db.begin_nested():
            if sender:
                self.consume(workspace, "handoff_agent", 1, subject=sender)
            self.consume(workspace, "handoff", 1)
        return status
