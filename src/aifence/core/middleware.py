# SPDX-License-Identifier: AGPL-3.0-or-later
"""Generic, model-free HTTP middleware shared by the composed application.

Only cross-cutting middleware that has no subsystem dependency lives here:
security headers and a streamed request-size limiter. Stateful, model-backed
middleware (e.g. guard's database rate limiter, which needs its own tables)
stays with the subsystem that owns those tables.
"""
from __future__ import annotations

import json
from collections.abc import Awaitable, Callable, Mapping
from uuid import uuid4

from fastapi import Request, Response
from starlette.datastructures import Headers
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Assigns a request id and hardens response headers."""

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


class _RequestBodyTooLarge(Exception):
    pass


class RequestSizeMiddleware:
    """ASGI receive wrapper enforcing streamed byte limits, including chunked bodies.

    ``route_limits`` maps an exact request path to a per-route byte ceiling
    (e.g. guard's artifact-scan route), so subsystems can raise the limit for
    specific endpoints without a bespoke middleware.
    """

    def __init__(
        self,
        app: ASGIApp,
        max_bytes: int,
        route_limits: Mapping[str, int] | None = None,
    ) -> None:
        self.app = app
        self.max_bytes = max_bytes
        self.route_limits = dict(route_limits or {})

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        path = str(scope.get("path", ""))
        limit = self.route_limits.get(path, self.max_bytes)
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
                    raise _RequestBodyTooLarge
            return message

        try:
            await self.app(scope, limited_receive, send)
        except _RequestBodyTooLarge:
            if not exceeded:
                raise
            await self._reject(send, limit)

    @staticmethod
    async def _json_error(
        send: Send, status: int, code: str, message: str, details: dict[str, object] | None = None
    ) -> None:
        body = json.dumps(
            {"error": {"code": code, "message": message, "details": details or {}}},
            separators=(",", ":"),
        ).encode()
        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode()),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})

    async def _reject(self, send: Send, limit: int) -> None:
        await self._json_error(
            send,
            413,
            "request_too_large",
            "request body exceeds the configured route limit",
            {"max_bytes": limit},
        )
