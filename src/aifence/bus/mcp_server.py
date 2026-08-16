# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

from typing import Any, Literal, cast

from .a2a_adapter import pack_data_part, unpack_data_part
from .bus import SemanticBus
from .codec import SageCodec
from .compiler import compile_content
from .config import get_settings
from .conformance import run_tck, run_wire_fuzz
from .db import SessionLocal, init_db
from .economics import run_sage_economics_benchmark
from .evals import run_eval
from .knowledge import KnowledgeStore
from .patterns import PatternStore
from .protocol_spec import SAGE_PROTOCOL, SAGE_WIRE_VERSION
from .references import ReferenceStore
from .schemas import (
    Budget,
    Capabilities,
    EconomicsBenchmarkRequest,
    EncodeRequest,
    EvalCase,
    EvalRequest,
    Provenance,
    StatePatchRequest,
)
from .state import StateStore


def build_server() -> Any:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Install SAGE with the 'mcp' extra: pip install '.[mcp]'") from exc

    mcp = FastMCP(
        "SAGE",
        instructions=(
            "Use sage_send/sage_receive as the default communication transport. "
            "SAGE automatically applies receiver-aware deltas, refs, budgets, semantic codes, "
            "provenance and caching. Resolve refs only when required. Use sage_explain to inspect "
            "why information was compressed or referenced."
        ),
        stateless_http=True,
        json_response=True,
        host="0.0.0.0",
        port=8080,
    )
    settings = get_settings()

    @mcp.tool()
    def sage_send(
        content: Any,
        receiver: str,
        sender: str | None = None,
        act: str = "report",
        budget_tokens: int | None = None,
        workspace: str = "default",
        run_id: str | None = None,
        source_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Send through SAGE's receiver-aware, budget-constrained semantic transport."""
        with SessionLocal() as db:
            codec = SageCodec(db, settings)
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

    @mcp.tool()
    def sage_receive(
        wire: dict[str, Any],
        receiver: str,
        workspace: str = "default",
        resolve_refs: bool = False,
    ) -> dict[str, Any]:
        """Receive a compact SAGE wire packet and acknowledge receiver knowledge."""
        with SessionLocal() as db:
            codec = SageCodec(db, settings)
            packet = codec.expand(wire)
            return codec.decode(
                packet,
                resolve_refs,
                receiver=receiver,
                workspace=workspace,
                acknowledge=True,
            ).model_dump()

    @mcp.tool()
    def sage_explain(packet_id: str) -> dict[str, Any]:
        """Explain why SAGE selected refs, deltas, semantic codes, cache or fallback behavior."""
        from sqlalchemy import select

        from .db_models import MessageAudit

        with SessionLocal() as db:
            item = db.scalar(select(MessageAudit).where(MessageAudit.packet_id == packet_id))
            if item is None:
                raise ValueError(f"unknown packet: {packet_id}")
            return {
                "packet_id": item.packet_id,
                "strategy": item.strategy,
                "decisions": item.decisions,
                "provenance": item.provenance,
                "input_bytes": item.input_bytes,
                "output_bytes": item.output_bytes,
                "estimated_tokens": item.estimated_tokens,
                "budget_tokens": item.budget_tokens,
                "task_success": item.task_success,
            }

    @mcp.tool()
    def sage_handoff(
        content: Any,
        receiver: str,
        sender: str | None = None,
        workspace: str = "default",
        run_id: str | None = None,
        correlation_id: str | None = None,
        priority: int = 0,
        ttl_seconds: int | None = None,
        budget_tokens: int | None = None,
    ) -> dict[str, Any]:
        """Compress and durably enqueue a framework-neutral agent-to-agent handoff."""
        with SessionLocal() as db:
            item = SemanticBus(db, settings).handoff(
                receiver=receiver,
                content=content,
                sender=sender,
                workspace=workspace,
                run_id=run_id,
                correlation_id=correlation_id,
                priority=priority,
                ttl_seconds=ttl_seconds,
                budget_tokens=budget_tokens,
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

    @mcp.tool()
    def sage_poll(
        receiver: str,
        workspace: str = "default",
        limit: int = 20,
        claim: bool = True,
        budget_tokens: int | None = None,
    ) -> list[dict[str, Any]]:
        """Pull pending SAGE handoffs for this agent identity."""
        with SessionLocal() as db:
            items = SemanticBus(db, settings).pull(
                receiver=receiver, workspace=workspace, limit=limit, claim=claim, budget_tokens=budget_tokens
            )
            if claim:
                db.commit()
            return [
                {
                    "message_id": item.id,
                    "packet_id": item.packet_id,
                    "sender": item.sender,
                    "correlation_id": item.correlation_id,
                    "wire": item.wire,
                    "strategy": item.strategy,
                }
                for item in items
            ]

    @mcp.tool()
    def sage_ack(message_id: str, receiver: str, workspace: str = "default") -> dict[str, Any]:
        """Acknowledge a pulled SAGE handoff and update receiver knowledge."""
        with SessionLocal() as db:
            item = SemanticBus(db, settings).ack(
                message_id, receiver=receiver, workspace=workspace
            )
            db.commit()
            return {"message_id": item.id, "status": item.status}

    @mcp.tool()
    def sage_a2a_pack(wire: dict[str, Any]) -> dict[str, Any]:
        """Wrap a SAGE packet as an A2A 1.0 DataPart."""
        return pack_data_part(wire)

    @mcp.tool()
    def sage_a2a_unpack(part: dict[str, Any]) -> dict[str, Any]:
        """Extract a SAGE packet from an A2A 1.0 DataPart."""
        return {"wire": unpack_data_part(part)}

    @mcp.tool()
    def sage_encode(
        content: Any,
        sender: str | None = None,
        receiver: str | None = None,
        act: str = "report",
        base_state: str | None = None,
        auto_learn: bool = True,
        include_metrics: bool = False,
    ) -> dict[str, Any]:
        """Encode information into SAGE. Prefer sage_send for automatic receiver-aware transport."""
        with SessionLocal() as db:
            codec = SageCodec(db, settings)
            result = codec.encode(
                EncodeRequest(
                    content=content,
                    sender=sender,
                    receiver=receiver,
                    act=act,
                    base_state=base_state,
                    auto_learn=auto_learn,
                )
            )
            if include_metrics:
                return result.model_dump()
            return {"packet_id": result.packet.id, "wire": codec.compact(result.packet)}

    @mcp.tool()
    def sage_decode(packet: dict[str, Any], resolve_refs: bool = False) -> dict[str, Any]:
        """Decode a canonical SAGE 0.2 wire packet."""
        with SessionLocal() as db:
            codec = SageCodec(db, settings)
            parsed = codec.expand(packet)
            return codec.decode(parsed, resolve_refs, receiver=parsed.receiver).model_dump()

    @mcp.tool()
    def sage_store(
        value: Any,
        workspace: str = "default",
        owner: str | None = None,
        acl: list[str] | None = None,
        allowed_paths: list[str] | None = None,
        tier: str = "warm",
        ttl_seconds: int | None = None,
        encrypt: bool = False,
    ) -> dict[str, Any]:
        """Store reusable information with ACL, tier, TTL and optional AES-GCM encryption."""
        with SessionLocal() as db:
            item = ReferenceStore(db, settings).put(
                value,
                workspace=workspace,
                owner=owner,
                acl=acl or [],
                allowed_paths=allowed_paths or [],
                tier=tier,
                ttl_seconds=ttl_seconds,
                encrypt=encrypt,
            )
            grant = ReferenceStore(db, settings).grant_metadata(item.id, actor=owner, workspace=workspace)
            db.commit()
            return {"ref": item.id, "byte_size": item.byte_size, "tier": grant.tier, "encrypted": item.ciphertext is not None, "expires_at": grant.expires_at.isoformat() if grant.expires_at else None}

    @mcp.tool()
    def sage_resolve(ref: str, actor: str | None = None, workspace: str = "default", fields: list[str] | None = None) -> dict[str, Any]:
        """Resolve authorized fields from a content-addressed ref only when needed."""
        with SessionLocal() as db:
            store = ReferenceStore(db, settings)
            item = store.get(ref, actor=actor, workspace=workspace)
            if item is None:
                raise ValueError(f"unknown reference: {ref}")
            grant = store.grant_metadata(item.id, actor=actor, workspace=workspace)
            return {"ref": item.id, "media_type": item.media_type, "byte_size": item.byte_size, "tier": grant.tier, "value": store.resolve(ref, actor=actor, workspace=workspace, fields=fields)}

    @mcp.tool()
    def sage_memory_policy(
        ref: str,
        actor: str | None = None,
        workspace: str = "default",
        tier: str | None = None,
        ttl_seconds: int | None = None,
        invalidate: bool = False,
    ) -> dict[str, Any]:
        """Promote/demote memory tiers, update TTL, or invalidate an owned reference."""
        with SessionLocal() as db:
            item = ReferenceStore(db, settings).policy(
                ref,
                actor=actor,
                workspace=workspace,
                tier=tier,
                ttl_seconds=ttl_seconds,
                invalidate=invalidate,
            )
            db.commit()
            grant = ReferenceStore(db, settings).grant_metadata(item.id, actor=actor, workspace=workspace)
            return {"ref": item.id, "tier": grant.tier, "invalidated": grant.invalidated_at is not None}

    @mcp.tool()
    def sage_register(
        canonical: str,
        description: str = "",
        codebook: str | None = None,
        aliases: list[str] | None = None,
    ) -> dict[str, Any]:
        """Register a deliberate semantic concept and optional aliases in a namespace."""
        from .codebook import Codebook

        with SessionLocal() as db:
            cb = Codebook(db, settings)
            item = cb.register(codebook or settings.codebook, canonical, description, aliases or [])
            db.commit()
            return {
                "code": item.code,
                "version": item.version,
                "canonical": item.canonical,
                "description": item.description,
                "codebook": item.codebook,
                "embedding_space": item.embedding_space,
            }

    @mcp.tool()
    def sage_deprecate(code: str, replacement_code: str | None = None) -> dict[str, Any]:
        """Deprecate a semantic code and optionally redirect it to a replacement code."""
        from .codebook import Codebook

        with SessionLocal() as db:
            item = Codebook(db, settings).deprecate(code, replacement_code)
            db.commit()
            return {"code": code, "status": item.status, "version": item.version, "replacement": replacement_code}

    @mcp.tool()
    def sage_state(value: Any, workspace: str = "default", created_by: str | None = None) -> dict[str, Any]:
        """Create/deduplicate immutable content-addressed shared state."""
        with SessionLocal() as db:
            item = StateStore(db).create(value, workspace=workspace, created_by=created_by)
            db.commit()
            return {"state": item.id, "revision": item.revision, "value": item.payload}

    @mcp.tool()
    def sage_get_state(state: str, workspace: str = "default") -> dict[str, Any]:
        """Resolve shared state by content-addressed ID."""
        with SessionLocal() as db:
            item = StateStore(db).get(state, workspace=workspace)
            if item is None:
                raise ValueError(f"unknown state: {state}")
            return {"state": item.id, "revision": item.revision, "parent": item.parent_id, "value": item.payload}

    @mcp.tool()
    def sage_delta(base: str, value: Any, mode: str = "target", workspace: str = "default") -> dict[str, Any]:
        """Create immutable target state plus lossless JSON Patch delta from a known base."""
        req = StatePatchRequest(
            base=base,
            value=value,
            mode=cast(Literal["target", "patch"], mode),
            workspace=workspace,
        )
        with SessionLocal() as db:
            item, delta = StateStore(db).transition(req.base, req.value, is_patch=req.mode == "patch", workspace=workspace)
            db.commit()
            return {"state": item.id, "revision": item.revision, "delta": delta, "value": item.payload}

    @mcp.tool()
    def sage_replay(run_id: str) -> dict[str, Any]:
        """Replay the exact packet history and decisions for a multi-agent run."""
        from sqlalchemy import select

        from .db_models import MessageAudit

        with SessionLocal() as db:
            items = list(db.scalars(select(MessageAudit).where(MessageAudit.run_id == run_id).order_by(MessageAudit.created_at, MessageAudit.id)))
            return {"run_id": run_id, "packets": [{"packet_id": x.packet_id, "packet": x.packet, "strategy": x.strategy, "decisions": x.decisions} for x in items]}

    @mcp.tool()
    def sage_negotiate(
        receiver: str,
        known_codes: list[str] | None = None,
        codebook: str | None = None,
        max_packet_bytes: int = 8192,
        supports_refs: bool = True,
        supports_deltas: bool = True,
        supports_patterns: bool = True,
        workspace: str = "default",
    ) -> dict[str, Any]:
        """Negotiate protocol/capabilities and synchronize receiver codebook knowledge."""
        from .codebook import Codebook

        with SessionLocal() as db:
            cb = Codebook(db, settings)
            cb_name = codebook or settings.codebook
            caps = Capabilities(
                codebooks=[cb_name],
                max_packet_bytes=min(max_packet_bytes, settings.max_packet_bytes),
                supports_refs=supports_refs,
                supports_deltas=supports_deltas,
                supports_patterns=supports_patterns,
            )
            KnowledgeStore(db).update_capabilities(receiver, caps.model_dump(), workspace)
            missing = [
                {"code": c.code, "version": c.version, "canonical": c.canonical, "description": c.description}
                for c in cb.all_chain(cb_name)
                if c.code not in set(known_codes or [])
            ]
            pattern_store = PatternStore(db, settings, cb)
            missing_patterns = [pattern_store.response(p) for p in pattern_store.list(cb_name, status="active")] if supports_patterns else []
            db.commit()
            return {
                "protocol": "sage/0.2",
                "codebook": cb_name,
                "codebook_chain": cb.namespace_chain(cb_name),
                "embedding_space": cb.embedding_space,
                "fingerprint": cb.fingerprint(cb_name),
                "capabilities": caps.model_dump(),
                "missing": missing[:500],
                "missing_patterns": missing_patterns[:500],
            }

    @mcp.tool()
    def sage_patterns(codebook: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        """List learned higher-order patterns and their lifecycle/effectiveness metrics."""
        with SessionLocal() as db:
            store = PatternStore(db, settings)
            return [store.response(item) for item in store.list(codebook or settings.codebook, status=status)]

    @mcp.tool()
    def sage_pattern_candidates(codebook: str | None = None) -> list[dict[str, Any]]:
        """List recurring pattern candidates that have not yet reached shadow status."""
        with SessionLocal() as db:
            items = PatternStore(db, settings).candidates(codebook or settings.codebook)
            return [
                {
                    "codebook": item.codebook,
                    "signature": item.signature,
                    "canonical": item.canonical,
                    "composition": item.composition,
                    "occurrence_count": item.occurrence_count,
                    "estimated_savings_bytes": item.estimated_savings_bytes,
                    "semantic_variance": item.semantic_variance,
                }
                for item in items
            ]

    @mcp.tool()
    def sage_observe_patterns(content: Any, codebook: str | None = None, source_ids: list[str] | None = None, source_trust: float = 0.5, trust_scope: str = "session") -> list[dict[str, Any]]:
        """Mine a payload for recurring higher-order semantic patterns without sending it."""
        with SessionLocal() as db:
            store = PatternStore(db, settings)
            items = store.observe_units(
                codebook or settings.codebook,
                compile_content(content)[: settings.max_message_atoms],
                source_ids=source_ids,
                trust_score=source_trust,
                trust_scope=trust_scope,
            )
            db.commit()
            return [store.response(item) for item in items]

    @mcp.tool()
    def sage_set_pattern_status(pattern_id: str, status: str) -> dict[str, Any]:
        """Manually change a learned pattern lifecycle state for operations/testing."""
        with SessionLocal() as db:
            store = PatternStore(db, settings)
            item = store.set_status(pattern_id, status)
            db.commit()
            return store.response(item)

    @mcp.tool()
    def sage_eval(cases: list[dict[str, Any]], budget_tokens: int = 1200) -> dict[str, Any]:
        """Run offline semantic-fidelity and communication-efficiency evaluation."""
        parsed = EvalRequest(cases=[EvalCase.model_validate(c) for c in cases], budget_tokens=budget_tokens)
        with SessionLocal() as db:
            return run_eval(db, settings, parsed)


    @mcp.tool()
    def sage_protocol_info() -> dict[str, Any]:
        """Return the frozen SAGE protocol/wire version exposed by this adapter."""
        return {"protocol": SAGE_PROTOCOL, "wire_version": SAGE_WIRE_VERSION, "adapter": "mcp"}

    @mcp.tool()
    def sage_tck() -> dict[str, Any]:
        """Run the installed SAGE 0.2 conformance vectors."""
        return run_tck().as_dict()

    @mcp.tool()
    def sage_benchmark_economics(request: dict[str, Any]) -> dict[str, Any]:
        """Benchmark model-token/cost economics; exact counting requires a configured exact tokenizer."""
        parsed = EconomicsBenchmarkRequest.model_validate(request)
        with SessionLocal() as db:
            return run_sage_economics_benchmark(db, settings, parsed)

    @mcp.tool()
    def sage_pack_latent(vector: list[float], space: str) -> dict[str, Any]:
        """Quantize/package a custom model-provided latent vector."""
        from .latent import pack_latent
        return pack_latent(vector, space).model_dump()

    @mcp.tool()
    def sage_unpack_latent(packet: dict[str, Any]) -> dict[str, Any]:
        """Validate/reconstruct a SAGE latent packet for a compatible custom model worker."""
        from .latent import unpack_latent
        from .schemas import LatentPacket
        parsed = LatentPacket.model_validate(packet)
        return {"space": parsed.space, "vector": unpack_latent(parsed)}

    @mcp.tool()
    def sage_inspect(packet_id: str) -> dict[str, Any]:
        """Inspect SAGE compression waterfall, semantic loss, refs, and learned patterns."""
        from .inspector import Inspector
        with SessionLocal() as db:
            return Inspector(db).packet(packet_id)

    @mcp.tool()
    def sage_pattern_counterfactual(pattern_id: str, full_success: float, compressed_success: float, semantic_fidelity: float, receiver: str = "*", model: str = "*", task_family: str = "*", workspace: str = "default") -> dict[str, Any]:
        """Record paired full-vs-compressed behavior for shadow pattern validation."""
        with SessionLocal() as db:
            store = PatternStore(db, settings)
            item = store.record_counterfactual(pattern_id, full_success=full_success, compressed_success=compressed_success, semantic_fidelity=semantic_fidelity, receiver=receiver, model=model, task_family=task_family, workspace=workspace)
            db.commit()
            return store.response(item)

    @mcp.tool()
    def sage_forward_refs(receiver: str, refs: list[str], sender: str | None = None, workspace: str = "default") -> dict[str, Any]:
        """Zero-copy handoff of existing content-addressed references."""
        with SessionLocal() as db:
            item = SemanticBus(db, settings).forward_refs(receiver=receiver, refs=refs, sender=sender, workspace=workspace)
            db.commit()
            return {"message_id": item.id, "packet_id": item.packet_id, "wire": item.wire, "strategy": item.strategy}

    @mcp.tool()
    def sage_fact(subject: str, predicate: str, object: Any, epistemic_type: str = "fact", source: str | None = None, confidence: float = 1.0, workspace: str = "default", depends_on: list[str] | None = None) -> dict[str, Any]:
        """Store an epistemically typed fact with contradiction and dependency tracking."""
        from .facts import FactStore
        with SessionLocal() as db:
            store = FactStore(db)
            item = store.put(workspace=workspace, subject=subject, predicate=predicate, object=object, epistemic_type=epistemic_type, source=source, confidence=confidence, depends_on=depends_on or [])
            db.commit()
            return store.response(item)

    @mcp.tool()
    def sage_fact_invalidate(fact_id: str, reason: str = "source_changed") -> dict[str, Any]:
        """Causally invalidate a fact and every fact derived from it."""
        from .facts import FactStore
        with SessionLocal() as db:
            ids = FactStore(db).invalidate(fact_id, reason=reason)
            db.commit()
            return {"invalidated": ids}

    @mcp.tool()
    def sage_contradiction_resolve(contradiction_id: str, winner_fact_id: str, note: str = "") -> dict[str, Any]:
        """Resolve an explicit semantic contradiction and invalidate loser dependencies."""
        from .facts import FactStore
        with SessionLocal() as db:
            item = FactStore(db).resolve_contradiction(contradiction_id, winner_fact_id, note)
            db.commit()
            return {"contradiction_id": item.id, "status": item.status, "resolution": item.resolution}

    @mcp.tool()
    def sage_subscribe(agent: str, concepts: list[str], workspace: str = "default") -> dict[str, Any]:
        """Subscribe an agent to semantic concepts on the SAGE bus."""
        from .routing import SemanticPubSub
        with SessionLocal() as db:
            item = SemanticPubSub(db, settings).subscribe(workspace=workspace, agent=agent, concepts=concepts)
            db.commit()
            return {"subscription_id": item.id}

    @mcp.tool()
    def sage_publish(content: Any, sender: str | None = None, workspace: str = "default", confidence: float = 1.0) -> dict[str, Any]:
        """Publish semantic content only to interested subscribers."""
        from .routing import SemanticPubSub
        with SessionLocal() as db:
            recipients = SemanticPubSub(db, settings).publish(content=content, workspace=workspace, sender=sender, confidence=confidence)
            db.commit()
            return {"recipients": recipients}

    @mcp.tool()
    def sage_register_agent(agent: str, capabilities: list[str], authority: list[str] | None = None, workspace: str = "default", cost_score: float = 1.0, latency_ms: float = 0.0, available: bool = True, concepts: list[str] | None = None) -> dict[str, Any]:
        """Register an agent for capability/knowledge-aware semantic routing."""
        from .routing import SemanticRouter
        with SessionLocal() as db:
            item = SemanticRouter(db, settings).register_agent(workspace=workspace, agent=agent, capabilities=capabilities, authority=authority or [], cost_score=cost_score, latency_ms=latency_ms, available=available, metadata={"concepts": concepts or []})
            db.commit()
            return {"agent": item.agent, "capabilities": item.capabilities, "authority": item.authority, "available": item.available}

    @mcp.tool()
    def sage_route(content: Any, capability: str | None = None, authority: str | None = None, workspace: str = "default", sender: str | None = None) -> dict[str, Any]:
        """Choose the cheapest qualified agent while preferring existing relevant knowledge."""
        from .routing import SemanticRouter
        with SessionLocal() as db:
            winner, score = SemanticRouter(db, settings).choose(content=content, workspace=workspace, capability=capability, authority=authority, exclude={sender} if sender else None)
            return {"agent": winner.agent, "score": score}

    @mcp.tool()
    def sage_pattern_gc(codebook: str | None = None) -> dict[str, int]:
        """Cool and retire learned patterns that no longer justify their vocabulary cost."""
        with SessionLocal() as db:
            result = PatternStore(db, settings).garbage_collect(codebook)
            db.commit()
            return result

    @mcp.tool()
    def sage_pattern_promote_namespace(pattern_id: str, target_codebook: str) -> dict[str, Any]:
        """Promote a high-utility local pattern into a parent semantic namespace."""
        with SessionLocal() as db:
            store = PatternStore(db, settings)
            item = store.promote_namespace(pattern_id, target_codebook)
            db.commit()
            return store.response(item)

    @mcp.tool()
    def sage_federation_register_peer(name: str, base_url: str, public_key_b64: str, allowed_namespaces: list[str], workspace: str = "default") -> dict[str, Any]:
        """Register a signed federated SAGE peer and its allowed semantic namespaces."""
        from .federation import FederationStore
        with SessionLocal() as db:
            item = FederationStore(db, settings).register_peer(workspace=workspace, name=name, base_url=base_url, public_key_b64=public_key_b64, allowed_namespaces=allowed_namespaces)
            db.commit()
            return {"peer_id": item.id, "name": item.name, "allowed_namespaces": item.allowed_namespaces}

    @mcp.tool()
    def sage_federation_export(namespace: str, source: str = "local") -> dict[str, Any]:
        """Export selected concepts/patterns as a namespace-scoped signed federation bundle."""
        from .federation import FederationStore
        with SessionLocal() as db:
            return FederationStore(db, settings).export_bundle(namespace, source=source)

    @mcp.tool()
    def sage_federation_import(bundle: dict[str, Any], workspace: str = "default") -> dict[str, int]:
        """Import a signed, namespace-authorized federation bundle for local revalidation."""
        from .federation import FederationStore
        with SessionLocal() as db:
            result = FederationStore(db, settings).import_bundle(bundle, workspace=workspace)
            db.commit()
            return result

    @mcp.tool()
    def sage_conform(fuzz_iterations: int = 0) -> dict[str, Any]:
        """Run the installed TCK plus optional deterministic malformed-wire checks."""
        tck = run_tck()
        fuzz = run_wire_fuzz(fuzz_iterations) if fuzz_iterations else None
        return {"ok": tck.ok and (fuzz.ok if fuzz else True), "tck": tck.as_dict(), "wire_fuzz": fuzz.as_dict() if fuzz else None}

    return mcp


def run() -> None:
    settings = get_settings()
    if settings.auth_required:
        raise RuntimeError("sage-mcp direct mode has no HTTP auth wrapper; run sage-api and use /mcp instead")
    init_db()
    build_server().run(transport="streamable-http")


if __name__ == "__main__":
    run()
