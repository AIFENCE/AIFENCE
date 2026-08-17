# SPDX-License-Identifier: AGPL-3.0-or-later
"""Authentication for the AIFENCE-native routers (the fence flow and quality).

Those routers are served by the composed application itself rather than by a
mounted subsystem, so they do not inherit the guard sub-application's
router-level authentication. This module binds them to the *same* API-key
identity guard enforces, so the fence has exactly one identity model rather
than a second, weaker one.

It fails closed: when no identity provider is installed, the endpoints refuse
to serve instead of silently accepting anonymous callers.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .core.errors import AuthenticationError, DependencyUnavailableError

if TYPE_CHECKING:
    from .guard.auth import AuthContext

bearer_scheme = HTTPBearer(auto_error=False, scheme_name="AIFenceBearer")


def require_identity(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> AuthContext:
    """Authenticate a caller against the guard tier's API keys.

    Raises 503 when no identity provider is composed in, 401 when the bearer
    credential is missing or invalid.
    """
    guard_app = getattr(request.app.state, "guard_app", None)
    if guard_app is None:
        raise DependencyUnavailableError(
            "no identity provider is installed; this endpoint refuses anonymous access"
        )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationError("a Bearer API key is required")

    from .guard.auth import authenticate

    peppers = guard_app.state.settings.accepted_peppers()
    with request.app.state.session_factory() as session:
        return authenticate(session, credentials.credentials.strip(), peppers)


#: Dependency alias for routers composed directly onto the application.
IdentityDep = Annotated["AuthContext", Depends(require_identity)]
