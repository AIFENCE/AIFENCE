from aifence.bus.codec import AifenceCodec
from aifence.bus.config import Settings
from aifence.bus.db import SessionLocal
from aifence.bus.schemas import EncodeRequest
from aifence.bus.state import StateStore


def test_large_input_becomes_reference():
    with SessionLocal() as db:
        settings = Settings(auth_required=False, database_url="sqlite://", max_inline_bytes=32)
        result = AifenceCodec(db, settings).encode(EncodeRequest(content={"blob": "x" * 2000}))
        assert len(result.packet.refs) == 1
        assert not result.packet.atoms
        assert result.output_bytes_msgpack < result.input_bytes


def test_state_delta_suppresses_full_payload():
    with SessionLocal() as db:
        settings = Settings(auth_required=False, database_url="sqlite://")
        state = StateStore(db).create({"failed": 3, "branch": "main"})
        db.commit()
        codec = AifenceCodec(db, settings)
        result = codec.encode(
            EncodeRequest(content={"failed": 1, "branch": "main"}, base_state=state.id)
        )
        assert result.packet.delta == [{"op": "replace", "path": "/failed", "value": 1}]
        assert result.packet.atoms == []
        assert result.packet.refs == []
        assert result.packet.meta["state"].startswith("S")
        decoded = codec.decode(result.packet)
        assert decoded.resolved_state == {"failed": 1, "branch": "main"}


def test_adaptive_learning_replaces_repeated_literal():
    with SessionLocal() as db:
        settings = Settings(auth_required=False, database_url="sqlite://", promotion_min_count=2, promotion_min_savings_bytes=0)
        codec = AifenceCodec(db, settings)
        first = codec.encode(EncodeRequest(content="refund requested"))
        second = codec.encode(EncodeRequest(content="refund requested"))
        assert first.packet.atoms[0].code is None
        assert second.packet.atoms[0].code is not None
        decoded = codec.decode(second.packet)
        assert decoded.concepts[0]["canonical"] == "refund_requested"


def test_known_code_still_transmits_occurrence():
    with SessionLocal() as db:
        settings = Settings(auth_required=False, database_url="sqlite://")
        codec = AifenceCodec(db, settings)
        concept = codec.codebook.register("global", "refund_requested")
        db.commit()
        result = codec.encode(
            EncodeRequest(content="refund requested", receiver_known_codes={concept.code})
        )
        assert result.packet.atoms[0].code == concept.code
