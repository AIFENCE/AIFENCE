from aifence.bus.codec import AifenceCodec
from aifence.bus.config import Settings
from aifence.bus.db import SessionLocal
from aifence.bus.schemas import EncodeRequest


def test_unknown_literal_is_preserved_not_silently_mapped():
    with SessionLocal() as db:
        codec = AifenceCodec(db, Settings(auth_required=False, database_url="sqlite://"))
        result = codec.encode(
            EncodeRequest(
                content={"approval": False, "limit": 0, "note": "do not deploy"},
                auto_learn=False,
                use_cache=False,
            )
        )
        values = {(atom.path, atom.literal) for atom in result.packet.atoms}
        assert ("$.approval", False) in values
        assert ("$.limit", 0) in values
        assert ("$.note", "do not deploy") in values


def test_explicit_null_and_delete_survive_delta_round_trip():
    with SessionLocal() as db:
        codec = AifenceCodec(db, Settings(auth_required=False, database_url="sqlite://"))
        first = codec.encode(
            EncodeRequest(content={"a": 1, "b": 2}, sender="a", receiver="b", use_cache=False)
        )
        codec.decode(first.packet, receiver="b", acknowledge=True)
        second = codec.encode(
            EncodeRequest(
                content={"a": None},
                sender="a",
                receiver="b",
                base_state=first.packet.meta["state"],
                use_cache=False,
            )
        )
        decoded = codec.decode(second.packet, receiver="b")
        assert decoded.resolved_state == {"a": None}
