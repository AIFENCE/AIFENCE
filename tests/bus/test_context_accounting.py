"""Context-accounting instrumentation tests (issue #16, stage 1).

Covers:
* token-estimation fallback heuristic and tiktoken path (import guard);
* accounting math on known payloads;
* the shared no-op collector (zero behavioral change when disabled);
* cross-exchange report merging;
* codec instrumentation: encode/decode record real metrics;
* wire-byte identity: the instrumented codec must emit byte-identical wire
  output for a representative payload set (golden bytes captured from the
  pre-instrumentation codec at commit cf46d42, wire version 2).
"""

from __future__ import annotations

import json
import math
import threading

import pytest
from sqlalchemy import text

import aifence.bus.context_accounting as ca
from aifence.bus.codec import AifenceCodec
from aifence.bus.config import Settings
from aifence.bus.db import SessionLocal
from aifence.bus.schemas import Atom, EncodeRequest, Packet, Provenance
from aifence.bus.state import StateStore

PROV = Provenance(observed_at="2026-08-01T00:00:00+00:00", producer="alice")


def _fixed_packet_id(codec: AifenceCodec, name: str) -> None:
    import hashlib

    codec._packet_id = lambda n=name: "P" + hashlib.sha256(n.encode()).hexdigest()[:32]  # type: ignore[method-assign]


def _base_request(**kw) -> EncodeRequest:
    req = dict(
        sender="alice",
        receiver="bob",
        provenance=PROV,
        use_cache=False,
        use_receiver_knowledge=False,
        record_learning=False,
        auto_learn=False,
    )
    req.update(kw)
    return EncodeRequest(**req)


# ---------------------------------------------------------------------------
# Token estimation
# ---------------------------------------------------------------------------


def test_estimate_tokens_fallback_heuristic_without_tiktoken(monkeypatch):
    monkeypatch.setattr(ca, "_encoder", None)
    monkeypatch.setattr(ca, "_tiktoken_attempted", True)
    assert ca.estimate_tokens("hello world") == math.ceil(11 / 4.0)
    assert ca.estimate_tokens("x" * 100) == 25
    assert ca.estimate_tokens("") == 1
    # custom chars-per-token width is honored
    assert ca.estimate_tokens("x" * 10, chars_per_token=2.0) == 5


def test_estimate_tokens_uses_tiktoken_when_available(monkeypatch):
    class _FakeEncoder:
        def encode(self, text: str):
            return list(range(len(text)))

    monkeypatch.setattr(ca, "_encoder", _FakeEncoder())
    monkeypatch.setattr(ca, "_tiktoken_attempted", True)
    assert ca.estimate_tokens("abcd") == 4
    assert ca.estimate_tokens("") == 0


# ---------------------------------------------------------------------------
# Accounting math on known payloads
# ---------------------------------------------------------------------------


def test_accounting_math_on_known_payloads():
    acc = ca.ContextAccounting(estimate=lambda s: len(s))
    acc.record_exchange("P1", "semantic")
    acc.record_wire_bytes(100, 80)
    acc.record_stored_bytes(50)
    acc.record_model_tokens(25)
    acc.record_codebook_fingerprint("abc123")  # 6 bytes / 6 tokens
    acc.record_codebook_definition("C1", "hello world")  # "C1 hello world" -> 14 bytes / 14 tokens
    acc.record_pattern_definition("a_b_c")  # 5 bytes / 5 tokens
    acc.record_decoding_text("hello world", {"x": 1})  # "hello world {'x': 1}" -> 20 bytes / 20 tokens
    acc.record_reference_fetch(512)
    acc.record_reference_fetch(None)  # counts, adds no bytes
    acc.record_fallback("unknown thing")  # 13 bytes / 13 tokens

    rep = acc.snapshot()
    assert rep.exchanges == 1
    assert rep.packet_id == "P1"
    assert rep.strategy == "semantic"
    assert rep.wire_bytes_json == 100
    assert rep.wire_bytes_msgpack == 80
    assert rep.stored_bytes == 50
    assert rep.model_tokens == 25
    assert rep.codebook_setup_bytes == 20  # 6 fingerprint + 14 definition
    assert rep.codebook_setup_tokens == 20
    assert rep.codebook_definitions == 1
    assert rep.pattern_setup_bytes == 5
    assert rep.pattern_setup_tokens == 5
    assert rep.pattern_definitions == 1
    assert rep.decoding_bytes == 20
    assert rep.decoding_tokens == 20
    assert rep.reference_fetch_bytes == 512
    assert rep.reference_fetch_count == 2
    assert rep.fallback_bytes == 13
    assert rep.fallback_tokens == 13
    assert rep.fallback_count == 1


def test_snapshot_is_detached_and_reset_clears():
    acc = ca.ContextAccounting(estimate=lambda s: len(s))
    acc.record_wire_bytes(10, 5)
    snap = acc.snapshot()
    acc.record_wire_bytes(10, 5)
    assert snap.wire_bytes_json == 10  # snapshot unaffected by later recording
    acc.reset()
    assert acc.snapshot().wire_bytes_msgpack == 0


def test_report_merge_accumulates():
    a = ca.ContextReport(exchanges=1, wire_bytes_json=100, wire_bytes_msgpack=80, fallback_count=1)
    b = ca.ContextReport(exchanges=1, wire_bytes_json=50, wire_bytes_msgpack=40, fallback_count=2)
    merged = ca.ContextReport().merge(a).merge(b)
    assert merged.exchanges == 2
    assert merged.wire_bytes_json == 150
    assert merged.wire_bytes_msgpack == 120
    assert merged.fallback_count == 3


# ---------------------------------------------------------------------------
# No-op collector
# ---------------------------------------------------------------------------


def test_noop_collector_is_behaviorally_inert():
    noop = ca.collector(False)
    assert noop.enabled is False
    assert ca.collector(False) is noop  # shared singleton
    # every recorder is a safe no-op
    noop.record_exchange("P1", "semantic")
    noop.record_wire_bytes(1, 2)
    noop.record_stored_bytes(3)
    noop.record_model_tokens(4)
    noop.record_codebook_fingerprint("fp")
    noop.record_codebook_definition("C1", "canonical")
    noop.record_pattern_definition("pat")
    noop.record_decoding_text("canonical", "literal")
    noop.record_reference_fetch(100)
    noop.record_fallback("fallback")
    rep = noop.snapshot()
    assert rep == ca.ContextReport()
    # enabled collectors are fresh instances, not the singleton
    assert ca.collector(True) is not noop
    assert ca.collector(True).enabled is True


# ---------------------------------------------------------------------------
# Codec instrumentation
# ---------------------------------------------------------------------------


def test_codec_disabled_accounting_is_default_and_inert():
    with SessionLocal() as db:
        codec = AifenceCodec(db, Settings(auth_required=False, database_url="sqlite://"))
        assert codec.accounting.enabled is False
        result = codec.encode(_base_request(content="hello world"))
        assert codec.context_report() is None
        decoded = codec.decode(result.packet)
        assert decoded.concepts == []


def test_encode_records_accounting_metrics():
    with SessionLocal() as db:
        settings = Settings(
            auth_required=False, database_url="sqlite://", context_accounting_enabled=True
        )
        codec = AifenceCodec(db, settings)
        result = codec.encode(_base_request(content="hello world"))
        rep = codec.context_report()
        assert rep is not None
        assert rep.exchanges == 1
        assert rep.packet_id == result.packet.id
        assert rep.strategy == "semantic"
        assert rep.wire_bytes_json == result.output_bytes_json
        assert rep.wire_bytes_msgpack == result.output_bytes_msgpack
        assert rep.model_tokens > 0
        assert rep.codebook_setup_bytes > 0  # fingerprint recorded
        assert rep.fallback_count >= 1  # unknown unit fell back to literal


def test_encode_records_codebook_definitions_for_unknown_codes():
    with SessionLocal() as db:
        settings = Settings(
            auth_required=False, database_url="sqlite://", context_accounting_enabled=True
        )
        codec = AifenceCodec(db, settings)
        codec.codebook.register("global", "refund_requested")
        db.commit()
        codec.encode(_base_request(content="refund requested"))
        rep = codec.context_report()
        assert rep is not None
        assert rep.codebook_definitions == 1  # receiver does not know C00000001
        assert rep.codebook_setup_tokens > 0


def test_encode_records_stored_bytes_for_state_and_reference():
    with SessionLocal() as db:
        settings = Settings(
            auth_required=False, database_url="sqlite://", context_accounting_enabled=True
        )
        codec = AifenceCodec(db, settings)
        codec.encode(_base_request(content={"status": "blocked", "count": 3}))
        rep = codec.context_report()
        assert rep is not None
        assert rep.stored_bytes == len(b'{"count":3,"status":"blocked"}')
        codec.encode(_base_request(content={"blob": "x" * 3000}))
        rep2 = codec.context_report()
        assert rep2 is not None
        assert rep2.strategy == "reference"
        assert rep2.stored_bytes > 0
        assert rep2.reference_fetch_count == 0  # fetch happens on decode, not encode


def test_decode_records_decoding_and_reference_fetch_metrics():
    with SessionLocal() as db:
        settings = Settings(
            auth_required=False, database_url="sqlite://", context_accounting_enabled=True
        )
        codec = AifenceCodec(db, settings)
        encoded = codec.encode(_base_request(content={"blob": "x" * 3000}))
        codec.decode(encoded.packet, resolve_refs=True, receiver="bob")
        rep = codec.context_report()
        assert rep is not None
        assert rep.strategy == "reference"
        assert rep.reference_fetch_count >= 1
        assert rep.reference_fetch_bytes > 0
        # reference packets carry no atoms: expansion cost is the fetch volume
        assert rep.decoding_bytes == 0
        assert rep.decoding_tokens == 0


def test_decode_records_fallback_for_unknown_code():
    with SessionLocal() as db:
        settings = Settings(
            auth_required=False, database_url="sqlite://", context_accounting_enabled=True
        )
        codec = AifenceCodec(db, settings)
        encoded = codec.encode(_base_request(content="hello world"))
        codec.decode(encoded.packet, receiver="bob")
        rep = codec.context_report()
        assert rep is not None
        # unknown (no-code) atoms are decoded as literals: expansion recorded,
        # no codebook definition cost on the receive side
        assert rep.decoding_bytes > 0
        assert rep.fallback_count == 0


# ---------------------------------------------------------------------------
# Wire-byte identity (golden bytes captured from pre-instrumentation codec)
# ---------------------------------------------------------------------------

GOLDEN_CASES = {
    "delta": {
        "strategy": "delta",
        "wire_json": "{\"a\":\"report\",\"b\":\"S2976efd240d42031d5b8b5ef196fc25232f37d29\",\"c\":\"global\",\"d\":[{\"op\":\"replace\",\"path\":\"/failed\",\"value\":1}],\"i\":\"P4f4a9410ffcdf895c4adb880659e9b5c\",\"m\":{\"revision\":2,\"state\":\"S495c3c766e5c28338dbf242ed7b7ad624142457f\"},\"p\":{\"p\":\"alice\",\"t\":1785542400},\"r\":\"bob\",\"s\":\"alice\",\"v\":2}",
        "wire_msgpack_b64": "iqFhpnJlcG9ydKFi2SlTMjk3NmVmZDI0MGQ0MjAzMWQ1YjhiNWVmMTk2ZmMyNTIzMmYzN2QyOaFjpmdsb2JhbKFkkYOib3CncmVwbGFjZaRwYXRopy9mYWlsZWSldmFsdWUBoWnZIVA0ZjRhOTQxMGZmY2RmODk1YzRhZGI4ODA2NTllOWI1Y6FtgqhyZXZpc2lvbgKlc3RhdGXZKVM0OTVjM2M3NjZlNWMyODMzOGRiZjI0MmVkN2I3YWQ2MjQxNDI0NTdmoXCCoXClYWxpY2WhdM5qbTcAoXKjYm9ioXOlYWxpY2WhdgI=",
        "output_bytes_json": 297,
        "output_bytes_msgpack": 233,
        "packet_id": "P4f4a9410ffcdf895c4adb880659e9b5c",
    },
    "literal_string": {
        "strategy": "semantic",
        "wire_json": "{\"a\":\"report\",\"c\":\"global\",\"i\":\"P1a17e4773202e98bb505febb620a1b52\",\"p\":{\"p\":\"alice\",\"t\":1785542400},\"r\":\"bob\",\"s\":\"alice\",\"v\":2,\"x\":[{\"h\":1,\"l\":\"hello world\",\"p\":\"$\"}]}",
        "wire_msgpack_b64": "iKFhpnJlcG9ydKFjpmdsb2JhbKFp2SFQMWExN2U0NzczMjAyZTk4YmI1MDVmZWJiNjIwYTFiNTKhcIKhcKVhbGljZaF0zmptNwChcqNib2Khc6VhbGljZaF2AqF4kYOhaAGhbKtoZWxsbyB3b3JsZKFwoSQ=",
        "output_bytes_json": 168,
        "output_bytes_msgpack": 116,
        "packet_id": "P1a17e4773202e98bb505febb620a1b52",
    },
    "reference": {
        "strategy": "reference",
        "wire_json": "{\"R\":[\"aifence:sha256:b6b7f9a9be427689b75d86a5fd3b63d874bd5a453d51c324ada7772552764c4a\"],\"a\":\"report\",\"c\":\"global\",\"i\":\"P52367a6622b19f08825e915fad80c542\",\"m\":{\"memory_tier\":\"hot\",\"revision\":1,\"state\":\"Sf95883a1680cc9f429b2b69cc86afcaa7aed7dd2\"},\"p\":{\"p\":\"alice\",\"t\":1785542400},\"r\":\"bob\",\"s\":\"alice\",\"v\":2}",
        "wire_msgpack_b64": "iaFSkdlPYWlmZW5jZTpzaGEyNTY6YjZiN2Y5YTliZTQyNzY4OWI3NWQ4NmE1ZmQzYjYzZDg3NGJkNWE0NTNkNTFjMzI0YWRhNzc3MjU1Mjc2NGM0YaFhpnJlcG9ydKFjpmdsb2JhbKFp2SFQNTIzNjdhNjYyMmIxOWYwODgyNWU5MTVmYWQ4MGM1NDKhbYOrbWVtb3J5X3RpZXKjaG90qHJldmlzaW9uAaVzdGF0ZdkpU2Y5NTg4M2ExNjgwY2M5ZjQyOWIyYjY5Y2M4NmFmY2FhN2FlZDdkZDKhcIKhcKVhbGljZaF0zmptNwChcqNib2Khc6VhbGljZaF2Ag==",
        "output_bytes_json": 307,
        "output_bytes_msgpack": 253,
        "packet_id": "P52367a6622b19f08825e915fad80c542",
    },
    "semantic_code": {
        "strategy": "semantic",
        "wire_json": "{\"a\":\"report\",\"c\":\"global\",\"i\":\"Pe6f55b5aeb4ac5efde6f1c724c342f81\",\"p\":{\"p\":\"alice\",\"t\":1785542400},\"r\":\"bob\",\"s\":\"alice\",\"v\":2,\"x\":[{\"c\":\"C00000001\",\"p\":\"$\",\"v\":1}]}",
        "wire_msgpack_b64": "iKFhpnJlcG9ydKFjpmdsb2JhbKFp2SFQZTZmNTViNWFlYjRhYzVlZmRlNmYxYzcyNGMzNDJmODGhcIKhcKVhbGljZaF0zmptNwChcqNib2Khc6VhbGljZaF2AqF4kYOhY6lDMDAwMDAwMDGhcKEkoXYB",
        "output_bytes_json": 166,
        "output_bytes_msgpack": 114,
        "packet_id": "Pe6f55b5aeb4ac5efde6f1c724c342f81",
    },
    "state_checkpoint": {
        "strategy": "semantic",
        "wire_json": "{\"a\":\"report\",\"c\":\"global\",\"i\":\"P81ae62c0ca668c37dc9dc68d09042f96\",\"m\":{\"revision\":1,\"state\":\"Sd3819d6c535a664d593768d6ea6ee40e53984528\"},\"p\":{\"p\":\"alice\",\"t\":1785542400},\"r\":\"bob\",\"s\":\"alice\",\"v\":2,\"x\":[{\"h\":1,\"l\":3,\"p\":\"$.count\"},{\"h\":1,\"l\":\"blocked\",\"p\":\"$.status\"}]}",
        "wire_msgpack_b64": "iaFhpnJlcG9ydKFjpmdsb2JhbKFp2SFQODFhZTYyYzBjYTY2OGMzN2RjOWRjNjhkMDkwNDJmOTahbYKocmV2aXNpb24BpXN0YXRl2SlTZDM4MTlkNmM1MzVhNjY0ZDU5Mzc2OGQ2ZWE2ZWU0MGU1Mzk4NDUyOKFwgqFwpWFsaWNloXTOam03AKFyo2JvYqFzpWFsaWNloXYCoXiSg6FoAaFsA6FwpyQuY291bnSDoWgBoWynYmxvY2tlZKFwqCQuc3RhdHVz",
        "output_bytes_json": 270,
        "output_bytes_msgpack": 198,
        "packet_id": "P81ae62c0ca668c37dc9dc68d09042f96",
    }
}


@pytest.mark.parametrize(
    "name,golden",
    sorted(GOLDEN_CASES.items()),
    ids=sorted(GOLDEN_CASES),
)
def test_instrumented_codec_wire_bytes_match_pre_instrumentation_golden(name, golden):
    with SessionLocal() as db:
        settings = Settings(auth_required=False, database_url="sqlite://")
        codec = AifenceCodec(db, settings)
        _fixed_packet_id(codec, name)

        if name == "delta":
            state = StateStore(db).create({"failed": 3, "branch": "main"})
            db.commit()
            req = _base_request(content={"failed": 1, "branch": "main"}, base_state=state.id)
        elif name == "semantic_code":
            codec.codebook.register("global", "refund_requested")
            db.commit()
            req = _base_request(content="refund requested")
        elif name == "state_checkpoint":
            req = _base_request(content={"status": "blocked", "count": 3})
        elif name == "reference":
            req = _base_request(content={"blob": "x" * 3000})
        else:
            req = _base_request(content="hello world")

        result = codec.encode(req)
        assert result.strategy == golden["strategy"]
        assert result.wire_json == golden["wire_json"]
        assert result.wire_msgpack_b64 == golden["wire_msgpack_b64"]
        assert result.output_bytes_json == golden["output_bytes_json"]
        assert result.output_bytes_msgpack == golden["output_bytes_msgpack"]
        assert result.packet.id == golden["packet_id"]
        # wire version stays 2 (protocol frozen; instrumentation is additive)
        assert json.loads(result.wire_json)["v"] == 2


# ---------------------------------------------------------------------------
# Hardening (issue #16 stage 1): recorders never raise, reports are
# call-local and thread-safe (adversary findings F1/F2/F3)
# ---------------------------------------------------------------------------


def test_decode_survives_corrupted_byte_size_reference_row():
    """F1: a non-int ``byte_size`` in the references store must not make
    the instrumented decode raise; the report records a deterministic value."""
    with SessionLocal() as db:
        settings = Settings(
            auth_required=False, database_url="sqlite://", context_accounting_enabled=True
        )
        codec = AifenceCodec(db, settings)
        encoded = codec.encode(_base_request(content={"blob": "x" * 3000}))
        ref_id = encoded.packet.refs[0]
        # SQLite does not enforce Integer on the column; corrupt it directly.
        db.execute(
            text('UPDATE "references" SET byte_size = :v WHERE id = :rid'),
            {"v": "garbage", "rid": ref_id},
        )
        db.commit()
        decoded = codec.decode(encoded.packet, resolve_refs=True, receiver="bob")
        # decode succeeded; the raw (corrupt) value is surfaced untouched
        assert decoded.references[0]["byte_size"] == "garbage"
        rep = codec.context_report()
        assert rep is not None
        assert rep.reference_fetch_count >= 1
        assert rep.reference_fetch_bytes == 0  # deterministic fallback for non-int byte_size


def test_record_methods_never_raise_on_adversarial_inputs():
    """F2: every record_* method survives non-typed/adversarial inputs with
    deterministic fallbacks (the docstring 'never raise' contract)."""

    class _RaisingStr:
        def __str__(self):
            raise RuntimeError("__str__ exploded")

    acc = ca.ContextAccounting()
    calls = [
        ("exchange None", lambda: acc.record_exchange(None, None)),
        ("exchange non-str", lambda: acc.record_exchange(123, 456)),
        ("wire_bytes str", lambda: acc.record_wire_bytes("x", "y")),
        ("wire_bytes dict", lambda: acc.record_wire_bytes({"a": 1}, [1])),
        ("stored_bytes str", lambda: acc.record_stored_bytes("x")),
        ("model_tokens str", lambda: acc.record_model_tokens("x")),
        ("fingerprint int", lambda: acc.record_codebook_fingerprint(123)),
        ("fingerprint None", lambda: acc.record_codebook_fingerprint(None)),
        ("codebook_definition None", lambda: acc.record_codebook_definition(None, None)),
        ("codebook_definition raising __str__", lambda: acc.record_codebook_definition(_RaisingStr(), "x")),
        ("pattern_definition None", lambda: acc.record_pattern_definition(None)),
        ("pattern_definition int", lambda: acc.record_pattern_definition(7)),
        ("decoding_text raising literal", lambda: acc.record_decoding_text("a", _RaisingStr())),
        ("decoding_text raising canonical", lambda: acc.record_decoding_text(_RaisingStr(), "b")),
        ("reference_fetch str", lambda: acc.record_reference_fetch("garbage")),
        ("reference_fetch dict", lambda: acc.record_reference_fetch({"n": 1})),
        ("reference_fetch None", lambda: acc.record_reference_fetch(None)),
        ("fallback None", lambda: acc.record_fallback(None)),
        ("fallback int", lambda: acc.record_fallback(42)),
    ]
    for _, fn in calls:
        fn()  # must never raise

    rep = acc.snapshot()
    # deterministic fallbacks for the unparseable inputs above:
    # int() failures -> 0; str() always succeeds except for a raising
    # __str__, which maps to ""; str(None) == "None" as in plain Python
    assert rep.exchanges == 2
    assert rep.packet_id == "123" and rep.strategy == "456"  # coerced to str
    assert rep.wire_bytes_json == 0 and rep.wire_bytes_msgpack == 0
    assert rep.stored_bytes == 0 and rep.model_tokens == 0
    assert rep.reference_fetch_count == 3 and rep.reference_fetch_bytes == 0
    assert rep.codebook_definitions == 2 and rep.codebook_setup_bytes == 17
    assert rep.pattern_definitions == 2 and rep.pattern_setup_bytes == 5
    assert rep.decoding_bytes == 2
    assert rep.fallback_count == 2 and rep.fallback_bytes == 6

    # the disabled no-op survives the same adversarial inputs, unchanged
    noop = ca.collector(False)
    for fn in (
        lambda: noop.record_reference_fetch("garbage"),
        lambda: noop.record_wire_bytes("x", "y"),
        lambda: noop.record_codebook_fingerprint(123),
        lambda: noop.record_pattern_definition(None),
        lambda: noop.record_fallback(None),
        lambda: noop.record_decoding_text("a", _RaisingStr()),
    ):
        fn()
    assert noop.snapshot() == ca.ContextReport()


def test_round_trip_retains_both_encode_and_decode_reports():
    """F3: a sequential encode -> decode round-trip on one codec instance
    must retain BOTH completed reports (encode metrics are not lost)."""
    with SessionLocal() as db:
        settings = Settings(
            auth_required=False, database_url="sqlite://", context_accounting_enabled=True
        )
        codec = AifenceCodec(db, settings)
        encoded = codec.encode(_base_request(content="hello world"))
        encode_rep = codec.context_report()
        assert encode_rep is not None
        assert encode_rep.exchanges == 1
        assert encode_rep.wire_bytes_json == encoded.output_bytes_json
        assert encode_rep.decoding_bytes == 0  # encoding records no expansion cost

        codec.decode(encoded.packet, receiver="bob")
        decode_rep = codec.context_report()
        assert decode_rep is not None
        assert decode_rep.exchanges == 1
        assert decode_rep.wire_bytes_json == 0  # decoding records no wire bytes
        assert decode_rep.decoding_bytes == len("hello world")

        # both completed reports are retrievable, most recent first
        recent = codec.context_reports(limit=10)
        assert len(recent) == 2
        assert recent[0].packet_id == decode_rep.packet_id
        assert recent[1].packet_id == encode_rep.packet_id
        assert recent[1].wire_bytes_json == encoded.output_bytes_json  # encode report retained
        assert recent[0].decoding_bytes == len("hello world")


def test_concurrent_exchanges_on_shared_codec_publish_uncorrupted_reports():
    """F3: overlapping exchanges on ONE shared codec instance cannot clobber
    or corrupt completed reports -- every exchange's report is retrievable
    with exactly its own metrics. Includes a real encode running concurrently
    with simulated exchanges; a barrier widens the overlap deterministically.
    """
    n = 8
    barrier = threading.Barrier(n)
    orig = ca.ContextAccounting.record_wire_bytes

    def barrier_record_wire(self, j, m):
        barrier.wait(timeout=30)  # all n recorders overlap at this point
        return orig(self, j, m)

    ca.ContextAccounting.record_wire_bytes = barrier_record_wire  # type: ignore[method-assign]
    try:
        with SessionLocal() as db:
            settings = Settings(
                auth_required=False, database_url="sqlite://", context_accounting_enabled=True
            )
            codec = AifenceCodec(db, settings)
            errors: list[str] = []
            err_lock = threading.Lock()
            real: dict[str, object] = {}

            def real_encode() -> None:
                try:
                    enc = codec.encode(_base_request(content="concurrent real encode"))
                    with err_lock:
                        real["id"] = enc.packet.id
                        real["out_json"] = enc.output_bytes_json
                except Exception as exc:  # noqa: BLE001
                    with err_lock:
                        errors.append(f"real: {type(exc).__name__}: {exc}")

            def sim_exchange(i: int) -> None:
                try:
                    acc = codec._begin_accounting()  # call-local recorder (encode/decode path)
                    acc.record_exchange(f"P-conc-{i}", "semantic")
                    acc.record_wire_bytes(100 + i, 80 + i)  # meets the barrier
                    acc.record_model_tokens(10 + i)
                    codec._publish_report(acc.snapshot())
                except Exception as exc:  # noqa: BLE001
                    with err_lock:
                        errors.append(f"sim {i}: {type(exc).__name__}: {exc}")

            threads = [threading.Thread(target=sim_exchange, args=(i,)) for i in range(n - 1)]
            threads.append(threading.Thread(target=real_encode))
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=60)
                assert not t.is_alive(), "exchange thread did not finish"
            assert errors == []
            assert "id" in real and "out_json" in real

            recent = codec.context_reports(limit=n + 8)
            assert len(recent) == n
            by_id = {r.packet_id: r for r in recent}
            assert set(by_id) == {f"P-conc-{i}" for i in range(n - 1)} | {real["id"]}

            for i in range(n - 1):
                rep = by_id[f"P-conc-{i}"]
                assert rep.exchanges == 1
                assert rep.wire_bytes_json == 100 + i  # exactly its own metrics
                assert rep.wire_bytes_msgpack == 80 + i
                assert rep.model_tokens == 10 + i

            real_rep = by_id[real["id"]]
            assert real_rep.exchanges == 1
            assert real_rep.strategy == "semantic"
            assert real_rep.wire_bytes_json == real["out_json"]

            # most recent completed exchange is retrievable and not a partial
            latest = codec.context_report()
            assert latest is not None
            assert latest.packet_id in by_id
    finally:
        ca.ContextAccounting.record_wire_bytes = orig


def test_context_reports_history_api_disabled_and_bounded():
    with SessionLocal() as db:
        codec = AifenceCodec(db, Settings(auth_required=False, database_url="sqlite://"))
        assert codec.context_report() is None  # disabled: no completed reports
        assert codec.context_reports(limit=5) == []

    history = ca.ContextReportHistory(maxlen=4)
    for i in range(6):
        history.publish(ca.ContextReport(exchanges=1, packet_id=f"P{i}", wire_bytes_json=i))
    assert history.most_recent().packet_id == "P5"
    recent = history.recent(limit=10)
    assert [r.packet_id for r in recent] == ["P5", "P4", "P3", "P2"]  # bounded, most recent first
    # readers get detached copies
    snap = history.most_recent()
    history.publish(ca.ContextReport(exchanges=1, packet_id="P6"))
    assert snap.packet_id == "P5"


def test_text_recorders_survive_lone_surrogates():
    """G1: lone-surrogate str inputs must not raise UnicodeEncodeError."""
    acc = ca.ContextAccounting()
    acc.record_codebook_fingerprint("\ud800")
    acc.record_codebook_definition("C\ud800", "x")
    acc.record_pattern_definition("\ud800")
    acc.record_decoding_text("\ud800", "literal")
    acc.record_fallback("\ud800")
    rep = acc.snapshot()
    # surrogate-safe byte counts (3 bytes per lone surrogate, CESU-8 style)
    assert rep.codebook_setup_bytes == 9  # fp "\ud800" 3 + def "C\ud800 x" 6
    assert rep.pattern_setup_bytes == 3
    assert rep.decoding_bytes == len("\ud800 literal".encode("utf-8", errors="surrogatepass"))
    assert rep.fallback_bytes == 3


def test_decode_survives_lone_surrogate_atom_with_accounting_enabled():
    """G1 (wire path): decoding a foreign packet carrying a \\ud800 escape
    must not raise with accounting enabled (the pre-instrumentation codec
    decodes the same packet fine)."""
    with SessionLocal() as db:
        settings = Settings(
            auth_required=False, database_url="sqlite://", context_accounting_enabled=True
        )
        codec = AifenceCodec(db, settings)
        packet = Packet(
            cb="global",
            sender="alice",
            receiver="bob",
            act="report",
            prov=PROV,
            atoms=[Atom(literal="bad \ud800 value", has_literal=True, path="$")],
        )
        decoded = codec.decode(packet, receiver="bob")
        assert decoded.literals[0]["literal"] == "bad \ud800 value"
        rep = codec.context_report()
        assert rep is not None
        assert rep.exchanges == 1
        assert rep.decoding_bytes == len("bad \ud800 value".encode("utf-8", errors="surrogatepass"))
