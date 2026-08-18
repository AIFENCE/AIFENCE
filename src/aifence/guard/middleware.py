# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import asyncio
import hashlib
import json
import time
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import Request, Response
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session, sessionmaker
from starlette.datastructures import Headers
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .errors import RateLimitError
from .models import RateLimitBucket


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("x-request-id") or f"req_{uuid4().hex}"
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        nonce = getattr(request.state, "csp_nonce", None)
        if nonce:
            response.headers["Content-Security-Policy"] = (
                "default-src 'none'; base-uri 'none'; frame-ancestors 'none'; "
                f"script-src 'nonce-{nonce}'; style-src 'nonce-{nonce}'; "
                "connect-src 'self'; form-action 'none'"
            )
        else:
            response.headers["Content-Security-Policy"] = (
                "default-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"
            )
        response.headers["Cache-Control"] = "no-store"
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response


class RequestSizeMiddleware:
    """ASGI receive wrapper that enforces actual streamed bytes, including chunked bodies."""

    def __init__(self, app: ASGIApp, max_bytes: int, max_artifact_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes
        # Multipart framing and headers need bounded overhead beyond the artifact payload.
        self.max_artifact_bytes = max_artifact_bytes + 1024 * 1024

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        path = str(scope.get("path", ""))
        limit = self.max_artifact_bytes if path == "/v1/artifacts/scan" else self.max_bytes
        headers = Headers(scope=scope)
        content_length = headers.get("content-length")
        if content_length is not None:
            try:
                if int(content_length) > limit:
                    await self._reject(send, limit)
                    return
            except ValueError:
                await self._json_error(send, 400, "invalid_content_length", "Content-Length is invalid")
                return

        consumed = 0
        exceeded = False

        async def limited_receive() -> Message:
            nonlocal consumed, exceeded
            message = await receive()
            if message["type"] == "http.request":
                consumed += len(message.get("body", b""))
                if consumed > limit:
                    exceeded = True
                    # Raise a private exception before Starlette/FastAPI parse the body.
                    raise _RequestBodyTooLarge
            return message

        try:
            await self.app(scope, limited_receive, send)
        except _RequestBodyTooLarge:
            if not exceeded:
                raise
            await self._reject(send, limit)

    @staticmethod
    async def _json_error(send: Send, status: int, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        body = json.dumps({"error": {"code": code, "message": message, "details": details or {}}}, separators=(",", ":")).encode()
        await send({"type": "http.response.start", "status": status, "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())]})
        await send({"type": "http.response.body", "body": body})

    async def _reject(self, send: Send, limit: int) -> None:
        await self._json_error(
            send,
            413,
            "request_too_large",
            "request body exceeds the configured route limit",
            {"max_bytes": limit},
        )


class _RequestBodyTooLarge(Exception):
    pass


class DatabaseRateLimiter:
    """Database-atomic fixed-window limiter shared by every service replica."""

    def __init__(self, session_factory: sessionmaker[Session], requests_per_minute: int) -> None:
        self.session_factory = session_factory
        self.limit = requests_per_minute
        self._cleanup_lock = asyncio.Lock()
        self._last_cleanup_window = -1

    def check_sync(self, identity: str) -> tuple[int, int]:
        now = int(time.time())
        window_start = now // 60
        identity_hash = hashlib.sha256(identity.encode()).hexdigest()
        count = self._increment(self.session_factory, identity_hash, window_start, False)
        return count, max(1, 60 - (now % 60))

    def enforce_authenticated(self, *, tenant_id: str, key_id: str, path: str) -> None:
        count, retry_after = self.check_sync(f"authenticated:{tenant_id}:{key_id}:{path}")
        if count > self.limit:
            raise RateLimitError(
                "authenticated API key rate limit exceeded",
                details={"retry_after": retry_after},
            )

    async def check_network(self, identity: str) -> tuple[int, int]:
        now = int(time.time())
        window_start = now // 60
        identity_hash = hashlib.sha256(identity.encode()).hexdigest()
        cleanup = False
        async with self._cleanup_lock:
            if self._last_cleanup_window != window_start:
                self._last_cleanup_window = window_start
                cleanup = True
        count = await asyncio.to_thread(
            self._increment,
            self.session_factory,
            identity_hash,
            window_start,
            cleanup,
        )
        return count, max(1, 60 - (now % 60))

    @staticmethod
    def _increment(
        session_factory: sessionmaker[Session],
        identity_hash: str,
        window_start: int,
        cleanup: bool,
    ) -> int:
        with session_factory() as session:
            dialect = session.get_bind().dialect.name
            values = {
                "identity_hash": identity_hash,
                "window_start": window_start,
                "request_count": 1,
                "updated_at": datetime.now(UTC),
            }
            if dialect == "postgresql":
                statement = postgresql_insert(RateLimitBucket).values(**values)
                statement = statement.on_conflict_do_update(
                    index_elements=[RateLimitBucket.identity_hash, RateLimitBucket.window_start],
                    set_={
                        "request_count": RateLimitBucket.request_count + 1,
                        "updated_at": values["updated_at"],
                    },
                ).returning(RateLimitBucket.request_count)
                count = int(session.execute(statement).scalar_one())
            elif dialect == "sqlite":
                statement = sqlite_insert(RateLimitBucket).values(**values)
                statement = statement.on_conflict_do_update(
                    index_elements=[RateLimitBucket.identity_hash, RateLimitBucket.window_start],
                    set_={
                        "request_count": RateLimitBucket.request_count + 1,
                        "updated_at": values["updated_at"],
                    },
                ).returning(RateLimitBucket.request_count)
                count = int(session.execute(statement).scalar_one())
            else:
                statement = select(RateLimitBucket).where(
                    RateLimitBucket.identity_hash == identity_hash,
                    RateLimitBucket.window_start == window_start,
                ).with_for_update()
                bucket = session.scalar(statement)
                if bucket is None:
                    bucket = RateLimitBucket(**values)
                    session.add(bucket)
                    count = 1
                else:
                    bucket.request_count += 1
                    bucket.updated_at = values["updated_at"]  # type: ignore[assignment]
                    count = bucket.request_count
            if cleanup:
                session.execute(delete(RateLimitBucket).where(RateLimitBucket.window_start < window_start - 2))
            session.commit()
            return count


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Pre-authentication network limiter; credential buckets are applied after authentication."""

    def __init__(self, app: Any, limiter: DatabaseRateLimiter) -> None:
        super().__init__(app)
        self.limiter = limiter

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.url.path in {"/health/live", "/health/ready", "/internal/health/ready", "/internal/metrics"}:
            return await call_next(request)
        network = request.client.host if request.client else "unknown"
        try:
            count, retry_after = await self.limiter.check_network(f"network:{network}")
        except Exception:
            return JSONResponse(
                status_code=503,
                content={"error": {"code": "rate_limit_store_unavailable", "message": "request admission could not be verified"}},
            )
        if count > self.limiter.limit:
            return JSONResponse(
                status_code=429,
                headers={"Retry-After": str(retry_after)},
                content={"error": {"code": "rate_limit_exceeded", "message": "network rate limit exceeded"}},
            )
        return await call_next(request)
