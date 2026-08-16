# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

from typing import Any

from sqlalchemy import select

from .bus import SemanticBus
from .codec import SageCodec
from .compiler import compile_content
from .config import Settings, get_settings
from .db import SessionLocal
from .db_models import MessageAudit
from .facts import FactStore
from .federation import FederationStore
from .inspector import Inspector
from .patterns import PatternStore
from .references import ReferenceStore
from .routing import SemanticPubSub, SemanticRouter
from .schemas import Budget, EncodeRequest, Provenance


class SageRuntime:
    """High-level transport façade for agent runtimes.

    Agent frameworks should depend on this interface rather than manually deciding when
    to use semantic IDs, refs, deltas or cache entries.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def send(
        self,
        *,
        receiver: str,
        content: Any,
        sender: str | None = None,
        act: str = "report",
        budget_tokens: int | None = None,
        workspace: str = "default",
        run_id: str | None = None,
        source_ids: list[str] | None = None,
        receiver_model: str | None = None,
    ) -> dict[str, Any]:
        with SessionLocal() as db:
            codec = SageCodec(db, self.settings)
            result = codec.encode(
                EncodeRequest(
                    content=content,
                    sender=sender,
                    receiver=receiver,
                    act=act,
                    workspace=workspace,
                    run_id=run_id,
                    budget=Budget(max_tokens=budget_tokens) if budget_tokens else None,
                    provenance=Provenance(source_ids=source_ids or [], producer=sender),
                    receiver_model=receiver_model,
                )
            )
            return {
                "packet_id": result.packet.id,
                "wire": codec.compact(result.packet),
                "strategy": result.strategy,
                "estimated_tokens": result.estimated_tokens,
                "wire_bytes": result.output_bytes_msgpack,
                "cache_hit": result.cache_hit,
            }

    def receive(
        self,
        *,
        receiver: str,
        wire: dict[str, Any],
        workspace: str = "default",
        resolve_refs: bool = False,
    ) -> dict[str, Any]:
        with SessionLocal() as db:
            codec = SageCodec(db, self.settings)
            packet = codec.expand(wire)
            return codec.decode(
                packet,
                resolve_refs,
                receiver=receiver,
                workspace=workspace,
                acknowledge=True,
            ).model_dump()


    def handoff(
        self,
        *,
        receiver: str,
        content: Any,
        sender: str | None = None,
        workspace: str = "default",
        run_id: str | None = None,
        correlation_id: str | None = None,
        priority: int = 0,
        ttl_seconds: int | None = None,
        budget_tokens: int | None = None,
        source_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Compress and durably enqueue a cross-agent handoff."""
        with SessionLocal() as db:
            item = SemanticBus(db, self.settings).handoff(
                receiver=receiver,
                content=content,
                sender=sender,
                workspace=workspace,
                run_id=run_id,
                correlation_id=correlation_id,
                priority=priority,
                ttl_seconds=ttl_seconds,
                budget_tokens=budget_tokens,
                source_ids=source_ids,
            )
            db.commit()
            return {
                "message_id": item.id,
                "packet_id": item.packet_id,
                "wire": item.wire,
                "strategy": item.strategy,
                "estimated_tokens": item.estimated_tokens,
                "wire_bytes": item.wire_bytes,
            }

    def poll(
        self,
        *,
        receiver: str,
        workspace: str = "default",
        limit: int = 20,
        claim: bool = True,
        budget_tokens: int | None = None,
    ) -> list[dict[str, Any]]:
        """Pull pending handoffs for a framework-local agent identity."""
        with SessionLocal() as db:
            items = SemanticBus(db, self.settings).pull(
                receiver=receiver, workspace=workspace, limit=limit, claim=claim, budget_tokens=budget_tokens
            )
            if claim:
                db.commit()
            return [
                {
                    "message_id": item.id,
                    "packet_id": item.packet_id,
                    "sender": item.sender,
                    "receiver": item.receiver,
                    "wire": item.wire,
                    "strategy": item.strategy,
                    "correlation_id": item.correlation_id,
                }
                for item in items
            ]

    def ack(self, message_id: str, *, receiver: str, workspace: str = "default") -> None:
        """Acknowledge delivery and update the receiver knowledge model."""
        with SessionLocal() as db:
            SemanticBus(db, self.settings).ack(message_id, receiver=receiver, workspace=workspace)
            db.commit()

    def memory_put(
        self,
        value: Any,
        *,
        workspace: str = "default",
        owner: str | None = None,
        acl: list[str] | None = None,
        allowed_paths: list[str] | None = None,
        tier: str = "warm",
        ttl_seconds: int | None = None,
        encrypt: bool = False,
    ) -> str:
        with SessionLocal() as db:
            item = ReferenceStore(db, self.settings).put(
                value,
                workspace=workspace,
                owner=owner,
                acl=acl or [],
                allowed_paths=allowed_paths or [],
                tier=tier,
                ttl_seconds=ttl_seconds,
                encrypt=encrypt,
            )
            db.commit()
            return item.id

    def memory_get(self, ref: str, *, actor: str | None = None, workspace: str = "default", fields: list[str] | None = None) -> Any:
        with SessionLocal() as db:
            store = ReferenceStore(db, self.settings)
            item = store.get(ref, actor=actor, workspace=workspace)
            if item is None:
                raise KeyError(ref)
            return store.resolve(ref, actor=actor, workspace=workspace, fields=fields)


    def forward_refs(self, *, receiver: str, refs: list[str], sender: str | None = None, workspace: str = "default", run_id: str | None = None, correlation_id: str | None = None) -> dict[str, Any]:
        """Zero-copy forward existing content-addressed refs to another agent."""
        with SessionLocal() as db:
            item = SemanticBus(db, self.settings).forward_refs(receiver=receiver, refs=refs, sender=sender, workspace=workspace, run_id=run_id, correlation_id=correlation_id)
            db.commit()
            return {"message_id": item.id, "packet_id": item.packet_id, "wire": item.wire, "strategy": item.strategy}

    def memory_grant(self, ref: str, *, workspace: str = "default", owner: str | None = None, acl: list[str] | None = None, allowed_paths: list[str] | None = None, tier: str = "warm", ttl_seconds: int | None = None) -> dict[str, Any]:
        with SessionLocal() as db:
            store = ReferenceStore(db, self.settings)
            grant = store.grant(ref, workspace=workspace, owner=owner, acl=acl or [], allowed_paths=allowed_paths or [], tier=tier, ttl_seconds=ttl_seconds)
            db.commit()
            return {"ref": ref, "workspace": grant.workspace, "owner": grant.owner, "acl": grant.acl, "allowed_paths": grant.allowed_paths, "tier": grant.tier}

    def explain(self, packet_id: str) -> dict[str, Any]:
        with SessionLocal() as db:
            item = db.scalar(select(MessageAudit).where(MessageAudit.packet_id == packet_id))
            if item is None:
                raise KeyError(packet_id)
            return {
                "packet_id": item.packet_id,
                "strategy": item.strategy,
                "decisions": item.decisions,
                "provenance": item.provenance,
                "cache_hit": item.cache_hit,
                "input_bytes": item.input_bytes,
                "output_bytes": item.output_bytes,
                "estimated_tokens": item.estimated_tokens,
            }


    def observe_patterns(
        self,
        content: Any,
        *,
        codebook: str | None = None,
        source_ids: list[str] | None = None,
        source_trust: float = 0.5,
        trust_scope: str = "session",
    ) -> list[dict[str, Any]]:
        """Mine recurring higher-order semantic templates without sending a packet."""
        with SessionLocal() as db:
            store = PatternStore(db, self.settings)
            promoted = store.observe_units(
                codebook or self.settings.codebook,
                compile_content(content)[: self.settings.max_message_atoms],
                source_ids=source_ids,
                trust_score=source_trust,
                trust_scope=trust_scope,
            )
            db.commit()
            return [store.response(item) for item in promoted]

    def patterns(self, *, codebook: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        """List learned patterns with lifecycle, savings, diversity and utility metrics."""
        with SessionLocal() as db:
            store = PatternStore(db, self.settings)
            return [store.response(item) for item in store.list(codebook or self.settings.codebook, status=status)]

    def pattern_candidates(self, *, codebook: str | None = None) -> list[dict[str, Any]]:
        """List recurring templates still below the shadow-promotion threshold."""
        with SessionLocal() as db:
            items = PatternStore(db, self.settings).candidates(codebook or self.settings.codebook)
            return [
                {
                    "codebook": item.codebook,
                    "signature": item.signature,
                    "canonical": item.canonical,
                    "composition": item.composition,
                    "relation_structure": item.relation_structure,
                    "occurrence_count": item.occurrence_count,
                    "estimated_savings_bytes": item.estimated_savings_bytes,
                    "semantic_variance": item.semantic_variance,
                    "trust_scope": item.trust_scope,
                    "source_diversity": item.source_diversity,
                    "dominant_source_share": item.dominant_source_share,
                    "trust_score": item.trust_score,
                }
                for item in items
            ]

    def set_pattern_status(self, pattern_id: str, status: str) -> dict[str, Any]:
        """Override a learned pattern lifecycle state."""
        with SessionLocal() as db:
            store = PatternStore(db, self.settings)
            item = store.set_status(pattern_id, status)
            db.commit()
            return store.response(item)

    def feedback(self, packet_id: str, task_success: float) -> dict[str, Any]:
        """Record task outcome and advance matching shadow-pattern validation."""
        if not 0.0 <= task_success <= 1.0:
            raise ValueError("task_success must be in [0, 1]")
        with SessionLocal() as db:
            item = db.scalar(select(MessageAudit).where(MessageAudit.packet_id == packet_id))
            if item is None:
                raise KeyError(packet_id)
            item.task_success = task_success
            store = PatternStore(db, self.settings)
            updated = store.record_feedback(item.decisions, task_success)
            responses = [store.response(pattern) for pattern in updated]
            db.commit()
            return {"packet_id": packet_id, "task_success": task_success, "patterns_updated": responses}


    def inspect(self, packet_id: str) -> dict[str, Any]:
        with SessionLocal() as db:
            return Inspector(db).packet(packet_id)

    def pattern_counterfactual(self, pattern_id: str, *, full_success: float, compressed_success: float, semantic_fidelity: float, receiver: str = "*", model: str = "*", task_family: str = "*", workspace: str = "default") -> dict[str, Any]:
        with SessionLocal() as db:
            store = PatternStore(db, self.settings)
            item = store.record_counterfactual(pattern_id, full_success=full_success, compressed_success=compressed_success, semantic_fidelity=semantic_fidelity, receiver=receiver, model=model, task_family=task_family, workspace=workspace)
            db.commit()
            return store.response(item)


    def pattern_promote_namespace(self, pattern_id: str, target_codebook: str) -> dict[str, Any]:
        with SessionLocal() as db:
            store = PatternStore(db, self.settings)
            item = store.promote_namespace(pattern_id, target_codebook)
            db.commit()
            return store.response(item)

    def pattern_gc(self, codebook: str | None = None) -> dict[str, int]:
        with SessionLocal() as db:
            result = PatternStore(db, self.settings).garbage_collect(codebook)
            db.commit()
            return result

    def fact_put(self, *, subject: str, predicate: str, object: Any, epistemic_type: str = "fact", source: str | None = None, confidence: float = 1.0, workspace: str = "default", depends_on: list[str] | None = None) -> dict[str, Any]:
        with SessionLocal() as db:
            store = FactStore(db)
            item = store.put(workspace=workspace, subject=subject, predicate=predicate, object=object, epistemic_type=epistemic_type, source=source, confidence=confidence, depends_on=depends_on or [])
            db.commit()
            return store.response(item)

    def fact_invalidate(self, fact_id: str, *, workspace: str = "default", reason: str = "source_changed") -> list[str]:
        with SessionLocal() as db:
            store = FactStore(db)
            if store.get(fact_id, workspace=workspace) is None:
                raise KeyError(fact_id)
            result = store.invalidate(fact_id, reason=reason)
            db.commit()
            return result


    def contradiction_resolve(self, contradiction_id: str, winner_fact_id: str, *, note: str = "") -> dict[str, Any]:
        with SessionLocal() as db:
            item = FactStore(db).resolve_contradiction(contradiction_id, winner_fact_id, note)
            db.commit()
            return {"contradiction_id": item.id, "status": item.status, "resolution": item.resolution}

    def subscribe(self, *, agent: str, concepts: list[str], workspace: str = "default", filters: dict[str, Any] | None = None, min_confidence: float = 0.0) -> str:
        with SessionLocal() as db:
            item = SemanticPubSub(db, self.settings).subscribe(workspace=workspace, agent=agent, concepts=concepts, filters=filters or {}, min_confidence=min_confidence)
            db.commit()
            return item.id

    def publish(self, content: Any, *, sender: str | None = None, workspace: str = "default", confidence: float = 1.0) -> list[str]:
        with SessionLocal() as db:
            recipients = SemanticPubSub(db, self.settings).publish(content=content, workspace=workspace, sender=sender, confidence=confidence)
            db.commit()
            return recipients

    def register_agent(self, *, agent: str, capabilities: list[str], authority: list[str] | None = None, workspace: str = "default", cost_score: float = 1.0, latency_ms: float = 0.0, available: bool = True, metadata: dict[str, Any] | None = None) -> None:
        with SessionLocal() as db:
            SemanticRouter(db, self.settings).register_agent(workspace=workspace, agent=agent, capabilities=capabilities, authority=authority or [], cost_score=cost_score, latency_ms=latency_ms, available=available, metadata=metadata or {})
            db.commit()

    def route(self, content: Any, *, capability: str | None = None, authority: str | None = None, workspace: str = "default", sender: str | None = None) -> dict[str, Any]:
        with SessionLocal() as db:
            winner, score = SemanticRouter(db, self.settings).choose(content=content, workspace=workspace, capability=capability, authority=authority, exclude={sender} if sender else None)
            return {"agent": winner.agent, "score": score}


    def federation_register_peer(self, *, name: str, base_url: str, public_key_b64: str, allowed_namespaces: list[str], workspace: str = "default", enabled: bool = True) -> dict[str, Any]:
        with SessionLocal() as db:
            item = FederationStore(db, self.settings).register_peer(workspace=workspace, name=name, base_url=base_url, public_key_b64=public_key_b64, allowed_namespaces=allowed_namespaces, enabled=enabled)
            db.commit()
            return {"peer_id": item.id, "name": item.name, "allowed_namespaces": item.allowed_namespaces, "enabled": item.enabled}

    def conform(self, *, fuzz_iterations: int = 0) -> dict[str, Any]:
        from .conformance import run_tck, run_wire_fuzz
        tck = run_tck()
        fuzz = run_wire_fuzz(fuzz_iterations) if fuzz_iterations else None
        return {"ok": tck.ok and (fuzz.ok if fuzz else True), "tck": tck.as_dict(), "wire_fuzz": fuzz.as_dict() if fuzz else None}

    def federation_export(self, namespace: str, *, source: str = "local") -> dict[str, Any]:
        with SessionLocal() as db:
            return FederationStore(db, self.settings).export_bundle(namespace, source=source)

    def federation_import(self, bundle: dict[str, Any], *, workspace: str = "default") -> dict[str, int]:
        with SessionLocal() as db:
            result = FederationStore(db, self.settings).import_bundle(bundle, workspace=workspace)
            db.commit()
            return result
