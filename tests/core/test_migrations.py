# SPDX-License-Identifier: AGPL-3.0-or-later
"""The committed migrations must build exactly the declared schema.

Production runs with ``auto_create_schema`` disabled, so Alembic is the only
thing that creates tables. If a subsystem adds a model without a migration,
deployment would fail at runtime rather than here — this test catches the drift.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

import aifence.bus.db_models  # noqa: F401  (registers bus models on Base)
import aifence.guard.models  # noqa: F401  (registers guard models on Base)
from aifence.core.db import Base

ROOT = Path(__file__).resolve().parents[2]


def _upgrade_to_head(url: str) -> None:
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "alembic"))
    command.upgrade(config, "head")


def test_migrations_build_the_declared_schema(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    database = tmp_path / "migrated.db"
    url = f"sqlite+pysqlite:///{database}"
    # alembic/env.py resolves the URL from AIFENCE configuration.
    monkeypatch.setenv("AIFENCE_DATABASE_URL", url)

    _upgrade_to_head(url)

    engine = create_engine(url)
    try:
        migrated = {t for t in inspect(engine).get_table_names() if t != "alembic_version"}
    finally:
        engine.dispose()
    declared = set(Base.metadata.tables)

    assert not declared - migrated, f"models with no migration: {sorted(declared - migrated)}"
    assert not migrated - declared, f"migration creates unknown tables: {sorted(migrated - declared)}"


def test_migration_history_has_a_single_head() -> None:
    from alembic.script import ScriptDirectory

    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "alembic"))
    heads = ScriptDirectory.from_config(config).get_heads()
    assert len(heads) == 1, f"merged history must have exactly one head, found: {heads}"


def test_v010_release_database_fixture_upgrades_and_preserves_data(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The first public schema snapshot becomes the migration fixture for every later release."""
    import sqlite3

    from sqlalchemy import text

    fixture = ROOT / "compat/db/aifence-v0.1.0.sql"
    assert fixture.is_file()
    database = tmp_path / "from-v0.1.0.db"
    raw = sqlite3.connect(database)
    try:
        raw.executescript(fixture.read_text(encoding="utf-8"))
        raw.commit()
    finally:
        raw.close()

    url = f"sqlite+pysqlite:///{database}"
    monkeypatch.setenv("AIFENCE_DATABASE_URL", url)
    _upgrade_to_head(url)

    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            row = connection.execute(text("SELECT name, status FROM tenants WHERE id='ten_compat_001'")).one()
            assert row.name == "Compatibility Fixture"
            assert row.status == "active"
    finally:
        engine.dispose()
