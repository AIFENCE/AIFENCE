from aifence.bus.db import SessionLocal
from aifence.bus.references import ReferenceStore


def test_reference_is_content_addressed_and_deduplicated():
    with SessionLocal() as db:
        store = ReferenceStore(db)
        a = store.put({"x": [1, 2, 3]})
        b = store.put({"x": [1, 2, 3]})
        db.commit()
        assert a.id == b.id
        assert store.get(a.id).payload == {"x": [1, 2, 3]}
