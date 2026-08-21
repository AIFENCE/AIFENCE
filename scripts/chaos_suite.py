from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from aifence.bus.bus import SemanticBus
from aifence.bus.config import Settings
from aifence.bus.db import Base
from aifence.bus.db_models import BusMessage, ReceiverKnowledgeItem
from aifence.bus.references import ReferenceExpiredError, ReferenceStore


def _pull_exact(bus: SemanticBus, *, receiver: str, total: int) -> list[BusMessage]:
    """Claim up to ``total`` messages across the Bus' bounded pull batches."""
    claimed: list[BusMessage] = []
    while len(claimed) < total:
        batch = bus.pull(receiver=receiver, limit=total - len(claimed), claim=True)
        if not batch:
            break
        claimed.extend(batch)
    return claimed


def run(messages: int) -> dict[str, int]:
    if messages < 1:
        raise ValueError("messages must be positive")

    with TemporaryDirectory() as temp:
        engine = create_engine(
            f"sqlite:///{Path(temp) / 'chaos.db'}",
            connect_args={"check_same_thread": False},
        )
        try:
            Base.metadata.create_all(engine)
            sessions = sessionmaker(bind=engine, expire_on_commit=False)
            settings = Settings(
                auth_required=False,
                auto_create_schema=True,
                bus_claim_lease_seconds=1,
            )
            with sessions() as db:
                bus = SemanticBus(db, settings)
                ids = [
                    bus.handoff(
                        receiver="r",
                        sender="s",
                        content={"n": i},
                        idempotency_key=f"k-{i}",
                    ).id
                    for i in range(messages)
                ]
                db.commit()

            with sessions() as db:
                bus = SemanticBus(db, settings)
                claimed = _pull_exact(bus, receiver="r", total=messages)
                if {item.id for item in claimed} != set(ids):
                    raise AssertionError(
                        f"initial claim mismatch: expected {messages}, got {len(claimed)}"
                    )
                db.commit()
                if db.scalar(select(ReceiverKnowledgeItem).limit(1)) is not None:
                    raise AssertionError("knowledge changed before ACK")

                split = len(claimed) // 2
                for item in claimed[:split]:
                    bus.ack(item.id, receiver="r")

                # Make the remaining claim lease deterministically stale instead of sleeping.
                # This avoids scheduler/filesystem timing variance across Windows and CI hosts.
                stale_at = datetime.now(UTC) - timedelta(
                    seconds=settings.bus_claim_lease_seconds + 1
                )
                for item in claimed[split:]:
                    item.claimed_at = stale_at
                expected = {item.id for item in claimed[split:]}
                db.commit()

            with sessions() as db:
                bus = SemanticBus(db, settings)
                recovered = _pull_exact(bus, receiver="r", total=len(expected))
                recovered_ids = {item.id for item in recovered}
                if recovered_ids != expected:
                    raise AssertionError(
                        "lease recovery mismatch: "
                        f"expected {len(expected)}, got {len(recovered_ids)}"
                    )
                for item in recovered:
                    bus.ack(item.id, receiver="r")
                db.commit()

                duplicate = bus.handoff(
                    receiver="r2",
                    sender="s",
                    content={"x": 1},
                    idempotency_key="stable",
                )
                same = bus.handoff(
                    receiver="r2",
                    sender="s",
                    content={"x": 1},
                    idempotency_key="stable",
                )
                if duplicate.id != same.id:
                    raise AssertionError("idempotency violation")

                ref_store = ReferenceStore(db, settings)
                ref = ref_store.put({"secret": 1}, workspace="w", owner="s", ttl_seconds=1)
                grant = ref_store.grant_metadata(ref.id, actor="s", workspace="w")
                grant.expires_at = datetime.now(UTC) - timedelta(seconds=1)
                db.flush()
                try:
                    ref_store.resolve(ref.id, actor="s", workspace="w")
                except ReferenceExpiredError:
                    pass
                else:
                    raise AssertionError("expired reference resolved")

                pending = db.scalar(select(BusMessage).where(BusMessage.id == duplicate.id))
                if pending is None:
                    raise AssertionError("idempotent message missing")
        finally:
            # SQLite keeps the file open on Windows until pooled connections are disposed.
            engine.dispose()

    return {
        "messages": messages,
        "recovered_after_lease": len(expected),
        "idempotent_writes": 1,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--messages", type=int, default=64)
    args = parser.parse_args()
    print(json.dumps(run(args.messages), sort_keys=True))


if __name__ == "__main__":
    main()
