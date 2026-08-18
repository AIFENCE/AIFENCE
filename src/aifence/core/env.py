# SPDX-License-Identifier: AGPL-3.0-or-later
"""Environment-variable readers shared by every subsystem config loader.

These helpers are deliberately tiny and dependency-free so ``core``, ``bus``,
``guard``, and ``quality`` can all parse ``AIFENCE_*`` variables the same way.
Each reader also accepts an ordered list of legacy variable names, which
preserves backward compatibility for pre-existing deployments (see
``docs/CONFIGURATION.md``).
"""
from __future__ import annotations

import os
from pathlib import Path

_TRUE = {"1", "true", "yes", "on"}


def adopt_legacy_prefix(legacy_prefix: str, prefix: str) -> None:
    """Accept a subsystem's pre-merge env prefix as an alias for its current one.

    For every ``{legacy_prefix}NAME`` variable set in the environment, populate
    ``{prefix}NAME`` unless that is already set. Deployments written against the
    pre-merge variable names keep working, and an explicitly set current name
    always wins over the legacy alias.
    """
    for key, value in list(os.environ.items()):
        if key.startswith(legacy_prefix):
            os.environ.setdefault(prefix + key[len(legacy_prefix):], value)


def env_str(name: str, default: str = "", *, legacy: tuple[str, ...] = ()) -> str:
    for candidate in (name, *legacy):
        value = os.getenv(candidate)
        if value is not None:
            return value
    return default


def env_bool(name: str, default: bool, *, legacy: tuple[str, ...] = ()) -> bool:
    raw = env_str(name, legacy=legacy)
    if raw == "":
        return default
    return raw.strip().lower() in _TRUE


def env_int(name: str, default: int, *, legacy: tuple[str, ...] = ()) -> int:
    raw = env_str(name, legacy=legacy)
    return default if raw == "" else int(raw)


def env_float(name: str, default: float, *, legacy: tuple[str, ...] = ()) -> float:
    raw = env_str(name, legacy=legacy)
    return default if raw == "" else float(raw)


def env_csv(name: str, default: tuple[str, ...] = (), *, legacy: tuple[str, ...] = ()) -> tuple[str, ...]:
    raw = env_str(name, legacy=legacy)
    if not raw:
        return default
    return tuple(item.strip() for item in raw.split(",") if item.strip())


def env_secret(name: str, default: str = "", *, legacy: tuple[str, ...] = ()) -> str:
    """Read a secret from ``NAME`` or, failing that, the file at ``NAME_FILE``.

    Legacy names are tried for both the direct value and the ``*_FILE`` form so
    existing secret mounts keep working after the rename.
    """
    for candidate in (name, *legacy):
        direct = os.getenv(candidate)
        if direct is not None:
            return direct
    for candidate in (name, *legacy):
        path = os.getenv(f"{candidate}_FILE")
        if path:
            return Path(path).read_text(encoding="utf-8").strip()
    return default
