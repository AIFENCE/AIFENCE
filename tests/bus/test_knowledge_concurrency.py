from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from aifence.bus.db_models import Base, ReceiverKnowledge, ReceiverKnowledgeItem
from aifence.bus.knowledge import KnowledgeStore


def _store(tmp_path, name: str):
    engine = create_engine(
        f"sqlite:///{tmp_path / name}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine, expire_on_commit=False)


def test_concurrent_ensure_creates_single_row(tmp_path):
    """Concurrent ensure() must not raise IntegrityError on the unique constraint."""
    engine, Session = _store(tmp_path, "ensure.db")
    errors: list[Exception] = []

    def worker() -> None:
        try:
            with Session() as db:
                KnowledgeStore(db).ensure("racer", "default")
                db.commit()
        except Exception as exc:  # pragma: no cover - assertion below
            errors.append(exc)

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda _: worker(), range(16)))
    assert not errors, errors
    with Session() as db:
        count = db.scalar(select(func.count()).select_from(ReceiverKnowledge))
        assert count == 1
    engine.dispose()


def test_concurrent_add_value_creates_single_item(tmp_path):
    """Concurrent _add_value() must not raise IntegrityError for the same item."""
    engine, Session = _store(tmp_path, "items.db")
    errors: list[Exception] = []

    def worker() -> None:
        try:
            with Session() as db:
                store = KnowledgeStore(db)
                store.ensure("racer", "default")
                store._add_value("racer", "default", "code", "c:123", 0.9)
                db.commit()
        except Exception as exc:  # pragma: no cover - assertion below
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors, errors
    with Session() as db:
        count = db.scalar(select(func.count()).select_from(ReceiverKnowledgeItem))
        assert count == 1
        item = db.scalar(select(ReceiverKnowledgeItem))
        assert item is not None and item.confidence == 0.9
    engine.dispose()
