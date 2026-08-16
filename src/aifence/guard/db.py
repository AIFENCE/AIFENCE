# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

# The merged schema uses one declarative Base for every subsystem, so guard's
# models attach to the same metadata and a single Alembic history / create_all
# builds the whole database. (Was a standalone Base in AGENTDANCE.)
from ..core.db import Base
from .config import Settings

__all__ = ["Base", "create_database_engine", "create_session_factory", "session_dependency", "set_key_context", "set_tenant_context"]


def create_database_engine(settings: Settings) -> Engine:
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
        def _sqlite_pragmas(dbapi_connection: object, _connection_record: object) -> None:
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
        session.execute(text("SELECT set_config('agentdance.key_id', :value, true)"), {"value": key_id})
    session.info["key_id"] = key_id


def set_tenant_context(session: Session, tenant_id: str) -> None:
    """Set transaction-local tenant context for PostgreSQL row-level security."""
    if session.get_bind().dialect.name == "postgresql":
        session.execute(
            text("SELECT set_config('agentdance.tenant_id', :value, true)"),
            {"value": tenant_id},
        )
    session.info["tenant_id"] = tenant_id


def session_dependency(factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    session = factory()
    try:
        yield session
    finally:
        session.close()
