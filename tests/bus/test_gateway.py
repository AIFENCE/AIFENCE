from __future__ import annotations

import base64
import secrets
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from aifence.bus.codebook import Codebook
from aifence.bus.codec import AifenceCodec
from aifence.bus.config import Settings
from aifence.bus.db import SessionLocal
from aifence.bus.main import app
from aifence.bus.references import ReferenceAccessError, ReferenceExpiredError, ReferenceStore
from aifence.bus.schemas import Budget, EncodeRequest


def test_receiver_aware_send_automatically_uses_delta_after_ack():
    with SessionLocal() as db:
        codec = AifenceCodec(db, Settings(auth_required=False, database_url="sqlite://"))
        first = codec.encode(
            EncodeRequest(
                content={"project": "phoenix", "failed": 3, "blocked": True, "context": "x" * 1000},
                sender="test-agent",
                receiver="deploy-agent",
                use_cache=False,
            )
        )
        assert first.packet.meta["state"].startswith("S")
        codec.decode(first.packet, receiver="deploy-agent", acknowledge=True)
        second = codec.encode(
            EncodeRequest(
                content={"project": "phoenix", "failed": 1, "blocked": True, "context": "x" * 1000},
                sender="test-agent",
                receiver="deploy-agent",
                use_cache=False,
            )
        )
        assert second.strategy == "delta"
        assert second.packet.delta == [{"op": "replace", "path": "/failed", "value": 1}]


def test_compact_wire_round_trip_preserves_provenance():
    with SessionLocal() as db:
        codec = AifenceCodec(db, Settings(auth_required=False, database_url="sqlite://"))
        result = codec.encode(
            EncodeRequest(
                content={"screen_damage": True},
                sender="support",
                receiver="resolution",
                provenance={"source_ids": ["email:42"], "confidence": 0.9, "derivation": "extract"},
                use_cache=False,
            )
        )
        wire = codec.compact(result.packet)
        rebuilt = codec.expand(wire)
        assert rebuilt.sender == "support"
        assert rebuilt.receiver == "resolution"
        assert rebuilt.prov.source_ids == ["email:42"]
        assert rebuilt.prov.confidence == 0.9
        assert rebuilt.meta["state"].startswith("S")


def test_semantic_cache_reuses_safe_packet_template_but_new_packet_id():
    with SessionLocal() as db:
        settings = Settings(auth_required=False, database_url="sqlite://")
        codec = AifenceCodec(db, settings)
        codec.codebook.register("global", "refund_requested")
        db.commit()
        first = codec.encode(
            EncodeRequest(content="refund requested", sender="a", receiver="b")
        )
        second = codec.encode(
            EncodeRequest(content="refund requested", sender="a", receiver="b")
        )
        assert first.cache_hit is False
        assert second.cache_hit is True
        assert first.packet.id != second.packet.id
        assert second.packet.atoms[0].code is not None


def test_private_encrypted_reference_acl_ttl_and_tier_policy():
    key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    settings = Settings(
        auth_required=False,
        database_url="sqlite://",
        ref_encryption_key=key,
    )
    with SessionLocal() as db:
        store = ReferenceStore(db, settings)
        item = store.put(
            {"secret": "value"},
            owner="agent-a",
            acl=["agent-b"],
            encrypt=True,
            tier="cold",
            ttl_seconds=60,
        )
        db.commit()
        assert item.payload is None
        assert item.ciphertext
        assert store.value(store.get(item.id, actor="agent-b")) == {"secret": "value"}
        with pytest.raises(ReferenceAccessError):
            store.get(item.id, actor="agent-c")
        store.policy(item.id, actor="agent-a", workspace="default", tier="hot")
        assert item.tier == "hot"
        item.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        db.commit()
        with pytest.raises(ReferenceExpiredError):
            store.get(item.id, actor="agent-b")


def test_concept_namespace_alias_and_deprecation_redirect():
    with SessionLocal() as db:
        settings = Settings(auth_required=False, database_url="sqlite://")
        cb = Codebook(db, settings)
        core = cb.register("core", "payment")
        specific = cb.register("finance.billing", "refund_requested", aliases=["money_back_requested"])
        replacement = cb.register("finance.billing", "refund_intent")
        db.commit()
        assert cb.match("finance.billing", "payment").concept.code == core.code
        assert cb.exact("finance.billing", "money back requested").code == specific.code
        cb.deprecate(specific.code, replacement.code)
        db.commit()
        assert cb.get_by_code(specific.code).code == replacement.code


def test_budget_falls_back_to_reference_without_dropping_content():
    with SessionLocal() as db:
        codec = AifenceCodec(db, Settings(auth_required=False, database_url="sqlite://"))
        content = {"blob": "x" * 5000, "critical": "must-preserve"}
        result = codec.encode(
            EncodeRequest(
                content=content,
                sender="a",
                receiver="b",
                budget=Budget(max_tokens=100),
                use_cache=False,
            )
        )
        assert result.strategy == "reference"
        decoded = codec.decode(result.packet, resolve_refs=True, receiver="b")
        assert decoded.references[0]["value"] == content


def test_explain_replay_eval_and_native_gate_api():
    with TestClient(app) as client:
        sent = client.post(
            "/v1/transport/send",
            json={
                "content": {"x": 1},
                "sender": "a",
                "receiver": "b",
                "run_id": "run-1",
                "provenance": {"source_ids": ["source:1"]},
            },
        )
        assert sent.status_code == 200
        packet_id = sent.json()["packet_id"]
        explanation = client.get(f"/v1/explain/{packet_id}")
        assert explanation.status_code == 200
        assert explanation.json()["decisions"]
        replay = client.get("/v1/runs/run-1/replay")
        assert replay.status_code == 200
        assert replay.json()["packets"][0]["packet_id"] == packet_id
        report = client.post(
            "/v1/evals/run",
            json={"cases": [{"content": {"blob": "x" * 5000}}], "budget_tokens": 100},
        )
        assert report.status_code == 200
        assert report.json()["summary"]["semantic_fidelity"] == 1.0
        blocked = client.post("/v1/native-token-gate", json={"eval_score": 0.5})
        allowed = client.post("/v1/native-token-gate", json={"eval_score": 0.999})
        assert blocked.json()["allowed"] is False
        assert allowed.json()["allowed"] is True


def test_eval_reports_lossless_plain_transport_baselines():
    with TestClient(app) as client:
        response = client.post(
            "/v1/evals/run",
            json={"cases": [{"content": {"blob": "abc" * 1000, "n": 42}}]},
        )
        assert response.status_code == 200
        baselines = response.json()["baselines"]
        assert baselines["raw_json_bytes"] > 0
        assert baselines["raw_msgpack_bytes"] > 0
        assert baselines["raw_gzip_json_bytes"] > 0
        assert baselines["aifence_bus_msgpack_bytes"] > 0


def test_integration_config_hermes_release_asset() -> None:
    from aifence.bus.integrations import config_for

    cfg = config_for("hermes", "http://aifence:8080", "hermes-a", "team")
    assert cfg.config["workspace"] == "team"
    assert "AIFENCE_BUS_WORKSPACE=team" in cfg.files["env"]
    assert any("aifence-hermes-plugin-v0.2.7.zip" in command for command in cfg.commands)


def test_integration_config_openclaw_release_asset() -> None:
    from aifence.bus.integrations import config_for

    cfg = config_for("openclaw", "http://aifence:8080", "claw-a", "team")
    assert cfg.config["workspace"] == "team"
    assert "AIFENCE_BUS_WORKSPACE=team" in cfg.files["env"]
    assert any("aifence-agent-openclaw-aifence-0.2.7.tgz" in command for command in cfg.commands)
