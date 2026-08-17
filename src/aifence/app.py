# SPDX-License-Identifier: AGPL-3.0-or-later
"""The composed AIFENCE FastAPI application factory.

``create_app`` builds one application that owns the shared engine, session
factory, middleware stack, error envelope, health surface, and OpenAPI
document — then invites each installed subsystem to mount itself. There is no
module-level ``app`` and no import-time database work, so the app is safe to
build repeatedly (tests, workers, embedders).
"""
from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.routing import Mount

from . import __version__
from .core.config import CoreSettings
from .core.db import Base, create_database_engine, create_session_factory
from .core.errors import install_exception_handlers
from .core.metrics import MetricsMiddleware, metrics_response
from .core.middleware import RequestSizeMiddleware, SecurityHeadersMiddleware
from .core.telemetry import configure_telemetry
from .subsystems import SubsystemContext, discover_subsystems

_logger = logging.getLogger(__name__)


def _guarded(shutdown: Callable[[], Awaitable[None]]) -> Callable[[], Awaitable[None]]:
    """Wrap a shutdown hook so one failure cannot abort the remaining teardown."""

    async def run() -> None:
        try:
            await shutdown()
        except Exception:  # pragma: no cover - defensive shutdown
            _logger.exception("subsystem shutdown hook failed")

    return run


async def _noop() -> None:
    return None


def _closer(resource: Any) -> Callable[[], Awaitable[None]]:
    async def close() -> None:
        resource.close()

    return close


def _install_tier_handler(app: FastAPI) -> None:
    """Render a fail-closed tier outage as 503 rather than a 500."""
    from .resilience import TierUnavailable

    @app.exception_handler(TierUnavailable)
    async def _tier_unavailable(request: Request, exc: TierUnavailable) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            headers={"Retry-After": "5"},
            content={
                "error": {
                    "code": "tier_unavailable",
                    "message": str(exc),
                    "details": {"tier": exc.tier, "reason": exc.reason},
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )


def create_app(settings: CoreSettings | None = None) -> FastAPI:
    settings = settings or CoreSettings.from_env()
    logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO))

    engine = create_database_engine(settings)
    session_factory = create_session_factory(engine)
    ctx = SubsystemContext(settings=settings, engine=engine, session_factory=session_factory)

    subsystems = discover_subsystems()

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        async with AsyncExitStack() as stack:
            # Starlette does NOT run a mounted sub-application's lifespan, so a
            # subsystem mounted as a sub-app would never start or clean up its
            # own resources (HTTP clients, durable workers, object-store and KMS
            # clients). Bridge each mounted lifespan into the composed one so the
            # whole fence starts and shuts down as a single unit.
            for route in application.routes:
                sub = getattr(route, "app", None)
                lifespan_context = getattr(getattr(sub, "router", None), "lifespan_context", None)
                if isinstance(route, Mount) and lifespan_context is not None:
                    await stack.enter_async_context(lifespan_context(sub))
                    _logger.debug("bridged lifespan for sub-application at %s", route.path)
            for startup, shutdown in ctx.lifespan_hooks:
                await startup()
                stack.push_async_callback(_guarded(shutdown))
            yield

    app = FastAPI(
        title="AIFENCE",
        summary="One governed fence around AI agents: quality, enforcement, and semantic transport.",
        version=__version__,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
        lifespan=lifespan,
    )
    app.state.version = __version__
    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = session_factory

    # --- shared middleware (outermost first) ---
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestSizeMiddleware, max_bytes=settings.max_request_bytes)
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
    if settings.allowed_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.allowed_hosts))

    install_exception_handlers(app)

    # --- shared operational surface ---
    @app.get("/health/live", include_in_schema=False)
    def health_live() -> dict[str, object]:
        return {"alive": True, "version": __version__}

    @app.get("/health/ready", include_in_schema=False)
    def health_ready() -> dict[str, object]:
        return {
            "ready": True,
            "version": __version__,
            "subsystems": [name for name, _ in subsystems],
        }

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> object:
        return metrics_response()

    # --- subsystem composition (the merge seam) ---
    registered: list[str] = []
    for name, module in subsystems:
        module.register(app, ctx)
        registered.append(name)
        _logger.info("registered subsystem %s", name)
    app.state.subsystems = registered

    # --- the fence flow: the three tiers as one logical pipeline ---
    from .flow import FlowBreakers
    from .flow import router as fence_router

    app.state.flow_breakers = FlowBreakers.from_settings(settings)
    ctx.add_lifespan_hook(_noop, _closer(app.state.flow_breakers))
    app.include_router(fence_router)
    _install_tier_handler(app)

    # Build the whole schema once, now that every subsystem has registered its
    # models against the one shared Base. Done eagerly (not only in the lifespan)
    # so the composed app is immediately usable end to end.
    if settings.auto_create_schema:
        Base.metadata.create_all(engine)

    _install_openapi(app, settings)
    configure_telemetry(app, engine, settings)
    return app


def _install_openapi(app: FastAPI, settings: CoreSettings) -> None:
    def _merge_mounted(schema: dict[str, Any]) -> None:
        """Fold each mounted sub-app's OpenAPI into the one composed document.

        Guard and bus are mounted sub-applications; without this, their paths
        live only in ``/guard/openapi.json`` and ``/bus/openapi.json``. Merging
        gives the fence a single API surface: sub-app paths are re-based under
        their mount, and component schemas are namespaced by mount to avoid
        collisions between subsystems.
        """
        paths: dict[str, Any] = schema.setdefault("paths", {})
        components: dict[str, Any] = schema.setdefault("components", {}).setdefault("schemas", {})
        for route in app.routes:
            sub = getattr(route, "app", None)
            openapi = getattr(sub, "openapi", None)
            if not isinstance(route, Mount) or openapi is None:
                continue
            mount = route.path.rstrip("/")
            prefix = mount.lstrip("/").replace("/", "_").capitalize()
            try:
                sub_schema = openapi()
            except Exception:  # pragma: no cover - a sub-app without OpenAPI
                continue
            for sub_path, item in sub_schema.get("paths", {}).items():
                merged = json.loads(json.dumps(item).replace("#/components/schemas/", f"#/components/schemas/{prefix}_"))
                paths[f"{mount}{sub_path}"] = merged
            for name, definition in sub_schema.get("components", {}).get("schemas", {}).items():
                fixed = json.loads(json.dumps(definition).replace("#/components/schemas/", f"#/components/schemas/{prefix}_"))
                components[f"{prefix}_{name}"] = fixed

    def custom_openapi() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            summary=app.summary,
            routes=app.routes,
        )
        info = schema.setdefault("info", {})
        info["license"] = {"name": "AGPL-3.0-or-later OR Commercial"}
        info["x-aifence-source-code"] = settings.source_code_url
        info["x-aifence-commercial-license"] = settings.commercial_license_url
        schema["servers"] = [{"url": settings.public_base_url}]
        _merge_mounted(schema)
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi  # type: ignore[method-assign]
