# SPDX-License-Identifier: AGPL-3.0-or-later
"""Shared SQLAlchemy engine, session, and row-level-security helpers.

Every subsystem persists through this single ``Base`` (one metadata, one
Alembic history) and builds its engine/session with these factories, so the
merged application has exactly one connection pool and one schema. The
PostgreSQL row-level-security config namespace is ``aifence``.
"""
from __future__ import annotations

from collections.abc import Generator
from typing import Protocol

from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

#: PostgreSQL ``set_config`` namespace used by row-level-security policies.
RLS_NAMESPACE = "aifence"


class EngineConfig(Protocol):
    """The minimal settings surface :func:`create_database_engine` needs.

    Declared as read-only properties so frozen settings dataclasses satisfy it.
    """

    @property
    def database_url(self) -> str: ...

    @property
    def db_pool_size(self) -> int: ...

    @property
    def db_max_overflow(self) -> int: ...


class Base(DeclarativeBase):
    """Declarative base shared by all subsystem models."""


def create_database_engine(settings: EngineConfig) -> Engine:
    kwargs: dict[str, object] = {"pool_pre_ping": True, "future": True}
    if settings.database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    else:
        kwargs.update(
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_recycle=1800,
        )
    engine = create_engine(settings.database_url, **kwargs)
    if settings.database_url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _sqlite_pragmas(dbapi_connection: object, _record: object) -> None:
            cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=FULL")
            cursor.close()

    return engine


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, class_=Session, expire_on_commit=False, future=True)


def set_key_context(session: Session, key_id: str) -> None:
    """Set the API-key lookup context used by PostgreSQL RLS during authentication."""
    if session.get_bind().dialect.name == "postgresql":
        session.execute(
            text(f"SELECT set_config('{RLS_NAMESPACE}.key_id', :value, true)"),
            {"value": key_id},
        )
    session.info["key_id"] = key_id


def set_tenant_context(session: Session, tenant_id: str) -> None:
    """Set transaction-local tenant context for PostgreSQL row-level security."""
    if session.get_bind().dialect.name == "postgresql":
        session.execute(
            text(f"SELECT set_config('{RLS_NAMESPACE}.tenant_id', :value, true)"),
            {"value": tenant_id},
        )
    session.info["tenant_id"] = tenant_id


def session_dependency(factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    session = factory()
    try:
        yield session
    finally:
        session.close()
