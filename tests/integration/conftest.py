# SPDX-License-Identifier: AGPL-3.0-or-later
"""Shared fixtures for composed-application tests.

The fence flow and quality routers require the same API-key identity guard
enforces, so integration tests mint a real tenant key rather than bypassing
authentication.
"""
from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from aifence.app import create_app
from aifence.core.config import CoreSettings


@pytest.fixture()
def app(tmp_path) -> FastAPI:
    return create_app(CoreSettings(database_url=f"sqlite+pysqlite:///{tmp_path/'aifence.db'}", metrics_public=True))


@pytest.fixture()
def token(app: FastAPI) -> str:
    """Mint a real, fully scoped API key through the guard tier."""
    with app.state.session_factory() as session:
        _tenant, _key, secret = app.state.guard_app.state.service.create_tenant_and_key(
            session, tenant_name="Integration Tenant", key_name="integration", scopes=["*"]
        )
    return str(secret)


@pytest.fixture()
def client(app: FastAPI, token: str) -> Iterator[TestClient]:
    """An authenticated client for the composed application."""
    with TestClient(app, headers={"Authorization": f"Bearer {token}"}) as test_client:
        yield test_client


@pytest.fixture()
def anon_client(app: FastAPI) -> Iterator[TestClient]:
    """An unauthenticated client, for asserting that endpoints refuse anonymous access."""
    with TestClient(app) as test_client:
        yield test_client
