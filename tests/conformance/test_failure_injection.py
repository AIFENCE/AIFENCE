from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import aifence.flow as flow
from aifence.app import create_app
from aifence.core.config import CoreSettings
from aifence.guard.auth import FULL_ADMIN_SCOPES


def _client(tmp_path, *, fail_open: tuple[str, ...] = ()) -> tuple[TestClient, object]:
    suffix = "-".join(fail_open) or "closed"
    app = create_app(
        CoreSettings(
            environment="test",
            database_url=f"sqlite+pysqlite:///{tmp_path / f'failure-{suffix}.db'}",
            flow_fail_open_tiers=fail_open,
            flow_failure_threshold=1,
            flow_recovery_seconds=60,
        )
    )
    with app.state.session_factory() as session:
        _, _, token = app.state.guard_app.state.service.create_tenant_and_key(
            session,
            tenant_name="Failure Injection",
            key_name="test",
            scopes=FULL_ADMIN_SCOPES,
        )
    return TestClient(app, headers={"Authorization": f"Bearer {token}"}), app


def _payload() -> dict[str, object]:
    return {
        "artifact": (
            "# Safe artifact\n\n"
            "This controlled handoff is complete and ready for receiver validation."
        ),
        "content_type": "text/markdown",
        "receiver": "receiver",
        "action": {"operation": "read"},
        "risk_score": 10,
    }


def _allow_quality(_request: object) -> dict[str, object]:
    return {
        "tier": "quality",
        "passed": True,
        "score": 100,
        "mode": "admission",
        "profile": "test",
        "outcome": "pass",
    }


def _allow_guard(*_args: object) -> dict[str, object]:
    return {
        "tier": "guard",
        "outcome": "allow",
        "reason_codes": ["TEST_ALLOW"],
        "reasons": [],
        "constraints": {},
        "policy_version": "test",
        "matched_rule": "test",
        "signals": [],
        "explain": {},
    }


def _raise_runtime(message: str):
    def raise_error(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError(message)

    return raise_error


def test_quality_exception_fails_closed_by_default(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, app = _client(tmp_path)
    monkeypatch.setattr(flow, "_run_quality", _raise_runtime("quality offline"))
    with client as active_client:
        response = active_client.post("/v1/fence/submit", json=_payload())
    assert response.status_code == 503
    app.state.engine.dispose()


def test_quality_exception_can_degrade_only_when_explicitly_configured(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, app = _client(tmp_path, fail_open=("quality",))
    monkeypatch.setattr(flow, "_run_quality", _raise_runtime("quality offline"))
    monkeypatch.setattr(flow, "_run_guard", _allow_guard)
    monkeypatch.setattr(
        flow,
        "_run_bus",
        lambda *_args: {
            "tier": "bus",
            "receiver": "receiver",
            "message_id": "msg-test",
            "delivered": True,
        },
    )
    with client as active_client:
        response = active_client.post("/v1/fence/submit", json=_payload())

    body = response.json()
    assert response.status_code == 200
    assert body["allowed"] is True
    assert body["degraded_tiers"] == ["quality"]
    app.state.engine.dispose()


def test_guard_exception_is_always_fail_closed(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, app = _client(tmp_path, fail_open=("quality", "bus"))
    monkeypatch.setattr(flow, "_run_quality", _allow_quality)
    monkeypatch.setattr(flow, "_run_guard", _raise_runtime("guard offline"))
    with client as active_client:
        response = active_client.post("/v1/fence/submit", json=_payload())
    assert response.status_code == 503
    app.state.engine.dispose()


def test_bus_exception_fails_closed_unless_bus_fail_open_is_explicit(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, app = _client(tmp_path)
    monkeypatch.setattr(flow, "_run_quality", _allow_quality)
    monkeypatch.setattr(flow, "_run_guard", _allow_guard)
    monkeypatch.setattr(flow, "_run_bus", _raise_runtime("bus offline"))
    with client as active_client:
        response = active_client.post("/v1/fence/submit", json=_payload())
    assert response.status_code == 503
    app.state.engine.dispose()

    client, app = _client(tmp_path, fail_open=("bus",))
    monkeypatch.setattr(flow, "_run_quality", _allow_quality)
    monkeypatch.setattr(flow, "_run_guard", _allow_guard)
    monkeypatch.setattr(flow, "_run_bus", _raise_runtime("bus offline"))
    with client as active_client:
        response = active_client.post("/v1/fence/submit", json=_payload())

    body = response.json()
    assert response.status_code == 200
    assert body["allowed"] is True
    assert body["final_outcome"] == "authorized_not_delivered"
    assert "bus" in body["degraded_tiers"]
    app.state.engine.dispose()
