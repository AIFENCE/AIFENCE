# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import logging
import os
import secrets
import ssl
from pathlib import Path

import uvicorn
from alembic import command
from alembic.config import Config

from .application import create_app
from .audit import export_tenant_audit, verify_tenant_chain
from .auth import KNOWN_SCOPES, AuthContext
from .config import Settings
from .crypto import SigningKey, generate_key_files
from .db import set_tenant_context
from .evaluation import SecurityEvaluationRunner
from .maintenance import run_tenant_maintenance
from .policy import PolicyEngine, load_baseline_policy
from .service import AifenceService

FULL_ADMIN_SCOPES = sorted(KNOWN_SCOPES)

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aifence")
    sub = parser.add_subparsers(dest="command", required=True)
    serve = sub.add_parser("serve", help="run the AIFENCE API")
    serve.add_argument("--workers", type=int, default=1)
    keygen = sub.add_parser("keygen", help="generate signing and encryption material")
    keygen.add_argument("--directory", type=Path, required=True)
    migrate = sub.add_parser("migrate", help="apply database migrations")
    migrate.add_argument("--revision", default="head")
    bootstrap = sub.add_parser("bootstrap", help="create the first tenant and administrative API key")
    bootstrap.add_argument("--tenant-name", required=True)
    bootstrap.add_argument("--key-name", default="initial-administrator")
    verify = sub.add_parser("verify-audit", help="verify a tenant's signed audit chain")
    verify.add_argument("--tenant-id", required=True)
    export = sub.add_parser("export-audit", help="export a verified NDJSON audit archive")
    export.add_argument("--tenant-id", required=True)
    export.add_argument("--output", type=Path, required=True)
    openapi = sub.add_parser("openapi", help="write the OpenAPI document")
    openapi.add_argument("--output", type=Path, default=Path("openapi.json"))
    reencrypt = sub.add_parser(
        "reencrypt", help="re-encrypt one tenant's stored secrets under the active tenant key route"
    )
    reencrypt.add_argument("--tenant-id", required=True)
    reencrypt.add_argument("--batch-size", type=int, default=500)
    rotate_tenant_key = sub.add_parser(
        "rotate-tenant-key", help="activate a new external KMS key and re-encrypt tenant data"
    )
    rotate_tenant_key.add_argument("--tenant-id", required=True)
    rotate_tenant_key.add_argument("--new-key-id", required=True)
    rotate_tenant_key.add_argument("--batch-size", type=int, default=500)
    retire_tenant_key = sub.add_parser(
        "retire-tenant-key", help="remove an unused historical tenant KMS key from the route"
    )
    retire_tenant_key.add_argument("--tenant-id", required=True)
    retire_tenant_key.add_argument("--key-id", required=True)
    retire_tenant_key.add_argument("--batch-size", type=int, default=500)
    prune = sub.add_parser("prune-artifacts", help="delete one tenant's expired artifacts")
    prune.add_argument("--tenant-id", required=True)
    prune.add_argument("--batch-size", type=int, default=500)
    worker = sub.add_parser("worker", help="run the durable broker dispatcher")
    worker.add_argument("--once", action="store_true")
    worker.add_argument("--limit", type=int, default=None)
    worker.add_argument("--worker-id", default=f"worker-{os.getpid()}")
    lifecycle_worker = sub.add_parser("lifecycle-worker", help="run tenant lifecycle and retention jobs")
    lifecycle_worker.add_argument("--once", action="store_true")
    lifecycle_worker.add_argument("--limit", type=int, default=None)
    lifecycle_worker.add_argument("--worker-id", default=f"lifecycle-{os.getpid()}")
    anchor_worker = sub.add_parser("anchor-worker", help="deliver and verify durable audit anchors")
    anchor_worker.add_argument("--once", action="store_true")
    anchor_worker.add_argument("--limit", type=int, default=None)
    anchor_worker.add_argument("--worker-id", default=f"anchor-{os.getpid()}")
    anchor = sub.add_parser("anchor-audit", help="publish and verify an external audit-chain anchor")
    anchor.add_argument("--tenant-id", required=True)
    anchor.add_argument("--destination", choices=["file", "webhook"], required=True)
    evaluation = sub.add_parser("evaluate", help="run the deterministic agentic security evaluation corpus")
    evaluation.add_argument("--corpus", type=Path, default=Path("evals/agentic-security-v1.json"))
    evaluation.add_argument("--policy", type=Path)
    evaluation.add_argument("--output", type=Path)
    evaluation.add_argument("--fail-under", type=float, default=1.0)
    maintenance = sub.add_parser("maintenance", help="run bounded tenant retention and expiry maintenance")
    maintenance.add_argument("--tenant-id", required=True)
    maintenance.add_argument("--batch-size", type=int, default=500)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    logging.basicConfig(
        level=os.getenv("AIFENCE_GUARD_LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    if args.command == "keygen":
        private_path, public_path = generate_key_files(args.directory)
        master = base64.b64encode(secrets.token_bytes(32)).decode()
        pepper = secrets.token_urlsafe(48)
        output = {
            "signing_private_key_file": str(private_path),
            "signing_public_key_file": str(public_path),
            "master_key_id": "master-v1",
            "master_key_b64": master,
            "master_keyring": {"master-v1": master},
            "api_key_pepper_id": "pepper-v1",
            "api_key_pepper": pepper,
            "api_key_pepperring": {"pepper-v1": pepper},
        }
        master_path = args.directory / "master-key.b64"
        keyring_path = args.directory / "master-keyring.json"
        pepper_path = args.directory / "api-key-pepper"
        pepperring_path = args.directory / "api-key-pepperring.json"
        master_path.write_text(master + "\n")
        keyring_path.write_text(json.dumps({"master-v1": master}, indent=2) + "\n")
        pepper_path.write_text(pepper + "\n")
        pepperring_path.write_text(json.dumps({"pepper-v1": pepper}, indent=2) + "\n")
        os.chmod(master_path, 0o600)
        os.chmod(keyring_path, 0o600)
        os.chmod(pepper_path, 0o600)
        os.chmod(pepperring_path, 0o600)
        secrets_path = args.directory / "generated-secrets.json"
        secrets_path.write_text(json.dumps(output, indent=2) + "\n")
        os.chmod(secrets_path, 0o600)
        print(json.dumps({"created": [str(private_path), str(public_path), str(master_path), str(keyring_path), str(pepper_path), str(pepperring_path), str(secrets_path)]}, indent=2))
        return
    if args.command == "migrate":
        settings = Settings.from_env()
        config = Config(os.getenv("AIFENCE_GUARD_ALEMBIC_INI", str(Path.cwd() / "alembic.ini")))
        config.set_main_option("sqlalchemy.url", settings.database_url)
        command.upgrade(config, args.revision)
        return
    if args.command == "openapi":
        settings = Settings(
            environment="test",
            database_url="sqlite+pysqlite:///:memory:",
            auto_create_schema=True,
            docs_enabled=True,
        )
        app = create_app(settings, SigningKey.ephemeral_for_tests())
        args.output.write_text(json.dumps(app.openapi(), indent=2) + "\n")
        return

    if args.command == "evaluate":
        baseline = load_baseline_policy(None)
        policy_document = json.loads(args.policy.read_text()) if args.policy else None
        report = SecurityEvaluationRunner(PolicyEngine(baseline)).run_file(
            args.corpus, policy_document=policy_document
        )
        rendered = json.dumps(report.to_dict(), indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered)
        print(rendered, end="")
        raise SystemExit(0 if report.pass_rate >= args.fail_under else 1)

    settings = Settings.from_env()
    if args.command == "serve":
        ssl_cert_reqs = ssl.CERT_REQUIRED if settings.require_mtls else ssl.CERT_NONE
        uvicorn.run(
            "aifence.main:app",
            host=settings.bind_host,
            port=settings.bind_port,
            workers=args.workers,
            proxy_headers=bool(settings.trusted_proxy_cidrs),
            forwarded_allow_ips=",".join(settings.trusted_proxy_cidrs) or None,
            ssl_certfile=settings.tls_cert_file or None,
            ssl_keyfile=settings.tls_key_file or None,
            ssl_ca_certs=settings.tls_client_ca_file or None,
            ssl_cert_reqs=ssl_cert_reqs,
            timeout_graceful_shutdown=settings.shutdown_grace_seconds,
            server_header=False,
        )
        return

    app = create_app(settings)
    service: AifenceService = app.state.service
    factory = app.state.session_factory
    if args.command in {"worker", "lifecycle-worker", "anchor-worker"}:
        target = {
            "worker": app.state.dispatcher,
            "lifecycle-worker": app.state.lifecycle_worker,
            "anchor-worker": app.state.anchor_worker,
        }[args.command]
        target.worker_id = args.worker_id
        async def run_worker() -> None:
            try:
                if args.once:
                    result = await target.run_once(limit=args.limit)
                    print(json.dumps(result.__dict__, indent=2, default=str))
                else:
                    await target.run_forever()
            finally:
                await target.close()
                await app.state.http_client.aclose()
        asyncio.run(run_worker())
        return
    with factory() as session:
        if args.command == "reencrypt":
            set_tenant_context(session, args.tenant_id)
            result = service.reencrypt_stored_secrets(
                session, tenant_id=args.tenant_id, batch_size=args.batch_size
            )
            print(json.dumps(result, indent=2))
            return
        if args.command == "rotate-tenant-key":
            result = service.rotate_tenant_key(
                session, tenant_id=args.tenant_id, new_key_id=args.new_key_id,
                batch_size=args.batch_size,
            )
            print(json.dumps(result, indent=2))
            return
        if args.command == "retire-tenant-key":
            result = service.retire_tenant_key(
                session, tenant_id=args.tenant_id, key_id=args.key_id,
                batch_size=args.batch_size,
            )
            print(json.dumps(result, indent=2))
            return
        if args.command == "prune-artifacts":
            set_tenant_context(session, args.tenant_id)
            result = service.prune_expired_artifacts(
                session, tenant_id=args.tenant_id, batch_size=args.batch_size
            )
            print(json.dumps(result, indent=2))
            return
        if args.command == "anchor-audit":
            set_tenant_context(session, args.tenant_id)
            auth = AuthContext(args.tenant_id, "cli-anchor", frozenset({"*"}))
            result = app.state.advanced.anchor_audit(
                session, auth, args.destination
            )
            print(json.dumps(result.model_dump(mode="json"), indent=2, default=str))
            return
        if args.command == "maintenance":
            set_tenant_context(session, args.tenant_id)
            result = run_tenant_maintenance(
                session, service, tenant_id=args.tenant_id, batch_size=args.batch_size
            )
            print(json.dumps(result, indent=2, default=str))
            return
        if args.command == "bootstrap":
            tenant, key, token = service.create_tenant_and_key(
                session,
                tenant_name=args.tenant_name,
                key_name=args.key_name,
                scopes=FULL_ADMIN_SCOPES,
            )
            print(
                json.dumps(
                    {
                        "tenant_id": tenant.id,
                        "api_key_id": key.id,
                        "api_key": token,
                        "warning": "This API key is shown once. Store it in a secret manager immediately.",
                    },
                    indent=2,
                )
            )
            return
        if args.command == "verify-audit":
            set_tenant_context(session, args.tenant_id)
            result = verify_tenant_chain(session, app.state.signing_key, args.tenant_id)
            print(json.dumps(result, indent=2))
            raise SystemExit(0 if result["valid"] else 1)
        if args.command == "export-audit":
            set_tenant_context(session, args.tenant_id)
            result = export_tenant_audit(
                session, app.state.signing_key, args.tenant_id, args.output
            )
            print(json.dumps(result, indent=2))
            return


if __name__ == "__main__":
    main()
