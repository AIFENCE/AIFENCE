# SPDX-License-Identifier: AGPL-3.0-or-later
"""Shared foundation for every AIFENCE subsystem.

``aifence.core`` owns the cross-cutting concerns the bus, guard, and quality
tiers all depend on — configuration, database engine/session management,
structured errors, generic middleware, HTTP metrics, and telemetry — so those
concerns are defined once and reused rather than duplicated per subsystem.
"""
from __future__ import annotations

from .config import CoreSettings
from .db import Base, create_database_engine, create_session_factory, session_dependency

__all__ = [
    "Base",
    "CoreSettings",
    "create_database_engine",
    "create_session_factory",
    "session_dependency",
]
