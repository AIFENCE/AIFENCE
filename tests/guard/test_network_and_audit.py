# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import hashlib
import json
import socket
import time
from pathlib import Path

import pytest
from sqlalchemy import select

from aifence.guard.audit import export_tenant_audit
from aifence.guard.errors import AuthorizationError, ConflictError
from aifence.guard.models import Event, Tenant
from aifence.guard.network import (
    canonical_path,
    pin_validated_target,
    revalidate_resolution,
    safe_join,
    validate_endpoint,
)
from tests.guard.conftest import auth


def _public_records(address: str = "93.184.216.34") -> list[tuple[object, ...]]:
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, 443))]


def test_network_canonicalization_resolution_and_revalidation(monkeypatch) -> None:
    assert canonical_path("/v1/items/~safe") == "/v1/items/~safe"
    assert safe_join("https://api.example.com/v1", "/items/7", ["/items/*"]) == (
        "https://api.example.com/v1/items/7"
    )
    for invalid in ("relative", "/a/../b", "/a%252f..%252fb", "/a\\b", "/a//b", "/a?x=1"):
        with pytest.raises(ConflictError):
            canonical_path(invalid)

    monkeypatch.setattr(socket, "getaddrinfo", lambda *args, **kwargs: _public_records())
    endpoint = validate_endpoint(
        "https://api.example.com/v1/",
        allowed_hosts=("api.example.com",),
        network_zone="public",
        resolution_timeout_seconds=1,
    )
    assert endpoint.canonical_url == "https://api.example.com/v1"
    assert endpoint.resolved_addresses == ("93.184.216.34",)
    revalidate_resolution(endpoint)

    monkeypatch.setattr(socket, "getaddrinfo", lambda *args, **kwargs: _public_records("10.0.0.7"))
    with pytest.raises(AuthorizationError):
        revalidate_resolution(endpoint)
    with pytest.raises(AuthorizationError):
        validate_endpoint(
            "https://api.example.com",
            allowed_hosts=("other.example.com",),
            network_zone="public",
        )
    with pytest.raises(ConflictError):
        validate_endpoint(
            "http://api.example.com",
            allowed_hosts=("api.example.com",),
            network_zone="public",
        )


def test_network_target_is_pinned_after_revalidation(monkeypatch) -> None:
    monkeypatch.setattr(socket, "getaddrinfo", lambda *args, **kwargs: _public_records())
    endpoint = validate_endpoint(
        "https://api.example.com/v1",
        allowed_hosts=("api.example.com",),
        network_zone="public",
        resolution_timeout_seconds=1,
    )
    target, host, extensions = pin_validated_target(
        "https://api.example.com/v1/items?limit=5", endpoint
    )
    assert target == "https://93.184.216.34/v1/items?limit=5"
    assert host == "api.example.com"
    assert extensions == {"sni_hostname": "api.example.com"}

    with pytest.raises(AuthorizationError, match="validated endpoint"):
        pin_validated_target("https://other.example.com/v1/items", endpoint)


def test_network_target_pinning_formats_ipv6(monkeypatch) -> None:
    records = [(socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("2606:2800:220:1:248:1893:25c8:1946", 443, 0, 0))]
    monkeypatch.setattr(socket, "getaddrinfo", lambda *args, **kwargs: records)
    endpoint = validate_endpoint(
        "https://api.example.com/", allowed_hosts=("api.example.com",),
        network_zone="public", resolution_timeout_seconds=1,
    )
    target, _, _ = pin_validated_target("https://api.example.com/v1", endpoint)
    assert target == "https://[2606:2800:220:1:248:1893:25c8:1946]/v1"


def test_network_dns_timeout_is_bounded(monkeypatch) -> None:
    def blocked(*args, **kwargs):
        time.sleep(1.5)
        return _public_records()

    monkeypatch.setattr(socket, "getaddrinfo", blocked)
    started = time.monotonic()
    with pytest.raises(ConflictError, match="timed out"):
        validate_endpoint(
            "https://api.example.com",
            allowed_hosts=("api.example.com",),
            network_zone="public",
            resolution_timeout_seconds=1,
        )
    assert time.monotonic() - started < 1.4


def test_signed_audit_export_and_invalid_chain_refusal(client, tmp_path: Path) -> None:
    test_client, app, token = client
    for index in range(2):
        response = test_client.post(
            "/v1/events",
            json={
                "trace_id": "trc_export_0001",
                "event_type": "test.export",
                "payload": {"index": index},
            },
            headers=auth(token),
        )
        assert response.status_code == 201

    archive = tmp_path / "tenant-audit.ndjson"
    with app.state.session_factory() as session:
        tenant_id = session.scalar(select(Tenant.id))
        assert tenant_id is not None
        result = export_tenant_audit(session, app.state.signing_key, tenant_id, archive)
        assert result["events"] >= 3  # bootstrap plus the two explicit events
        assert result["head_hash"] != "0" * 64

    raw = archive.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == result["sha256"]
    records = [json.loads(line) for line in raw.splitlines()]
    assert records[0]["record_type"] == "event"
    manifest_path = Path(result["manifest_path"])
    manifest = json.loads(manifest_path.read_text())
    assert manifest["archive"] == archive.name
    assert manifest["signature"]

    with app.state.session_factory() as session:
        event = session.scalar(select(Event).order_by(Event.sequence.desc()))
        assert event is not None
        event.payload = {"tampered": True}
        session.commit()
        with pytest.raises(ValueError, match="invalid audit chain"):
            export_tenant_audit(session, app.state.signing_key, event.tenant_id, tmp_path / "bad.ndjson")


def test_cursor_pagination_is_stable(client) -> None:
    test_client, _, token = client
    created_ids: list[str] = []
    for index in range(4):
        response = test_client.post(
            "/v1/api-keys",
            json={"name": f"reader-{index}", "scopes": ["events:read"]},
            headers=auth(token),
        )
        assert response.status_code == 201
        created_ids.append(response.json()["id"])

    first = test_client.get("/v1/api-keys?limit=2", headers=auth(token))
    assert first.status_code == 200
    assert len(first.json()) == 2
    cursor = first.json()[-1]["id"]
    second = test_client.get(f"/v1/api-keys?limit=2&after_id={cursor}", headers=auth(token))
    assert second.status_code == 200
    assert len(second.json()) == 2
    assert {row["id"] for row in first.json()}.isdisjoint({row["id"] for row in second.json()})

    missing = test_client.get("/v1/api-keys?after_id=key_missing", headers=auth(token))
    assert missing.status_code == 404
