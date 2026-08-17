# SPDX-License-Identifier: AGPL-3.0-or-later
"""Phase 3: the bus subsystem composes into the AIFENCE app and shares core."""
from __future__ import annotations

from fastapi.testclient import TestClient

from aifence.core.db import Base


def test_bus_registered_as_subsystem(client: TestClient) -> None:
    body = client.get("/health/ready").json()
    assert "aifence.bus" in body["subsystems"]


def test_bus_mounted_and_alive(client: TestClient) -> None:
    response = client.get("/bus/health/live")
    assert response.status_code == 200
    assert response.json()["alive"] is True


def test_bus_shares_core_database_url(tmp_path) -> None:
    # register() pins SAGE to the shared database URL before importing the app.
    # Use a fresh tmp database so guard's ephemeral signing key never collides.
    import os

    from aifence.app import create_app as _create
    from aifence.core.config import CoreSettings as _CS

    url = f"sqlite+pysqlite:///{tmp_path/'share_probe.db'}"
    _create(_CS(database_url=url))
    assert os.environ["SAGE_DATABASE_URL"] == url


def test_bus_models_attached_to_shared_base(client: TestClient) -> None:
    import aifence.bus.db_models  # noqa: F401  (registers bus models)

    tables = set(Base.metadata.tables)
    # Both guard and bus tables coexist on the one shared metadata.
    assert len(tables) > 5


def test_all_three_layers_coexist(client: TestClient) -> None:
    assert client.get("/health/live").status_code == 200          # core
    assert client.get("/guard/health/ready").status_code == 200   # guard
    assert client.get("/bus/health/live").status_code == 200      # bus
