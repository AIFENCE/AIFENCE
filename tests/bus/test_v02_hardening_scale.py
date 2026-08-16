from __future__ import annotations

import base64
from datetime import UTC

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient
from sqlalchemy import select

from aifence.bus.bus import SemanticBus
from aifence.bus.codebook import Codebook
from aifence.bus.codebook_releases import CodebookReleaseStore
from aifence.bus.config import Settings
from aifence.bus.db import SessionLocal
from aifence.bus.db_models import BusMessage, OrderingCounter, StateCheckpoint
from aifence.bus.economics import score_observation
from aifence.bus.information_flow import InformationFlowStore
from aifence.bus.merkle import CodebookMerkle
from aifence.bus.reliability import ModelIdentityStore
from aifence.bus.state import StateStore


def _private_key() -> tuple[str, str]:
    key = Ed25519PrivateKey.generate()
    private = key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
    public = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)

    def _b64(raw: bytes) -> str:
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

    return _b64(private), _b64(public)


def test_ordering_idempotency_and_backpressure_are_deterministic():
    with SessionLocal() as db:
        settings = Settings(
            auth_required=False,
            pattern_learning_enabled=False,
            semantic_cache_enabled=False,
            max_pending_messages_per_workspace=3,
            backpressure_degraded_ratio=0.34,
            backpressure_throttled_ratio=0.9,
        )
        bus = SemanticBus(db, settings)
        one = bus.handoff(receiver="r", sender="s", content={"n": 1}, ordering_key="stream", idempotency_key="k1")
        replay = bus.handoff(receiver="r", sender="s", content={"n": 1}, ordering_key="stream", idempotency_key="k1")
        two = bus.handoff(receiver="r", sender="s", content={"n": 2}, ordering_key="stream", idempotency_key="k2")
        assert replay.id == one.id
        assert (one.sequence_no, two.sequence_no) == (1, 2)
        assert one.partition_key == two.partition_key
        assert db.scalar(select(OrderingCounter).where(OrderingCounter.ordering_key == "stream")).sequence_no == 2
        assert bus.backpressure()["state"] == "degraded"
        assert [m.sequence_no for m in db.scalars(select(BusMessage).order_by(BusMessage.sequence_no))] == [1, 2]



def test_agent_quota_failure_does_not_consume_workspace_quota():
    from aifence.bus.db_models import QuotaCounter
    from aifence.bus.resilience import QuotaExceededError

    with SessionLocal() as db:
        settings = Settings(
            auth_required=False,
            pattern_learning_enabled=False,
            semantic_cache_enabled=False,
            quota_handoffs_per_window=3,
            quota_handoffs_per_agent_window=1,
            max_pending_messages_per_workspace=100,
        )
        bus = SemanticBus(db, settings)
        bus.handoff(receiver="r", sender="a", content={"n": 1})
        try:
            bus.handoff(receiver="r", sender="a", content={"n": 2})
        except QuotaExceededError:
            pass
        else:
            raise AssertionError("second handoff from sender a must be rejected")
        bus.handoff(receiver="r", sender="b", content={"n": 3})
        bus.handoff(receiver="r", sender="c", content={"n": 4})
        workspace_counter = db.scalar(
            select(QuotaCounter).where(
                QuotaCounter.workspace == "default",
                QuotaCounter.resource == "handoff",
            )
        )
        assert workspace_counter is not None
        assert workspace_counter.used == 3
        try:
            bus.handoff(receiver="r", sender="d", content={"n": 5})
        except QuotaExceededError:
            pass
        else:
            raise AssertionError("workspace quota must reject the fourth successful handoff")





def test_partition_filtered_claim_only_returns_requested_shard():
    with SessionLocal() as db:
        settings = Settings(auth_required=False, pattern_learning_enabled=False, semantic_cache_enabled=False, bus_partition_count=64)
        bus = SemanticBus(db, settings)
        first = bus.handoff(receiver="r", sender="a", content={"n": 1}, partition_key="alpha")
        second = bus.handoff(receiver="r", sender="b", content={"n": 2}, partition_key="beta")
        assert first.partition_key != second.partition_key
        claimed = bus.pull(receiver="r", partition=first.partition_key, limit=10, claim=True)
        assert [item.id for item in claimed] == [first.id]
        remaining = bus.pull(receiver="r", limit=10, claim=False)
        assert second.id in {item.id for item in remaining}


def test_throttled_backpressure_rejects_new_work():
    from aifence.bus.resilience import BackpressureError

    with SessionLocal() as db:
        settings = Settings(
            auth_required=False,
            pattern_learning_enabled=False,
            semantic_cache_enabled=False,
            max_pending_messages_per_workspace=2,
            backpressure_degraded_ratio=0.25,
            backpressure_throttled_ratio=0.5,
        )
        bus = SemanticBus(db, settings)
        bus.handoff(receiver="r", sender="a", content={"n": 1})
        assert bus.backpressure()["state"] == "throttled"
        try:
            bus.handoff(receiver="r", sender="b", content={"n": 2})
        except BackpressureError as exc:
            assert exc.state == "throttled"
        else:
            raise AssertionError("throttled queue must reject new work")


def test_optional_learning_and_cache_failures_preserve_delivery(monkeypatch):
    from aifence.bus.cache import CacheStore
    from aifence.bus.codec import SageCodec
    from aifence.bus.patterns import PatternStore
    from aifence.bus.schemas import EncodeRequest

    with SessionLocal() as db:
        settings = Settings(auth_required=False, pattern_learning_enabled=True, semantic_cache_enabled=True)
        monkeypatch.setattr(PatternStore, "observe_units", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("learning unavailable")))
        monkeypatch.setattr(CacheStore, "get", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("cache unavailable")))
        monkeypatch.setattr(CacheStore, "put", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("cache unavailable")))
        result = SageCodec(db, settings).encode(EncodeRequest(content={"permission": "do not delete"}, sender="a", receiver="b"))
        assert result.packet.atoms or result.packet.refs
        audit = db.scalar(select(__import__("aifence.bus.db_models", fromlist=["MessageAudit"]).MessageAudit).where(__import__("aifence.bus.db_models", fromlist=["MessageAudit"]).MessageAudit.packet_id == result.packet.id))
        subsystems = {row.get("subsystem") for row in audit.decisions if row.get("action") == "optional_subsystem_fallback"}
        assert "pattern_learning" in subsystems
        assert "semantic_cache_read" in subsystems


def test_model_identity_changes_when_runtime_configuration_changes():
    with SessionLocal() as db:
        store = ModelIdentityStore(db)
        first = store.register(workspace="w", receiver="agent", provider="p", model="m", model_version="1", runtime="r", runtime_version="1", configuration={"temp": 0})
        second = store.register(workspace="w", receiver="agent", provider="p", model="m", model_version="1", runtime="r", runtime_version="2", configuration={"temp": 0})
        assert first.identity_hash != second.identity_hash
        assert first.active is False
        assert second.active is True


def test_merkle_and_signed_codebook_release_are_verifiable():
    private, public = _private_key()
    with SessionLocal() as db:
        settings = Settings(auth_required=False)
        book = Codebook(db, settings)
        book.register("software", "deployment_blocked")
        book.register("software", "test_failure")
        db.flush()
        manifest = CodebookMerkle(db).manifest("software")
        assert len(manifest.root) == 64
        store = CodebookReleaseStore(db)
        release = store.create("software", "2026.07.31.1", private, "release-key")
        repeated = store.create("software", "2026.07.31.1", private, "release-key")
        assert release.id == repeated.id
        assert release.signature == repeated.signature
        assert release.merkle_root == manifest.root
        assert CodebookReleaseStore.verify(release, public) is True



def test_merkle_diff_respects_nondefault_partition_width():
    with SessionLocal() as db:
        settings = Settings(auth_required=False)
        book = Codebook(db, settings)
        book.register("software", "deployment_blocked")
        db.flush()
        merkle = CodebookMerkle(db)
        local = merkle.manifest("software", partition_prefix=4)
        remote = {"root": "0" * 64, "partitions": {}, "entries": {}}
        diff = merkle.diff(local, remote)
        assert diff["equal"] is False
        assert diff["entries"] == ["concept:C00000001"]
        assert all(len(prefix) == 4 for prefix in diff["changed_partitions"])


def test_checkpoint_lookup_never_crosses_state_branches():
    with SessionLocal() as db:
        settings = Settings(auth_required=False, checkpoint_interval_revisions=2)
        states = StateStore(db, settings)
        root = states.create({"v": 0}, workspace="w")
        left, _ = states.transition(root.id, {"v": 1, "branch": "left"}, workspace="w")
        right, _ = states.transition(root.id, {"v": 1, "branch": "right"}, workspace="w")
        assert db.scalar(select(StateCheckpoint).where(StateCheckpoint.state_id == left.id)) is not None
        assert db.scalar(select(StateCheckpoint).where(StateCheckpoint.state_id == right.id)) is not None
        left2, _ = states.transition(left.id, {"v": 2, "branch": "left"}, workspace="w")
        plan = states.replay_plan(left2.id, workspace="w")
        assert plan["checkpoint_state"] == left.id
        assert right.id not in plan["states"]


def test_information_flow_labels_union_without_downgrade():
    with SessionLocal() as db:
        flow = InformationFlowStore(db)
        flow.assign(workspace="w", object_kind="fact", object_id="a", labels=["secret", "customer"])
        flow.assign(workspace="w", object_kind="fact", object_id="b", labels=["internal"])
        labels = flow.propagate(workspace="w", target_kind="inference", target_id="c", sources=[("fact", "a"), ("fact", "b")])
        assert set(labels) == {"secret", "customer", "internal"}


def test_economics_includes_infrastructure_cost_and_utility_per_bit():
    row = score_observation(
        {
            "strategy": "sage",
            "input_tokens": 100,
            "output_tokens": 10,
            "task_success": 1.0,
            "wire_bytes": 100,
            "provider_cost_usd": 0.01,
            "infrastructure_cost_usd": 0.002,
            "retrieval_cost_usd": 0.001,
            "retry_cost_usd": 0.003,
        },
        {"input_per_million": 999, "output_per_million": 999},
    )
    assert row["cost"] == 0.016
    assert row["task_utility_per_bit"] == 1 / 800


def test_http_write_idempotency_replays_same_response():
    from aifence.bus.main import app

    headers = {"X-Idempotency-Key": "state-create-1"}
    payload = {"value": {"status": "ready"}, "workspace": "default"}
    with TestClient(app) as client:
        first = client.post("/v1/states", json=payload, headers=headers)
        second = client.post("/v1/states", json=payload, headers=headers)
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.headers.get("x-sage-idempotent-replay") == "true"
    assert first.json() == second.json()



def test_http_write_idempotency_rejects_payload_change():
    from aifence.bus.main import app

    headers = {"X-Idempotency-Key": "state-conflict-1"}
    with TestClient(app) as client:
        first = client.post("/v1/states", json={"value": {"status": "ready"}, "workspace": "default"}, headers=headers)
        second = client.post("/v1/states", json={"value": {"status": "changed"}, "workspace": "default"}, headers=headers)
    assert first.status_code == 200
    assert second.status_code == 409


def test_holdout_activation_requires_distinct_validation_traffic():
    from aifence.bus.codec import SageCodec
    from aifence.bus.db_models import LearnedPattern
    from aifence.bus.schemas import EncodeRequest

    with SessionLocal() as db:
        settings = Settings(
            auth_required=False,
            learning_mode="managed",
            pattern_learning_enabled=True,
            pattern_string_constants_enabled=True,
            pattern_candidate_min_count=1,
            pattern_min_components=2,
            pattern_max_components=2,
            pattern_min_savings_bytes=0,
            pattern_utility_min_score=0.0,
            pattern_shadow_min_samples=1,
            pattern_shadow_min_success=0.0,
            pattern_counterfactual_min_samples=1,
            pattern_holdout_min_samples=3,
            pattern_holdout_min_sources=3,
            pattern_holdout_min_fidelity=0.99,
            pattern_min_source_diversity=1,
            pattern_session_min_sources=1,
            pattern_min_trust_score=0.0,
            pattern_max_source_share=1.0,
            semantic_cache_enabled=False,
        )
        codec = SageCodec(db, settings)
        result = codec.encode(EncodeRequest(content={"a": "x", "b": "y"}, sender="trainer", source_trust=1.0, use_cache=False))
        pattern = db.scalar(select(LearnedPattern))
        assert pattern is not None
        codec.patterns.record_feedback(next(a.decisions for a in db.query(__import__('aifence.bus.db_models', fromlist=['MessageAudit']).MessageAudit).filter_by(packet_id=result.packet.id)), 1.0)
        for _ in range(3):
            codec.patterns.record_counterfactual(pattern.pattern_id, full_success=1, compressed_success=1, semantic_fidelity=1, validation_id="same")
        assert pattern.status != "active"
        codec.patterns.record_counterfactual(pattern.pattern_id, full_success=1, compressed_success=1, semantic_fidelity=1, validation_id="second")
        codec.patterns.record_counterfactual(pattern.pattern_id, full_success=1, compressed_success=1, semantic_fidelity=1, validation_id="third")
        assert pattern.status == "active"


def test_reliability_drift_cools_active_pattern():
    from datetime import datetime, timedelta

    from aifence.bus.db_models import LearnedPattern, ReliabilityWindow
    from aifence.bus.reliability import ReliabilityMonitor

    with SessionLocal() as db:
        settings = Settings(auth_required=False, pattern_drift_min_samples=2, pattern_drift_window_minutes=60, pattern_drift_max_drop=0.1)
        concept = Codebook(db, settings).register(settings.codebook, "drift_pattern")
        pattern = LearnedPattern(
            codebook=settings.codebook,
            signature="d" * 64,
            canonical="drift_pattern",
            concept_id=concept.id,
            composition=[],
            relation_structure={},
            status="active",
        )
        db.add(pattern)
        db.flush()
        now = datetime.now(UTC)
        current_start = datetime.fromtimestamp(int(now.timestamp()) - (int(now.timestamp()) % 3600), tz=UTC)
        db.add(ReliabilityWindow(
            workspace="w", receiver="r", model_identity_hash="model-build", pattern_id=pattern.id,
            task_family="task", window_start=current_start - timedelta(hours=1), sample_count=10, fidelity_sum=9.9,
        ))
        db.flush()
        monitor = ReliabilityMonitor(db, settings)
        monitor._record_window(pattern=pattern, workspace="w", receiver="r", model_identity_hash="model-build", task_family="task", fidelity=0.5)
        monitor._record_window(pattern=pattern, workspace="w", receiver="r", model_identity_hash="model-build", task_family="task", fidelity=0.5)
        assert pattern.status == "cooling"
        assert monitor.latest_status(workspace="w", receiver="r", model_identity_hash="model-build", pattern_id=pattern.id, task_family="task")["status"] == "degraded"


def test_reachability_gc_removes_only_old_unreachable_state():
    from datetime import datetime, timedelta

    from aifence.bus.maintenance import cleanup
    from aifence.bus.state import StateStore

    with SessionLocal() as db:
        settings = Settings(
            auth_required=False,
            state_retention_days=1,
            audit_retention_days=1,
            pattern_learning_enabled=False,
            semantic_cache_enabled=False,
        )
        states = StateStore(db, settings)
        retained = states.create({"status": "retained"}, workspace="w")
        removed = states.create({"status": "removed"}, workspace="w")
        states.checkpoints.create(retained)
        old = datetime.now(UTC) - timedelta(days=5)
        retained.created_at = old
        removed.created_at = old
        db.commit()
        result = cleanup(db, settings)
        assert result["orphan_states_deleted"] == 1
        assert states.get(retained.id, workspace="w") is not None
        assert states.get(removed.id, workspace="w") is None
