from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import HTTPException

from aifence.bus import api_transport
from aifence.bus.protocol_spec import AIFENCE_PROTOCOL
from aifence.bus.schemas import (
    A2AMesaifencePackRequest,
    A2AMesaifenceUnpackRequest,
    A2AUnpackRequest,
    BusAckRequest,
    BusBatchAckRequest,
    EncodeRequest,
    FeedbackRequest,
    HandoffRequest,
    SendRequest,
)


class _DB:
    def __init__(self, scalar_value: Any = None) -> None:
        self.scalar_value = scalar_value
        self.commits = 0
        self.rollbacks = 0

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1

    def scalar(self, _statement: Any) -> Any:
        return self.scalar_value


def test_protocol_and_integration_error_contracts(monkeypatch: pytest.MonkeyPatch) -> None:
    info = api_transport.protocol_info()
    assert info["protocol"] == AIFENCE_PROTOCOL
    assert api_transport.protocol_wire_schema()
    assert api_transport.protocol_tck()["ok"] is True

    with pytest.raises(HTTPException) as invalid:
        api_transport.protocol_validate({"v": 999})
    assert invalid.value.status_code == 422

    monkeypatch.setattr(api_transport, "config_for", lambda *_: (_ for _ in ()).throw(KeyError("unknown")))
    with pytest.raises(HTTPException) as missing:
        api_transport.integration_config("nope", "https://example.test", "agent")
    assert missing.value.status_code == 404


def test_a2a_error_mapping_and_production_https(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(HTTPException) as bad_part:
        api_transport.a2a_unpack(A2AUnpackRequest(part={"kind": "data", "data": {}}))
    assert bad_part.value.status_code == 422

    monkeypatch.setattr(api_transport, "pack_message", lambda *a, **k: (_ for _ in ()).throw(ValueError("bad message")))
    req = A2AMesaifencePackRequest(wire={"v": 2}, role="ROLE_AGENT")
    with pytest.raises(HTTPException) as bad_pack:
        api_transport.a2a_message_pack(req)
    assert bad_pack.value.status_code == 422

    monkeypatch.setattr(api_transport, "unpack_message", lambda _m: (_ for _ in ()).throw(ValueError("bad message")))
    with pytest.raises(HTTPException) as bad_unpack:
        api_transport.a2a_message_unpack(A2AMesaifenceUnpackRequest(message={"role": "agent", "parts": []}))
    assert bad_unpack.value.status_code == 422

    monkeypatch.setattr(api_transport.settings, "env", "production", raising=False)
    with pytest.raises(HTTPException) as insecure:
        api_transport.a2a_agent_card("http://example.test")
    assert insecure.value.status_code == 422


def test_handoff_maps_backpressure_quota_and_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_transport, "enforce_agent_scope", lambda **_: "sender")

    class _Bus:
        def __init__(self, *_: Any) -> None: pass
        def handoff(self, **_: Any) -> Any: raise api_transport.BackpressureError("backpressure")

    monkeypatch.setattr(api_transport, "SemanticBus", _Bus)
    req = HandoffRequest(receiver="r", sender="s", content="hello")
    with pytest.raises(HTTPException) as busy:
        api_transport.bus_handoff(req, _DB())
    assert busy.value.status_code == 429
    assert busy.value.headers == {"Retry-After": "1"}

    class _Unavailable(_Bus):
        def handoff(self, **_: Any) -> Any: raise api_transport.BackpressureError("unavailable")

    monkeypatch.setattr(api_transport, "SemanticBus", _Unavailable)
    with pytest.raises(HTTPException) as down:
        api_transport.bus_handoff(req, _DB())
    assert down.value.status_code == 503

    class _Quota(_Bus):
        def handoff(self, **_: Any) -> Any: raise api_transport.QuotaExceededError("quota")

    monkeypatch.setattr(api_transport, "SemanticBus", _Quota)
    with pytest.raises(HTTPException) as quota:
        api_transport.bus_handoff(req, _DB())
    assert quota.value.status_code == 429

    class _NoContent(_Bus):
        def handoff(self, **_: Any) -> Any: raise AssertionError("not called")

    monkeypatch.setattr(api_transport, "SemanticBus", _NoContent)
    empty = HandoffRequest(receiver="r", sender="s", refs=[], content=None)
    with pytest.raises(HTTPException) as invalid:
        api_transport.bus_handoff(empty, _DB())
    assert invalid.value.status_code == 422


def test_ack_error_mapping_rolls_back_batch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_transport, "enforce_agent_scope", lambda **_: "receiver")

    class _Bus:
        def __init__(self, *_: Any) -> None: pass
        def ack(self, *_: Any, **__: Any) -> Any: raise PermissionError("forbidden")
        def nack(self, *_: Any, **__: Any) -> Any: raise KeyError("missing")

    monkeypatch.setattr(api_transport, "SemanticBus", _Bus)
    db = _DB()
    with pytest.raises(HTTPException) as denied:
        api_transport.bus_ack_batch(BusBatchAckRequest(receiver="receiver", message_ids=["m1"]), db)
    assert denied.value.status_code == 403
    assert db.rollbacks == 1

    with pytest.raises(HTTPException) as missing:
        api_transport.bus_nack("m1", BusAckRequest(receiver="receiver"), _DB())
    assert missing.value.status_code == 404


def test_encode_send_map_codec_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_transport, "enforce_agent_scope", lambda **kw: kw.get("actor"))
    monkeypatch.setattr(api_transport, "_apply_trace_headers", lambda *a, **k: None)

    class _Codec:
        def __init__(self, *_: Any) -> None: pass
        def encode(self, _req: Any) -> Any: raise ValueError("payload exceeds configured maximum")

    monkeypatch.setattr(api_transport, "AifenceCodec", _Codec)
    send_req = SendRequest(content="x", receiver="r", sender="s")
    with pytest.raises(HTTPException) as too_large:
        api_transport.send(send_req, _DB())
    assert too_large.value.status_code == 413

    with pytest.raises(HTTPException) as encoded:
        api_transport.encode(EncodeRequest(content="x"), _DB())
    assert encoded.value.status_code == 413

    class _MissingCodec(_Codec):
        def encode(self, _req: Any) -> Any: raise KeyError("missing ref")

    monkeypatch.setattr(api_transport, "AifenceCodec", _MissingCodec)
    with pytest.raises(HTTPException) as not_found:
        api_transport.send(send_req, _DB())
    assert not_found.value.status_code == 404


def test_inspection_feedback_and_explain_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    db = _DB(None)
    with pytest.raises(HTTPException) as explain_missing:
        api_transport.explain("missing", db)
    assert explain_missing.value.status_code == 404

    with pytest.raises(HTTPException) as feedback_missing:
        api_transport.feedback("missing", FeedbackRequest(task_success=True), db)
    assert feedback_missing.value.status_code == 404

    monkeypatch.setattr(api_transport, "current_principal", lambda: SimpleNamespace(kind="agent", workspace="w", agent="a"))

    class _Inspector:
        def __init__(self, _db: Any) -> None: pass
        def packet(self, *_: Any, **__: Any) -> Any: raise KeyError("missing")
        def run(self, *_: Any, **__: Any) -> Any: raise KeyError("missing")

    monkeypatch.setattr(api_transport, "Inspector", _Inspector)
    with pytest.raises(HTTPException) as packet_missing:
        api_transport.inspect_packet("p", db)
    assert packet_missing.value.status_code == 404
    with pytest.raises(HTTPException) as run_missing:
        api_transport.inspect_run("r", db)
    assert run_missing.value.status_code == 404
