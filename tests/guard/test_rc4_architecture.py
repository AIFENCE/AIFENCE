# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import io
import zipfile
from datetime import UTC

from tests.guard.conftest import auth


def test_tenant_export_is_downloadable_integrity_bundle(client) -> None:
    test_client, _, token = client
    exported = test_client.post(
        "/v1/tenant/lifecycle",
        json={
            "action": "export", "reason": "portable tenant export",
            "parameters": {}, "idempotency_key": "tenant-export-rc4-0001",
        },
        headers=auth(token),
    )
    assert exported.status_code == 202, exported.text
    body = exported.json()
    assert body["status"] == "completed"
    downloaded = test_client.get(
        f"/v1/tenant/lifecycle/{body['id']}/content", headers=auth(token)
    )
    assert downloaded.status_code == 200, downloaded.text
    assert downloaded.headers["content-type"].startswith("application/zip")
    with zipfile.ZipFile(io.BytesIO(downloaded.content)) as archive:
        names = set(archive.namelist())
        assert "MANIFEST.json" in names
        assert any(name.startswith("records/") for name in names)


def test_legal_hold_lifecycle_and_release(client) -> None:
    test_client, _, token = client
    created = test_client.post(
        "/v1/tenant/legal-holds",
        json={"scope": "tenant", "reason": "pending investigation"},
        headers=auth(token),
    )
    assert created.status_code == 201, created.text
    hold = created.json()
    listed = test_client.get("/v1/tenant/legal-holds", headers=auth(token))
    assert listed.status_code == 200
    assert hold["id"] in {item["id"] for item in listed.json()}
    released = test_client.post(
        f"/v1/tenant/legal-holds/{hold['id']}/release",
        json={"reason": "investigation closed"}, headers=auth(token),
    )
    assert released.status_code == 200
    assert released.json()["status"] == "released"


def test_protocol_manifest_versions_are_exposed(client) -> None:
    test_client, _, token = client
    registered = test_client.post(
        "/v1/protocols",
        json={
            "protocol": "mcp", "external_id": "rc4-native-mcp",
            "endpoint": "https://api.openai.com/mcp", "protocol_version": "2025-06-18",
            "manifest": {"tools": [{"name": "lookup", "inputSchema": {"type": "object"}}]},
        },
        headers=auth(token),
    )
    assert registered.status_code == 201, registered.text
    versions = test_client.get(
        f"/v1/protocols/{registered.json()['id']}/manifest-versions", headers=auth(token)
    )
    assert versions.status_code == 200, versions.text
    assert versions.json()[0]["version"] == 1
    assert versions.json()[0]["source"] == "submitted"


def test_lifecycle_jobs_are_idempotent_and_readable(client) -> None:
    test_client, _, token = client
    request = {
        "action": "export", "reason": "idempotent export", "parameters": {},
        "idempotency_key": "tenant-export-rc4-0002",
    }
    first = test_client.post("/v1/tenant/lifecycle", json=request, headers=auth(token))
    second = test_client.post("/v1/tenant/lifecycle", json=request, headers=auth(token))
    assert first.status_code == second.status_code == 202
    assert first.json()["id"] == second.json()["id"]
    fetched = test_client.get(
        f"/v1/tenant/lifecycle/{first.json()['id']}", headers=auth(token)
    )
    assert fetched.status_code == 200
    assert fetched.json()["status"] == "completed"


def test_audit_anchor_batch_tracks_quorum(client, tmp_path) -> None:
    test_client, app, token = client
    object.__setattr__(app.state.settings, "audit_anchor_directory", str(tmp_path / "anchors"))
    batch = test_client.post(
        "/v1/audit/anchors/batch",
        json={"destinations": ["file"], "required_quorum": 1},
        headers=auth(token),
    )
    assert batch.status_code == 202, batch.text
    body = batch.json()
    assert body["satisfied"] is True
    assert body["verified_count"] == 1
    status = test_client.get(
        f"/v1/audit/anchors/quorum?sequence={body['sequence']}", headers=auth(token)
    )
    assert status.status_code == 200
    assert status.json()["satisfied"] is True


def test_native_protocol_discovery_normalizes_mcp_and_a2a(monkeypatch) -> None:
    from aifence.guard.protocols import discover_protocol_manifest

    class Response:
        def __init__(self, document, *, headers=None):
            import json
            self._document = document
            self.content = json.dumps(document).encode()
            self.headers = headers or {"content-type": "application/json"}
            self.status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return self._document

    class Client:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def post(self, endpoint, **kwargs):
            assert endpoint == "https://mcp.example/rpc"
            assert kwargs["json"]["method"] == "tools/list"
            return Response(
                {"jsonrpc": "2.0", "id": "agentdance-discovery", "result": {
                    "tools": [{"name": "lookup", "description": "Lookup", "inputSchema": {"type": "object"}}]
                }},
                headers={"content-type": "application/json", "MCP-Protocol-Version": "2025-06-18"},
            )

        def get(self, endpoint, **kwargs):
            assert endpoint == "https://a2a.example/.well-known/agent-card.json"
            return Response({"name": "remote-agent", "protocolVersion": "0.3"})

    monkeypatch.setattr("aifence.guard.protocols.httpx.Client", Client)
    mcp, mcp_version, mcp_verification = discover_protocol_manifest(
        protocol="mcp", endpoint="https://mcp.example/rpc", auth_header_name="Authorization",
        auth_value="Bearer test", proxy_url="", max_response_bytes=64_000,
    )
    assert mcp_version == "2025-06-18"
    assert mcp["tools"][0]["name"] == "lookup"
    assert mcp_verification["source"] == "native-discovery"

    a2a, a2a_version, a2a_verification = discover_protocol_manifest(
        protocol="a2a", endpoint="https://a2a.example", auth_header_name=None,
        auth_value=None, proxy_url="https://proxy.example", max_response_bytes=64_000,
    )
    assert a2a_version == "0.3"
    assert a2a["name"] == "remote-agent"
    assert a2a_verification["http_status"] == 200


def test_native_protocol_discovery_rejects_invalid_manifest(monkeypatch) -> None:
    from aifence.guard.errors import ConflictError
    from aifence.guard.protocols import discover_protocol_manifest

    class Response:
        content = b'{"result":{"tools":[{"description":"missing name"}]}}'
        headers = {"content-type": "application/json"}
        status_code = 200

        def raise_for_status(self): return None
        def json(self): return {"result": {"tools": [{"description": "missing name"}]}}

    class Client:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): return None
        def post(self, *args, **kwargs): return Response()

    monkeypatch.setattr("aifence.guard.protocols.httpx.Client", Client)
    try:
        discover_protocol_manifest(
            protocol="mcp", endpoint="https://mcp.example/rpc", auth_header_name=None,
            auth_value=None, proxy_url="", max_response_bytes=64_000,
        )
    except ConflictError as exc:
        assert "descriptor" in str(exc)
    else:
        raise AssertionError("invalid MCP manifest was accepted")


def test_completed_tenant_deletion_preserves_lifecycle_audit_key(client) -> None:
    import asyncio

    test_client, app, token = client
    requested = test_client.post(
        "/v1/tenant/lifecycle",
        json={
            "action": "delete",
            "reason": "qualification deletion",
            "parameters": {"grace_period_days": 0},
            "idempotency_key": "tenant-delete-rc5-0001",
        },
        headers=auth(token),
    )
    assert requested.status_code == 202, requested.text
    job_id = requested.json()["id"]

    result = asyncio.run(app.state.lifecycle_worker.run_once(limit=1))
    assert result.completed == 1, result

    # The requesting key is deliberately retained with lifecycle/audit-only scopes so
    # deletion evidence remains retrievable after the tenant becomes inactive.
    status = test_client.get(f"/v1/tenant/lifecycle/{job_id}", headers=auth(token))
    assert status.status_code == 200, status.text
    assert status.json()["status"] == "completed"

    # The same retained key must not regain ordinary tenant authority.
    providers = test_client.get("/v1/providers", headers=auth(token))
    assert providers.status_code == 403, providers.text


def test_lifecycle_governed_deferral_does_not_consume_attempt_budget(client) -> None:
    import asyncio
    from datetime import datetime

    from aifence.guard.models import LifecycleClaim, TenantLifecycleJob

    test_client, app, token = client
    hold = test_client.post(
        "/v1/tenant/legal-holds",
        json={"scope": "tenant", "reason": "qualification hold"},
        headers=auth(token),
    )
    assert hold.status_code == 201, hold.text
    requested = test_client.post(
        "/v1/tenant/lifecycle",
        json={
            "action": "delete",
            "reason": "defer while held",
            "parameters": {"grace_period_days": 0},
            "idempotency_key": "tenant-delete-deferral-rc5-0001",
        },
        headers=auth(token),
    )
    assert requested.status_code == 202, requested.text
    job_id = requested.json()["id"]

    first = asyncio.run(app.state.lifecycle_worker.run_once(limit=1))
    assert first.retried == 1, first
    with app.state.session_factory() as session:
        claim = session.get(LifecycleClaim, job_id)
        job = session.get(TenantLifecycleJob, job_id)
        assert claim is not None and job is not None
        assert claim.attempts == 0
        assert job.attempt_count == 0

    released = test_client.post(
        f"/v1/tenant/legal-holds/{hold.json()['id']}/release",
        json={"reason": "qualification complete"},
        headers=auth(token),
    )
    assert released.status_code == 200, released.text
    with app.state.session_factory() as session:
        claim = session.get(LifecycleClaim, job_id)
        job = session.get(TenantLifecycleJob, job_id)
        assert claim is not None and job is not None
        claim.available_at = datetime.now(UTC)
        job.available_at = datetime.now(UTC)
        session.commit()

    second = asyncio.run(app.state.lifecycle_worker.run_once(limit=1))
    assert second.completed == 1, second


def test_lifecycle_genuine_failures_stop_at_max_attempts(client) -> None:
    import asyncio
    from datetime import datetime

    from sqlalchemy import select

    from aifence.guard.models import APIKey, LifecycleClaim, TenantLifecycleJob

    _, app, _ = client
    with app.state.session_factory() as session:
        key = session.scalar(select(APIKey).where(APIKey.status == "active"))
        assert key is not None
        now = datetime.now(UTC)
        job_id = "job_rc5_max_attempts"
        session.add(TenantLifecycleJob(
            id=job_id, tenant_id=key.tenant_id, job_type="unsupported-test-job",
            idempotency_key="unsupported-test-job", status="pending", parameters={}, result={},
            requested_by_key_id=key.id, priority=0, max_attempts=1,
            available_at=now, created_at=now, updated_at=now,
        ))
        session.add(LifecycleClaim(
            job_id=job_id, tenant_id=key.tenant_id, job_type="unsupported-test-job",
            status="pending", priority=0, attempts=0, max_attempts=1,
            available_at=now, created_at=now,
        ))
        session.commit()

    first = asyncio.run(app.state.lifecycle_worker.run_once(limit=1))
    assert first.failed == 1, first
    with app.state.session_factory() as session:
        claim = session.get(LifecycleClaim, "job_rc5_max_attempts")
        job = session.get(TenantLifecycleJob, "job_rc5_max_attempts")
        assert claim is not None and job is not None
        assert claim.attempts == 1
        assert claim.status == "dead_lettered"
        assert job.status == "failed"

    second = asyncio.run(app.state.lifecycle_worker.run_once(limit=1))
    assert second.claimed == 0, second
