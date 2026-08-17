# SPDX-License-Identifier: AGPL-3.0-or-later
"""The operator console and multi-region topology guardrails."""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from aifence.app import create_app
from aifence.core.config import CoreSettings

ARTIFACT = {
    "artifact": (
        "# Quarterly Report\n\nRevenue grew 12% to $4.2M across all regions on strong "
        "enterprise demand."
    ),
    "content_type": "text/markdown",
    "action": {"operation": "read"},
}


# --- console ---

def test_console_status_requires_authentication(anon_client: TestClient) -> None:
    assert anon_client.get("/v1/console/status").status_code == 401


def test_console_page_requires_authentication(anon_client: TestClient) -> None:
    assert anon_client.get("/v1/console/").status_code == 401


def test_console_status_reports_every_tier(client: TestClient) -> None:
    body = client.get("/v1/console/status").json()
    assert set(body) >= {"breakers", "bus", "approvals", "transport", "quality", "subsystems"}
    assert {b["tier"] for b in body["breakers"]} == {"quality", "guard", "bus"}
    assert body["quality"]["controls"] > 0


def test_console_status_reflects_real_activity(client: TestClient) -> None:
    before = client.get("/v1/console/status").json()["bus"]["total"]
    client.post("/v1/fence/submit", json=ARTIFACT)
    after = client.get("/v1/console/status").json()["bus"]["total"]
    assert after == before + 1, "the console must show real handoffs, not a static page"


def test_console_page_renders_without_inline_script(client: TestClient) -> None:
    response = client.get("/v1/console/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # The app sends a strict CSP; the page must not depend on script execution.
    assert "<script" not in response.text
    assert "script-src" not in response.headers.get("content-security-policy", "")


def test_console_page_shows_the_tenant(client: TestClient) -> None:
    assert "tenant ten_" in client.get("/v1/console/").text


# --- multi-region ---

def test_readiness_reports_region_and_write_eligibility(app: FastAPI) -> None:
    with TestClient(app) as client:
        body = client.get("/health/ready").json()
    assert body["region_role"] == "active"
    assert body["accepts_writes"] is True


def test_standby_region_does_not_accept_writes(tmp_path) -> None:
    settings = CoreSettings(
        database_url=f"sqlite+pysqlite:///{tmp_path/'standby.db'}",
        region="us-east-1",
        region_role="standby",
    )
    with TestClient(create_app(settings)) as client:
        body = client.get("/health/ready").json()
    assert body["ready"] is True, "a standby region is healthy, just not writable"
    assert body["accepts_writes"] is False


@pytest.mark.parametrize("role", ["dispatcher", "lifecycle", "anchor"])
def test_standby_region_cannot_run_durable_workers(role: str) -> None:
    # Running a durable worker against a read replica would fail on write or
    # split-brain the active region, so it is refused at startup.
    with pytest.raises(ValueError, match="standby region cannot run"):
        CoreSettings(region_role="standby", runtime_role=role).validate()


def test_standby_region_may_serve_the_control_plane() -> None:
    CoreSettings(region_role="standby", runtime_role="control-plane").validate()


def test_invalid_region_role_is_rejected() -> None:
    with pytest.raises(ValueError, match="AIFENCE_REGION_ROLE"):
        CoreSettings(region_role="primary").validate()
