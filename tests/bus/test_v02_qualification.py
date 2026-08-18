from __future__ import annotations

from sqlalchemy import select

from aifence.bus.calibration import CalibrationStore
from aifence.bus.codebook import Codebook
from aifence.bus.codec import AifenceCodec
from aifence.bus.config import Settings
from aifence.bus.db import SessionLocal
from aifence.bus.db_models import LearnedPattern, PatternCandidate
from aifence.bus.qualification import (
    bus_chaos,
    concurrent_bus,
    concurrent_pattern_learning,
    profile_encode,
)
from aifence.bus.schemas import EncodeRequest, TraceContext


def trust_settings(**updates) -> Settings:
    values = {
        "auth_required": False,
        "max_inline_bytes": 100_000,
        "default_token_budget": 100_000,
        "max_packet_bytes": 100_000,
        "promotion_min_count": 999,
        "pattern_learning_enabled": True,
        "pattern_string_constants_enabled": True,
        "pattern_candidate_min_count": 2,
        "pattern_min_savings_bytes": 0,
        "pattern_utility_min_score": 0.0,
        "pattern_trust_required": True,
        "pattern_min_source_diversity": 2,
        "pattern_max_source_share": 0.75,
        "pattern_min_trust_score": 0.6,
        "semantic_cache_enabled": False,
    }
    values.update(updates)
    return Settings(**values)


def test_pattern_poisoning_requires_diverse_trusted_sources():
    with SessionLocal() as db:
        settings = trust_settings()
        codec = AifenceCodec(db, settings)
        content = {"deployment": "blocked", "reason": "tests"}
        for _ in range(5):
            codec.encode(EncodeRequest(content=content, sender="agent-a", source_trust=1.0, use_cache=False))
        assert db.scalar(select(LearnedPattern)) is None
        candidate = db.scalar(select(PatternCandidate))
        assert candidate is not None
        assert candidate.source_diversity == 1
        assert candidate.dominant_source_share == 1.0
        codec.encode(EncodeRequest(content=content, sender="agent-b", source_trust=1.0, use_cache=False))
        codec.encode(EncodeRequest(content=content, sender="agent-b", source_trust=1.0, use_cache=False))
        pattern = db.scalar(select(LearnedPattern))
        assert pattern is not None
        assert pattern.source_diversity == 2
        assert pattern.dominant_source_share <= 0.75
        assert pattern.trust_score == 1.0



def test_pattern_trust_scope_requires_broader_source_diversity():
    with SessionLocal() as db:
        settings = trust_settings(
            pattern_candidate_min_count=1,
            pattern_session_min_sources=2,
            pattern_project_min_sources=3,
            pattern_workspace_min_sources=4,
            pattern_domain_min_sources=5,
            pattern_federation_min_sources=6,
        )
        codec = AifenceCodec(db, settings)
        content = {"deployment": "blocked", "reason": "tests"}
        for index in range(3):
            codec.encode(
                EncodeRequest(
                    content=content,
                    sender=f"workspace-agent-{index}",
                    source_trust=1.0,
                    learning_scope="workspace",
                    use_cache=False,
                )
            )
        assert db.scalar(select(LearnedPattern)) is None
        codec.encode(
            EncodeRequest(
                content=content,
                sender="workspace-agent-3",
                source_trust=1.0,
                learning_scope="workspace",
                use_cache=False,
            )
        )
        pattern = db.scalar(select(LearnedPattern))
        assert pattern is not None
        assert pattern.trust_scope == "workspace"
        assert pattern.source_diversity == 4

def test_calibration_reduces_overconfident_probability():
    with SessionLocal() as db:
        store = CalibrationStore(db, buckets=10, min_samples=10)
        for index in range(20):
            store.record(
                predicted=0.95,
                observed=1.0 if index < 10 else 0.0,
                receiver="agent-b",
                model="model-b",
                task_family="triage",
            )
        report = store.report(0.95, receiver="agent-b", model="model-b", task_family="triage")
        assert report.sample_count == 20
        assert report.calibrated_probability < 0.95
        assert report.expected_calibration_error > 0.3
        assert report.brier_score > 0.4


def test_large_vocabulary_uses_bounded_lsh_candidates():
    with SessionLocal() as db:
        settings = Settings(
            auth_required=False,
            semantic_fuzzy_scan_limit=10,
            semantic_candidate_limit=16,
            semantic_lsh_bits=8,
            semantic_lsh_hamming=1,
        )
        codebook = Codebook(db, settings)
        for index in range(200):
            codebook.register(settings.codebook, f"concept_{index:04d}")
        db.commit()
        exact = codebook.match(settings.codebook, "concept_0100", observe=False)
        assert exact.concept is not None and exact.concept.canonical == "concept_0100"
        vector = codebook.embedder.embed("unseen_probe")
        candidates = codebook._fuzzy_candidates(settings.codebook, vector)
        assert len(candidates) <= settings.semantic_candidate_limit


def test_trace_context_round_trips_wire_v2():
    with SessionLocal() as db:
        codec = AifenceCodec(db, Settings(auth_required=False, semantic_cache_enabled=False))
        trace = TraceContext(
            traceparent="00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
            tracestate="vendor=value",
        )
        result = codec.encode(EncodeRequest(content={"status": "ready"}, trace=trace, use_cache=False))
        wire = codec.compact(result.packet)
        assert wire["v"] == 2
        assert wire["z"]["p"] == trace.traceparent
        expanded = codec.expand(wire)
        assert expanded.trace == trace


def test_qualification_chaos_and_query_profile():
    with SessionLocal() as db:
        settings = Settings(auth_required=False, semantic_cache_enabled=False, pattern_learning_enabled=False)
        chaos = bus_chaos(db, settings, messages=12)
        assert chaos["redelivered"] == 6
        profile = profile_encode(db, settings, {"status": "ready", "count": 1}, iterations=8)
        assert profile["p95_ms"] > 0
        assert profile["query_max"] < 40


def test_concurrent_bus_delivery_is_lossless():
    report = concurrent_bus(
        Settings(auth_required=False, semantic_cache_enabled=False, pattern_learning_enabled=False),
        workers=3,
        messages_per_worker=4,
    )
    assert report["produced"] == 12
    assert report["consumed"] == 12


def test_concurrent_pattern_learning_preserves_single_lifecycle_and_evidence():
    report = concurrent_pattern_learning(
        trust_settings(
            pattern_candidate_min_count=3,
            pattern_session_min_sources=2,
            pattern_project_min_sources=2,
            pattern_workspace_min_sources=2,
            pattern_domain_min_sources=2,
            pattern_federation_min_sources=2,
        ),
        workers=4,
        observations_per_worker=3,
    )
    assert report["observed"] == 12
    assert report["source_diversity"] == 4
    assert report["evidence_count"] == 12
