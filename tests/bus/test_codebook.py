from aifence.bus.codebook import Codebook
from aifence.bus.config import Settings
from aifence.bus.db import SessionLocal


def test_concept_registration_and_lookup():
    with SessionLocal() as db:
        cb = Codebook(db, Settings(auth_required=False, database_url="sqlite://"))
        concept = cb.register("global", "refund_requested")
        db.commit()
        assert concept.code.startswith("C")
        assert cb.get_by_code(concept.code).canonical == "refund_requested"
        assert cb.match("global", "refund_requested").similarity == 1.0


def test_candidate_promotes_after_threshold():
    with SessionLocal() as db:
        settings = Settings(auth_required=False, database_url="sqlite://", promotion_min_count=3, promotion_min_savings_bytes=0)
        cb = Codebook(db, settings)
        assert cb.observe_candidate("global", "deployment_blocked") is None
        assert cb.observe_candidate("global", "deployment_blocked") is None
        promoted = cb.observe_candidate("global", "deployment_blocked")
        db.commit()
        assert promoted is not None
        assert promoted.canonical == "deployment_blocked"


def test_registration_normalizes_human_label():
    with SessionLocal() as db:
        cb = Codebook(db, Settings(auth_required=False, database_url="sqlite://"))
        concept = cb.register("global", "Refund Requested")
        db.commit()
        assert concept.canonical == "refund_requested"
        assert cb.exact("global", "refund requested").code == concept.code
