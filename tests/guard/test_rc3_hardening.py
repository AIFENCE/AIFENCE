# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import base64
import copy
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient

from aifence.guard.audit_anchor import WebhookAnchorBackend, build_anchor_envelope
from aifence.guard.auth import AuthContext
from aifence.guard.crypto import SigningKey, canonical_json, parse_api_key
from aifence.guard.errors import ConflictError
from aifence.guard.key_management import ManagedEnvelopeCipher
from aifence.guard.models import APIKey, BudgetReservation, DispatchClaim, Execution, OutboxMessage
from tests.guard.conftest import agent_registration, auth, decision_payload


def _register(client: TestClient, token: str, suffix: str = "") -> dict[str, object]:
    body = copy.deepcopy(agent_registration())
    if suffix:
        body["external_id"] = f"agent-{suffix}"
        body["name"] = f"Agent {suffix}"
        body["workload_identity"] = f"spiffe://test/agents/{suffix}"
        body["instruction_hash"] = suffix[0] * 64
    response = client.post("/v1/agents/register", json=body, headers=auth(token))
    assert response.status_code == 201, response.text
    return response.json()


def test_managed_kms_routes_only_to_immutable_allowlisted_providers() -> None:
    class FakeProvider:
        def __init__(self, key_id: str) -> None:
            self.key_id = key_id
            self.wrap_calls = 0
            self.unwrap_calls = 0

        def wrap(self, plaintext_key: bytes, *, context: bytes) -> bytes:
            self.wrap_calls += 1
            return self.key_id.encode() + b":" + plaintext_key

        def unwrap(self, wrapped_key: bytes, *, context: bytes) -> bytes:
            self.unwrap_calls += 1
            prefix = self.key_id.encode() + b":"
            if not wrapped_key.startswith(prefix):
                raise ValueError("wrong provider")
            return wrapped_key[len(prefix):]

    active = FakeProvider("key-a")
    historical = FakeProvider("key-b")
    cipher = ManagedEnvelopeCipher(
        providers={"key-a": active, "key-b": historical}, active_key_id="key-a"
    )
    encrypted = cipher.encrypt(b"secret", context=b"tenant:artifact")
    assert cipher.decrypt(encrypted, context=b"tenant:artifact") == b"secret"
    assert active.wrap_calls == 1 and active.unwrap_calls == 1
    assert historical.wrap_calls == historical.unwrap_calls == 0

    tampered = bytearray(encrypted)
    key_length = int.from_bytes(tampered[4:6], "big")
    assert key_length == len("key-a")
    tampered[6:6 + key_length] = b"key-z"
    with pytest.raises(ValueError, match="unapproved key"):
        cipher.decrypt(bytes(tampered), context=b"tenant:artifact")
    assert cipher.provider is active


def test_budget_settlement_cannot_exceed_reservation_or_settle_expired(client) -> None:
    test_client, app, token = client
    budget = test_client.post(
        "/v1/budgets",
        json={"scope_type": "trace", "scope_id": "trc_rc3_budget", "limits": {"amount_usd": 10}},
        headers=auth(token),
    )
    assert budget.status_code == 201, budget.text
    reserved = test_client.post(
        f"/v1/budgets/{budget.json()['id']}/reserve",
        json={
            "trace_id": "trc_rc3_budget",
            "idempotency_key": "rc3-budget-reserve-1",
            "amounts": {"amount_usd": 5},
            "lifetime_seconds": 60,
        },
        headers=auth(token),
    )
    assert reserved.status_code == 201, reserved.text
    over = test_client.post(
        f"/v1/budget-reservations/{reserved.json()['id']}/settle",
        json={"action": "commit", "actual_amounts": {"amount_usd": 6}, "reason": "invalid overage"},
        headers=auth(token),
    )
    assert over.status_code == 403, over.text

    expired = test_client.post(
        f"/v1/budgets/{budget.json()['id']}/reserve",
        json={
            "trace_id": "trc_rc3_budget",
            "idempotency_key": "rc3-budget-reserve-2",
            "amounts": {"amount_usd": 1},
            "lifetime_seconds": 60,
        },
        headers=auth(token),
    )
    with app.state.session_factory() as session:
        row = session.get(BudgetReservation, expired.json()["id"])
        row.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        session.commit()
    result = test_client.post(
        f"/v1/budget-reservations/{expired.json()['id']}/settle",
        json={"action": "release", "reason": "expired reservation"},
        headers=auth(token),
    )
    assert result.status_code == 409, result.text


def test_canary_cohort_is_stable_across_caller_chosen_trace_ids(client) -> None:
    test_client, app, token = client
    agent = _register(test_client, token)
    document = copy.deepcopy(app.state.service.policy_engine.baseline)
    document["version"] = "rc3-canary"
    published = test_client.post(
        "/v1/policies",
        json={"version": "rc3-canary", "document": document, "activate": False},
        headers=auth(token),
    )
    rollout_key = test_client.post(
        "/v1/api-keys",
        json={"name": "rollout-controller", "scopes": ["policies:read", "policies:activate"]},
        headers=auth(token),
    ).json()["api_key"]
    canary = test_client.post(
        f"/v1/policies/{published.json()['id']}/canary",
        json={"percentage": 50, "reason": "stable cohort test"},
        headers=auth(rollout_key),
    )
    assert canary.status_code == 200, canary.text

    versions: list[str] = []
    for index in range(10):
        request = decision_payload(str(agent["id"]))
        request["trace_id"] = f"trc_canary_trace_{index:02d}"
        request["idempotency_key"] = f"canary-decision-{index:02d}"
        response = test_client.post("/v1/decisions", json=request, headers=auth(token))
        assert response.status_code == 200, response.text
        versions.append(response.json()["policy_version"])
    assert len(set(versions)) == 1


def test_a2a_authorization_is_idempotent_and_consumes_delegated_authority(client) -> None:
    test_client, _, token = client
    parent = _register(test_client, token, "p")
    child = _register(test_client, token, "c")
    grant = test_client.post(
        "/v1/delegations",
        json={
            "parent_agent_id": parent["id"],
            "child_agent_id": child["id"],
            "trace_id": "trc_rc3_a2a_0001",
            "objective": "Read one order",
            "allowed_tools": ["orders.read"],
            "allowed_data_classes": ["customer"],
            "resource_patterns": ["order:123"],
            "max_depth": 1,
            "max_fanout": 1,
            "budget_limits": {"messages": 1, "steps": 2, "tool_calls": 1},
            "expires_at": (datetime.now(UTC) + timedelta(minutes=10)).isoformat(),
        },
        headers=auth(token),
    )
    registration = test_client.post(
        "/v1/protocols",
        json={
            "protocol": "a2a",
            "external_id": "child-agent",
            "agent_id": child["id"],
            "endpoint": "https://api.openai.com/a2a",
            "manifest": {"version": "0.3", "tasks": ["read-order"]},
        },
        headers=auth(token),
    )
    body = {
        "delegation_grant_id": grant.json()["id"],
        "trace_id": "trc_rc3_a2a_0001",
        "task_id": "task-123",
        "objective": "Read one order",
        "tool": "orders.read",
        "resource": "order:123",
        "data_classes": ["customer"],
        "step_count": 1,
        "budget_amounts": {"tool_calls": 1},
        "message": {"role": "user", "content": "read order 123"},
        "artifacts": [],
        "idempotency_key": "rc3-a2a-task-001",
    }
    endpoint = f"/v1/protocols/a2a/{registration.json()['id']}/authorize"
    over_depth = test_client.post(
        endpoint,
        json={**body, "task_id": "task-depth", "idempotency_key": "rc3-a2a-depth-001",
              "delegation_depth": 2},
        headers=auth(token),
    )
    assert over_depth.status_code == 403
    first = test_client.post(endpoint, json=body, headers=auth(token))
    replay = test_client.post(endpoint, json=body, headers=auth(token))
    assert first.status_code == replay.status_code == 200
    assert first.json()["receipt"] == replay.json()["receipt"]

    second = test_client.post(
        endpoint,
        json={**body, "task_id": "task-124", "idempotency_key": "rc3-a2a-task-002"},
        headers=auth(token),
    )
    assert second.status_code == 403
    outside = test_client.post(
        endpoint,
        json={**body, "task_id": "task-125", "idempotency_key": "rc3-a2a-task-003", "resource": "order:999"},
        headers=auth(token),
    )
    assert outside.status_code == 403


def test_signed_webhook_anchor_requires_remote_readback_and_nonce(tmp_path: Path) -> None:
    remote_private = Ed25519PrivateKey.generate()
    public_file = tmp_path / "anchor-public.pem"
    public_file.write_bytes(remote_private.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    ))
    local = SigningKey.ephemeral_for_tests()
    envelope = build_anchor_envelope(
        local,
        tenant_id="ten_1",
        sequence=7,
        chain_head="a" * 64,
        destination="webhook",
        previous_receipt_id="receipt-6",
    )
    unsigned = {
        "receipt_id": "receipt-7",
        "tenant_id": "ten_1",
        "sequence": 7,
        "chain_head": "a" * 64,
        "stored_at": datetime.now(UTC).isoformat(),
        "nonce": envelope["nonce"],
        "previous_receipt_id": "receipt-6",
        "key_id": "anchor-key-1",
    }
    signature = base64.urlsafe_b64encode(remote_private.sign(canonical_json(unsigned))).rstrip(b"=").decode()
    receipt = {**unsigned, "signature": signature}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            return httpx.Response(200, json=receipt, request=request)
        return httpx.Response(200, json=receipt, request=request)

    backend = WebhookAnchorBackend(
        "https://evidence.example/anchors",
        "token",
        "https://evidence.example/receipts",
        str(public_file),
        ("anchor-key-1",),
    )
    backend.client.close()
    backend.client = httpx.Client(transport=httpx.MockTransport(handler))
    published = backend.publish(envelope)
    assert backend.verify(envelope, published)
    changed = {**published, "nonce": "attacker-controlled-nonce"}
    assert not backend.verify(envelope, changed)
    wrong_key_backend = WebhookAnchorBackend(
        "https://evidence.example/anchors", "token",
        "https://evidence.example/receipts", str(public_file), ("anchor-key-2",),
    )
    wrong_key_backend.client.close()
    wrong_key_backend.client = httpx.Client(transport=httpx.MockTransport(handler))
    with pytest.raises(RuntimeError, match="invalid signed receipt"):
        wrong_key_backend.publish(envelope)
    wrong_key_backend.client.close()
    backend.client.close()


def test_anchor_readback_percent_encodes_signed_receipt_identifier(tmp_path: Path) -> None:
    remote_private = Ed25519PrivateKey.generate()
    public_file = tmp_path / "anchor-public.pem"
    public_file.write_bytes(remote_private.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    ))
    envelope = build_anchor_envelope(
        SigningKey.ephemeral_for_tests(), tenant_id="ten_1", sequence=1,
        chain_head="b" * 64, destination="webhook",
    )
    unsigned = {
        "receipt_id": "receipt/with?delimiters", "tenant_id": "ten_1", "sequence": 1,
        "chain_head": "b" * 64, "stored_at": datetime.now(UTC).isoformat(),
        "nonce": envelope["nonce"], "previous_receipt_id": None, "key_id": "anchor-key-1",
    }
    signature = base64.urlsafe_b64encode(remote_private.sign(canonical_json(unsigned))).rstrip(b"=").decode()
    receipt = {**unsigned, "signature": signature}
    paths: list[str] = []
    def handler(request: httpx.Request) -> httpx.Response:
        paths.append(request.url.raw_path.decode())
        return httpx.Response(200, json=receipt, request=request)
    backend = WebhookAnchorBackend(
        "https://evidence.example/anchors", "token", "https://evidence.example/receipts",
        str(public_file), ("anchor-key-1",),
    )
    backend.client.close()
    backend.client = httpx.Client(transport=httpx.MockTransport(handler))
    published = backend.publish(envelope)
    assert backend.verify(envelope, published)
    assert paths[-1].endswith("/receipt%2Fwith%3Fdelimiters")
    backend.client.close()


def test_stale_dispatcher_fencing_token_cannot_finalize(client) -> None:
    test_client, app, token = client
    agent = _register(test_client, token)
    provider = test_client.post(
        "/v1/providers",
        json={
            "name": "orders.read",
            "base_url": "https://api.openai.com",
            "auth_header_name": "Authorization",
            "auth_value": "Bearer upstream",
            "allowed_paths": ["/v1/*"],
        },
        headers=auth(token),
    )
    object.__setattr__(app.state.settings, "dispatch_mode", "async")
    request = decision_payload(str(agent["id"]))
    request["trace_id"] = "trc_rc3_fencing_01"
    request["objective"]["approved_scope"] = ["https://api.openai.com/v1/read"]
    queued = test_client.post(
        f"/v1/providers/{provider.json()['id']}/invoke",
        json={
            "decision": request,
            "path": "/v1/read",
            "body": {"order": "1"},
            "query": {},
            "idempotency_key": "rc3-fencing-request",
        },
        headers=auth(token),
    )
    assert queued.status_code == 202, queued.text
    execution_id = queued.json()["execution_id"]
    key_id, _ = parse_api_key(token)
    with app.state.session_factory() as session:
        tenant_id = session.get(APIKey, key_id).tenant_id
        execution = session.get(Execution, execution_id)
        message = session.scalar(__import__("sqlalchemy").select(OutboxMessage).where(OutboxMessage.aggregate_id == execution_id))
        claim = session.get(DispatchClaim, message.id)
        execution.state = "dispatching"
        execution.fencing_token = 2
        message.fencing_token = 2
        claim.fencing_token = 2
        session.commit()
        internal = AuthContext(tenant_id=tenant_id, key_id="worker:test", scopes=frozenset({"*"}))
        with pytest.raises(ConflictError, match="fencing token"):
            app.state.service.finalize_execution_success(
                session,
                internal,
                execution_id,
                status_code=200,
                headers={},
                body={"ok": True},
                response_hash="b" * 64,
                expected_fencing_token=1,
            )
