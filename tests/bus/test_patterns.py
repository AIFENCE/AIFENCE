from __future__ import annotations

from sqlalchemy import select

from aifence.bus.codec import AifenceCodec
from aifence.bus.config import Settings
from aifence.bus.db import SessionLocal
from aifence.bus.db_models import LearnedPattern, MesaifenceAudit, PatternCandidate
from aifence.bus.patterns import PatternStore
from aifence.bus.schemas import EncodeRequest


def pattern_settings(**overrides):
    values = dict(
        auth_required=False,
        max_inline_bytes=100_000,
        default_token_budget=100_000,
        max_packet_bytes=100_000,
        promotion_min_count=999,
        pattern_learning_enabled=True,
        pattern_string_constants_enabled=True,
        pattern_min_components=2,
        pattern_max_components=4,
        pattern_max_observations_per_message=32,
        pattern_candidate_min_count=2,
        pattern_min_savings_bytes=0,
        pattern_shadow_min_samples=2,
        pattern_shadow_min_success=0.9,
        pattern_auto_activate=True,
        pattern_counterfactual_required=True,
        pattern_counterfactual_min_samples=1,
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


def test_pattern_lifecycle_candidate_shadow_active_and_wire_use():
    with SessionLocal() as db:
        settings = pattern_settings()
        codec = AifenceCodec(db, settings)
        content = {"cause": "test_failure", "deployment": "blocked"}

        codec.encode(EncodeRequest(content=content, auto_learn=True, record_learning=True, use_cache=False))
        assert db.scalar(select(PatternCandidate)) is not None

        second = codec.encode(EncodeRequest(content=content, auto_learn=True, record_learning=True, use_cache=False))
        pattern = db.scalar(select(LearnedPattern).where(LearnedPattern.status == "shadow"))
        assert pattern is not None
        audit2 = db.scalar(select(MesaifenceAudit).where(MesaifenceAudit.packet_id == second.packet.id))
        assert audit2 is not None
        assert any(
            d.get("action") == "pattern_shadow_match" and d.get("pattern_id") == pattern.pattern_id
            for d in audit2.decisions
        )

        store = PatternStore(db, settings, codec.codebook)
        store.record_feedback(audit2.decisions, 1.0)
        db.commit()
        assert pattern.status == "shadow"

        third = codec.encode(EncodeRequest(content=content, auto_learn=True, record_learning=True, use_cache=False))
        audit3 = db.scalar(select(MesaifenceAudit).where(MesaifenceAudit.packet_id == third.packet.id))
        assert audit3 is not None
        store.record_feedback(audit3.decisions, 1.0)
        db.commit()
        assert pattern.status == "validated"
        store.record_counterfactual(
            pattern.pattern_id, full_success=1.0, compressed_success=1.0, semantic_fidelity=1.0, validation_id="test-holdout"
        )
        db.commit()
        assert pattern.status == "active"

        fourth = codec.encode(EncodeRequest(content=content, auto_learn=True, record_learning=True, use_cache=False))
        assert len(fourth.packet.atoms) == 1
        assert fourth.packet.atoms[0].code is not None
        audit4 = db.scalar(select(MesaifenceAudit).where(MesaifenceAudit.packet_id == fourth.packet.id))
        assert audit4 is not None
        assert any(
            d.get("action") == "pattern_code" and d.get("pattern_id") == pattern.pattern_id
            for d in audit4.decisions
        )

        decoded = codec.decode(fourth.packet)
        assert decoded.concepts[0]["pattern"]["pattern_id"] == pattern.pattern_id
        assert decoded.concepts[0]["pattern"]["composition"] == pattern.composition


def test_pattern_slots_preserve_dynamic_values():
    with SessionLocal() as db:
        settings = pattern_settings(pattern_candidate_min_count=1, pattern_shadow_min_samples=1)
        codec = AifenceCodec(db, settings)
        store = codec.patterns
        content = {"attempt": 10, "latency_ms": 125.5}

        first = codec.encode(EncodeRequest(content=content, use_cache=False))
        pattern = db.scalar(select(LearnedPattern).where(LearnedPattern.status == "shadow"))
        assert pattern is not None
        audit = db.scalar(select(MesaifenceAudit).where(MesaifenceAudit.packet_id == first.packet.id))
        assert audit is not None
        store.record_feedback(audit.decisions, 1.0)
        db.commit()
        assert pattern.status == "validated"
        store.record_counterfactual(
            pattern.pattern_id, full_success=1.0, compressed_success=1.0, semantic_fidelity=1.0, validation_id="test-holdout"
        )
        db.commit()
        assert pattern.status == "active"

        second_content = {"attempt": 11, "latency_ms": 200.25}
        second = codec.encode(EncodeRequest(content=second_content, use_cache=False))
        assert len(second.packet.atoms) == 1
        assert second.packet.atoms[0].has_literal is True
        assert second.packet.atoms[0].literal == [11, 200.25]

        decoded = codec.decode(second.packet)
        assert decoded.concepts[0]["pattern"]["bindings"] == [11, 200.25]
        assert pattern.semantic_variance > 0.0


def test_pattern_status_can_be_manually_controlled():
    with SessionLocal() as db:
        settings = pattern_settings(pattern_candidate_min_count=1)
        codec = AifenceCodec(db, settings)
        codec.encode(EncodeRequest(content={"a": "x", "b": "y"}, use_cache=False))
        pattern = db.scalar(select(LearnedPattern))
        assert pattern is not None
        store = codec.patterns
        store.set_status(pattern.pattern_id, "active")
        assert pattern.status == "active"
        old_version = pattern.version
        store.set_status(pattern.pattern_id, "retired")
        assert pattern.status == "retired"
        assert pattern.version == old_version + 1


def test_pattern_rest_surface_is_end_to_end():
    from fastapi.testclient import TestClient

    from aifence.bus.main import app

    content = {"cause": "test_failure", "deployment": "blocked"}
    with TestClient(app) as client:
        promoted = []
        for _ in range(4):
            response = client.post("/v1/patterns/observe", json={"content": content, "source_ids": [f"source-{_}"], "source_trust": 0.9, "trust_scope": "workspace"})
            assert response.status_code == 200
            if response.json():
                promoted = response.json()
        assert promoted
        pattern_id = promoted[0]["pattern_id"]
        assert promoted[0]["status"] == "shadow"

        listed = client.get("/v1/patterns")
        assert listed.status_code == 200
        assert any(item["pattern_id"] == pattern_id for item in listed.json())

        activated = client.post(f"/v1/patterns/{pattern_id}/status", json={"status": "active"})
        assert activated.status_code == 200
        assert activated.json()["status"] == "active"

        sent = client.post(
            "/v1/send",
            json={"content": content, "receiver": "planner", "use_cache": False},
        )
        assert sent.status_code == 200
        body = sent.json()
        assert len(body["packet"]["atoms"]) == 1
        explain = client.get(f"/v1/explain/{body['packet']['id']}")
        assert explain.status_code == 200
        assert any(
            item.get("action") == "pattern_code" and item.get("pattern_id") == pattern_id
            for item in explain.json()["decisions"]
        )


def test_negotiation_syncs_active_pattern_definitions_and_can_disable_patterns():
    from fastapi.testclient import TestClient

    from aifence.bus.main import app

    content = {"cause": "test_failure", "deployment": "blocked"}
    with TestClient(app) as client:
        promoted = []
        for _ in range(4):
            promoted = client.post("/v1/patterns/observe", json={"content": content, "source_ids": [f"source-{_}"], "source_trust": 0.9, "trust_scope": "workspace"}).json() or promoted
        pattern_id = promoted[0]["pattern_id"]
        client.post(f"/v1/patterns/{pattern_id}/status", json={"status": "active"})

        negotiated = client.post(
            "/v1/negotiate",
            json={
                "receiver": "planner",
                "capabilities": {"protocol_versions": ["aifence/0.2"], "supports_patterns": True},
            },
        )
        assert negotiated.status_code == 200
        body = negotiated.json()
        assert body["negotiated"]["supports_patterns"] is True
        assert any(item["pattern_id"] == pattern_id for item in body["missing_patterns"])

        disabled = client.post(
            "/v1/negotiate",
            json={
                "receiver": "plain-agent",
                "capabilities": {"protocol_versions": ["aifence/0.2"], "supports_patterns": False},
            },
        )
        assert disabled.status_code == 200
        assert disabled.json()["missing_patterns"] == []

        sent = client.post(
            "/v1/send",
            json={"content": content, "receiver": "plain-agent", "use_cache": False},
        )
        assert sent.status_code == 200
        assert len(sent.json()["packet"]["atoms"]) == 2


def test_runtime_pattern_api_round_trip():
    from aifence.bus.runtime import AifenceRuntime

    runtime = AifenceRuntime(pattern_settings(pattern_candidate_min_count=1))
    promoted = runtime.observe_patterns({"a": "x", "b": "y"})
    assert promoted and promoted[0]["status"] == "shadow"
    pattern_id = promoted[0]["pattern_id"]
    activated = runtime.set_pattern_status(pattern_id, "active")
    assert activated["status"] == "active"
    assert any(item["pattern_id"] == pattern_id for item in runtime.patterns(status="active"))
