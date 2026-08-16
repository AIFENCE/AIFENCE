# SPDX-License-Identifier: AGPL-3.0-or-later
"""AIFENCE bus subsystem — semantic communication runtime (from SAGE).

The bus mounts into the composed AIFENCE application as a sub-application under
``/bus``. It shares the merged declarative ``Base`` (so its tables join the one
schema) and is pinned to the shared database URL so it reads and writes the same
database as the rest of the fence. Heavy imports stay inside :func:`register` so
importing this package during subsystem discovery never pulls in the bus runtime
or its optional dependencies (e.g. ``mcp``) until it is actually composed in.
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

__version__ = "0.2.7"

if TYPE_CHECKING:
    from fastapi import FastAPI

    from ..subsystems import SubsystemContext


def register(app: FastAPI, ctx: SubsystemContext) -> None:
    """Mount the semantic bus under ``/bus`` on the composed app.

    SAGE reads its database URL from ``SAGE_DATABASE_URL`` at import time, so we
    pin it to the shared core database *before* importing the bus app, and let
    the shared core lifespan own schema creation.
    """
    os.environ["SAGE_DATABASE_URL"] = ctx.settings.database_url
    os.environ.setdefault("SAGE_AUTO_CREATE_SCHEMA", "false")

    from .main import app as bus_app

    app.mount("/bus", bus_app, name="bus")
    app.state.bus_app = bus_app
