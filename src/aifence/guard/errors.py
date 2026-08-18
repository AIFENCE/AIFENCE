# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from ..core.errors import AIFenceError


class AifenceError(AIFenceError):
    """Guard's error base, rooted in the shared hierarchy.

    Inheriting from ``AIFenceError`` means a guard exception raised outside the
    guard sub-application (e.g. by the shared authentication dependency serving
    the fence flow) is still rendered as the standard error envelope with the
    correct status code, instead of falling through as a 500.
    """

    code = "aifence_guard_error"
    status_code = 400

    def __init__(self, message: str, *, details: dict[str, object] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AuthenticationError(AifenceError):
    code = "authentication_failed"
    status_code = 401


class AuthorizationError(AifenceError):
    code = "authorization_failed"
    status_code = 403


class NotFoundError(AifenceError):
    code = "not_found"
    status_code = 404


class ConflictError(AifenceError):
    code = "conflict"
    status_code = 409


class PolicyError(AifenceError):
    code = "policy_error"
    status_code = 422


class DependencyUnavailableError(AifenceError):
    code = "dependency_unavailable"
    status_code = 503


class RateLimitError(AifenceError):
    code = "rate_limit_exceeded"
    status_code = 429


class PayloadTooLargeError(AifenceError):
    code = "request_too_large"
    status_code = 413


class UnsupportedMediaTypeError(AifenceError):
    code = "unsupported_media_type"
    status_code = 415
