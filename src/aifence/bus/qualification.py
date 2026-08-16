# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import argparse
import json
import math
import statistics
import threading
import time
import uuid
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session, sessionmaker

from .bus import SemanticBus
from .codebook import Codebook
from .codec import SageCodec
from .config import Settings
from .db import Base
from .db_models import BusMessage, LearnedPattern, PatternCandidate, PatternSourceEvidence
from .pattern_structure import pattern_signature
from .patterns import PatternStore
from .schemas import EncodeRequest


@dataclass
class QueryCounter:
    count: int = 0


@contextmanager
def count_queries(engine: Any) -> Iterator[QueryCounter]:
    counter = QueryCounter()

    def before_cursor_execute(*_: Any, **__: Any) -> None:
        counter.count += 1

    event.listen(engine, "before_cursor_execute", before_cursor_execute)
    try:
        yield counter
    finally:
        event.remove(engine, "before_cursor_execute", before_cursor_execute)


def percentiles(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    if not ordered:
        return {"p50_ms": 0.0, "p95_ms": 0.0, "p99_ms": 0.0}

    def pick(q: float) -> float:
        index = min(len(ordered) - 1, max(0, math.ceil(q * len(ordered)) - 1))
        return ordered[index]

    return {"p50_ms": pick(0.50), "p95_ms": pick(0.95), "p99_ms": pick(0.99)}


def profile_encode(db: Session, settings: Settings, content: Any, iterations: int = 100) -> dict[str, Any]:
    if iterations < 1:
        raise ValueError("iterations must be >= 1")
    codec = SageCodec(db, settings)
    durations: list[float] = []
    query_counts: list[int] = []
    engine = db.get_bind()
    for index in range(iterations):
        request = EncodeRequest(
            content=content,
            sender=f"profile-{index % 3}",
            receiver="profile-receiver",
            use_cache=False,
            auto_learn=False,
            record_learning=False,
        )
        started = time.perf_counter_ns()
        with count_queries(engine) as counter:
            codec.encode(request)
        durations.append((time.perf_counter_ns() - started) / 1_000_000)
        query_counts.append(counter.count)
    return {
        "iterations": iterations,
        **percentiles(durations),
        "query_p50": statistics.median(query_counts),
        "query_max": max(query_counts),
    }


def vocabulary_profile(db: Session, settings: Settings, sizes: list[int]) -> list[dict[str, Any]]:
    store = Codebook(db, settings)
    results: list[dict[str, Any]] = []
    current = 0
    for size in sorted(set(sizes)):
        if size < 1:
            raise ValueError("vocabulary sizes must be positive")
        while current < size:
            store.register(settings.codebook, f"scale_concept_{current:08d}")
            current += 1
        db.commit()
        exact_times: list[float] = []
        fuzzy_times: list[float] = []
        for offset in range(min(50, size)):
            started = time.perf_counter_ns()
            match = store.match(settings.codebook, f"scale_concept_{offset:08d}", observe=False)
            exact_times.append((time.perf_counter_ns() - started) / 1_000_000)
            if match.concept is None:
                raise AssertionError("exact concept lookup failed")
            started = time.perf_counter_ns()
            store.match(settings.codebook, f"unseen_scale_probe_{offset:08d}", observe=False)
            fuzzy_times.append((time.perf_counter_ns() - started) / 1_000_000)
        results.append({
            "concepts": size,
            "exact": percentiles(exact_times),
            "fuzzy": percentiles(fuzzy_times),
        })
    return results


def bus_chaos(db: Session, settings: Settings, messages: int = 50) -> dict[str, Any]:
    bus = SemanticBus(db, settings)
    ids: list[str] = []
    for index in range(messages):
        item = bus.handoff(
            receiver="chaos-receiver",
            sender=f"chaos-sender-{index % 3}",
            content={"sequence": index, "status": "pending"},
            correlation_id=f"chaos-{index}",
        )
        ids.append(item.id)
    db.commit()
    claimed = bus.pull(receiver="chaos-receiver", limit=messages, claim=True)
    db.commit()
    midpoint = len(claimed) // 2
    for item in claimed[:midpoint]:
        bus.ack(item.id, receiver="chaos-receiver")
    for item in claimed[midpoint:]:
        bus.nack(item.id, receiver="chaos-receiver")
    db.commit()
    redelivered = bus.pull(receiver="chaos-receiver", limit=messages, claim=True)
    redelivered_ids = {item.id for item in redelivered}
    expected = set(ids[midpoint:])
    if redelivered_ids != expected:
        raise AssertionError("nacked messages were not redelivered exactly once")
    for item in redelivered:
        bus.ack(item.id, receiver="chaos-receiver")
    db.commit()
    if bus.pending_count(receiver="chaos-receiver") != 0:
        raise AssertionError("bus did not drain")
    return {"messages": messages, "acked_first": midpoint, "redelivered": len(redelivered)}


def concurrent_bus(settings: Settings, workers: int = 8, messages_per_worker: int = 20) -> dict[str, Any]:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    if workers < 1 or messages_per_worker < 1:
        raise ValueError("workers and messages_per_worker must be positive")
    with TemporaryDirectory() as temp:
        db_path = Path(temp) / "concurrency.db"
        engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False}, pool_pre_ping=True)
        Base.metadata.create_all(engine)
        local_session = sessionmaker(bind=engine, expire_on_commit=False)

        def producer(worker: int) -> int:
            count = 0
            with local_session() as db:
                bus = SemanticBus(db, settings)
                for index in range(messages_per_worker):
                    bus.handoff(
                        receiver="concurrent-receiver",
                        sender=f"worker-{worker}",
                        content={"worker": worker, "sequence": index},
                        correlation_id=f"{worker}:{index}",
                    )
                    count += 1
                db.commit()
            return count

        with ThreadPoolExecutor(max_workers=workers) as pool:
            produced = sum(pool.map(producer, range(workers)))
        with local_session() as db:
            bus = SemanticBus(db, settings)
            consumed = 0
            seen: set[str] = set()
            while True:
                items = bus.pull(receiver="concurrent-receiver", limit=100, claim=True)
                if not items:
                    break
                for item in items:
                    if item.id in seen:
                        raise AssertionError("duplicate bus claim")
                    seen.add(item.id)
                    bus.ack(item.id, receiver="concurrent-receiver")
                    consumed += 1
                db.commit()
            if produced != consumed:
                raise AssertionError(f"produced {produced} but consumed {consumed}")
        engine.dispose()
    return {"workers": workers, "messages_per_worker": messages_per_worker, "produced": produced, "consumed": consumed}





def concurrent_pattern_learning(settings: Settings, workers: int = 6, observations_per_worker: int = 4) -> dict[str, Any]:
    if workers < 2 or observations_per_worker < 1:
        raise ValueError("workers must be >= 2 and observations_per_worker must be positive")
    with TemporaryDirectory() as temp:
        db_path = Path(temp) / "pattern-concurrency.db"
        engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False}, pool_pre_ping=True)
        Base.metadata.create_all(engine)
        local_session = sessionmaker(bind=engine, expire_on_commit=False)
        composition = [
            {"canonical": "deployment", "path": "$.deployment", "has_literal": True, "literal_mode": "slot", "literal_type": "str"},
            {"canonical": "reason", "path": "$.reason", "has_literal": True, "literal_mode": "slot", "literal_type": "str"},
        ]
        signature = pattern_signature(composition)

        def observe(worker: int) -> int:
            with local_session() as db:
                store = PatternStore(db, settings)
                for index in range(observations_per_worker):
                    store.observe(
                        settings.codebook,
                        composition,
                        slot_sample=f"{worker}:{index}",
                        source_ids=[f"source-{worker}"],
                        trust_score=1.0,
                        trust_scope="session",
                    )
                    db.commit()
            return observations_per_worker

        with ThreadPoolExecutor(max_workers=workers) as pool:
            observed = sum(pool.map(observe, range(workers)))

        with local_session() as db:
            candidates = list(db.scalars(select(PatternCandidate).where(PatternCandidate.signature == signature)))
            patterns = list(db.scalars(select(LearnedPattern).where(LearnedPattern.signature == signature)))
            evidence = list(db.scalars(select(PatternSourceEvidence).where(PatternSourceEvidence.signature == signature)))
            evidence_count = sum(item.observation_count for item in evidence)
            if len(candidates) + len(patterns) != 1:
                raise AssertionError("pattern signature split across duplicate lifecycle rows")
            if len(evidence) != workers or evidence_count != observed:
                raise AssertionError("concurrent pattern source evidence was lost or duplicated")
        engine.dispose()
    return {
        "workers": workers,
        "observations_per_worker": observations_per_worker,
        "observed": observed,
        "source_diversity": len(evidence),
        "evidence_count": evidence_count,
        "promoted": bool(patterns),
    }


def concurrent_ordering(settings: Settings, workers: int = 4, messages_per_worker: int = 10) -> dict[str, Any]:
    with TemporaryDirectory() as temp:
        db_path = Path(temp) / "ordering.db"
        engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False}, pool_pre_ping=True)
        Base.metadata.create_all(engine)
        local_session = sessionmaker(bind=engine, expire_on_commit=False)

        def producer(worker: int) -> int:
            with local_session() as db:
                bus = SemanticBus(db, settings)
                for index in range(messages_per_worker):
                    bus.handoff(
                        receiver="ordered-receiver", sender=f"worker-{worker}",
                        content={"worker": worker, "index": index}, ordering_key="shared-stream",
                        idempotency_key=f"ordered-{worker}-{index}",
                    )
                    db.commit()
            return messages_per_worker

        with ThreadPoolExecutor(max_workers=workers) as pool:
            produced = sum(pool.map(producer, range(workers)))
        from .db_models import BusMessage
        with local_session() as db:
            sequence = list(db.scalars(
                select(BusMessage.sequence_no)
                .where(BusMessage.ordering_key == "shared-stream")
                .order_by(BusMessage.sequence_no)
            ))
        engine.dispose()
        expected = list(range(1, produced + 1))
        if sequence != expected:
            raise AssertionError("ordered stream sequence is not contiguous and unique")
        return {"workers": workers, "messages": produced, "first": sequence[0], "last": sequence[-1]}

def concurrent_ordering_configured(settings: Settings, workers: int = 8, messages_per_worker: int = 20) -> dict[str, Any]:
    if workers < 1 or messages_per_worker < 1:
        raise ValueError("workers and messages_per_worker must be positive")
    is_sqlite = settings.database_url.startswith("sqlite")
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False} if is_sqlite else {},
    )
    Base.metadata.create_all(engine)
    local_session = sessionmaker(bind=engine, expire_on_commit=False)
    stream = f"ordered-{uuid.uuid4().hex}"
    receiver = f"ordered-receiver-{uuid.uuid4().hex}"

    def producer(worker: int) -> int:
        with local_session() as db:
            bus = SemanticBus(db, settings)
            for index in range(messages_per_worker):
                bus.handoff(
                    receiver=receiver,
                    sender=f"worker-{worker}",
                    content={"worker": worker, "index": index},
                    ordering_key=stream,
                    idempotency_key=f"{stream}:{worker}:{index}",
                )
                db.commit()
        return messages_per_worker

    with ThreadPoolExecutor(max_workers=workers) as pool:
        produced = sum(pool.map(producer, range(workers)))
    with local_session() as db:
        sequence = list(db.scalars(
            select(BusMessage.sequence_no)
            .where(BusMessage.ordering_key == stream)
            .order_by(BusMessage.sequence_no)
        ))
    engine.dispose()
    expected = list(range(1, produced + 1))
    if sequence != expected:
        raise AssertionError("configured ordered stream sequence is not contiguous and unique")
    return {
        "backend": "sqlite" if is_sqlite else "configured",
        "workers": workers,
        "messages": produced,
        "first": sequence[0],
        "last": sequence[-1],
    }



def profile_encode_isolated(settings: Settings, iterations: int = 30) -> dict[str, Any]:
    with TemporaryDirectory() as temp:
        db_path = Path(temp) / "profile.db"
        engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False}, pool_pre_ping=True)
        Base.metadata.create_all(engine)
        local_session = sessionmaker(bind=engine, expire_on_commit=False)
        with local_session() as db:
            report = profile_encode(db, settings, {"project": "phoenix", "status": "blocked", "failed": 3}, iterations)
        engine.dispose()
    return report

def vocabulary_profile_isolated(settings: Settings, sizes: list[int]) -> list[dict[str, Any]]:
    from sqlalchemy.orm import sessionmaker

    with TemporaryDirectory() as temp:
        db_path = Path(temp) / "vocabulary.db"
        engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False}, pool_pre_ping=True)
        Base.metadata.create_all(engine)
        local_session = sessionmaker(bind=engine, expire_on_commit=False)
        with local_session() as db:
            report = vocabulary_profile(db, settings, sizes)
        engine.dispose()
    return report

def concurrent_bus_configured(settings: Settings, workers: int = 8, messages_per_worker: int = 20) -> dict[str, Any]:
    if workers < 1 or messages_per_worker < 1:
        raise ValueError("workers and messages_per_worker must be positive")
    is_sqlite = settings.database_url.startswith("sqlite")
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False} if is_sqlite else {},
    )
    Base.metadata.create_all(engine)
    local_session = sessionmaker(bind=engine, expire_on_commit=False)
    receiver = f"qualified-{uuid.uuid4().hex}"

    def producer(worker: int) -> int:
        with local_session() as db:
            bus = SemanticBus(db, settings)
            for index in range(messages_per_worker):
                bus.handoff(
                    receiver=receiver,
                    sender=f"worker-{worker}",
                    content={"worker": worker, "sequence": index},
                    correlation_id=f"{worker}:{index}",
                )
            db.commit()
        return messages_per_worker

    with ThreadPoolExecutor(max_workers=workers) as pool:
        produced = sum(pool.map(producer, range(workers)))

    seen: set[str] = set()
    seen_lock = threading.Lock()

    def consumer(_: int) -> int:
        consumed = 0
        empty_rounds = 0
        while empty_rounds < 3:
            with local_session() as db:
                bus = SemanticBus(db, settings)
                items = bus.pull(receiver=receiver, limit=20, claim=True)
                if not items:
                    empty_rounds += 1
                    db.commit()
                    time.sleep(0.01)
                    continue
                empty_rounds = 0
                for item in items:
                    with seen_lock:
                        if item.id in seen:
                            raise AssertionError("duplicate bus claim")
                        seen.add(item.id)
                    bus.ack(item.id, receiver=receiver)
                    consumed += 1
                db.commit()
        return consumed

    consumer_workers = 1 if is_sqlite else workers
    with ThreadPoolExecutor(max_workers=consumer_workers) as pool:
        consumed = sum(pool.map(consumer, range(consumer_workers)))
    with local_session() as db:
        remaining = SemanticBus(db, settings).pending_count(receiver=receiver)
    engine.dispose()
    if produced != consumed or remaining != 0:
        raise AssertionError(f"produced={produced} consumed={consumed} remaining={remaining}")
    return {
        "backend": "sqlite" if is_sqlite else "configured",
        "producer_workers": workers,
        "consumer_workers": consumer_workers,
        "messages_per_worker": messages_per_worker,
        "produced": produced,
        "consumed": consumed,
    }

def main() -> None:
    parser = argparse.ArgumentParser(description="SAGE v0.2 qualification runner")
    parser.add_argument("--concurrency", action="store_true")
    parser.add_argument("--configured-concurrency", action="store_true")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--messages", type=int, default=20)
    parser.add_argument("--vocabulary", default="")
    parser.add_argument("--pattern-concurrency", action="store_true")
    parser.add_argument("--ordering-concurrency", action="store_true")
    parser.add_argument("--configured-ordering", action="store_true")
    parser.add_argument("--profile-encode", action="store_true")
    parser.add_argument("--profile-iterations", type=int, default=30)
    parser.add_argument("--max-query-count", type=int, default=40)
    args = parser.parse_args()
    settings = Settings(auth_required=False, auto_create_schema=True)
    report: dict[str, Any] = {}
    if args.concurrency:
        report["concurrency"] = concurrent_bus(settings, args.workers, args.messages)
    if args.configured_concurrency:
        report["configured_concurrency"] = concurrent_bus_configured(settings, args.workers, args.messages)
    if args.vocabulary:
        sizes = [int(item) for item in args.vocabulary.split(",") if item.strip()]
        report["vocabulary"] = vocabulary_profile_isolated(settings, sizes)
    if args.pattern_concurrency:
        report["pattern_concurrency"] = concurrent_pattern_learning(settings, args.workers, args.messages)
    if args.ordering_concurrency:
        report["ordering_concurrency"] = concurrent_ordering(settings, args.workers, args.messages)
    if args.configured_ordering:
        report["configured_ordering"] = concurrent_ordering_configured(settings, args.workers, args.messages)
    if args.profile_encode:
        profile = profile_encode_isolated(settings, args.profile_iterations)
        if profile["query_max"] > args.max_query_count:
            raise SystemExit(f"encode query budget exceeded: {profile['query_max']} > {args.max_query_count}")
        report["encode_profile"] = profile
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
