# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json

import httpx

from aifence.guard.api import _broker_response, _json_bytes, _safe_filename
from aifence.guard.clamav import ClamAVClient
from tests.guard.conftest import auth


class FakeSocket:
    def __init__(self, response: bytes) -> None:
        self.response = response
        self.sent = bytearray()
        self.read = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def sendall(self, value: bytes) -> None:
        self.sent.extend(value)

    def recv(self, size: int) -> bytes:
        if self.read:
            return b""
        self.read = True
        return self.response


def test_clamav_wire_protocol(monkeypatch) -> None:
    sockets = iter(
        [
            FakeSocket(b"PONG\0"),
            FakeSocket(b"stream: OK\0"),
            FakeSocket(b"stream: Eicar-Test-Signature FOUND\0"),
            FakeSocket(b"stream: protocol error\0"),
        ]
    )
    monkeypatch.setattr("socket.create_connection", lambda *args, **kwargs: next(sockets))
    client = ClamAVClient("clamav", 3310, 5)
    assert client.ping() is True
    assert client.scan(b"clean").status == "clean"
    infected = client.scan(b"infected")
    assert infected.status == "infected"
    assert infected.signature == "Eicar-Test-Signature"
    assert client.scan(b"unknown").status == "error"

    monkeypatch.setattr(
        "socket.create_connection", lambda *args, **kwargs: (_ for _ in ()).throw(OSError())
    )
    assert client.ping() is False


def test_broker_response_encodings_and_safe_helpers() -> None:
    json_response = httpx.Response(
        200, content=b'{"ok":true}', headers={"content-type": "application/json"}
    )
    assert _broker_response(json_response, "dec_1").body == {"ok": True}

    malformed = httpx.Response(
        200, content=b"{bad", headers={"content-type": "application/json"}
    )
    assert _broker_response(malformed, None).body["encoding"] == "base64"
    text = httpx.Response(200, text="hello", headers={"content-type": "text/plain"})
    assert _broker_response(text, None).body == "hello"
    binary = httpx.Response(200, content=b"\x00\x01")
    assert _broker_response(binary, None).body["encoding"] == "base64"
    assert _safe_filename('../../bad\nname.txt') == "....badname.txt"
    assert _safe_filename("///") == "artifact"
    assert _json_bytes({"b": 2, "a": 1}) == b'{"a":1,"b":2}'


def test_authentication_validation_and_security_headers(client) -> None:
    test_client, _, token = client
    missing = test_client.get("/v1/api-keys")
    assert missing.status_code == 401
    invalid = test_client.get("/v1/api-keys", headers=auth("adk_invalid"))
    assert invalid.status_code == 401
    found = test_client.get("/v1/agents/does-not-exist", headers=auth(token))
    assert found.status_code == 404
    assert found.headers["x-content-type-options"] == "nosniff"
    policy = found.headers["content-security-policy"]
    assert "default-src 'none'" in policy
    assert "frame-ancestors 'none'" in policy
    assert found.headers["x-request-id"]
    body = found.json()
    assert body["error"]["code"] == "not_found"
    assert json.loads(found.text)["error"]["message"]
