# SPDX-License-Identifier: AGPL-3.0-or-later
"""Executable contract for the composed AIFENCE fence.

These tests intentionally cross subsystem boundaries.  Unit tests prove each
implementation; this suite proves the product claim that Quality, Guard, Bus,
tenancy and audit semantics compose correctly.
"""
from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select

from aifence.app import create_app
from aifence.bus.bus import SemanticBus
from aifence.bus.config import get_settings as bus_settings
from aifence.bus.db_models import BusMessage
from aifence.core.config import CoreSettings
from aifence.guard.audit import verify_tenant_chain
from aifence.guard.models import Event

GOOD = (
    "# Release Readiness\n\n"
    "The candidate passed all required checks and is ready for controlled deployment. "
    "Rollback ownership and validation criteria are documented for the receiving agent."
)


@pytest.fixture()
def app(tmp_path) -> Iterator[FastAPI]:
    application = create_app(
        CoreSettings(
            environment="test",
            database_url=f"sqlite+pysqlite:///{tmp_path / 'conformance.db'}",
            metrics_public=True,
        )
    )
    yield application
    application.state.flow_breakers.close()
    application.state.engine.dispose()


@pytest.fixture()
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def mint(app: FastAPI, name: str) -> tuple[str, str]:
    with app.state.session_factory() as session:
        tenant, _key, token = app.state.guard_app.state.service.create_tenant_and_key(
            session, tenant_name=name, key_name="conformance", scopes=["*"]
        )
    return str(tenant.id), str(token)


def post_fence(client: TestClient, token: str, **overrides: object) -> dict[str, object]:
    body: dict[str, object] = {
        "artifact": GOOD,
        "content_type": "text/markdown",
        "receiver": "release-agent",
        "action": {"operation": "read"},
        "risk_score": 10,
    }
    body.update(overrides)
    response = client.post(
        "/v1/fence/submit", json=body, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_success_contract_is_claimable_and_auditable(app: FastAPI, client: TestClient) -> None:
    tenant_id, token = mint(app, "Conformance A")
    receipt = post_fence(client, token)

    assert receipt["tenant_id"] == tenant_id
    assert receipt["allowed"] is True
    assert receipt["final_outcome"] == "handed_off"

    quality = receipt["stages"]["quality"]
    assert quality["passed"] is True
    assert quality["mode"] == "admission"
    assert quality["profile"] == "admission/default-v1"
    assert quality["evaluator_version"]

    guard = receipt["stages"]["guard"]
    assert guard["outcome"] in {"allow", "allow_with_limits"}
    assert guard["matched_rule"]
    assert guard["reason_codes"]
    assert all(code.startswith("GUARD_") for code in guard["reason_codes"])

    bus = receipt["stages"]["bus"]
    assert bus["workspace"] == f"tenant:{tenant_id}"
    assert bus["message_id"].startswith("M")

    with app.state.session_factory() as session:
        semantic_bus = SemanticBus(session, bus_settings())
        claimed = semantic_bus.pull(
            receiver="release-agent", workspace=bus["workspace"], claim=True
        )
        assert [message.id for message in claimed] == [bus["message_id"]]
        acknowledged = semantic_bus.ack(
            bus["message_id"], receiver="release-agent", workspace=bus["workspace"]
        )
        assert acknowledged.status == "acked"
        session.commit()

        event = session.scalar(select(Event).where(Event.id == receipt["audit"]["event_id"]))
        assert event is not None
        assert event.event_type == "fence.completed"
        assert event.payload["artifact_sha256"]
        assert GOOD not in str(event.payload)
        verification = verify_tenant_chain(
            session, app.state.guard_app.state.signing_key, tenant_id
        )
        assert verification["valid"] is True


def test_quality_and_guard_blocks_are_explicit_and_audited(app: FastAPI, client: TestClient) -> None:
    _tenant_id, token = mint(app, "Conformance Blocks")

    quality_block = post_fence(client, token, artifact="TODO placeholder")
    assert quality_block["allowed"] is False
    assert quality_block["final_outcome"] == "blocked_by_quality"
    assert "guard" not in quality_block["stages"]
    findings = quality_block["stages"]["quality"]["findings"]
    assert findings
    assert all(item["finding_id"].startswith("AQ-") for item in findings)
    assert quality_block["audit"]["event_id"].startswith("evt_")

    guard_block = post_fence(
        client,
        token,
        action={"operation": "delete", "destructive": True},
        risk_score=80,
    )
    assert guard_block["allowed"] is False
    assert guard_block["final_outcome"] == "blocked_by_guard"
    assert "bus" not in guard_block["stages"]
    assert guard_block["stages"]["guard"]["matched_rule"]
    assert guard_block["stages"]["guard"]["reason_codes"]
    assert guard_block["audit"]["event_id"].startswith("evt_")


def test_anonymous_fence_is_rejected(client: TestClient) -> None:
    response = client.post("/v1/fence/submit", json={"artifact": GOOD})
    assert response.status_code == 401


def test_tenant_handoffs_are_isolated_by_workspace(app: FastAPI, client: TestClient) -> None:
    tenant_a, token_a = mint(app, "Tenant A")
    tenant_b, token_b = mint(app, "Tenant B")
    receipt_a = post_fence(client, token_a, receiver="shared-receiver")
    receipt_b = post_fence(client, token_b, receiver="shared-receiver")

    bus_a = receipt_a["stages"]["bus"]
    bus_b = receipt_b["stages"]["bus"]
    assert bus_a["workspace"] == f"tenant:{tenant_a}"
    assert bus_b["workspace"] == f"tenant:{tenant_b}"
    assert bus_a["workspace"] != bus_b["workspace"]

    with app.state.session_factory() as session:
        semantic_bus = SemanticBus(session, bus_settings())
        a_messages = semantic_bus.pull(
            receiver="shared-receiver", workspace=bus_a["workspace"], claim=False
        )
        b_messages = semantic_bus.pull(
            receiver="shared-receiver", workspace=bus_b["workspace"], claim=False
        )
    assert [message.id for message in a_messages] == [bus_a["message_id"]]
    assert [message.id for message in b_messages] == [bus_b["message_id"]]


def test_bus_idempotency_key_is_bound_to_payload(app: FastAPI) -> None:
    with app.state.session_factory() as session:
        bus = SemanticBus(session, bus_settings())
        first = bus.handoff(
            receiver="worker",
            sender="source",
            workspace="tenant:test",
            content="same content",
            idempotency_key="idem-contract",
        )
        same = bus.handoff(
            receiver="worker",
            sender="source",
            workspace="tenant:test",
            content="same content",
            idempotency_key="idem-contract",
        )
        assert same.id == first.id
        with pytest.raises(ValueError, match="different handoff"):
            bus.handoff(
                receiver="worker",
                sender="source",
                workspace="tenant:test",
                content="changed content",
                idempotency_key="idem-contract",
            )


def test_tampered_bus_wire_fails_closed_on_ack(app: FastAPI) -> None:
    with app.state.session_factory() as session:
        bus = SemanticBus(session, bus_settings())
        message = bus.handoff(
            receiver="worker",
            sender="source",
            workspace="tenant:test",
            content="validated content",
        )
        message_id = message.id
        session.commit()

    with app.state.session_factory() as session:
        message = session.get(BusMessage, message_id)
        assert message is not None
        tampered = dict(message.wire)
        tampered["v"] = 999
        message.wire = tampered
        session.commit()

    with app.state.session_factory() as session:
        bus = SemanticBus(session, bus_settings())
        with pytest.raises((ValueError, TypeError)):
            bus.ack(message_id, receiver="worker", workspace="tenant:test")


def test_request_size_limit_is_enforced_before_fence_execution(tmp_path) -> None:
    application = create_app(
        CoreSettings(
            environment="test",
            database_url=f"sqlite+pysqlite:///{tmp_path / 'small.db'}",
            max_request_bytes=1024,
            metrics_public=True,
        )
    )
    _tenant, token = mint(application, "Small Request")
    try:
        with TestClient(application, headers={"Authorization": f"Bearer {token}"}) as client:
            response = client.post(
                "/v1/fence/submit",
                json={"artifact": "x" * 4096, "action": {"operation": "read"}},
            )
        assert response.status_code == 413
    finally:
        application.state.flow_breakers.close()
        application.state.engine.dispose()
