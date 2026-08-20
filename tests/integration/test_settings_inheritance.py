# SPDX-License-Identifier: AGPL-3.0-or-later
"""Subsystems must inherit the composed application's shared settings.

Each subsystem reads its own environment variable names. Configuring the fence
only through the shared ``AIFENCE_*`` values previously left subsystems on their
own defaults — so a deployment set to ``production`` could run the guard tier in
``development``, silently skipping its fail-closed validation.
"""
from __future__ import annotations

import pytest
from fastapi import FastAPI

from aifence.app import create_app
from aifence.core.config import CoreSettings


def test_guard_and_bus_inherit_core_environment(app: FastAPI) -> None:
    assert app.state.guard_app.state.settings.environment == "development"

    from aifence.bus.config import get_settings

    assert get_settings().env == "development"


def test_guard_inherits_core_database_url(app: FastAPI) -> None:
    core_url = app.state.settings.database_url
    assert app.state.guard_app.state.settings.database_url == core_url


def test_programmatic_production_settings_fail_closed_before_boot(tmp_path) -> None:
    """Passing CoreSettings directly cannot bypass production validation."""
    settings = CoreSettings(
        environment="production",
        database_url=f"sqlite+pysqlite:///{tmp_path/'p.db'}",
    )
    with pytest.raises(ValueError, match="production|HTTPS"):
        create_app(settings)
