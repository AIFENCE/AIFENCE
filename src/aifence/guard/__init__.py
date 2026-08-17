# SPDX-License-Identifier: AGPL-3.0-or-later
"""AIFENCE guard subsystem — security control & enforcement plane.

Guard mounts into the composed AIFENCE application as a sub-application under
``/guard``, reusing the shared core engine and declarative ``Base`` so it
participates in the one merged schema, connection pool, and metrics registry.
Heavy imports stay inside :func:`register` so importing this package (e.g. during
subsystem discovery) never requires guard's optional dependencies until it is
actually composed in.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

__version__ = "1.0.0rc5"

if TYPE_CHECKING:
    from fastapi import FastAPI

    from ..subsystems import SubsystemContext


def register(app: FastAPI, ctx: SubsystemContext) -> None:
    """Mount the guard control plane under ``/guard`` on the composed app."""
    from dataclasses import replace

    from .application import create_app as create_guard_app
    from .config import Settings as GuardSettings

    guard_settings = GuardSettings.from_env()
    # The composed application owns these: guard shares the core engine and
    # lifecycle, so diverging on them is a bug, not a deployment option. Without
    # this, AIFENCE_ENVIRONMENT=production would leave guard in development and
    # silently skip its fail-closed validation. Injected directly rather than via
    # the environment so composing one app cannot leak settings into the next.
    core = ctx.settings
    guard_settings = replace(
        guard_settings,
        environment=core.environment,
        runtime_role=core.runtime_role,
        log_level=core.log_level,
        database_url=core.database_url,
        auto_create_schema=core.auto_create_schema,
        docs_enabled=core.docs_enabled,
    )
    guard_settings.validate()
    guard_app = create_guard_app(
        settings=guard_settings,
        engine=ctx.engine,
        session_factory=ctx.session_factory,
    )
    app.mount("/guard", guard_app, name="guard")
    app.state.guard_app = guard_app
