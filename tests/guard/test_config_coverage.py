from __future__ import annotations

import base64
import json
from pathlib import Path

import pytest

import aifence.guard.config as cfg


def test_env_helpers_and_secret_files(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    assert cfg._secret_value("NO_VALUE", "NO_FILE", "fallback") == "fallback"

    secret = tmp_path / "secret"
    secret.write_text("  from-file  \n")
    monkeypatch.setenv("SECRET_FILE", str(secret))
    assert cfg._secret_value("SECRET_VALUE", "SECRET_FILE") == "from-file"

    monkeypatch.setenv("SECRET_VALUE", "direct")
    assert cfg._secret_value("SECRET_VALUE", "SECRET_FILE") == "direct"

    assert cfg._bool("MISSING_BOOL", True) is True
    monkeypatch.setenv("BOOL", "yes")
    assert cfg._bool("BOOL", False) is True
    monkeypatch.setenv("BOOL", "off")
    assert cfg._bool("BOOL", True) is False

    assert cfg._int("MISSING_INT", 7) == 7
    monkeypatch.setenv("INT", "9")
    assert cfg._int("INT", 0) == 9

    assert cfg._csv("MISSING_CSV", ("d",)) == ("d",)
    monkeypatch.setenv("CSV", " a, ,b ")
    assert cfg._csv("CSV") == ("a", "b")


def test_from_env_extra_file_and_secret_rotation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    extra = tmp_path / "extra.json"
    extra.write_text('{"source":"file"}')
    database_url = tmp_path / "db.url"
    database_url.write_text(f"sqlite+pysqlite:///{tmp_path / 'db.sqlite'}")

    monkeypatch.setenv("AIFENCE_GUARD_ENVIRONMENT", "test")
    monkeypatch.setenv("AIFENCE_GUARD_EXTRA_JSON_FILE", str(extra))
    monkeypatch.setenv("AIFENCE_GUARD_DATABASE_URL_FILE", str(database_url))
    monkeypatch.setenv(
        "AIFENCE_GUARD_ALLOWED_ORIGINS",
        "https://one.example,https://two.example",
    )
    monkeypatch.setenv("AIFENCE_GUARD_TRUSTED_PROXY_CIDRS", "127.0.0.1/32")
    monkeypatch.setenv("AIFENCE_GUARD_INTERNAL_CIDRS", "10.0.0.0/8")
    monkeypatch.setenv("AIFENCE_GUARD_WORKLOAD_TRUST_DOMAINS", "example.org")
    monkeypatch.setenv("AIFENCE_GUARD_AUDIT_ANCHOR_DESTINATIONS", "file,webhook")

    settings = cfg.Settings.from_env()
    assert settings.extra == {"source": "file"}
    assert settings.allowed_origins == ("https://one.example", "https://two.example")
    assert settings.trusted_proxy_cidrs == ("127.0.0.1/32",)
    assert settings.audit_anchor_destinations == ("file", "webhook")

    extra.write_text("[]")
    with pytest.raises(ValueError, match="JSON object"):
        cfg.Settings.from_env()

    extra.unlink()
    with pytest.raises(ValueError, match="readable file"):
        cfg.Settings.from_env()


def test_keyring_and_pepper_validation_edges() -> None:
    key = base64.b64encode(b"k" * 32).decode()
    assert cfg.Settings(master_key_b64=key).encryption_keyring()[0] == "master-v1"

    with pytest.raises(ValueError):
        cfg.Settings(master_keyring_json="[]").encryption_keyring()
    with pytest.raises(ValueError):
        cfg.Settings(master_keyring_json='{"master-v1":"bad"}').encryption_keyring()
    with pytest.raises(ValueError):
        cfg.Settings(
            master_key_id="missing",
            master_keyring_json=json.dumps({"other": key}),
        ).encryption_keyring()

    assert cfg.Settings(api_key_pepper="x" * 48).accepted_peppers() == (b"x" * 48,)
    with pytest.raises(ValueError):
        cfg.Settings(api_key_pepperring_json="[]").accepted_peppers()
    with pytest.raises(ValueError):
        cfg.Settings(api_key_pepperring_json='{"p":"short"}').accepted_peppers()
    with pytest.raises(ValueError):
        cfg.Settings(
            api_key_pepper_id="missing",
            api_key_pepperring_json=json.dumps({"p": "x" * 48}),
        ).accepted_peppers()


def test_general_validation_edges() -> None:
    cases = [
        ({"runtime_role": "bad"}, "RUNTIME_ROLE"),
        ({"dispatch_mode": "bad"}, "DISPATCH_MODE"),
        ({"kms_backend": "bad"}, "KMS_BACKEND"),
        ({"tenant_key_backend": "bad"}, "TENANT_KEY_BACKEND"),
        ({"artifact_store_backend": "bad"}, "ARTIFACT_STORE_BACKEND"),
        ({"audit_anchor_backend": "bad"}, "AUDIT_ANCHOR_BACKEND"),
        ({"worker_concurrency": 0}, "WORKER_CONCURRENCY"),
        ({"max_page_size": 0}, "MAX_PAGE_SIZE"),
    ]
    for kwargs, message in cases:
        with pytest.raises(ValueError, match=message):
            cfg.Settings(environment="test", **kwargs).validate()
