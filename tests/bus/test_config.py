from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from aifence.bus.config import Settings


def test_default_sqlite_database_does_not_depend_on_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    monkeypatch.delenv("SAGE_DATABASE_URL", raising=False)
    settings = Settings(auth_required=False)

    assert settings.database_url == f"sqlite:///{Path.home() / 'sage.db'}"
    assert not settings.database_url.endswith("./sage.db")


def test_default_database_initializes_from_non_writable_working_directory(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    if sys.platform == "linux":
        # Linux's procfs is always available and cannot be used as a cwd for
        # relative database paths, preserving the original reproduction.
        unavailable_cwd = Path("/proc")
    else:
        unavailable_cwd = tmp_path / "unavailable-cwd"
        unavailable_cwd.mkdir()
        try:
            unavailable_cwd.chmod(0o555)
        except OSError as exc:
            pytest.skip(f"cannot create non-writable working directory: {exc}")
        if os.access(unavailable_cwd, os.W_OK):
            pytest.skip("platform does not provide a non-writable working directory here")

    source_root = Path(__file__).resolve().parents[2] / "src"
    script = """
from pathlib import Path

from sqlalchemy import inspect
from aifence.bus.config import Settings
from aifence.bus.db import Base, engine, init_db

assert Settings(auth_required=False).database_url == f"sqlite:///{Path.home() / 'sage.db'}"
init_db()
assert inspect(engine).has_table('concepts')
assert (Path.home() / 'sage.db').is_file()
"""
    env = {key: value for key, value in os.environ.items() if not key.startswith("SAGE_")}
    env.update({"HOME": str(home), "PYTHONPATH": str(source_root)})

    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=unavailable_cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (home / "sage.db").is_file()


def test_explicit_database_url_is_preserved(tmp_path, monkeypatch):
    database_url = f"sqlite:///{tmp_path / 'explicit.db'}"
    monkeypatch.setenv("SAGE_DATABASE_URL", database_url)

    settings = Settings(auth_required=False)

    assert settings.database_url == database_url


def test_production_still_rejects_sqlite():
    try:
        Settings(
            env="production",
            database_url="sqlite:////tmp/production.db",
            auth_required=True,
            api_keys=["s" * 32],
            auto_create_schema=False,
            allowed_hosts=["example.test"],
            docs_enabled=False,
        )
    except ValueError as exc:
        assert "production requires a server database" in str(exc)
    else:
        raise AssertionError("production SQLite configuration unexpectedly accepted")
