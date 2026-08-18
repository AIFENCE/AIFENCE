# SPDX-License-Identifier: AGPL-3.0-or-later
"""Canonical error hierarchy and the structured error-envelope handlers.

A single exception hierarchy so every subsystem raises the same types and every
response shares one envelope shape::

    {"error": {"code", "message", "details", "request_id"}}

Guard keeps its historical ``AifenceError`` name as an alias of
:class:`AIFenceError` during the merge (see ``aifence.guard.errors``).
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

if TYPE_CHECKING:
    from fastapi import FastAPI, Request

_logger = logging.getLogger(__name__)


class AIFenceError(Exception):
    code = "aifence_error"
    status_code = 400

    def __init__(self, message: str, *, details: dict[str, object] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AuthenticationError(AIFenceError):
    code = "authentication_failed"
    status_code = 401


class AuthorizationError(AIFenceError):
    code = "authorization_failed"
    status_code = 403


class NotFoundError(AIFenceError):
    code = "not_found"
    status_code = 404


class ConflictError(AIFenceError):
    code = "conflict"
    status_code = 409


class PolicyError(AIFenceError):
    code = "policy_error"
    status_code = 422


class DependencyUnavailableError(AIFenceError):
    code = "dependency_unavailable"
    status_code = 503


class RateLimitError(AIFenceError):
    code = "rate_limit_exceeded"
    status_code = 429


class PayloadTooLargeError(AIFenceError):
    code = "request_too_large"
    status_code = 413


class UnsupportedMediaTypeError(AIFenceError):
    code = "unsupported_media_type"
    status_code = 415


def _envelope(request: Request, code: str, message: str, details: dict[str, object] | None = None) -> dict[str, object]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "request_id": getattr(request.state, "request_id", None),
        }
    }


def install_exception_handlers(app: FastAPI) -> None:
    """Register the shared error-envelope handlers on a FastAPI application."""

    @app.exception_handler(AIFenceError)
    async def _aifence_error(request: Request, exc: AIFenceError) -> JSONResponse:
        headers: dict[str, str] = {}
        if isinstance(exc, RateLimitError) and "retry_after" in exc.details:
            headers["Retry-After"] = str(exc.details["retry_after"])
        return JSONResponse(
            status_code=exc.status_code,
            headers=headers,
            content=_envelope(request, exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_envelope(
                request,
                "validation_failed",
                "request validation failed",
                {"violations": jsonable_encoder(exc.errors())},
            ),
        )

    @app.exception_handler(SQLAlchemyError)
    async def _database_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        _logger.exception("database error", exc_info=exc)
        return JSONResponse(
            status_code=503,
            content=_envelope(
                request,
                "database_unavailable",
                "the persistence layer could not complete the request",
            ),
        )
