from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from aifence.bus.config import Settings
from aifence.bus.db import Base
from aifence.bus.qualification import (
    bus_chaos,
    concurrent_bus,
    concurrent_bus_configured,
    concurrent_ordering,
    concurrent_ordering_configured,
    concurrent_pattern_learning,
    percentiles,
    profile_encode,
    profile_encode_isolated,
    vocabulary_profile,
    vocabulary_profile_isolated,
)


@pytest.fixture
def settings() -> Settings:
    return Settings(auth_required=False, auto_create_schema=True)


def test_percentiles_and_validation(settings: Settings, tmp_path) -> None:
    assert percentiles([]) == {"p50_ms": 0.0, "p95_ms": 0.0, "p99_ms": 0.0}
    assert percentiles([3.0, 1.0, 2.0])["p50_ms"] == 2.0

    with pytest.raises(ValueError):
        concurrent_bus(settings, workers=0)
    with pytest.raises(ValueError):
        concurrent_pattern_learning(settings, workers=1)

    engine = create_engine(f"sqlite:///{tmp_path / 'q.db'}")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    with session_factory() as db:
        with pytest.raises(ValueError):
            profile_encode(db, settings, {"x": 1}, 0)
        with pytest.raises(ValueError):
            vocabulary_profile(db, settings, [0])
    engine.dispose()


def test_small_bus_chaos_and_profiles(settings: Settings, tmp_path) -> None:
    engine = create_engine(
        f"sqlite:///{tmp_path / 'runtime.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    with session_factory() as db:
        chaos = bus_chaos(db, settings, messages=6)
        assert chaos["redelivered"] == 3

        profile = profile_encode(
            db,
            settings,
            {"project": "phoenix", "status": "ready"},
            iterations=2,
        )
        assert profile["iterations"] == 2

        vocabulary = vocabulary_profile(db, settings, [1, 3])
        assert [row["concepts"] for row in vocabulary] == [1, 3]
    engine.dispose()


def test_isolated_concurrency_and_ordering(settings: Settings) -> None:
    result = concurrent_bus(settings, workers=2, messages_per_worker=2)
    assert result["produced"] == 4

    ordered = concurrent_ordering(settings, workers=2, messages_per_worker=2)
    assert ordered["messages"] == 4
    assert ordered["last"] == 4

    patterned = concurrent_pattern_learning(settings, workers=2, observations_per_worker=1)
    assert patterned["observed"] == 2


def test_configured_sqlite_and_isolated_profiles(settings: Settings, tmp_path) -> None:
    configured = Settings(
        auth_required=False,
        auto_create_schema=True,
        database_url=f"sqlite:///{tmp_path / 'configured.db'}",
    )
    result = concurrent_bus_configured(configured, workers=2, messages_per_worker=2)
    assert result["produced"] == result["consumed"] == 4

    ordering = concurrent_ordering_configured(configured, workers=2, messages_per_worker=2)
    assert ordering["messages"] == 4

    assert profile_encode_isolated(settings, iterations=2)["iterations"] == 2
    assert vocabulary_profile_isolated(settings, [1])[0]["concepts"] == 1
