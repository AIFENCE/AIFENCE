# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import hmac
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .crypto import api_key_digest, parse_api_key
from .db import set_key_context, set_tenant_context
from .errors import AuthenticationError, AuthorizationError
from .models import APIKey, Tenant

KNOWN_SCOPES = frozenset({
    "agents:read", "agents:write",
    "approvals:read", "approvals:write",
    "artifacts:read", "artifacts:write", "artifacts:quarantine:read",
    "audit:read", "audit:verify", "audit:checkpoint",
    "brokers:private",
    "capabilities:consume", "capabilities:issue", "capabilities:revoke",
    "decisions:read", "decisions:write",
    "events:read", "events:write",
    "executions:read", "executions:reconcile",
    "incidents:read", "incidents:write",
    "keys:read", "keys:write",
    "policies:activate", "policies:read", "policies:write",
    "providers:invoke", "providers:read", "providers:write",
    "tools:execute", "tools:read", "tools:write",
    "workloads:read", "workloads:write", "audit:anchor",
    "memory:read", "memory:write", "memory:quarantine",
    "delegations:read", "delegations:write", "delegations:revoke",
    "budgets:read", "budgets:write", "budgets:reserve",
    "tenants:lifecycle", "protocols:read", "protocols:write", "protocols:invoke",
    "dispatch:run",
})


@dataclass(frozen=True)
class AuthContext:
    tenant_id: str
    key_id: str
    scopes: frozenset[str]
    expires_at: datetime | None = None
    bound_agent_id: str | None = None
    bound_workload_identity: str | None = None
    bound_instance_id: str | None = None
    bound_principal_type: str | None = None
    bound_principal_id: str | None = None

    def require(self, *required: str) -> None:
        missing = [scope for scope in required if scope not in self.scopes and "*" not in self.scopes]
        if missing:
            raise AuthorizationError("API key lacks required scopes", details={"missing": missing})

    def assert_decision_identity(
        self,
        *,
        agent_id: str,
        workload_identity: str,
        instance_id: str,
        principal_type: str,
        principal_id: str,
    ) -> None:
        expected = {
            "agent_id": (self.bound_agent_id, agent_id),
            "workload_identity": (self.bound_workload_identity, workload_identity),
            "instance_id": (self.bound_instance_id, instance_id),
            "principal_type": (self.bound_principal_type, principal_type),
            "principal_id": (self.bound_principal_id, principal_id),
        }
        mismatches = [name for name, (bound, supplied) in expected.items() if bound is not None and bound != supplied]
        if mismatches:
            raise AuthorizationError(
                "authenticated identity is not bound to the supplied decision context",
                details={"mismatches": mismatches},
            )


def authenticate(session: Session, token: str, peppers: bytes | tuple[bytes, ...]) -> AuthContext:
    try:
        key_id, secret = parse_api_key(token)
    except ValueError as exc:
        raise AuthenticationError("invalid API key") from exc
    set_key_context(session, key_id)
    api_key = session.scalar(select(APIKey).where(APIKey.id == key_id))
    if api_key is None or api_key.status not in {"active", "lifecycle_only"}:
        raise AuthenticationError("API key is unknown or inactive")
    now = datetime.now(UTC)
    expires = api_key.expires_at
    if expires and expires.tzinfo is None:
        expires = expires.replace(tzinfo=UTC)
    if expires and expires <= now:
        raise AuthenticationError("API key has expired")
    accepted = (peppers,) if isinstance(peppers, bytes) else peppers
    if not accepted or not any(
        hmac.compare_digest(api_key_digest(pepper, secret), api_key.secret_digest)
        for pepper in accepted
    ):
        raise AuthenticationError("invalid API key")
    set_tenant_context(session, api_key.tenant_id)
    tenant = session.get(Tenant, api_key.tenant_id)
    if tenant is None:
        raise AuthenticationError("tenant is inactive")
    scopes = frozenset(api_key.scopes)
    lifecycle_scopes = frozenset({"tenants:lifecycle", "audit:read", "audit:verify"})
    if api_key.status == "lifecycle_only":
        scopes = lifecycle_scopes if "*" in scopes else scopes.intersection(lifecycle_scopes)
        if not scopes:
            raise AuthenticationError("lifecycle API key has no permitted lifecycle scope")
    if tenant.status != "active":
        scopes = lifecycle_scopes if "*" in scopes else scopes.intersection(lifecycle_scopes)
        if not scopes:
            raise AuthenticationError("tenant is inactive")
    return AuthContext(
        tenant_id=api_key.tenant_id,
        key_id=api_key.id,
        scopes=scopes,
        expires_at=expires,
        bound_agent_id=api_key.bound_agent_id,
        bound_workload_identity=api_key.bound_workload_identity,
        bound_instance_id=api_key.bound_instance_id,
        bound_principal_type=api_key.bound_principal_type,
        bound_principal_id=api_key.bound_principal_id,
    )
