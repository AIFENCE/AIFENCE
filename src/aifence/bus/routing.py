# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import math
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .bus import SemanticBus
from .compiler import compile_content
from .config import Settings
from .db_models import AgentCapability, Subscription
from .knowledge import KnowledgeStore


class SemanticRouter:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings
        self.knowledge = KnowledgeStore(db)

    def register_agent(
        self,
        *,
        workspace: str,
        agent: str,
        capabilities: list[str],
        authority: list[str],
        cost_score: float,
        latency_ms: float,
        available: bool,
        metadata: dict[str, Any],
    ) -> AgentCapability:
        item = self.db.scalar(select(AgentCapability).where(AgentCapability.workspace == workspace, AgentCapability.agent == agent))
        if item is None:
            item = AgentCapability(workspace=workspace, agent=agent)
            self.db.add(item)
        item.capabilities = sorted(set(capabilities))
        item.authority = sorted(set(authority))
        item.cost_score = cost_score
        item.latency_ms = latency_ms
        item.available = available
        item.details = metadata
        self.db.flush()
        return item

    def choose(
        self,
        *,
        content: Any,
        workspace: str = "default",
        capability: str | None = None,
        authority: str | None = None,
        exclude: set[str] | None = None,
    ) -> tuple[AgentCapability, dict[str, float]]:
        stmt = select(AgentCapability).where(AgentCapability.workspace == workspace, AgentCapability.available.is_(True))
        candidates = list(self.db.scalars(stmt))
        exclude = exclude or set()
        candidates = [c for c in candidates if c.agent not in exclude]
        if capability:
            candidates = [c for c in candidates if capability in c.capabilities]
        if authority:
            candidates = [c for c in candidates if authority in c.authority]
        if not candidates:
            raise LookupError("no available agent satisfies routing constraints")
        semantic_terms = {unit.canonical for unit in compile_content(content)}
        scored: list[tuple[float, AgentCapability, dict[str, float]]] = []
        for candidate in candidates:
            known = set(self.knowledge.known_codes(candidate.agent, workspace))
            meta_terms = set(candidate.details.get("concepts", []))
            overlap = len(semantic_terms & meta_terms) / max(1, len(semantic_terms))
            knowledge_score = overlap + min(1.0, math.log1p(len(known)) / 10.0)
            score = (
                self.settings.routing_cost_weight * candidate.cost_score
                + self.settings.routing_latency_weight * candidate.latency_ms
                - self.settings.routing_knowledge_weight * knowledge_score
            )
            detail = {"score": score, "knowledge": knowledge_score, "cost": candidate.cost_score, "latency_ms": candidate.latency_ms}
            scored.append((score, candidate, detail))
        scored.sort(key=lambda row: (row[0], row[1].agent))
        _, winner, detail = scored[0]
        return winner, detail


class SemanticPubSub:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings

    def subscribe(
        self,
        *,
        workspace: str,
        agent: str,
        concepts: list[str],
        filters: dict[str, Any] | None = None,
        min_confidence: float = 0.0,
    ) -> Subscription:
        item = Subscription(
            id="SUB" + uuid.uuid4().hex,
            workspace=workspace,
            agent=agent,
            concepts=sorted(set(concepts)),
            filters=filters or {},
            min_confidence=min_confidence,
        )
        self.db.add(item)
        self.db.flush()
        return item

    @staticmethod
    def _filters_match(content: Any, filters: dict[str, Any]) -> bool:
        if not filters:
            return True
        if not isinstance(content, dict):
            return False
        return all(content.get(k) == v for k, v in filters.items())

    def publish(
        self,
        *,
        content: Any,
        workspace: str,
        sender: str | None = None,
        confidence: float = 1.0,
        source_ids: list[str] | None = None,
    ) -> list[str]:
        concepts = {unit.canonical for unit in compile_content(content)}
        subscriptions = list(self.db.scalars(select(Subscription).where(Subscription.workspace == workspace, Subscription.active.is_(True))))
        recipients: list[str] = []
        bus = SemanticBus(self.db, self.settings)
        for sub in subscriptions:
            if confidence < sub.min_confidence:
                continue
            if sub.concepts and not (concepts & set(sub.concepts)):
                continue
            if not self._filters_match(content, sub.filters):
                continue
            bus.handoff(receiver=sub.agent, content=content, sender=sender, act="publish", workspace=workspace, source_ids=source_ids)
            recipients.append(sub.agent)
        self.db.flush()
        return recipients
