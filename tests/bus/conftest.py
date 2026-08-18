from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.orm import close_all_sessions

_USE_CONFIGURED_DB = os.getenv("AIFENCE_BUS_TEST_USE_CONFIGURED_DB", "").lower() in {"1", "true", "yes"}
_bootstrap_db = Path(tempfile.gettempdir()) / f"aifence-pytest-{os.getpid()}.db"
if os.name == "nt":
    os.environ.setdefault(
        "AIFENCE_BUS_SCRATCH_ROOT",
        str(Path(tempfile.gettempdir()) / "aifence-model-eval-scratch"),
    )
if not _USE_CONFIGURED_DB:
    os.environ["AIFENCE_BUS_DATABASE_URL"] = f"sqlite:///{_bootstrap_db}"
os.environ["AIFENCE_BUS_AUTH_REQUIRED"] = "false"
os.environ["AIFENCE_BUS_LEARNING_MODE"] = "managed"


def _clear_database(engine, metadata) -> None:
    if engine.dialect.name == "postgresql":
        tables = ", ".join(f'"{table.name}"' for table in metadata.sorted_tables)
        if tables:
            with engine.begin() as conn:
                conn.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE"))
        return
    with engine.begin() as conn:
        for table in reversed(metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture(scope="session", autouse=True)
def test_schema():
    from aifence.bus import db as db_module
    __import__("aifence.bus.db_models")

    db_module.SessionLocal.configure(bind=db_module.engine)
    db_module.Base.metadata.drop_all(db_module.engine)
    db_module.Base.metadata.create_all(db_module.engine)
    yield
    close_all_sessions()
    db_module.Base.metadata.drop_all(db_module.engine)
    if not _USE_CONFIGURED_DB:
        db_module.engine.dispose()
        try:
            _bootstrap_db.unlink()
        except FileNotFoundError:
            pass


@pytest.fixture(autouse=True)
def isolated_db(test_schema):
    from aifence.bus import db as db_module

    close_all_sessions()
    _clear_database(db_module.engine, db_module.Base.metadata)
    yield
    close_all_sessions()
