from __future__ import annotations

import argparse
import json
import time
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


def run(messages: int) -> dict[str, int]:
    with TemporaryDirectory() as temp:
        engine = create_engine(f"sqlite:///{Path(temp) / 'chaos.db'}", connect_args={"check_same_thread": False})
        Base.metadata.create_all(engine)
        sessions = sessionmaker(bind=engine, expire_on_commit=False)
        settings = Settings(auth_required=False, auto_create_schema=True, bus_claim_lease_seconds=1)
        with sessions() as db:
            bus = SemanticBus(db, settings)
            ids = [bus.handoff(receiver="r", sender="s", content={"n": i}, idempotency_key=f"k-{i}").id for i in range(messages)]
            db.commit()
        with sessions() as db:
            bus = SemanticBus(db, settings)
            claimed = bus.pull(receiver="r", limit=messages, claim=True)
            db.commit()
            if db.scalar(select(ReceiverKnowledgeItem).limit(1)) is not None:
                raise AssertionError("knowledge changed before ACK")
            for item in claimed[: len(claimed)//2]:
                bus.ack(item.id, receiver="r")
            db.commit()
        time.sleep(1.05)
        with sessions() as db:
            bus = SemanticBus(db, settings)
            recovered = bus.pull(receiver="r", limit=messages, claim=True)
            expected = set(ids[len(ids)//2:])
            if {item.id for item in recovered} != expected:
                raise AssertionError("lease recovery mismatch")
            for item in recovered:
                bus.ack(item.id, receiver="r")
            db.commit()
            duplicate = bus.handoff(receiver="r2", sender="s", content={"x": 1}, idempotency_key="stable")
            same = bus.handoff(receiver="r2", sender="s", content={"x": 1}, idempotency_key="stable")
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
        engine.dispose()
    return {"messages": messages, "recovered_after_lease": len(expected), "idempotent_writes": 1}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--messages", type=int, default=64)
    args = parser.parse_args()
    print(json.dumps(run(args.messages), sort_keys=True))


if __name__ == "__main__":
    main()
