from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import aifence.guard.anchor_dispatcher as mod
from aifence.core.db import Base
from aifence.guard.models import AuditAnchor, AuditAnchorClaim, Tenant


def _factory(tmp_path):
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'anchors.db'}")
    Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine, expire_on_commit=False)


def _seed(factory, *, aid: str = "anc-1", attempts: int = 0, max_attempts: int = 3) -> None:
    now = datetime.now(UTC)
    with factory() as session:
        if session.get(Tenant, "ten-1") is None:
            session.add(
                Tenant(
                    id="ten-1",
                    name="Anchor Tenant",
                    status="active",
                    retention_policy={},
                    created_at=now,
                )
            )
        sequence = 1 if aid == "anc-1" else 2
        session.add(
            AuditAnchor(
                id=aid,
                tenant_id="ten-1",
                sequence=sequence,
                chain_head="a" * 64,
                destination="webhook",
                envelope={"sequence": sequence},
                receipt={},
                receipt_hash="",
                status="pending",
                priority=100,
                attempts=attempts,
                max_attempts=max_attempts,
                available_at=now,
                anchored_at=now,
            )
        )
        session.add(
            AuditAnchorClaim(
                anchor_id=aid,
                tenant_id="ten-1",
                destination="webhook",
                status="pending",
                priority=100,
                attempts=attempts,
                max_attempts=max_attempts,
                available_at=now,
                created_at=now,
            )
        )
        session.commit()


def _worker(factory):
    settings = SimpleNamespace(
        anchor_batch_size=20,
        anchor_poll_milliseconds=1,
        anchor_lease_seconds=30,
    )
    return mod.AuditAnchorWorker(
        session_factory=factory,
        service=SimpleNamespace(settings=settings),
        worker_id="worker-1",
    )


def test_claim_deliver_verify_and_close(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, factory = _factory(tmp_path)
    _seed(factory)
    worker = _worker(factory)
    backend = SimpleNamespace(
        publish=lambda envelope: {"receipt": "ok"},
        verify=lambda envelope, receipt: True,
    )
    monkeypatch.setattr(mod, "build_anchor_backend", lambda settings, destination: backend)

    result = asyncio.run(worker.run_once())
    assert result.claimed == 1
    assert result.verified == 1
    assert result.anchor_ids == ("anc-1",)

    with factory() as session:
        anchor = session.get(AuditAnchor, "anc-1")
        claim = session.get(AuditAnchorClaim, "anc-1")
        assert anchor.status == "verified"
        assert anchor.receipt_hash
        assert claim.status == "processed"

    asyncio.run(worker.close())
    assert worker._closed is True
    engine.dispose()


def test_delivery_failure_retries_then_dead_letters(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, factory = _factory(tmp_path)
    _seed(factory, max_attempts=2)
    worker = _worker(factory)

    class BadBackend:
        def publish(self, envelope):
            raise RuntimeError("remote unavailable")

        def verify(self, envelope, receipt):
            return False

    monkeypatch.setattr(
        mod,
        "build_anchor_backend",
        lambda settings, destination: BadBackend(),
    )

    first = asyncio.run(worker.run_once())
    assert first.retried == 1

    with factory() as session:
        claim = session.get(AuditAnchorClaim, "anc-1")
        claim.available_at = datetime.now(UTC) - timedelta(seconds=1)
        anchor = session.get(AuditAnchor, "anc-1")
        anchor.available_at = claim.available_at
        session.commit()

    second = asyncio.run(worker.run_once())
    assert second.failed == 1

    with factory() as session:
        assert session.get(AuditAnchorClaim, "anc-1").status == "dead_lettered"
        assert session.get(AuditAnchor, "anc-1").status == "failed"
    engine.dispose()


def test_claim_preserves_destination_order_and_handles_missing_anchor(tmp_path) -> None:
    engine, factory = _factory(tmp_path)
    _seed(factory, aid="anc-1")
    _seed(factory, aid="anc-2")
    worker = _worker(factory)

    claims = worker._claim(10)
    assert [claim[0] for claim in claims] == ["anc-1"]

    with factory() as session:
        # Finish the earlier claim so the second destination item is eligible,
        # then delete its anchor while leaving the payload-free claim index.
        first = session.get(AuditAnchorClaim, "anc-1")
        first.status = "processed"
        first.processed_at = datetime.now(UTC)

        anchor = session.get(AuditAnchor, "anc-2")
        session.delete(anchor)
        claim = session.get(AuditAnchorClaim, "anc-2")
        claim.status = "pending"
        claim.available_at = datetime.now(UTC) - timedelta(seconds=1)
        session.commit()

    claims = worker._claim(10)
    assert claims == []
    with factory() as session:
        assert session.get(AuditAnchorClaim, "anc-2").status == "dead_lettered"
    engine.dispose()


def test_locked_anchor_rejects_stale_or_missing(tmp_path) -> None:
    engine, factory = _factory(tmp_path)
    _seed(factory)
    worker = _worker(factory)
    with factory() as session:
        with pytest.raises(RuntimeError, match="stale"):
            worker._locked_anchor(session, "anc-1", "ten-1", 1)
        with pytest.raises(RuntimeError, match="disappeared"):
            worker._locked_anchor(session, "missing", "ten-1", 1)
    engine.dispose()
