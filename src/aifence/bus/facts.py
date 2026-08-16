# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .db_models import Contradiction, FactDependency, SemanticFact
from .information_flow import InformationFlowStore


def _now() -> datetime:
    return datetime.now(UTC)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _fact_id(workspace: str, subject: str, predicate: str, value: Any, source: str | None) -> str:
    raw = f"{workspace}\0{subject}\0{predicate}\0{_canonical(value)}\0{source or ''}".encode()
    return "F" + hashlib.sha256(raw).hexdigest()[:40]


class FactStore:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.flow = InformationFlowStore(db)

    def get(self, fact_id: str, *, workspace: str | None = None) -> SemanticFact | None:
        item = self.db.get(SemanticFact, fact_id)
        if item is not None and workspace is not None and item.workspace != workspace:
            return None
        return item

    def put(
        self,
        *,
        workspace: str,
        subject: str,
        predicate: str,
        object: Any,
        epistemic_type: str = "fact",
        source: str | None = None,
        confidence: float = 1.0,
        provenance: dict[str, Any] | None = None,
        depends_on: list[str] | None = None,
        sensitivity: list[str] | None = None,
    ) -> SemanticFact:
        ident = _fact_id(workspace, subject, predicate, object, source)
        existing = self.db.get(SemanticFact, ident)
        if existing is not None:
            if existing.status == "stale":
                existing.status = "active"
                existing.invalidated_at = None
            existing.confidence = max(existing.confidence, confidence)
            return existing
        item = SemanticFact(
            id=ident,
            workspace=workspace,
            subject=subject,
            predicate=predicate,
            object=object,
            epistemic_type=epistemic_type,
            source=source,
            confidence=confidence,
            provenance=provenance or {},
            sensitivity=sorted(set(sensitivity or [])),
        )
        self.db.add(item)
        self.db.flush()
        inherited = set(sensitivity or [])
        for parent_id in depends_on or []:
            parent = self.get(parent_id, workspace=workspace)
            if parent is None:
                raise KeyError(parent_id)
            inherited.update(parent.sensitivity or [])
            self.db.add(FactDependency(parent_fact_id=parent_id, child_fact_id=ident))
        item.sensitivity = sorted(inherited)
        self.flow.assign(workspace, "fact", ident, inherited)
        self.db.flush()
        self._detect_contradictions(item)
        return item

    def _detect_contradictions(self, item: SemanticFact) -> list[Contradiction]:
        others = list(
            self.db.scalars(
                select(SemanticFact).where(
                    SemanticFact.workspace == item.workspace,
                    SemanticFact.subject == item.subject,
                    SemanticFact.predicate == item.predicate,
                    SemanticFact.status.in_(["active", "contradicted"]),
                    SemanticFact.id != item.id,
                )
            )
        )
        created: list[Contradiction] = []
        for other in others:
            if _canonical(other.object) == _canonical(item.object):
                continue
            left, right = sorted([item.id, other.id])
            existing = self.db.scalar(
                select(Contradiction).where(
                    Contradiction.left_fact_id == left,
                    Contradiction.right_fact_id == right,
                )
            )
            if existing is None:
                existing = Contradiction(
                    id="X" + uuid.uuid4().hex,
                    workspace=item.workspace,
                    left_fact_id=left,
                    right_fact_id=right,
                )
                self.db.add(existing)
                created.append(existing)
            item.status = "contradicted"
            other.status = "contradicted"
        self.db.flush()
        return created

    def contradictions(self, fact_id: str) -> list[Contradiction]:
        return list(
            self.db.scalars(
                select(Contradiction).where(
                    or_(Contradiction.left_fact_id == fact_id, Contradiction.right_fact_id == fact_id),
                    Contradiction.status == "open",
                )
            )
        )

    def resolve_contradiction(self, contradiction_id: str, winner_fact_id: str, note: str = "") -> Contradiction:
        item = self.db.get(Contradiction, contradiction_id)
        if item is None:
            raise KeyError(contradiction_id)
        if winner_fact_id not in {item.left_fact_id, item.right_fact_id}:
            raise ValueError("winner must be one of the contradictory facts")
        loser_id = item.right_fact_id if winner_fact_id == item.left_fact_id else item.left_fact_id
        winner = self.db.get(SemanticFact, winner_fact_id)
        loser = self.db.get(SemanticFact, loser_id)
        if winner:
            winner.status = "active"
        if loser:
            loser.status = "stale"
            loser.invalidated_at = _now()
        item.status = "resolved"
        item.resolution = {"winner": winner_fact_id, "note": note}
        item.resolved_at = _now()
        if loser:
            self.invalidate(loser.id, reason="contradiction_resolved")
        return item

    def invalidate(self, fact_id: str, *, reason: str = "source_changed") -> list[str]:
        root = self.db.get(SemanticFact, fact_id)
        if root is None:
            raise KeyError(fact_id)
        invalidated: list[str] = []
        queue = [fact_id]
        seen: set[str] = set()
        while queue:
            current_id = queue.pop(0)
            if current_id in seen:
                continue
            seen.add(current_id)
            current = self.db.get(SemanticFact, current_id)
            if current is None:
                continue
            current.status = "stale"
            current.invalidated_at = _now()
            prov = dict(current.provenance or {})
            prov["invalidation_reason"] = reason
            current.provenance = prov
            invalidated.append(current_id)
            children = list(
                self.db.scalars(
                    select(FactDependency.child_fact_id).where(FactDependency.parent_fact_id == current_id)
                )
            )
            queue.extend(children)
        self.db.flush()
        return invalidated

    def response(self, item: SemanticFact) -> dict[str, Any]:
        return {
            "id": item.id,
            "subject": item.subject,
            "predicate": item.predicate,
            "object": item.object,
            "epistemic_type": item.epistemic_type,
            "source": item.source,
            "confidence": item.confidence,
            "status": item.status,
            "sensitivity": item.sensitivity,
            "contradictions": [c.id for c in self.contradictions(item.id)],
        }
