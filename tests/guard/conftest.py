# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from aifence.guard.application import create_app
from aifence.guard.config import Settings
from aifence.guard.crypto import SigningKey


@pytest.fixture()
def app_and_key(tmp_path) -> Generator[tuple[object, str], None, None]:
    database = tmp_path / "aifence-test.db"
    settings = Settings(
        environment="test",
        database_url=f"sqlite+pysqlite:///{database}",
        auto_create_schema=True,
        docs_enabled=True,
        rate_limit_per_minute=10000,
        max_request_bytes=2 * 1024 * 1024,
        provider_allowed_hosts=("api.openai.com",),
        tool_allowed_hosts=("api.openai.com",),
        artifact_store_path=str(tmp_path / "artifacts"),
        internal_cidrs=("127.0.0.0/8",),
    )
    app = create_app(settings, SigningKey.ephemeral_for_tests())
    with app.state.session_factory() as session:
        _, _, token = app.state.service.create_tenant_and_key(
            session,
            tenant_name="Test Tenant",
            key_name="administrator-one",
            scopes=["*"],
        )
    yield app, token
    app.state.engine.dispose()


@pytest.fixture()
def client(app_and_key) -> Generator[tuple[TestClient, object, str], None, None]:
    app, token = app_and_key
    with TestClient(app) as test_client:
        yield test_client, app, token


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def agent_registration() -> dict[str, object]:
    return {
        "external_id": "refund-agent",
        "name": "Refund Agent",
        "version": "1.0.0",
        "workload_identity": "spiffe://test/agents/refund-agent",
        "model": "provider/model",
        "instruction_hash": "a" * 64,
        "allowed_tools": ["orders.read", "payments.refund"],
        "allowed_data_classes": ["customer", "financial"],
        "metadata": {"owner": "payments-security"},
    }


def decision_payload(agent_id: str, **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "trace_id": "trc_test_00000001",
        "principal": {
            "type": "human",
            "id": "user-1",
            "authorization_context": ["support-tier-2"],
        },
        "agent": {
            "id": agent_id,
            "instance_id": "instance-1",
            "version": "1.0.0",
            "workload_identity": "spiffe://test/agents/refund-agent",
            "model": "provider/model",
            "instruction_hash": "a" * 64,
        },
        "objective": {
            "declared_goal": "Inspect order 78122",
            "approved_scope": ["order:78122"],
            "delegation_depth": 0,
        },
        "action": {
            "type": "tool.call",
            "tool": "orders.read",
            "operation": "read",
            "target": "order:78122",
            "arguments": {"order_id": "78122"},
            "destructive": False,
            "reversible": True,
            "external_effect": False,
        },
        "security_context": {
            "data_classes": ["customer"],
            "credential_scope": ["orders:read"],
            "environment": "production",
            "labels": {},
        },
    }
    payload.update(overrides)
    return payload
