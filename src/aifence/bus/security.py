# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import hmac
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Literal

from fastapi import Header, HTTPException, Request, status

from .config import get_settings


@dataclass(frozen=True)
class AuthPrincipal:
    kind: Literal["service", "agent", "development"]
    agent: str | None = None
    workspace: str | None = None

    @property
    def is_service(self) -> bool:
        return self.kind in {"service", "development"}


_principal: ContextVar[AuthPrincipal | None] = ContextVar(
    "sage_auth_principal", default=None
)

_AGENT_ALLOWED_PREFIXES = (
    "/v1/bus/",
    "/v1/transport/",
    "/v1/refs",
    "/v1/states",
    "/v1/negotiate",
    "/v1/send",
    "/v1/receive",
    "/v1/a2a/",
    "/v1/protocol",
    "/v1/facts",
    "/v1/publish",
    "/v1/subscriptions",
    "/v1/routing/choose",
    "/v1/routing/send",
    "/v1/inspect/",
)


def _agent_scope(value: str) -> tuple[str, str]:
    if ":" in value:
        workspace, agent = value.split(":", 1)
    else:
        workspace, agent = "default", value
    if not workspace or not agent:
        raise ValueError("agent key scope must be 'workspace:agent' or 'agent'")
    return workspace, agent




def bearer_token(authorization: str | None) -> str | None:
    if authorization is None:
        return None
    scheme, separator, token = authorization.partition(" ")
    if not separator or scheme.lower() != "bearer":
        return None
    token = token.strip()
    return token or None

def authenticate_token(token: str) -> AuthPrincipal | None:
    settings = get_settings()
    for expected in settings.api_keys:
        if hmac.compare_digest(token, expected):
            return AuthPrincipal("service")
    for expected, scope in settings.agent_keys.items():
        if hmac.compare_digest(token, expected):
            workspace, agent = _agent_scope(scope)
            return AuthPrincipal("agent", agent=agent, workspace=workspace)
    return None


async def require_api_key(
    request: Request,
    authorization: str | None = Header(default=None),
) -> AuthPrincipal:
    settings = get_settings()
    principal: AuthPrincipal | None
    if not settings.auth_required:
        principal = AuthPrincipal("development")
        _principal.set(principal)
        return principal
    supplied = bearer_token(authorization)
    if supplied is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    principal = authenticate_token(supplied)
    if principal is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if principal.kind == "agent" and not request.url.path.startswith(_AGENT_ALLOWED_PREFIXES):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="agent-scoped credentials cannot access control-plane endpoints",
        )
    _principal.set(principal)
    return principal


def current_principal() -> AuthPrincipal:
    principal = _principal.get()
    if principal is None:
        return AuthPrincipal("development")
    return principal


def enforce_agent_scope(*, actor: str | None, workspace: str) -> str | None:
    """Bind actor/workspace to an agent-scoped credential; service credentials pass through."""
    principal = current_principal()
    if principal.is_service:
        return actor
    assert principal.agent is not None and principal.workspace is not None
    if workspace != principal.workspace:
        raise HTTPException(status_code=403, detail="credential is scoped to another workspace")
    if actor is not None and actor != principal.agent:
        raise HTTPException(status_code=403, detail="credential cannot impersonate another agent")
    return principal.agent
