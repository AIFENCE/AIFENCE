# SPDX-License-Identifier: AGPL-3.0-or-later
"""Top-level AIFENCE operator/developer CLI.

The monorepo previously exposed several subsystem-specific entry points.  This
CLI provides one supported front door for the common lifecycle: inspect the
installation, validate configuration, bootstrap a tenant, and run a complete
Quality -> Guard -> Bus demonstration.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from sqlalchemy import text

from .core.config import CoreSettings
from .versions import version_inventory


def _json(data: object) -> None:
    print(json.dumps(data, indent=2, sort_keys=True, default=str))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aifence", description="AIFENCE control-plane CLI")
    parser.add_argument("--version", action="store_true", help="print the AIFENCE platform version")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("version", help="show platform, subsystem, SDK, and protocol versions")
    sub.add_parser("status", help="show resolved non-secret runtime configuration")

    doctor = sub.add_parser("doctor", help="validate configuration and runtime dependencies")
    doctor.add_argument("--json", action="store_true", dest="as_json")

    bootstrap = sub.add_parser("bootstrap", help="create the first tenant and administrative API key")
    bootstrap.add_argument("--tenant-name", required=True)
    bootstrap.add_argument("--key-name", default="initial-administrator")

    demo = sub.add_parser("demo", help="run a local end-to-end Quality -> Guard -> Bus lifecycle")
    demo.add_argument("--artifact", default=None, help="artifact text to submit")
    demo.add_argument("--receiver", default="demo-receiver")

    sub.add_parser("serve", help="run the composed HTTP API")
    return parser


def _resolved_status() -> dict[str, object]:
    settings = CoreSettings.from_env()
    return {
        "versions": version_inventory(),
        "runtime": {
            "environment": settings.environment,
            "runtime_role": settings.runtime_role,
            "public_base_url": settings.public_base_url,
            "database_backend": "sqlite" if settings.is_sqlite else "server",
            "docs_enabled": settings.docs_enabled,
            "region": settings.region or None,
            "region_role": settings.region_role,
            "bus_transport": settings.bus_transport,
            "flow_fail_open_tiers": list(settings.flow_fail_open_tiers),
        },
    }


def _doctor() -> dict[str, object]:
    checks: list[dict[str, object]] = []

    def record(name: str, fn: Any) -> None:
        try:
            detail = fn()
            checks.append({"name": name, "ok": True, "detail": detail})
        except Exception as exc:  # doctor must report all failures, not stop at the first one
            checks.append({"name": name, "ok": False, "error": f"{type(exc).__name__}: {exc}"})

    settings_holder: dict[str, CoreSettings] = {}

    def check_settings() -> str:
        settings = CoreSettings.from_env()
        settings_holder["settings"] = settings
        return f"{settings.environment}/{settings.runtime_role}"

    record("core.configuration", check_settings)

    def check_app() -> str:
        from .app import create_app

        settings = settings_holder.get("settings") or CoreSettings.from_env()
        app = create_app(settings)
        with app.state.session_factory() as session:
            session.execute(text("SELECT 1")).scalar_one()
        app.state.engine.dispose()
        return ",".join(app.state.subsystems)

    record("composed.application", check_app)

    def check_quality() -> str:
        from .quality.controls import load_controls, registry_path

        controls = load_controls()
        if not controls:
            raise RuntimeError(f"quality registry is empty: {registry_path()}")
        return f"{len(controls)} controls"

    record("quality.registry", check_quality)

    def check_protocol() -> str:
        from .bus.protocol_spec import AIFENCE_PROTOCOL, AIFENCE_WIRE_VERSION, wire_schema

        schema = wire_schema()
        if not isinstance(schema, dict) or not schema:
            raise RuntimeError("wire schema is empty")
        return f"{AIFENCE_PROTOCOL} wire={AIFENCE_WIRE_VERSION}"

    record("bus.protocol", check_protocol)

    ok = all(bool(item["ok"]) for item in checks)
    return {"ok": ok, "versions": version_inventory(), "checks": checks}


def _bootstrap(tenant_name: str, key_name: str) -> dict[str, object]:
    from .app import create_app
    from .guard.auth import FULL_ADMIN_SCOPES

    app = create_app(CoreSettings.from_env())
    service = app.state.guard_app.state.service
    with app.state.session_factory() as session:
        tenant, key, token = service.create_tenant_and_key(
            session,
            tenant_name=tenant_name,
            key_name=key_name,
            scopes=FULL_ADMIN_SCOPES,
        )
    app.state.engine.dispose()
    return {
        "tenant_id": tenant.id,
        "api_key_id": key.id,
        "api_key": token,
        "warning": "This API key is shown once. Store it in a secret manager immediately.",
    }


def _demo(artifact: str | None, receiver: str) -> dict[str, object]:
    """Run the real composed application against an isolated SQLite database."""
    from fastapi.testclient import TestClient

    from .app import create_app
    from .bus.bus import SemanticBus
    from .bus.config import get_settings as bus_settings
    from .guard.auth import FULL_ADMIN_SCOPES

    sample = artifact or (
        "# Release Readiness\n\n"
        "The candidate passed all required checks and is ready for controlled deployment. "
        "Rollback ownership and validation criteria are documented for the receiving agent."
    )
    with tempfile.TemporaryDirectory(prefix="aifence-demo-") as tmp:
        db_path = Path(tmp) / "aifence.db"
        app = create_app(CoreSettings(environment="test", database_url=f"sqlite+pysqlite:///{db_path}"))
        with app.state.session_factory() as session:
            tenant, key, token = app.state.guard_app.state.service.create_tenant_and_key(
                session,
                tenant_name="AIFENCE Demo",
                key_name="demo",
                scopes=FULL_ADMIN_SCOPES,
            )

        with TestClient(app, headers={"Authorization": f"Bearer {token}"}) as client:
            response = client.post(
                "/v1/fence/submit",
                json={
                    "artifact": sample,
                    "content_type": "text/markdown",
                    "receiver": receiver,
                    "action": {"operation": "read"},
                    "risk_score": 10,
                },
            )
            response.raise_for_status()
            receipt = response.json()

        message_id = receipt.get("stages", {}).get("bus", {}).get("message_id")
        with app.state.session_factory() as session:
            workspace = receipt.get("stages", {}).get("bus", {}).get("workspace", "default")
            claimed = SemanticBus(session, bus_settings()).pull(
                receiver=receiver, workspace=str(workspace), claim=True
            )
            session.commit()
        app.state.engine.dispose()
        return {
            "ok": receipt.get("allowed") is True and any(item.id == message_id for item in claimed),
            "tenant_id": tenant.id,
            "api_key_id": key.id,
            "request_id": receipt.get("request_id"),
            "final_outcome": receipt.get("final_outcome"),
            "quality": receipt.get("stages", {}).get("quality"),
            "guard": receipt.get("stages", {}).get("guard"),
            "bus": receipt.get("stages", {}).get("bus"),
            "receiver_claimed_message_ids": [item.id for item in claimed],
        }


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.version and args.command is None:
        print(version_inventory()["platform"])
        return
    if args.command in {None, "version"}:
        _json(version_inventory())
        return
    if args.command == "status":
        _json(_resolved_status())
        return
    if args.command == "doctor":
        result = _doctor()
        if args.as_json:
            print(json.dumps(result, separators=(",", ":"), sort_keys=True, default=str))
        else:
            _json(result)
        raise SystemExit(0 if result["ok"] else 1)
    if args.command == "bootstrap":
        _json(_bootstrap(args.tenant_name, args.key_name))
        return
    if args.command == "demo":
        result = _demo(args.artifact, args.receiver)
        _json(result)
        raise SystemExit(0 if result["ok"] else 1)
    if args.command == "serve":
        from .main import run

        run()
        return
    parser.error(f"unknown command: {args.command}")


def doctor_main() -> None:
    main(["doctor", *sys.argv[1:]])


def demo_main() -> None:
    main(["demo", *sys.argv[1:]])


def bootstrap_main() -> None:
    # Preserve all command-line arguments after the entry-point name.
    main(["bootstrap", *sys.argv[1:]])


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv[1:])
