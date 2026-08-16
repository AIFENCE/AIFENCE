# SPDX-License-Identifier: AGPL-3.0-or-later
"""Alembic environment for the single, merged AIFENCE schema.

Every subsystem registers its ORM models against :data:`aifence.core.db.Base`,
so importing those model modules here makes the whole schema visible to
``--autogenerate``. Model modules are imported best-effort: a subsystem that has
not been ported yet simply contributes nothing.
"""
from __future__ import annotations

import importlib
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from aifence.core.config import CoreSettings
from aifence.core.db import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Bind the URL from AIFENCE configuration rather than hard-coding it in the ini.
config.set_main_option("sqlalchemy.url", CoreSettings.from_env().database_url)

# Import subsystem model modules so their tables attach to Base.metadata.
_MODEL_MODULES = (
    "aifence.guard.models",
    "aifence.bus.db_models",
    "aifence.quality.models",
)
for _module in _MODEL_MODULES:
    try:
        importlib.import_module(_module)
    except ImportError:
        continue

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
