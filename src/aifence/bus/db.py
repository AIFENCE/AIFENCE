# SPDX-License-Identifier: AGPL-3.0-or-later
# AIFENCE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Share the one merged declarative Base so bus tables live in the same schema
# and metadata as every other AIFENCE subsystem.
from ..core.db import Base
from .config import get_settings

# Re-exported: bus modules import Base from here, as they did before the merge.
__all__ = ["Base", "SessionLocal", "engine", "get_db", "init_db"]

settings = get_settings()
is_sqlite = settings.database_url.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}
engine_kwargs = {"pool_pre_ping": True, "connect_args": connect_args}
if not is_sqlite:
    engine_kwargs.update(
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout_seconds,
        pool_recycle=settings.db_pool_recycle_seconds,
    )
engine = create_engine(settings.database_url, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


def init_db() -> None:
    __import__("aifence.bus.db_models")
    Base.metadata.create_all(bind=engine)
