# SPDX-License-Identifier: AGPL-3.0-or-later
"""Subsystem registration protocol and discovery.

The composed application stays open/closed: :func:`create_app` does not import
``bus``/``guard``/``quality`` directly, it discovers whichever subsystems are
installed and calls their ``register`` hook. A subsystem module exposes::

    def register(app: FastAPI, ctx: SubsystemContext) -> None: ...

and mounts its router, wires its workers into ``ctx.lifespan_hooks``, and reads
its own settings. This is the seam that lets the three tiers be ported one at a
time (Phases 2–4) without ever editing the app factory.
"""
from __future__ import annotations

import importlib
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

if TYPE_CHECKING:
    from fastapi import FastAPI

    from .core.config import CoreSettings

_logger = logging.getLogger(__name__)

#: Subsystem modules the application will try to load, in flow order:
#: quality gate → guard enforcement → bus transport. Missing ones are skipped,
#: so the app runs with any subset installed.
SUBSYSTEM_MODULES: tuple[str, ...] = (
    "aifence.quality",
    "aifence.guard",
    "aifence.bus",
)

#: An async ``(startup, shutdown)`` pair a subsystem can add to the lifespan.
LifespanHook = tuple[Callable[[], Awaitable[None]], Callable[[], Awaitable[None]]]


@dataclass
class SubsystemContext:
    """Everything a subsystem needs to wire itself into the composed app."""

    settings: CoreSettings
    engine: Engine
    session_factory: sessionmaker[Session]
    lifespan_hooks: list[LifespanHook] = field(default_factory=list)

    def add_lifespan_hook(
        self,
        startup: Callable[[], Awaitable[None]],
        shutdown: Callable[[], Awaitable[None]],
    ) -> None:
        self.lifespan_hooks.append((startup, shutdown))


@runtime_checkable
class Subsystem(Protocol):
    def register(self, app: FastAPI, ctx: SubsystemContext) -> None: ...


def discover_subsystems() -> list[tuple[str, Subsystem]]:
    """Import each installed subsystem module exposing a ``register`` callable."""
    found: list[tuple[str, Subsystem]] = []
    for name in SUBSYSTEM_MODULES:
        try:
            module = importlib.import_module(name)
        except ImportError:
            continue
        if hasattr(module, "register"):
            found.append((name, module))
        else:
            _logger.warning("subsystem %s has no register() hook; skipping", name)
    return found
