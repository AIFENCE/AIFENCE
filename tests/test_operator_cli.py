from __future__ import annotations

import json
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

from aifence import cli
from aifence.guard import cli as guard_cli


class _ScalarResult:
    def scalar_one(self) -> int:
        return 1


class _Session:
    def execute(self, _statement: object) -> _ScalarResult:
        return _ScalarResult()


@contextmanager
def _session_factory() -> Iterator[_Session]:
    yield _Session()


class _Engine:
    def __init__(self) -> None:
        self.disposed = False

    def dispose(self) -> None:
        self.disposed = True


def test_build_parser_exposes_operator_commands() -> None:
    parser = cli._build_parser()
    assert parser.parse_args(["version"]).command == "version"
    assert parser.parse_args(["doctor", "--json"]).as_json is True
    assert parser.parse_args(["bootstrap", "--tenant-name", "tenant"]).tenant_name == "tenant"
    assert parser.parse_args(["demo", "--receiver", "worker"]).receiver == "worker"
    assert parser.parse_args(["serve"]).command == "serve"


def test_resolved_status_uses_runtime_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = SimpleNamespace(
        environment="test",
        runtime_role="all",
        public_base_url="http://localhost:8080",
        is_sqlite=True,
        docs_enabled=True,
        region="us-test-1",
        region_role="primary",
        bus_transport="database",
        flow_fail_open_tiers=(),
    )
    monkeypatch.setattr(cli.CoreSettings, "from_env", classmethod(lambda cls: settings))
    status = cli._resolved_status()
    runtime = status["runtime"]
    assert isinstance(runtime, dict)
    assert runtime["database_backend"] == "sqlite"
    assert runtime["region"] == "us-test-1"
    assert runtime["flow_fail_open_tiers"] == []


def test_doctor_reports_all_successes(monkeypatch: pytest.MonkeyPatch) -> None:
    import aifence.app as app_module
    import aifence.quality.controls as controls_module

    settings = SimpleNamespace(environment="test", runtime_role="all")
    monkeypatch.setattr(cli.CoreSettings, "from_env", classmethod(lambda cls: settings))
    engine = _Engine()
    fake_app = SimpleNamespace(
        state=SimpleNamespace(
            session_factory=_session_factory,
            engine=engine,
            subsystems=("aifence.quality", "aifence.guard", "aifence.bus"),
        )
    )
    monkeypatch.setattr(app_module, "create_app", lambda _settings: fake_app)
    monkeypatch.setattr(controls_module, "load_controls", lambda: [SimpleNamespace(id="AQ-TEST")])

    result = cli._doctor()

    assert result["ok"] is True
    assert engine.disposed is True
    checks = result["checks"]
    assert isinstance(checks, list)
    assert len(checks) == 4
    assert all(item["ok"] for item in checks)


def test_doctor_collects_failures_instead_of_stopping(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        cli.CoreSettings,
        "from_env",
        classmethod(lambda cls: (_ for _ in ()).throw(RuntimeError("bad settings"))),
    )
    result = cli._doctor()
    assert result["ok"] is False
    checks = result["checks"]
    assert isinstance(checks, list)
    assert checks[0]["name"] == "core.configuration"
    assert checks[0]["ok"] is False
    assert any(item["name"] == "bus.protocol" for item in checks)


def test_bootstrap_returns_one_time_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    import aifence.app as app_module

    class _Service:
        def create_tenant_and_key(self, _session: object, **kwargs: Any) -> tuple[object, object, str]:
            assert kwargs["tenant_name"] == "Acme"
            assert kwargs["key_name"] == "root"
            assert kwargs["scopes"]
            return SimpleNamespace(id="tenant-1"), SimpleNamespace(id="key-1"), "secret-token"

    engine = _Engine()
    fake_app = SimpleNamespace(
        state=SimpleNamespace(
            guard_app=SimpleNamespace(state=SimpleNamespace(service=_Service())),
            session_factory=_session_factory,
            engine=engine,
        )
    )
    monkeypatch.setattr(app_module, "create_app", lambda _settings: fake_app)
    monkeypatch.setattr(
        cli.CoreSettings,
        "from_env",
        classmethod(lambda cls: SimpleNamespace(environment="test")),
    )

    result = cli._bootstrap("Acme", "root")

    assert result["tenant_id"] == "tenant-1"
    assert result["api_key_id"] == "key-1"
    assert result["api_key"] == "secret-token"
    assert engine.disposed is True


def test_demo_runs_real_composed_quality_guard_bus_lifecycle() -> None:
    result = cli._demo(None, "coverage-receiver")
    assert result["ok"] is True
    assert result["final_outcome"] == "handed_off"
    assert result["bus"]
    assert result["receiver_claimed_message_ids"]


@pytest.mark.parametrize(
    ("argv", "patch_name", "patch_value", "expected_exit"),
    [
        (["status"], "_resolved_status", {"ok": True}, None),
        (["bootstrap", "--tenant-name", "Acme"], "_bootstrap", {"tenant_id": "t"}, None),
        (["doctor", "--json"], "_doctor", {"ok": True, "checks": []}, 0),
        (["demo"], "_demo", {"ok": True}, 0),
    ],
)
def test_main_dispatches_commands(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    argv: list[str],
    patch_name: str,
    patch_value: dict[str, object],
    expected_exit: int | None,
) -> None:
    if patch_name == "_bootstrap":
        monkeypatch.setattr(cli, patch_name, lambda *_args: patch_value)
    elif patch_name == "_demo":
        monkeypatch.setattr(cli, patch_name, lambda *_args: patch_value)
    else:
        monkeypatch.setattr(cli, patch_name, lambda: patch_value)

    if expected_exit is None:
        cli.main(argv)
    else:
        with pytest.raises(SystemExit) as exc:
            cli.main(argv)
        assert exc.value.code == expected_exit
    assert capsys.readouterr().out


def test_main_version_forms_and_failed_doctor(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    cli.main(["--version"])
    assert capsys.readouterr().out.strip()

    cli.main(["version"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["platform"]

    monkeypatch.setattr(cli, "_doctor", lambda: {"ok": False, "checks": [{"ok": False}]})
    with pytest.raises(SystemExit) as exc:
        cli.main(["doctor"])
    assert exc.value.code == 1


def test_main_serve_and_entrypoint_wrappers(monkeypatch: pytest.MonkeyPatch) -> None:
    called: list[object] = []
    main_module = ModuleType("aifence.main")
    main_module.run = lambda: called.append("serve")  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "aifence.main", main_module)
    cli.main(["serve"])
    assert called == ["serve"]

    monkeypatch.setattr(cli, "main", lambda args=None: called.append(args))
    monkeypatch.setattr(sys, "argv", ["aifence-doctor", "--json"])
    cli.doctor_main()
    monkeypatch.setattr(sys, "argv", ["aifence-demo", "--receiver", "agent"])
    cli.demo_main()
    monkeypatch.setattr(sys, "argv", ["aifence-bootstrap", "--tenant-name", "Acme"])
    cli.bootstrap_main()
    assert called[1:] == [
        ["doctor", "--json"],
        ["demo", "--receiver", "agent"],
        ["bootstrap", "--tenant-name", "Acme"],
    ]


def test_guard_build_parser_covers_supported_operator_surface() -> None:
    parser = guard_cli.build_parser()
    assert parser.parse_args(["serve"]).command == "serve"
    assert parser.parse_args(["bootstrap", "--tenant-name", "Acme"]).tenant_name == "Acme"
    assert parser.parse_args(["worker", "--once"]).once is True
    assert parser.parse_args(["verify-audit", "--tenant-id", "t"]).tenant_id == "t"
    assert parser.parse_args(["evaluate"]).fail_under == 1.0


def test_guard_keygen_writes_secret_material(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    private_path = tmp_path / "signing-private.pem"
    public_path = tmp_path / "signing-public.pem"
    private_path.write_text("private", encoding="utf-8")
    public_path.write_text("public", encoding="utf-8")
    monkeypatch.setattr(guard_cli, "generate_key_files", lambda _directory: (private_path, public_path))
    monkeypatch.setattr(sys, "argv", ["aifence-guard", "keygen", "--directory", str(tmp_path)])

    guard_cli.main()

    output = json.loads(capsys.readouterr().out)
    assert str(tmp_path / "generated-secrets.json") in output["created"]
    assert (tmp_path / "master-key.b64").exists()
    assert (tmp_path / "master-keyring.json").exists()
    assert (tmp_path / "api-key-pepper").exists()
    assert (tmp_path / "api-key-pepperring.json").exists()


def test_guard_migrate_dispatches_alembic(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[object, str]] = []

    class _Config:
        def __init__(self, filename: str) -> None:
            self.filename = filename
            self.options: dict[str, str] = {}

        def set_main_option(self, name: str, value: str) -> None:
            self.options[name] = value

    monkeypatch.setattr(
        guard_cli.Settings,
        "from_env",
        classmethod(lambda cls: SimpleNamespace(database_url="sqlite:///test.db")),
    )
    monkeypatch.setattr(guard_cli, "Config", _Config)
    monkeypatch.setattr(guard_cli.command, "upgrade", lambda config, revision: calls.append((config, revision)))
    monkeypatch.setattr(sys, "argv", ["aifence-guard", "migrate", "--revision", "head"])

    guard_cli.main()

    assert len(calls) == 1
    config, revision = calls[0]
    assert revision == "head"
    assert isinstance(config, _Config)
    assert config.options["sqlalchemy.url"] == "sqlite:///test.db"


def test_guard_openapi_writes_document(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    output = tmp_path / "openapi.json"
    fake_app = SimpleNamespace(openapi=lambda: {"openapi": "3.1.0", "info": {"title": "AIFENCE"}})
    monkeypatch.setattr(guard_cli, "create_app", lambda *_args: fake_app)
    monkeypatch.setattr(
        guard_cli.SigningKey,
        "ephemeral_for_tests",
        classmethod(lambda cls: SimpleNamespace()),
    )
    monkeypatch.setattr(sys, "argv", ["aifence-guard", "openapi", "--output", str(output)])

    guard_cli.main()

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["openapi"] == "3.1.0"


def test_guard_evaluate_emits_report_and_exit_code(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    report = SimpleNamespace(pass_rate=1.0, to_dict=lambda: {"pass_rate": 1.0, "passed": 3})

    class _Runner:
        def __init__(self, _engine: object) -> None:
            pass

        def run_file(self, _corpus: Path, *, policy_document: object) -> object:
            assert policy_document is None
            return report

    monkeypatch.setattr(guard_cli, "load_baseline_policy", lambda _path: {"rules": []})
    monkeypatch.setattr(guard_cli, "PolicyEngine", lambda baseline: baseline)
    monkeypatch.setattr(guard_cli, "SecurityEvaluationRunner", _Runner)
    monkeypatch.setattr(sys, "argv", ["aifence-guard", "evaluate"])

    with pytest.raises(SystemExit) as exc:
        guard_cli.main()

    assert exc.value.code == 0
    assert json.loads(capsys.readouterr().out)["passed"] == 3


def test_guard_serve_maps_settings_to_uvicorn(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}
    settings = SimpleNamespace(
        require_mtls=False,
        bind_host="127.0.0.1",
        bind_port=9090,
        trusted_proxy_cidrs=("10.0.0.0/8",),
        tls_cert_file="",
        tls_key_file="",
        tls_client_ca_file="",
        shutdown_grace_seconds=15,
    )
    monkeypatch.setattr(guard_cli.Settings, "from_env", classmethod(lambda cls: settings))
    monkeypatch.setattr(guard_cli.uvicorn, "run", lambda *args, **kwargs: captured.update({"args": args, **kwargs}))
    monkeypatch.setattr(sys, "argv", ["aifence-guard", "serve", "--workers", "2"])

    guard_cli.main()

    assert captured["args"] == ("aifence.main:app",)
    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 9090
    assert captured["workers"] == 2
    assert captured["forwarded_allow_ips"] == "10.0.0.0/8"


def test_guard_bootstrap_dispatches_service(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    class _Service:
        def create_tenant_and_key(self, _session: object, **kwargs: Any) -> tuple[object, object, str]:
            assert kwargs["scopes"] == guard_cli.FULL_ADMIN_SCOPES
            return SimpleNamespace(id="tenant-2"), SimpleNamespace(id="key-2"), "token-2"

    @contextmanager
    def factory() -> Iterator[object]:
        yield object()

    fake_app = SimpleNamespace(state=SimpleNamespace(service=_Service(), session_factory=factory))
    monkeypatch.setattr(guard_cli.Settings, "from_env", classmethod(lambda cls: SimpleNamespace()))
    monkeypatch.setattr(guard_cli, "create_app", lambda _settings: fake_app)
    monkeypatch.setattr(
        sys,
        "argv",
        ["aifence-guard", "bootstrap", "--tenant-name", "Acme", "--key-name", "admin"],
    )

    guard_cli.main()

    payload = json.loads(capsys.readouterr().out)
    assert payload["tenant_id"] == "tenant-2"
    assert payload["api_key_id"] == "key-2"
    assert payload["api_key"] == "token-2"


def test_guard_tenant_maintenance_commands(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    calls: list[tuple[str, object]] = []

    class _Service:
        def reencrypt_stored_secrets(self, _session: object, **kwargs: Any) -> dict[str, object]:
            calls.append(("reencrypt", kwargs))
            return {"updated": 1}

        def rotate_tenant_key(self, _session: object, **kwargs: Any) -> dict[str, object]:
            calls.append(("rotate", kwargs))
            return {"rotated": True}

        def retire_tenant_key(self, _session: object, **kwargs: Any) -> dict[str, object]:
            calls.append(("retire", kwargs))
            return {"retired": True}

        def prune_expired_artifacts(self, _session: object, **kwargs: Any) -> dict[str, object]:
            calls.append(("prune", kwargs))
            return {"deleted": 2}

    @contextmanager
    def factory() -> Iterator[object]:
        yield object()

    fake_app = SimpleNamespace(state=SimpleNamespace(service=_Service(), session_factory=factory))
    monkeypatch.setattr(guard_cli.Settings, "from_env", classmethod(lambda cls: SimpleNamespace()))
    monkeypatch.setattr(guard_cli, "create_app", lambda _settings: fake_app)
    monkeypatch.setattr(guard_cli, "set_tenant_context", lambda session, tenant_id: calls.append(("tenant", tenant_id)))

    commands = [
        ["reencrypt", "--tenant-id", "t1", "--batch-size", "10"],
        ["rotate-tenant-key", "--tenant-id", "t1", "--new-key-id", "kms-v2"],
        ["retire-tenant-key", "--tenant-id", "t1", "--key-id", "kms-v1"],
        ["prune-artifacts", "--tenant-id", "t1", "--batch-size", "20"],
    ]
    for command in commands:
        monkeypatch.setattr(sys, "argv", ["aifence-guard", *command])
        guard_cli.main()
        assert json.loads(capsys.readouterr().out)

    assert any(name == "reencrypt" for name, _value in calls)
    assert any(name == "rotate" for name, _value in calls)
    assert any(name == "retire" for name, _value in calls)
    assert any(name == "prune" for name, _value in calls)


def test_guard_audit_and_maintenance_commands(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    calls: list[tuple[str, object]] = []

    class _Result:
        def model_dump(self, *, mode: str) -> dict[str, object]:
            assert mode == "json"
            return {"anchored": True}

    class _Advanced:
        def anchor_audit(self, _session: object, auth: object, destination: str) -> _Result:
            calls.append(("anchor", (auth, destination)))
            return _Result()

    @contextmanager
    def factory() -> Iterator[object]:
        yield object()

    fake_app = SimpleNamespace(
        state=SimpleNamespace(
            service=SimpleNamespace(),
            session_factory=factory,
            advanced=_Advanced(),
            signing_key=object(),
        )
    )
    monkeypatch.setattr(guard_cli.Settings, "from_env", classmethod(lambda cls: SimpleNamespace()))
    monkeypatch.setattr(guard_cli, "create_app", lambda _settings: fake_app)
    monkeypatch.setattr(guard_cli, "set_tenant_context", lambda session, tenant_id: calls.append(("tenant", tenant_id)))
    monkeypatch.setattr(
        guard_cli,
        "run_tenant_maintenance",
        lambda session, service, **kwargs: {"maintenance": kwargs["tenant_id"]},
    )
    monkeypatch.setattr(
        guard_cli,
        "verify_tenant_chain",
        lambda session, signing_key, tenant_id: {"valid": True, "tenant_id": tenant_id},
    )
    monkeypatch.setattr(
        guard_cli,
        "export_tenant_audit",
        lambda session, signing_key, tenant_id, output: {"tenant_id": tenant_id, "output": str(output)},
    )

    commands = [
        ["anchor-audit", "--tenant-id", "t2", "--destination", "file"],
        ["maintenance", "--tenant-id", "t2"],
        ["verify-audit", "--tenant-id", "t2"],
        ["export-audit", "--tenant-id", "t2", "--output", str(tmp_path / "audit.ndjson")],
    ]
    for command in commands:
        monkeypatch.setattr(sys, "argv", ["aifence-guard", *command])
        if command[0] == "verify-audit":
            with pytest.raises(SystemExit) as exc:
                guard_cli.main()
            assert exc.value.code == 0
        else:
            guard_cli.main()
        assert json.loads(capsys.readouterr().out)

    assert any(name == "anchor" for name, _value in calls)
