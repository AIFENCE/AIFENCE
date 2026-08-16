from __future__ import annotations

import base64

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from aifence.bus.config import Settings
from aifence.bus.main import BodyLimitMiddleware


def _production_settings(**overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "env": "production",
        "database_url": "postgresql+psycopg://sage:secret@db/sage",
        "auth_required": True,
        "api_keys": ["s" * 32],
        "allowed_hosts": ["sage.invalid"],
        "auto_create_schema": False,
        "docs_enabled": False,
    }
    values.update(overrides)
    return values


def test_production_fails_closed_without_authentication() -> None:
    with pytest.raises(ValidationError):
        Settings(**_production_settings(auth_required=False))


def test_production_rejects_sqlite_and_wildcard_hosts() -> None:
    with pytest.raises(ValidationError):
        Settings(**_production_settings(database_url="sqlite:///sage.db"))
    with pytest.raises(ValidationError):
        Settings(**_production_settings(allowed_hosts=["*"]))


def test_required_signatures_require_a_verification_key() -> None:
    with pytest.raises(ValidationError):
        Settings(require_packet_signatures=True)
    public_key = base64.urlsafe_b64encode(b"k" * 32).rstrip(b"=").decode()
    settings = Settings(require_packet_signatures=True, packet_signing_public_key=public_key)
    assert settings.require_packet_signatures is True


def test_service_and_agent_keys_cannot_overlap() -> None:
    key = "k" * 32
    with pytest.raises(ValidationError):
        Settings(auth_required=True, api_keys=[key], agent_keys={key: "w:a"})


def test_body_limit_rejects_oversized_payloads() -> None:
    app = FastAPI()
    app.add_middleware(BodyLimitMiddleware, max_bytes=32)

    @app.post("/ingest")
    async def ingest(payload: dict[str, str]) -> dict[str, str]:
        return payload

    with TestClient(app) as client:
        response = client.post("/ingest", json={"payload": "x" * 64})
        assert response.status_code == 413
