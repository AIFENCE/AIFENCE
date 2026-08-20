# SPDX-License-Identifier: AGPL-3.0-or-later
"""Phase 1 foundation smoke tests: the composed app boots and serves its shared surface."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from aifence.app import create_app
from aifence.core.config import CoreSettings


@pytest.fixture()
def client(tmp_path) -> TestClient:
    settings = CoreSettings(database_url=f"sqlite+pysqlite:///{tmp_path/'aifence.db'}", metrics_public=True)
    return TestClient(create_app(settings))


def test_health_live(client: TestClient) -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    body = response.json()
    assert body["alive"] is True
    assert body["version"]


def test_health_ready_lists_subsystems(client: TestClient) -> None:
    response = client.get("/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["ready"] is True
    assert isinstance(body["subsystems"], list)


def test_metrics_exposed(client: TestClient) -> None:
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "aifence_http_requests_total" in response.text


def test_security_headers_present(client: TestClient) -> None:
    response = client.get("/health/live")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["X-Request-ID"]


def test_openapi_carries_license_metadata(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    assert "AGPL-3.0-or-later OR Commercial" in schema["info"]["license"]["name"]
    assert schema["info"]["x-aifence-source-code"]


def test_settings_from_env_reads_legacy_names(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AIFENCE_DOCS_ENABLED", raising=False)
    monkeypatch.setenv("SAGE_DOCS_ENABLED", "false")
    settings = CoreSettings.from_env()
    assert settings.docs_enabled is False


def test_invalid_environment_rejected() -> None:
    with pytest.raises(ValueError):
        CoreSettings(environment="banana").validate()


def test_metrics_private_mode_requires_bearer(tmp_path) -> None:
    settings = CoreSettings(
        database_url=f"sqlite+pysqlite:///{tmp_path/'private-metrics.db'}",
        metrics_public=False,
        metrics_bearer_token="m" * 32,
    )
    client = TestClient(create_app(settings))
    assert client.get("/metrics").status_code == 401
    response = client.get("/metrics", headers={"Authorization": f"Bearer {'m' * 32}"})
    assert response.status_code == 200
    assert "aifence_http_requests_total" in response.text
