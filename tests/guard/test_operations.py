# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import httpx
from sqlalchemy import select

from aifence.guard.clamav import ScanResult
from aifence.guard.crypto import EnvelopeCipher
from aifence.guard.models import Artifact
from tests.guard.conftest import agent_registration, auth, decision_payload


def register(client, token: str) -> str:
    response = client.post("/v1/agents/register", json=agent_registration(), headers=auth(token))
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_discovery_events_policy_and_idempotent_decision(client) -> None:
    test_client, app, token = client
    assert test_client.get("/health/live").json() == {"status": "live"}
    ready = test_client.get("/health/ready")
    assert ready.status_code == 200
    assert ready.json() == {"status": "ready"}
    assert test_client.get("/metrics").status_code == 404
    deep_ready = test_client.get("/internal/health/ready")
    assert deep_ready.status_code == 200
    assert deep_ready.json()["dependencies"]["database"] == "ready"
    assert test_client.get("/internal/metrics").status_code == 200

    discovery = test_client.get("/.well-known/aifence.json")
    assert discovery.status_code == 200
    assert discovery.json()["event_spec"] == "aifence.event.v1"
    keys = test_client.get("/.well-known/aifence-signing-keys.json")
    assert keys.status_code == 200
    assert len(keys.json()["keys"]) == 1

    agent_id = register(test_client, token)
    agent = test_client.get(f"/v1/agents/{agent_id}", headers=auth(token))
    assert agent.status_code == 200
    assert agent.json()["status"] == "active"

    event = test_client.post(
        "/v1/events",
        json={
            "trace_id": "trc_event_0000001",
            "parent_event_id": None,
            "event_type": "agent.observation",
            "payload": {"fact": "tool returned 200"},
        },
        headers=auth(token),
    )
    assert event.status_code == 201, event.text
    trace = test_client.get("/v1/traces/trc_event_0000001", headers=auth(token))
    assert trace.status_code == 200
    assert trace.json()[0]["event_type"] == "agent.observation"

    policy = {
        "spec_version": "aifence.policy.v1",
        "version": "tenant-1",
        "default": {
            "outcome": "require_approval",
            "reasons": ["Tenant default requires review"],
            "constraints": {},
        },
        "rules": [
            {
                "id": "tenant-low-risk-read",
                "priority": 7000,
                "match": {"operations": ["read"], "max_risk": 34},
                "effect": {
                    "outcome": "allow",
                    "reasons": ["Tenant authorized read"],
                    "constraints": {"max_records": 50},
                },
            }
        ],
    }
    published = test_client.post(
        "/v1/policies",
        json={"version": "tenant-1", "document": policy, "activate": False},
        headers=auth(token),
    )
    assert published.status_code == 201, published.text
    from aifence.guard.auth import AuthContext

    with app.state.session_factory() as session:
        tenant_id = session.execute(
            __import__("sqlalchemy").text("SELECT id FROM tenants LIMIT 1")
        ).scalar_one()
        _, activator = app.state.service.create_api_key(
            session,
            AuthContext(tenant_id, "bootstrap", frozenset({"*"}), None),
            name="policy-activator",
            scopes=["policies:activate"],
        )
    activated = test_client.post(
        f"/v1/policies/{published.json()['id']}/activate",
        json={"reason": "Independent review completed"},
        headers=auth(activator),
    )
    assert activated.status_code == 200, activated.text
    assert activated.json()["active"] is True
    policies = test_client.get("/v1/policies", headers=auth(token))
    assert policies.status_code == 200
    assert policies.json()[0]["version"] == "tenant-1"

    payload = decision_payload(agent_id)
    payload["idempotency_key"] = "request-00000001"
    first = test_client.post("/v1/decisions", json=payload, headers=auth(token))
    second = test_client.post("/v1/decisions", json=payload, headers=auth(token))
    assert first.status_code == second.status_code == 200
    assert first.json()["decision_id"] == second.json()["decision_id"]
    fetched = test_client.get(
        f"/v1/decisions/{first.json()['decision_id']}", headers=auth(token)
    )
    assert fetched.status_code == 200
    assert fetched.json()["receipt"] == first.json()["receipt"]


def test_approval_listing_get_and_rejection(client) -> None:
    test_client, app, token = client
    agent_id = register(test_client, token)
    payload = decision_payload(agent_id)
    payload["trace_id"] = "trc_rejection_0001"
    payload["action"].update(
        {
            "type": "financial.transaction",
            "tool": "payments.refund",
            "operation": "create",
            "target": "order:78122",
            "destructive": True,
            "reversible": False,
            "external_effect": True,
            "amount_usd": 12.5,
        }
    )
    requested = test_client.post("/v1/decisions", json=payload, headers=auth(token))
    assert requested.status_code == 200
    approval_id = requested.json()["approval_id"]
    assert approval_id

    pending = test_client.get("/v1/approvals?status=pending", headers=auth(token))
    assert pending.status_code == 200
    assert any(row["id"] == approval_id for row in pending.json())
    detail = test_client.get(f"/v1/approvals/{approval_id}", headers=auth(token))
    assert detail.status_code == 200

    from aifence.guard.auth import AuthContext

    with app.state.session_factory() as session:
        tenant_id = session.execute(
            __import__("sqlalchemy").text("SELECT id FROM tenants LIMIT 1")
        ).scalar_one()
        _, approver = app.state.service.create_api_key(
            session,
            AuthContext(tenant_id, "bootstrap", frozenset({"*"}), None),
            name="independent-approver",
            scopes=["*"],
        )
    rejected = test_client.post(
        f"/v1/approvals/{approval_id}/decision",
        json={"decision": "rejected", "reason": "Requested refund lacks evidence"},
        headers=auth(approver),
    )
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "rejected"
    repeated = test_client.post(
        f"/v1/approvals/{approval_id}/decision",
        json={"decision": "approved", "reason": "Second decision is prohibited"},
        headers=auth(approver),
    )
    assert repeated.status_code == 409


def test_capability_revocation(client) -> None:
    test_client, _, token = client
    agent_id = register(test_client, token)
    decision = test_client.post(
        "/v1/decisions", json=decision_payload(agent_id), headers=auth(token)
    ).json()
    issued = test_client.post(
        "/v1/capabilities",
        json={
            "decision_id": decision["decision_id"],
            "max_uses": 2,
            "lifetime_seconds": 60,
        },
        headers=auth(token),
    )
    assert issued.status_code == 201
    capability_id = issued.json()["capability_id"]
    revoked = test_client.post(
        f"/v1/capabilities/{capability_id}/revoke",
        json={"reason": "Task was cancelled"},
        headers=auth(token),
    )
    assert revoked.status_code == 200
    assert revoked.json()["valid"] is False
    consumed = test_client.post(
        "/v1/capabilities/consume",
        json={
            "token": issued.json()["token"],
            "agent_id": agent_id,
            "trace_id": "trc_test_00000001",
            "tool": "orders.read",
            "operation": "read",
            "resource": "order:78122",
            "execution": issued.json()["required_execution"],
        },
        headers=auth(token),
    )
    assert consumed.status_code in {403, 409}


def test_clean_infected_and_unavailable_artifacts(client, monkeypatch) -> None:
    test_client, app, token = client
    monkeypatch.setattr(
        app.state.service.clamav,
        "scan",
        lambda content: ScanResult("clean", None, "stream: OK"),
    )
    clean = test_client.post(
        "/v1/artifacts/scan",
        data={"trace_id": "trc_artifact_clean"},
        files={"artifact": ("report.txt", b"verified output", "text/plain")},
        headers=auth(token),
    )
    assert clean.status_code == 201, clean.text
    clean_id = clean.json()["id"]
    assert clean.json()["scan_status"] == "clean"
    metadata = test_client.get(f"/v1/artifacts/{clean_id}", headers=auth(token))
    assert metadata.status_code == 200
    content = test_client.get(f"/v1/artifacts/{clean_id}/content", headers=auth(token))
    assert content.status_code == 200
    assert content.content == b"verified output"
    assert "sha-256=" in content.headers["digest"]

    monkeypatch.setattr(
        app.state.service.clamav,
        "scan",
        lambda content: ScanResult("infected", "Eicar-Test-Signature", "stream: Eicar FOUND"),
    )
    infected = test_client.post(
        "/v1/artifacts/scan",
        data={"trace_id": "trc_artifact_infected"},
        files={"artifact": ("sample.bin", b"malicious bytes", "application/octet-stream")},
        headers=auth(token),
    )
    assert infected.status_code == 201
    assert infected.json()["quarantined"] is True
    assert infected.json()["scan_result"]["signature"] == "Eicar-Test-Signature"

    monkeypatch.setattr(
        app.state.service.clamav,
        "scan",
        lambda content: (_ for _ in ()).throw(OSError("scanner offline")),
    )
    unavailable = test_client.post(
        "/v1/artifacts/scan",
        data={"trace_id": "trc_artifact_unavailable"},
        files={"artifact": ("unknown.bin", b"unknown", "application/octet-stream")},
        headers=auth(token),
    )
    assert unavailable.status_code == 201
    assert unavailable.json()["scan_status"] == "unavailable"
    incidents = test_client.get("/v1/incidents", headers=auth(token))
    assert incidents.status_code == 200
    assert len(incidents.json()) >= 2


def test_provider_and_tool_brokers_and_lifecycle(client, monkeypatch) -> None:
    test_client, _, token = client
    agent_id = register(test_client, token)

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
    provider_id = provider.json()["id"]
    assert test_client.get("/v1/providers", headers=auth(token)).status_code == 200

    async def forward(*args, **kwargs):
        return httpx.Response(
            200,
            json={"ok": True},
            headers={"content-type": "application/json", "x-request-id": "upstream-1"},
        )

    monkeypatch.setattr("aifence.guard.api._forward_json", forward)
    provider_decision = decision_payload(agent_id)
    provider_decision["trace_id"] = "trc_provider_0001"
    provider_decision["security_context"]["data_classes"] = []
    provider_decision["objective"]["approved_scope"] = [
        "https://api.openai.com/v1/models"
    ]
    invoked = test_client.post(
        f"/v1/providers/{provider_id}/invoke",
        json={
            "decision": provider_decision,
            "path": "/v1/models",
            "body": {"model": "validated-model", "stream": False},
            "query": {},
            "idempotency_key": "provider-invoke-0001",
        },
        headers=auth(token),
    )
    assert invoked.status_code == 200, invoked.text
    assert invoked.json()["body"] == {"ok": True}
    assert invoked.json()["decision_id"]

    tool = test_client.post(
        "/v1/tools",
        json={
            "name": "orders.read",
            "base_url": "https://api.openai.com",
            "auth_header_name": "X-Tool-Key",
            "auth_value": "tool-secret",
            "allowed_operations": {
                "read": {"method": "GET", "paths": ["/orders/*"]}
            },
        },
        headers=auth(token),
    )
    assert tool.status_code == 201, tool.text
    tool_id = tool.json()["id"]
    assert test_client.get("/v1/tools", headers=auth(token)).status_code == 200

    tool_decision = decision_payload(agent_id)
    tool_decision["trace_id"] = "trc_tool_0000001"
    tool_decision["action"]["arguments"] = {
        "method": "GET",
        "path": "/orders/78122",
        "body": None,
        "query": {},
    }
    decision = test_client.post(
        "/v1/decisions", json=tool_decision, headers=auth(token)
    ).json()
    capability = test_client.post(
        "/v1/capabilities",
        json={
            "decision_id": decision["decision_id"],
            "max_uses": 1,
            "lifetime_seconds": 60,
        },
        headers=auth(token),
    ).json()
    executed = test_client.post(
        f"/v1/tools/{tool_id}/execute",
        json={
            "capability_token": capability["token"],
            "trace_id": "trc_tool_0000001",
            "agent_id": agent_id,
            "operation": "read",
            "resource": "order:78122",
            **capability["required_execution"],
            "idempotency_key": "tool-execute-0001",
        },
        headers=auth(token),
    )
    assert executed.status_code == 200, executed.text
    assert executed.json()["body"] == {"ok": True}

    revoked_tool = test_client.post(
        f"/v1/tools/{tool_id}/revoke",
        json={"reason": "Tool integration retired"},
        headers=auth(token),
    )
    assert revoked_tool.status_code == 200
    assert revoked_tool.json()["status"] == "revoked"
    revoked_provider = test_client.post(
        f"/v1/providers/{provider_id}/revoke",
        json={"reason": "Provider integration retired"},
        headers=auth(token),
    )
    assert revoked_provider.status_code == 200
    assert revoked_provider.json()["status"] == "revoked"


def test_rotation_and_retention_maintenance(client, monkeypatch) -> None:
    test_client, app, token = client
    monkeypatch.setattr(
        app.state.service.clamav,
        "scan",
        lambda content: ScanResult("clean", None, "stream: OK"),
    )
    artifact = test_client.post(
        "/v1/artifacts/scan",
        data={"trace_id": "trc_maintenance_1"},
        files={"artifact": ("retire.txt", b"retained", "text/plain")},
        headers=auth(token),
    )
    assert artifact.status_code == 201
    provider = test_client.post(
        "/v1/providers",
        json={
            "name": "maintenance-provider",
            "base_url": "https://api.openai.com",
            "auth_header_name": "Authorization",
            "auth_value": "provider-secret",
            "allowed_paths": ["/v1/*"],
        },
        headers=auth(token),
    )
    assert provider.status_code == 201
    tool = test_client.post(
        "/v1/tools",
        json={
            "name": "maintenance-tool",
            "base_url": "https://api.openai.com",
            "auth_header_name": "Authorization",
            "auth_value": "tool-secret",
            "allowed_operations": {"read": {"method": "GET", "paths": ["/v1/*"]}},
        },
        headers=auth(token),
    )
    assert tool.status_code == 201

    app.state.service.cipher = EnvelopeCipher(
        active_key_id="master-v2",
        keyring={"master-v1": bytes.fromhex("1f" * 32), "master-v2": bytes.fromhex("2f" * 32)},
    )
    with app.state.session_factory() as session:
        counts = app.state.service.reencrypt_stored_secrets(session, batch_size=1)
        # RC4 writes secrets directly into tenant-specific envelopes, so rotating the
        # legacy root key has no records to migrate.
        assert counts == {"memory": 0, "artifacts": 0, "providers": 0, "tools": 0, "protocols": 0}
        second = app.state.service.reencrypt_stored_secrets(session, batch_size=10)
        assert second == {"memory": 0, "artifacts": 0, "providers": 0, "tools": 0, "protocols": 0}
        row = session.scalar(select(Artifact).where(Artifact.id == artifact.json()["id"]))
        assert row is not None
        row.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        session.commit()
        pruned = app.state.service.prune_expired_artifacts(session, batch_size=1)
        assert pruned == {"artifacts_deleted": 1, "tenants_affected": 1}


def test_public_source_and_license_discovery(client) -> None:
    test_client, _, _ = client
    response = test_client.get("/source")
    assert response.status_code == 200
    document = response.json()
    assert document["server_license"] == "AGPL-3.0-only OR commercial"
    assert document["sdk_license"] == "Apache-2.0"
    assert document["source_code_url"].startswith("https://")

    discovery = test_client.get("/.well-known/aifence.json").json()
    assert discovery["source_code_url"] == document["source_code_url"]
    assert discovery["commercial_license_url"] == document["commercial_license_url"]

    contract = test_client.get("/openapi.json").json()
    assert contract["info"]["license"]["identifier"] == "Apache-2.0"
    assert contract["info"]["x-aifence-server-license"] == "AGPL-3.0-only OR commercial"
    assert contract["paths"]["/source"]["get"]["security"] == []
