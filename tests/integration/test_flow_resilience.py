# SPDX-License-Identifier: AGPL-3.0-or-later
"""The fence flow under tier failure: fail-closed refuses, fail-open degrades."""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from aifence.app import create_app
from aifence.core.config import CoreSettings

ARTIFACT = {
    "artifact": (
        "# Quarterly Report\n\nRevenue grew 12% to $4.2M across all regions on strong "
        "enterprise demand and improved retention."
    ),
    "content_type": "text/markdown",
    "action": {"operation": "read"},
}


def _authenticated(app: FastAPI) -> TestClient:
    with app.state.session_factory() as session:
        _t, _k, secret = app.state.guard_app.state.service.create_tenant_and_key(
            session, tenant_name="Resilience", key_name="k", scopes=["*"]
        )
    return TestClient(app, headers={"Authorization": f"Bearer {secret}"})


def _break(app: FastAPI, tier: str) -> None:
    """Force a tier to fail on every call."""

    def _boom() -> None:
        raise RuntimeError(f"{tier} exploded")

    breaker = getattr(app.state.flow_breakers, tier)
    original = breaker.call
    breaker.call = lambda _operation: original(_boom)  # type: ignore[method-assign]


def test_quality_failure_is_fail_closed_by_default(app: FastAPI) -> None:
    _break(app, "quality")
    with _authenticated(app) as client:
        response = client.post("/v1/fence/submit", json=ARTIFACT)
    assert response.status_code == 503
    body = response.json()
    assert body["error"]["code"] == "tier_unavailable"
    assert body["error"]["details"]["tier"] == "quality"


def test_guard_failure_always_refuses(app: FastAPI) -> None:
    """Enforcement is never allowed to fail open, whatever the configuration."""
    _break(app, "guard")
    with _authenticated(app) as client:
        response = client.post("/v1/fence/submit", json=ARTIFACT)
    assert response.status_code == 503
    assert response.json()["error"]["details"]["tier"] == "guard"


def test_quality_failure_degrades_when_configured_to_fail_open(tmp_path) -> None:
    settings = CoreSettings(
        database_url=f"sqlite+pysqlite:///{tmp_path/'open.db'}",
        flow_fail_open_tiers=("quality",),
    )
    app = create_app(settings)
    _break(app, "quality")
    with _authenticated(app) as client:
        response = client.post("/v1/fence/submit", json=ARTIFACT)
    assert response.status_code == 200
    body = response.json()
    # The request proceeded, but the receipt is explicit about what was skipped.
    assert body["final_outcome"] == "handed_off"
    assert body["degraded_tiers"] == ["quality"]
    assert body["stages"]["quality"]["degraded"] is True


def test_bus_failure_reports_authorized_but_undelivered(tmp_path) -> None:
    settings = CoreSettings(
        database_url=f"sqlite+pysqlite:///{tmp_path/'bus.db'}",
        flow_fail_open_tiers=("bus",),
    )
    app = create_app(settings)
    _break(app, "bus")
    with _authenticated(app) as client:
        response = client.post("/v1/fence/submit", json=ARTIFACT)
    body = response.json()
    assert body["allowed"] is True
    # Never claim a handoff that did not happen.
    assert body["final_outcome"] == "authorized_not_delivered"
    assert body["degraded_tiers"] == ["bus"]


def test_healthy_flow_reports_no_degradation(client: TestClient) -> None:
    body = client.post("/v1/fence/submit", json=ARTIFACT).json()
    assert body["final_outcome"] == "handed_off"
    assert body["degraded_tiers"] == []


@pytest.mark.parametrize("tier", ["quality", "guard", "bus"])
def test_every_tier_has_a_breaker(app: FastAPI, tier: str) -> None:
    assert getattr(app.state.flow_breakers, tier).policy.timeout_seconds > 0
