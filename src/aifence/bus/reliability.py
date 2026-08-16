# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import Settings
from .db_models import LearnedPattern, ModelIdentity, PatternValidationEvidence, ReliabilityWindow


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _identity_hash(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


class ModelIdentityStore:
    def __init__(self, db: Session) -> None:
        self.db = db

    def register(
        self,
        *,
        workspace: str,
        receiver: str,
        provider: str,
        model: str,
        model_version: str,
        runtime: str,
        runtime_version: str,
        configuration: dict[str, Any] | None = None,
    ) -> ModelIdentity:
        config_hash = _identity_hash(configuration or {})
        identity = {
            "provider": provider,
            "model": model,
            "model_version": model_version,
            "runtime": runtime,
            "runtime_version": runtime_version,
            "config_hash": config_hash,
        }
        digest = _identity_hash(identity)
        existing = self.db.scalar(
            select(ModelIdentity).where(
                ModelIdentity.workspace == workspace,
                ModelIdentity.receiver == receiver,
                ModelIdentity.identity_hash == digest,
            )
        )
        now = _utcnow()
        if existing is not None:
            existing.active = True
            existing.last_seen_at = now
            return existing
        for old in self.db.scalars(
            select(ModelIdentity).where(ModelIdentity.workspace == workspace, ModelIdentity.receiver == receiver, ModelIdentity.active.is_(True))
        ):
            old.active = False
        item = ModelIdentity(
            workspace=workspace,
            receiver=receiver,
            provider=provider,
            model=model,
            model_version=model_version,
            runtime=runtime,
            runtime_version=runtime_version,
            config_hash=config_hash,
            identity_hash=digest,
            active=True,
            last_seen_at=now,
        )
        self.db.add(item)
        self.db.flush()
        return item

    def active(self, workspace: str, receiver: str) -> ModelIdentity | None:
        return self.db.scalar(
            select(ModelIdentity)
            .where(ModelIdentity.workspace == workspace, ModelIdentity.receiver == receiver, ModelIdentity.active.is_(True))
            .order_by(ModelIdentity.last_seen_at.desc())
            .limit(1)
        )


class ReliabilityMonitor:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings

    def record_holdout(
        self,
        *,
        pattern: LearnedPattern,
        workspace: str,
        receiver: str,
        model_identity_hash: str,
        task_family: str,
        full_success: float,
        compressed_success: float,
        fidelity: float,
        source_id: str = "",
    ) -> PatternValidationEvidence:
        item = PatternValidationEvidence(
            pattern_id=pattern.id,
            workspace=workspace,
            split="holdout",
            receiver=receiver,
            model_identity_hash=model_identity_hash or "*",
            task_family=task_family,
            full_success=full_success,
            compressed_success=compressed_success,
            fidelity=fidelity,
            source_hash=hashlib.sha256(source_id.encode()).hexdigest() if source_id else "",
        )
        self.db.add(item)
        self._record_window(
            pattern=pattern,
            workspace=workspace,
            receiver=receiver,
            model_identity_hash=model_identity_hash or "*",
            task_family=task_family,
            fidelity=fidelity,
        )
        self.db.flush()
        return item

    def holdout_summary(
        self,
        pattern: LearnedPattern,
        *,
        workspace: str = "default",
        receiver: str = "*",
        model_identity_hash: str = "*",
        task_family: str = "*",
    ) -> dict[str, float | int]:
        rows = list(
            self.db.scalars(
                select(PatternValidationEvidence).where(
                    PatternValidationEvidence.pattern_id == pattern.id,
                    PatternValidationEvidence.workspace == workspace,
                    PatternValidationEvidence.split == "holdout",
                    PatternValidationEvidence.receiver == receiver,
                    PatternValidationEvidence.model_identity_hash == model_identity_hash,
                    PatternValidationEvidence.task_family == task_family,
                )
            )
        )
        if not rows:
            return {"samples": 0, "sources": 0, "fidelity": 0.0, "full_success": 0.0, "compressed_success": 0.0}
        count = len(rows)
        sources = {row.source_hash for row in rows if row.source_hash}
        return {
            "samples": count,
            "sources": len(sources),
            "fidelity": sum(row.fidelity for row in rows) / count,
            "full_success": sum(row.full_success for row in rows) / count,
            "compressed_success": sum(row.compressed_success for row in rows) / count,
        }

    def holdout_ready(self, pattern: LearnedPattern, **scope: Any) -> bool:
        summary = self.holdout_summary(pattern, **scope)
        return bool(
            int(summary["samples"]) >= self.settings.pattern_holdout_min_samples
            and int(summary["sources"]) >= self.settings.pattern_holdout_min_sources
            and float(summary["fidelity"]) >= self.settings.pattern_holdout_min_fidelity
            and float(summary["compressed_success"]) + 1e-9 >= float(summary["full_success"])
        )

    def _record_window(
        self,
        *,
        pattern: LearnedPattern,
        workspace: str,
        receiver: str,
        model_identity_hash: str,
        task_family: str,
        fidelity: float,
    ) -> ReliabilityWindow:
        now = _utcnow()
        seconds = self.settings.pattern_drift_window_minutes * 60
        epoch = int(now.timestamp())
        start = datetime.fromtimestamp(epoch - (epoch % seconds), tz=UTC)
        item = self.db.scalar(
            select(ReliabilityWindow).where(
                ReliabilityWindow.workspace == workspace,
                ReliabilityWindow.receiver == receiver,
                ReliabilityWindow.model_identity_hash == model_identity_hash,
                ReliabilityWindow.pattern_id == pattern.id,
                ReliabilityWindow.task_family == task_family,
                ReliabilityWindow.window_start == start,
            )
        )
        if item is None:
            item = ReliabilityWindow(
                workspace=workspace,
                receiver=receiver,
                model_identity_hash=model_identity_hash,
                pattern_id=pattern.id,
                task_family=task_family,
                window_start=start,
            )
            self.db.add(item)
            self.db.flush()
        item.sample_count += 1
        item.fidelity_sum += fidelity
        previous = self.db.scalar(
            select(ReliabilityWindow)
            .where(
                ReliabilityWindow.workspace == workspace,
                ReliabilityWindow.receiver == receiver,
                ReliabilityWindow.model_identity_hash == model_identity_hash,
                ReliabilityWindow.pattern_id == pattern.id,
                ReliabilityWindow.task_family == task_family,
                ReliabilityWindow.window_start < start,
                ReliabilityWindow.sample_count >= self.settings.pattern_drift_min_samples,
            )
            .order_by(ReliabilityWindow.window_start.desc())
            .limit(1)
        )
        if previous is not None and item.sample_count >= self.settings.pattern_drift_min_samples:
            current_avg = item.fidelity_sum / item.sample_count
            previous_avg = previous.fidelity_sum / previous.sample_count
            item.drift_score = max(0.0, previous_avg - current_avg)
            if item.drift_score > self.settings.pattern_drift_max_drop:
                item.status = "degraded"
                if pattern.status == "active":
                    pattern.status = "cooling"
                    pattern.cooling_since = now
                    pattern.version += 1
            else:
                item.status = "stable"
        return item

    def latest_status(
        self,
        *,
        workspace: str,
        receiver: str,
        model_identity_hash: str,
        pattern_id: int | None = None,
        task_family: str = "*",
    ) -> dict[str, Any]:
        stmt = select(ReliabilityWindow).where(
            ReliabilityWindow.workspace == workspace,
            ReliabilityWindow.receiver == receiver,
            ReliabilityWindow.model_identity_hash == model_identity_hash,
            ReliabilityWindow.task_family == task_family,
        )
        if pattern_id is not None:
            stmt = stmt.where(ReliabilityWindow.pattern_id == pattern_id)
        row = self.db.scalar(stmt.order_by(ReliabilityWindow.window_start.desc()).limit(1))
        if row is None:
            return {"status": "unknown", "samples": 0, "fidelity": None, "drift_score": 0.0}
        return {
            "status": row.status,
            "samples": row.sample_count,
            "fidelity": row.fidelity_sum / row.sample_count if row.sample_count else None,
            "drift_score": row.drift_score,
            "window_start": row.window_start.isoformat(),
        }
