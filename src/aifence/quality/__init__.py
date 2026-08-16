# SPDX-License-Identifier: AGPL-3.0-or-later
"""AIFENCE quality subsystem — production quality gate (bridge to BizIQ).

The canonical BizIQ pack (standards, controls, schemas) is vendored under the
repository's top-level ``quality/`` directory and keeps its own Node builder.
This Python package is the *bridge*: it reads BizIQ's control registry and runs
a deterministic quality gate over AI-generated artifacts, exposing the result to
the composed fence so the quality tier can gate the flow before enforcement.

Unlike guard and bus (mounted as sub-applications), the quality bridge is native
AIFENCE code, so it registers its router directly onto the composed app and
shares the one OpenAPI document.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

__version__ = "2.0.0"

if TYPE_CHECKING:
    from fastapi import FastAPI

    from ..subsystems import SubsystemContext


def register(app: FastAPI, ctx: SubsystemContext) -> None:
    """Mount the quality gate router under ``/v1/quality`` on the composed app."""
    from .api import router

    app.include_router(router)
    app.state.quality_registry_loaded = True
