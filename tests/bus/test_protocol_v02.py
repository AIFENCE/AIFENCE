from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from aifence.bus.a2a_adapter import agent_card, pack_message, unpack_message
from aifence.bus.conformance import run_tck
from aifence.bus.main import app
from aifence.bus.protocol_spec import (
    canonical_digest,
    canonical_json_bytes,
    canonical_msgpack_bytes,
    validate_wire_v2,
)


def test_canonical_encoding_is_order_independent_and_stable():
    a = {"v": 2, "c": "global", "a": "report", "p": {}, "m": {"z": 1, "a": 2}}
    b = {"m": {"a": 2, "z": 1}, "p": {}, "a": "report", "c": "global", "v": 2}
    assert canonical_json_bytes(a) == canonical_json_bytes(b)
    assert canonical_msgpack_bytes(a) == canonical_msgpack_bytes(b)
    assert canonical_digest(a) == canonical_digest(b)


def test_wire_v2_rejects_unknown_fields_and_nonfinite_values():
    with pytest.raises(ValidationError):
        validate_wire_v2({"v": 2, "c": "global", "a": "report", "p": {}, "wat": 1})
    with pytest.raises(ValueError):
        canonical_json_bytes({"x": float("nan")})


def test_reference_tck_passes():
    result = run_tck()
    assert result.ok, result.failures
    assert result.total >= 8


def test_a2a_v1_message_and_agent_card_binding():
    wire = {"v": 2, "c": "global", "a": "handoff", "p": {}}
    message = pack_message(wire, message_id="msg-1", context_id="ctx-1")
    assert message["role"] == "ROLE_USER"
    assert message["extensions"]
    assert unpack_message(message) == wire
    card = agent_card(
        name="Planner",
        description="Plans work",
        url="https://a2a.invalid/a2a",
    )
    assert card["supportedInterfaces"][0]["protocolVersion"] == "1.0"
    assert card["capabilities"]["extensions"][0]["params"]["wireVersion"] == 2
    assert card["defaultInputModes"] == ["application/vnd.aifence.packet+json"]
    assert card["defaultOutputModes"] == ["application/vnd.aifence.packet+json"]
    assert card["skills"][0]["id"] == "aifence-semantic-handoff"


def test_protocol_api_reports_frozen_v02_and_validates_vectors():
    with TestClient(app) as client:
        info = client.get("/v1/protocol")
        assert info.status_code == 200
        assert info.json()["protocol"] == "aifence/0.2"
        assert info.json()["wire_version"] == 2
        tck = client.get("/v1/protocol/tck")
        assert tck.status_code == 200
        assert tck.json()["ok"] is True
        wire = {"v": 2, "c": "global", "a": "report", "p": {}}
        validated = client.post("/v1/protocol/validate", json=wire)
        assert validated.status_code == 200
        assert validated.json()["digest"].startswith("sha256:")
        schema = client.get("/v1/protocol/wire-schema")
        assert schema.status_code == 200
        assert schema.json()["properties"]["v"]["default"] == 2


def test_packaged_wire_schema_matches_reference_model():
    from importlib.resources import files

    from aifence.bus.protocol_spec import wire_schema

    packaged = json.loads(files("aifence.bus").joinpath("spec/schemas/wire-v2.schema.json").read_text(encoding="utf-8"))
    assert packaged == wire_schema()


def test_v02_is_the_only_supported_protocol_and_wire():
    from aifence.bus.protocol_spec import AIFENCE_SUPPORTED_PROTOCOLS, AIFENCE_SUPPORTED_WIRES

    assert AIFENCE_SUPPORTED_PROTOCOLS == ("aifence/0.2",)
    assert AIFENCE_SUPPORTED_WIRES == (2,)
    with pytest.raises(ValueError):
        validate_wire_v2({"v": 99, "c": "global", "a": "report", "p": {}})


def test_packaged_protocol_spec_and_protobuf_binding_present():
    from importlib.resources import files

    root = files("aifence.bus").joinpath("spec")
    spec = root.joinpath("AIFENCE-0.2.md").read_text(encoding="utf-8")
    proto = root.joinpath("aifence-v0.2.proto").read_text(encoding="utf-8")
    assert "initial protocol baseline" in spec
    assert 'package aifence.v02;' in proto
    assert 'uint32 wire_version = 1; // MUST be 2.' in proto
    assert 'string protocol = 1' in proto
    pattern_schema = json.loads(root.joinpath('schemas/pattern-v0.2.schema.json').read_text(encoding='utf-8'))
    assert pattern_schema['title'] == 'ProtocolPattern'
    assert 'composition' in pattern_schema['properties']
