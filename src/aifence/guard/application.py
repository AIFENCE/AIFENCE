# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from sqlalchemy import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from . import __version__
from .advanced import AdvancedOperations
from .anchor_dispatcher import AuditAnchorWorker
from .api import router
from .artifact_store import DisabledArtifactStore, FileArtifactStore, S3ArtifactStore
from .clamav import ClamAVClient
from .config import Settings
from .crypto import EnvelopeCipher, SigningKey, SigningProvider, build_signing_provider
from .db import Base, create_database_engine, create_session_factory
from .dispatcher import DispatchWorker
from .errors import AgentDanceError, RateLimitError
from .key_management import build_managed_cipher
from .lifecycle import TenantLifecycleWorker
from .metrics import MetricsMiddleware
from .middleware import (
    DatabaseRateLimiter,
    RateLimitMiddleware,
    RequestSizeMiddleware,
    SecurityHeadersMiddleware,
)
from .models import SigningPublicKey
from .policy import PolicyEngine, load_baseline_policy
from .service import AgentDanceService
from .telemetry import configure_telemetry
from .tenant_crypto import TenantCryptography


def create_app(
    settings: Settings | None = None,
    signing_key: SigningProvider | None = None,
    engine: Engine | None = None,
    session_factory: sessionmaker[Session] | None = None,
) -> FastAPI:
    settings = settings or Settings.from_env()
    # When composed inside AIFENCE, the shared core supplies one engine/session
    # factory so every subsystem shares a single pool and database. Standalone
    # callers still get a self-built engine.
    engine = engine or create_database_engine(settings)
    if settings.auto_create_schema:
        Base.metadata.create_all(engine)
    if signing_key is None:
        try:
            signing_key = build_signing_provider(settings)
        except FileNotFoundError:
            if settings.environment in {"development", "test"}:
                logging.getLogger(__name__).warning(
                    "using an ephemeral signing key; receipts will not survive restart"
                )
                signing_key = SigningKey.ephemeral_for_tests()
            else:
                raise
    if settings.runtime_role == "anchor":
        class _AnchorOnlyCipher:
            active_key_id = "anchor-only"
            def encrypt(self, *_args: object, **_kwargs: object) -> bytes:
                raise RuntimeError("audit-anchor workers cannot encrypt tenant data")
            def decrypt(self, *_args: object, **_kwargs: object) -> bytes:
                raise RuntimeError("audit-anchor workers cannot decrypt tenant data")
        cipher = _AnchorOnlyCipher()
    elif settings.kms_backend == "local":
        active_key_id, encryption_keys = settings.encryption_keyring()
        cipher = EnvelopeCipher(active_key_id=active_key_id, keyring=encryption_keys)
    else:
        cipher = build_managed_cipher(settings)
    baseline_policy = load_baseline_policy(settings.policy_file) if settings.policy_file else None
    policy_engine = PolicyEngine(baseline_policy)
    clamav = ClamAVClient(
        settings.clamav_host,
        settings.clamav_port,
        settings.clamav_timeout_seconds,
    )
    if settings.runtime_role in {"dispatcher", "anchor"}:
        artifact_store = DisabledArtifactStore()
    elif settings.artifact_store_backend == "s3":
        artifact_store = S3ArtifactStore(
            endpoint=settings.artifact_s3_endpoint,
            bucket=settings.artifact_s3_bucket,
            region=settings.artifact_s3_region,
            access_key=settings.artifact_s3_access_key,
            secret_key=settings.artifact_s3_secret_key,
            prefix=settings.artifact_s3_prefix,
            kms_key_id=settings.artifact_s3_kms_key_id,
            object_lock_days=settings.artifact_s3_object_lock_days,
            delete_enabled=settings.artifact_s3_delete_enabled,
            max_object_bytes=settings.max_artifact_bytes * 2,
        )
    else:
        artifact_store = FileArtifactStore(settings.artifact_store_path)
    tenant_crypto = TenantCryptography(cipher, settings)
    service = AgentDanceService(
        settings, signing_key, cipher, policy_engine, clamav,
        artifact_store=artifact_store, tenant_crypto=tenant_crypto,
    )
    advanced = AdvancedOperations(service)
    session_factory = session_factory or create_session_factory(engine)
    with session_factory() as key_session:
        current = key_session.get(SigningPublicKey, signing_key.key_id)
        public_pem = signing_key.public_pem()
        if current is not None and current.public_pem != public_pem:
            raise ValueError("signing key id already exists with different public key material")
        worker_role = settings.runtime_role in {"dispatcher", "lifecycle", "anchor"}
        if worker_role:
            if current is None:
                raise ValueError(
                    "worker signing public key is not registered; start the control plane "
                    "with the same signing identity before worker replicas"
                )
        elif current is None:
            key_session.add(
                SigningPublicKey(
                    key_id=signing_key.key_id,
                    algorithm="Ed25519",
                    public_pem=public_pem,
                    active=True,
                )
            )
        else:
            current.active = True
            current.retired_at = None
        if not worker_role:
            key_session.commit()
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        try:
            yield
        finally:
            for worker_name in ("dispatcher", "lifecycle_worker", "anchor_worker"):
                worker = getattr(application.state, worker_name, None)
                if worker is not None:
                    await worker.close()
            client = getattr(application.state, "http_client", None)
            if client is not None:
                await client.aclose()
            store = getattr(application.state, "artifact_store", None)
            store_client = getattr(store, "client", None)
            if store_client is not None and hasattr(store_client, "close"):
                store_client.close()
            managed_cipher = getattr(application.state, "cipher", None)
            provider = getattr(managed_cipher, "provider", None)
            provider_client = getattr(provider, "client", None)
            if provider_client is not None and hasattr(provider_client, "close"):
                provider_client.close()

    docs_url = "/docs" if settings.docs_enabled else None
    redoc_url = "/redoc" if settings.docs_enabled else None
    openapi_url = "/openapi.json" if settings.docs_enabled else None
    app = FastAPI(
        title="AGENTDANCE",
        summary="Security control and enforcement plane for AI agents",
        version=__version__,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        lifespan=lifespan,
    )
    app.state.version = __version__
    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.signing_key = signing_key
    app.state.service = service
    app.state.advanced = advanced
    app.state.cipher = cipher
    app.state.tenant_crypto = tenant_crypto
    app.state.artifact_store = artifact_store
    app.state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(settings.proxy_timeout_seconds),
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        follow_redirects=False,
        verify=True,
        trust_env=False,
        proxy=settings.egress_proxy_url or None,
    )
    app.state.dispatcher = DispatchWorker(
        session_factory=session_factory, service=service, client=app.state.http_client,
        worker_id=f"api-{id(app)}",
    )
    app.state.lifecycle_worker = TenantLifecycleWorker(
        session_factory=session_factory, service=service, worker_id=f"api-lifecycle-{id(app)}",
    )
    app.state.anchor_worker = AuditAnchorWorker(
        session_factory=session_factory, service=service, worker_id=f"api-anchor-{id(app)}",
    )

    rate_limiter = DatabaseRateLimiter(session_factory, settings.rate_limit_per_minute)
    app.state.rate_limiter = rate_limiter

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        RequestSizeMiddleware,
        max_bytes=settings.max_request_bytes,
        max_artifact_bytes=settings.max_artifact_bytes,
    )
    app.add_middleware(RateLimitMiddleware, limiter=rate_limiter)
    app.add_middleware(MetricsMiddleware)
    if settings.allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(settings.allowed_origins),
            allow_credentials=False,
            allow_methods=["GET", "POST"],
            allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
            max_age=600,
        )
    app.include_router(router)

    @app.exception_handler(AgentDanceError)
    async def agentdance_error_handler(request: Request, exc: AgentDanceError) -> JSONResponse:
        headers: dict[str, str] = {}
        if isinstance(exc, RateLimitError) and "retry_after" in exc.details:
            headers["Retry-After"] = str(exc.details["retry_after"])
        return JSONResponse(
            status_code=exc.status_code,
            headers=headers,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_failed",
                    "message": "request validation failed",
                    "details": {"violations": jsonable_encoder(exc.errors())},
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        logging.getLogger(__name__).exception("database error", exc_info=exc)
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "database_unavailable",
                    "message": "the persistence layer could not complete the request",
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    def custom_openapi() -> dict[str, object]:
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            summary=app.summary,
            routes=app.routes,
        )
        info = schema.setdefault("info", {})
        info["license"] = {"name": "Apache License 2.0", "identifier": "Apache-2.0"}
        info["x-agentdance-server-license"] = "AGPL-3.0-only OR commercial"
        info["x-agentdance-source-code"] = settings.source_code_url
        info["x-agentdance-commercial-license"] = settings.commercial_license_url
        components = schema.setdefault("components", {})
        security_schemes = components.setdefault("securitySchemes", {})
        security_schemes["AgentDanceBearer"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "adk_<key-id>.<secret>",
            "description": "AGENTDANCE API key, optionally bound to an immutable agent manifest, workload, instance, and principal.",
        }
        security_schemes["MutualTLS"] = {
            "type": "mutualTLS",
            "description": "Deployment-level mTLS for API-key callers.",
        }
        security_schemes["SPIFFEWorkload"] = {
            "type": "apiKey",
            "in": "header",
            "name": settings.workload_identity_direct_header,
            "description": "A SPIFFE ID asserted by a mutually authenticated, trusted workload-identity proxy. Direct Internet callers must not be able to set this header.",
        }
        schema["security"] = [
            {"AgentDanceBearer": [], "MutualTLS": []},
            {"SPIFFEWorkload": []},
        ]
        schema["servers"] = [{"url": settings.public_base_url}]
        schemas = components.setdefault("schemas", {})
        schemas["ErrorEnvelope"] = {
            "type": "object",
            "required": ["error"],
            "properties": {
                "error": {
                    "type": "object",
                    "required": ["code", "message"],
                    "properties": {
                        "code": {"type": "string"},
                        "message": {"type": "string"},
                        "details": {"type": "object", "additionalProperties": True},
                        "request_id": {"type": ["string", "null"]},
                    },
                }
            },
        }
        common_errors = {
            str(code): {
                "description": description,
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/ErrorEnvelope"}}
                },
            }
            for code, description in {
                400: "Malformed request", 401: "Authentication failed",
                403: "Authorization or policy enforcement failed",
                404: "Resource not found", 409: "State or idempotency conflict",
                413: "Request body too large", 415: "Unsupported media type",
                422: "Schema or policy validation failed", 429: "Rate limit exceeded",
                502: "Broker upstream returned an unusable response",
                503: "Required dependency unavailable",
            }.items()
        }
        for path, path_item in schema.get("paths", {}).items():
            for method, operation in path_item.items():
                if method.lower() not in {"get", "post", "put", "patch", "delete"} or not isinstance(operation, dict):
                    continue
                if path not in {"/health/live", "/health/ready", "/source"}:
                    operation["security"] = [{"AgentDanceBearer": [], "MutualTLS": []}, {"SPIFFEWorkload": []}]
                    responses = operation.setdefault("responses", {})
                    for code, response in common_errors.items():
                        responses.setdefault(code, response)
                    if path in {"/v1/providers/{provider_id}/invoke", "/v1/tools/{tool_id}/execute"} and method.lower() == "post":
                        responses.setdefault("202", {
                            "description": "Execution accepted for durable asynchronous dispatch",
                            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BrokerResponse"}}},
                        })
                operation.setdefault("parameters", []).append({
                    "name": "X-Request-ID", "in": "header", "required": False,
                    "schema": {"type": "string", "maxLength": 128},
                    "description": "Caller-provided correlation identifier; AGENTDANCE generates one when omitted.",
                })
        for public_path in ("/health/live", "/health/ready", "/source"):
            for operation in schema.get("paths", {}).get(public_path, {}).values():
                if isinstance(operation, dict):
                    operation["security"] = []
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi  # type: ignore[method-assign]
    configure_telemetry(app, engine, settings)
    return app
