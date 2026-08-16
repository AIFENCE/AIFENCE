# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations


class AgentDanceError(Exception):
    code = "agentdance_error"
    status_code = 400

    def __init__(self, message: str, *, details: dict[str, object] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AuthenticationError(AgentDanceError):
    code = "authentication_failed"
    status_code = 401


class AuthorizationError(AgentDanceError):
    code = "authorization_failed"
    status_code = 403


class NotFoundError(AgentDanceError):
    code = "not_found"
    status_code = 404


class ConflictError(AgentDanceError):
    code = "conflict"
    status_code = 409


class PolicyError(AgentDanceError):
    code = "policy_error"
    status_code = 422


class DependencyUnavailableError(AgentDanceError):
    code = "dependency_unavailable"
    status_code = 503


class RateLimitError(AgentDanceError):
    code = "rate_limit_exceeded"
    status_code = 429


class PayloadTooLargeError(AgentDanceError):
    code = "request_too_large"
    status_code = 413


class UnsupportedMediaTypeError(AgentDanceError):
    code = "unsupported_media_type"
    status_code = 415
