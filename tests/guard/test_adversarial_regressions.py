# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import asyncio
import io
import zipfile
from typing import Any

import httpx
from fastapi.testclient import TestClient
from starlette.types import Message, Receive, Scope, Send

from aifence.guard.application import create_app
from aifence.guard.clamav import ScanResult
from aifence.guard.config import Settings
from aifence.guard.crypto import SigningKey
from aifence.guard.middleware import RequestSizeMiddleware
from tests.guard.conftest import agent_registration, auth, decision_payload


def _register(test_client: TestClient, token: str) -> str:
    response = test_client.post(
        "/v1/agents/register", json=agent_registration(), headers=auth(token)
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_decision_key_identity_bindings_reject_spoofed_context(client) -> None:
    test_client, _, administrator = client
    agent_id = _register(test_client, administrator)
    key = test_client.post(
        "/v1/api-keys",
        json={
            "name": "bound-runtime",
            "scopes": ["decisions:write"],
            "bound_agent_id": agent_id,
            "bound_workload_identity": "spiffe://test/agents/refund-agent",
            "bound_instance_id": "instance-1",
            "bound_principal_type": "human",
            "bound_principal_id": "user-1",
        },
        headers=auth(administrator),
    )
    assert key.status_code == 201, key.text
    runtime_token = key.json()["api_key"]

    unbound = test_client.post(
        "/v1/api-keys",
        json={"name": "unbound-runtime", "scopes": ["decisions:write"]},
        headers=auth(administrator),
    )
    assert unbound.status_code == 201
    incomplete = test_client.post(
        "/v1/decisions",
        json={**decision_payload(agent_id), "trace_id": "trc_unbound_runtime"},
        headers=auth(unbound.json()["api_key"]),
    )
    assert incomplete.status_code == 403
    assert "agent_id" in incomplete.json()["error"]["details"]["missing_bindings"]

    accepted = test_client.post(
        "/v1/decisions", json=decision_payload(agent_id), headers=auth(runtime_token)
    )
    assert accepted.status_code == 200, accepted.text

    spoofed = decision_payload(agent_id)
    spoofed["trace_id"] = "trc_identity_spoof"
    spoofed["agent"]["instance_id"] = "attacker-instance"
    spoofed["principal"]["id"] = "another-user"
    rejected = test_client.post(
        "/v1/decisions", json=spoofed, headers=auth(runtime_token)
    )
    assert rejected.status_code == 403
    assert set(rejected.json()["error"]["details"]["mismatches"]) == {
        "instance_id",
        "principal_id",
    }


def test_provider_redaction_is_applied_and_idempotent(client, monkeypatch) -> None:
    test_client, _, token = client
    agent_id = _register(test_client, token)
    provider = test_client.post(
        "/v1/providers",
        json={
            "name": "orders.read",
            "base_url": "https://api.openai.com",
            "auth_header_name": "Authorization",
            "auth_value": "Bearer provider-secret",
            "allowed_paths": ["/v1/*"],
        },
        headers=auth(token),
    )
    assert provider.status_code == 201, provider.text

    forwarded: list[dict[str, Any]] = []

    async def capture_forward(*args: Any, **kwargs: Any) -> httpx.Response:
        forwarded.append(kwargs)
        return httpx.Response(
            200,
            json={"ok": True},
            headers={"content-type": "application/json"},
        )

    monkeypatch.setattr("aifence.guard.api._forward_json", capture_forward)
    decision = decision_payload(agent_id)
    decision["trace_id"] = "trc_redaction_0001"
    decision["security_context"]["data_classes"] = []
    decision["objective"]["approved_scope"] = ["https://api.openai.com/v1/responses"]
    request = {
        "decision": decision,
        "path": "/v1/responses",
        "body": {
            "model": "validated-model",
            "input": "Summarize the ticket",
            "password": "ordinary-non-pattern-value",
            "stream": False,
        },
        "query": {},
        "idempotency_key": "redaction-idempotency-0001",
    }
    first = test_client.post(
        f"/v1/providers/{provider.json()['id']}/invoke",
        json=request,
        headers=auth(token),
    )
    assert first.status_code == 200, first.text
    second = test_client.post(
        f"/v1/providers/{provider.json()['id']}/invoke",
        json=request,
        headers=auth(token),
    )
    assert second.status_code == 200, second.text
    assert len(forwarded) == 1
    assert forwarded[0]["body"]["password"] == "[REDACTED_BY_AIFENCE]"
    assert first.json()["execution_id"] == second.json()["execution_id"]


def test_rotating_invalid_bearer_tokens_share_network_rate_limit(tmp_path) -> None:
    settings = Settings(
        environment="test",
        database_url=f"sqlite+pysqlite:///{tmp_path / 'rate.db'}",
        auto_create_schema=True,
        docs_enabled=False,
        rate_limit_per_minute=1,
        provider_allowed_hosts=("api.openai.com",),
        tool_allowed_hosts=("api.openai.com",),
        artifact_store_path=str(tmp_path / "artifacts"),
    )
    app = create_app(settings, SigningKey.ephemeral_for_tests())
    with TestClient(app) as test_client:
        first = test_client.get("/v1/api-keys", headers=auth("invalid-one"))
        second = test_client.get("/v1/api-keys", headers=auth("invalid-two"))
    app.state.engine.dispose()
    assert first.status_code == 401
    assert second.status_code == 429


def test_streamed_body_limit_rejects_chunked_oversize() -> None:
    async def consuming_app(scope: Scope, receive: Receive, send: Send) -> None:
        while True:
            message = await receive()
            if not message.get("more_body", False):
                break
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    middleware = RequestSizeMiddleware(consuming_app, max_bytes=8, max_artifact_bytes=16)
    messages = iter(
        [
            {"type": "http.request", "body": b"12345", "more_body": True},
            {"type": "http.request", "body": b"67890", "more_body": False},
        ]
    )
    sent: list[Message] = []

    async def receive() -> Message:
        return next(messages)

    async def send(message: Message) -> None:
        sent.append(message)

    scope: Scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/v1/decisions",
        "raw_path": b"/v1/decisions",
        "query_string": b"",
        "headers": [(b"transfer-encoding", b"chunked")],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
        "root_path": "",
    }
    asyncio.run(middleware(scope, receive, send))
    assert sent[0]["type"] == "http.response.start"
    assert sent[0]["status"] == 413


def test_archive_traversal_is_quarantined(client, monkeypatch) -> None:
    test_client, app, token = client
    monkeypatch.setattr(
        app.state.service.clamav,
        "scan",
        lambda content: ScanResult("clean", None, "stream: OK"),
    )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("../escape.txt", "do not extract")
    response = test_client.post(
        "/v1/artifacts/scan",
        data={"trace_id": "trc_archive_traversal"},
        files={"artifact": ("payload.zip", buffer.getvalue(), "application/zip")},
        headers=auth(token),
    )
    assert response.status_code == 201, response.text
    assert response.json()["quarantined"] is True
    categories = {
        finding["category"]
        for finding in response.json()["scan_result"]["content_analysis"]["findings"]
    }
    assert "archive.path_traversal" in categories


def test_audit_checkpoint_endpoint_and_openapi_security(tmp_path) -> None:
    settings = Settings(
        environment="test",
        database_url=f"sqlite+pysqlite:///{tmp_path / 'audit.db'}",
        auto_create_schema=True,
        docs_enabled=True,
        rate_limit_per_minute=1000,
        audit_checkpoint_interval=1,
        provider_allowed_hosts=("api.openai.com",),
        tool_allowed_hosts=("api.openai.com",),
        artifact_store_path=str(tmp_path / "artifacts"),
    )
    app = create_app(settings, SigningKey.ephemeral_for_tests())
    with app.state.session_factory() as session:
        _, _, token = app.state.service.create_tenant_and_key(
            session,
            tenant_name="Audit Tenant",
            key_name="administrator",
            scopes=["*"],
        )
    with TestClient(app) as test_client:
        _register(test_client, token)
        verification = test_client.get("/v1/audit/verify", headers=auth(token))
        checkpoints = test_client.get("/v1/audit/checkpoints", headers=auth(token))
        contract = test_client.get("/openapi.json").json()
    app.state.engine.dispose()

    assert verification.status_code == 200
    assert verification.json()["valid"] is True
    assert checkpoints.status_code == 200
    assert checkpoints.json()
    schemes = contract["components"]["securitySchemes"]
    assert schemes["AifenceBearer"]["scheme"] == "bearer"
    assert schemes["MutualTLS"]["type"] == "mutualTLS"
    protected = contract["paths"]["/v1/decisions"]["post"]
    assert protected["security"] == [{"AifenceBearer": [], "MutualTLS": []}, {"SPIFFEWorkload": []}]
    assert "429" in protected["responses"]
    assert not any(
        parameter.get("name", "").lower() == "authorization"
        for parameter in protected.get("parameters", [])
    )
