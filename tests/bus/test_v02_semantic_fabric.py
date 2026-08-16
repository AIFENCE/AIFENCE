from __future__ import annotations

import base64
from datetime import UTC, datetime, timedelta

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from sqlalchemy import func, select

from aifence.bus.bus import SemanticBus
from aifence.bus.codec import SageCodec
from aifence.bus.compiler import compile_content
from aifence.bus.config import Settings
from aifence.bus.db import SessionLocal
from aifence.bus.db_models import (
    Contradiction,
    FactDependency,
    LearnedPattern,
    MessageAudit,
    PatternEdge,
    Reference,
    ReferenceGrant,
)
from aifence.bus.facts import FactStore
from aifence.bus.federation import FederationStore
from aifence.bus.inspector import Inspector
from aifence.bus.patterns import PatternStore, composition_for
from aifence.bus.references import ReferenceAccessError, ReferenceStore
from aifence.bus.routing import SemanticPubSub, SemanticRouter
from aifence.bus.schemas import EncodeRequest
from aifence.bus.signing import derive_public_key


def _b64u(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def signing_keys() -> tuple[str, str]:
    private = Ed25519PrivateKey.generate()
    raw = private.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    private_b64 = _b64u(raw)
    return private_b64, derive_public_key(private_b64)


def pattern_settings(**overrides) -> Settings:
    values = dict(
        auth_required=False,
        max_inline_bytes=100_000,
        max_packet_bytes=100_000,
        default_token_budget=100_000,
        promotion_min_count=999,
        pattern_learning_enabled=True,
        pattern_string_constants_enabled=True,
        pattern_min_components=2,
        pattern_max_components=2,
        pattern_candidate_min_count=1,
        pattern_min_savings_bytes=0,
        pattern_shadow_min_samples=1,
        pattern_shadow_min_success=0.9,
        pattern_auto_activate=True,
        pattern_holdout_min_samples=1,
        pattern_holdout_min_sources=1,
        pattern_holdout_min_fidelity=0.9,
        pattern_utility_min_score=0.0,
        semantic_cache_enabled=False,
        pattern_min_source_diversity=1,
        pattern_min_trust_score=0.0,
        pattern_max_source_share=1.0,
        pattern_session_min_sources=1,
        pattern_project_min_sources=1,
        pattern_workspace_min_sources=1,
        pattern_domain_min_sources=1,
        pattern_federation_min_sources=1,
    )
    values.update(overrides)
    return Settings(**values)


def test_semantic_firewall_preserves_critical_unknowns_and_epistemic_type():
    with SessionLocal() as db:
        settings = Settings(
            auth_required=False,
            semantic_firewall_enabled=True,
            critical_semantic_threshold=0.999,
            promotion_min_count=999,
            max_inline_bytes=100_000,
            semantic_cache_enabled=False,
        )
        codec = SageCodec(db, settings)
        result = codec.encode(
            EncodeRequest(
                content={"permission": "must not delete", "amount": 10000, "prediction": "likely outage"},
                use_cache=False,
            )
        )
        by_path = {atom.path: atom for atom in result.packet.atoms}
        assert by_path["$.permission"].has_literal is True
        assert by_path["$.permission"].literal == "must not delete"
        assert by_path["$.amount"].literal == 10000
        assert any(atom.epistemic_type in {"prediction", "constraint", "fact"} for atom in result.packet.atoms)
        audit = db.scalar(select(MessageAudit).where(MessageAudit.packet_id == result.packet.id))
        assert audit is not None and audit.semantic_loss_score == 0.0


def test_fact_contradictions_epistemics_resolution_and_causal_invalidation():
    with SessionLocal() as db:
        facts = FactStore(db)
        source = facts.put(
            workspace="w",
            subject="deploy-1",
            predicate="status",
            object="approved",
            epistemic_type="observation",
            source="db",
            confidence=0.999,
        )
        derived = facts.put(
            workspace="w",
            subject="deploy-1",
            predicate="can_ship",
            object=True,
            epistemic_type="inference",
            source="planner",
            confidence=0.9,
            depends_on=[source.id],
        )
        other = facts.put(
            workspace="w",
            subject="deploy-1",
            predicate="status",
            object="rejected",
            epistemic_type="fact",
            source="policy",
            confidence=1.0,
        )
        conflict = db.scalar(select(Contradiction))
        assert conflict is not None
        assert source.status == "contradicted"
        assert other.status == "contradicted"
        assert db.scalar(select(func.count(FactDependency.id))) == 1

        facts.resolve_contradiction(conflict.id, other.id, note="policy is authoritative")
        db.flush()
        assert other.status == "active"
        assert source.status == "stale"
        assert derived.status == "stale"
        assert conflict.status == "resolved"


def test_content_addressed_refs_selective_grants_and_zero_copy_forward():
    with SessionLocal() as db:
        settings = Settings(auth_required=False)
        refs = ReferenceStore(db, settings)
        value = {"case": {"status": "open", "note": "visible"}, "card": {"pan": "secret"}}
        a = refs.put(value, workspace="w", owner="agent-a", acl=["agent-a"], allowed_paths=["case"])
        b = refs.put(value, workspace="other", owner="agent-x", acl=["agent-x"])
        assert a.id == b.id
        assert a.id.startswith("sage:sha256:")
        assert db.scalar(select(func.count(Reference.id))) == 1
        assert db.scalar(select(func.count(ReferenceGrant.id))) == 2
        assert refs.resolve(a.id, actor="agent-a", workspace="w", fields=["case.status"]) == {"case.status": "open"}
        with pytest.raises(ReferenceAccessError):
            refs.resolve(a.id, actor="agent-a", workspace="w", fields=["card.pan"])

        msg = SemanticBus(db, settings).forward_refs(receiver="agent-b", refs=[a.id], sender="agent-a", workspace="w")
        assert msg.strategy == "zero_copy"
        assert db.scalar(select(func.count(Reference.id))) == 1
        assert refs.resolve(a.id, actor="agent-b", workspace="w", fields=["case.note"]) == {"case.note": "visible"}
        with pytest.raises(ReferenceAccessError):
            refs.resolve(a.id, actor="agent-b", workspace="w", fields=["card.pan"])


def test_signed_packets_verify_and_tamper_fails_closed():
    private_key, public_key = signing_keys()
    with SessionLocal() as db:
        signer = SageCodec(
            db,
            Settings(
                auth_required=False,
                packet_signing_private_key=private_key,
                packet_signing_key_id="test-key",
                semantic_cache_enabled=False,
            ),
        )
        sent = signer.encode(EncodeRequest(content={"status": "approved"}, use_cache=False))
        wire = signer.compact(sent.packet)
        assert wire["g"]["alg"] == "Ed25519"

        verifier = SageCodec(
            db,
            Settings(
                auth_required=False,
                packet_signing_public_key=public_key,
                require_packet_signatures=True,
                semantic_cache_enabled=False,
            ),
        )
        assert verifier.expand(wire).id == sent.packet.id
        tampered = dict(wire)
        tampered["a"] = "different"
        with pytest.raises(ValueError, match="signature"):
            verifier.expand(tampered)


def test_counterfactual_receiver_fidelity_controls_pattern_use_and_gc():
    with SessionLocal() as db:
        settings = pattern_settings(
            pattern_counterfactual_required=True,
            pattern_counterfactual_min_samples=1,
            pattern_receiver_min_fidelity=0.95,
            pattern_gc_cooling_days=1,
            pattern_gc_retire_days=2,
        )
        codec = SageCodec(db, settings)
        content = {"deployment": "blocked", "failure": "tests"}
        codec.encode(EncodeRequest(content=content, use_cache=False))
        pattern = db.scalar(select(LearnedPattern))
        assert pattern is not None and pattern.status == "shadow"

        codec.patterns.record_counterfactual(
            pattern.pattern_id,
            full_success=1.0,
            compressed_success=1.0,
            semantic_fidelity=1.0,
            receiver="good",
            model="model-good",
            validation_id="good-holdout",
        )
        assert pattern.status == "active"
        good = codec.encode(EncodeRequest(content=content, receiver="good", receiver_model="model-good", use_cache=False))
        assert len(good.packet.atoms) == 1

        codec.patterns.record_counterfactual(
            pattern.pattern_id,
            full_success=1.0,
            compressed_success=0.0,
            semantic_fidelity=0.2,
            receiver="bad",
            model="model-bad",
            validation_id="bad-holdout",
        )
        bad = codec.encode(EncodeRequest(content=content, receiver="bad", receiver_model="model-bad", use_cache=False))
        assert len(bad.packet.atoms) == 2
        assert codec.patterns.receiver_fidelity(pattern, "bad", "model-bad") == pytest.approx(0.2)
        assert codec.patterns.utility_score(pattern) >= 0.0

        old = datetime.now(UTC) - timedelta(days=3)
        pattern.last_used_at = old
        gc = codec.patterns.garbage_collect()
        assert gc["patterns_cooling"] == 1
        pattern.last_used_at = old
        gc = codec.patterns.garbage_collect()
        assert gc["patterns_retired"] == 1


def test_recursive_pattern_graph_and_namespace_promotion():
    with SessionLocal() as db:
        settings = pattern_settings(
            codebook="software.python.project",
            pattern_namespace_promotion_min_utility=0.0,
            pattern_recursive_learning_enabled=True,
        )
        store = PatternStore(db, settings)
        units = compile_content({"a": 1, "b": 2, "c": 3, "d": 4})
        left_comp = composition_for(units[:2], allow_string_constants=True)
        right_comp = composition_for(units[2:], allow_string_constants=True)
        left = store.observe(settings.codebook, left_comp, source_ids=["source-a"], trust_score=1.0)
        right = store.observe(settings.codebook, right_comp, source_ids=["source-b"], trust_score=1.0)
        assert left is not None and right is not None
        store.set_status(left.pattern_id, "active")
        store.set_status(right.pattern_id, "active")
        recursive = store._observe_recursive(settings.codebook, units, source_ids=["source-a", "source-b"], trust_score=1.0)
        assert recursive is not None
        assert recursive.relation_structure["recursive"] is True
        assert set(recursive.relation_structure["children"]) == {left.pattern_id, right.pattern_id}
        assert db.scalar(select(func.count(PatternEdge.id))) >= 2
        recursive.status = "active"
        recursive.occurrence_count = 100
        recursive.estimated_savings_bytes = 1000
        promoted = store.promote_namespace(recursive.pattern_id, "software.python")
        assert promoted.codebook == "software.python"
        assert promoted.relation_structure["promoted_from"] == recursive.pattern_id


def test_inspector_reports_compression_waterfall():
    with SessionLocal() as db:
        settings = Settings(auth_required=False, max_inline_bytes=32, semantic_cache_enabled=False)
        codec = SageCodec(db, settings)
        result = codec.encode(EncodeRequest(content={"blob": "x" * 4000}, run_id="run-inspect", use_cache=False))
        report = Inspector(db).packet(result.packet.id or "")
        assert report["original_bytes"] > report["sent_bytes"]
        assert report["waterfall"]["ref_bytes_avoided"] > 0
        run = Inspector(db).run("run-inspect")
        assert run["packets"][0]["packet_id"] == result.packet.id


def test_semantic_pubsub_and_knowledge_routing():
    with SessionLocal() as db:
        settings = Settings(auth_required=False, routing_cost_weight=1.0, routing_latency_weight=0.0, routing_knowledge_weight=5.0)
        pubsub = SemanticPubSub(db, settings)
        pubsub.subscribe(workspace="w", agent="security", concepts=["severity"], filters={"environment": "prod"})
        pubsub.subscribe(workspace="w", agent="billing", concepts=["payment"])
        recipients = pubsub.publish(content={"severity": "critical", "environment": "prod"}, workspace="w", sender="monitor")
        assert recipients == ["security"]
        bus = SemanticBus(db, settings)
        assert bus.pending_count(receiver="security", workspace="w") == 1
        assert bus.pending_count(receiver="billing", workspace="w") == 0

        router = SemanticRouter(db, settings)
        router.register_agent(
            workspace="w", agent="expert", capabilities=["triage"], authority=["prod"],
            cost_score=3.0, latency_ms=100, available=True, metadata={"concepts": ["severity", "environment"]},
        )
        router.register_agent(
            workspace="w", agent="cheap", capabilities=["triage"], authority=["prod"],
            cost_score=1.0, latency_ms=10, available=True, metadata={"concepts": []},
        )
        winner, detail = router.choose(content={"severity": "critical", "environment": "prod"}, workspace="w", capability="triage", authority="prod")
        assert winner.agent == "expert"
        assert detail["knowledge"] > 0


def test_federated_bundle_is_signed_and_namespace_scoped():
    private_key, public_key = signing_keys()
    with SessionLocal() as db:
        settings = Settings(auth_required=False, packet_signing_private_key=private_key, packet_signing_key_id="local")
        source = FederationStore(db, settings)
        source.codebook.register("software.python", "pytest_failure", "pytest test failure")
        bundle = source.export_bundle("software.python", source="peer-a")
        assert bundle.get("g")

        target = FederationStore(db, Settings(auth_required=False))
        target.register_peer(
            workspace="w", name="peer-a", base_url="https://peer-a.invalid", public_key_b64=public_key,
            allowed_namespaces=["software"],
        )
        result = target.import_bundle(bundle, workspace="w")
        assert result["concepts_imported"] >= 1
        denied = dict(bundle)
        denied["namespace"] = "finance"
        with pytest.raises(PermissionError):
            target.import_bundle(denied, workspace="w")
