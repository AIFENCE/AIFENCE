# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any, cast

import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from .crypto import SigningProvider, hash_object
from .errors import AuthorizationError, ConflictError, NotFoundError
from .models import Capability, Decision


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


def bound_action(decision: Decision) -> tuple[str, str, str, dict[str, Any]]:
    action = decision.enforcement_plan.get("transformed_action") if decision.enforcement_plan else None
    if not isinstance(action, dict):
        action = decision.request_json.get("action")
    if not isinstance(action, dict):
        raise AuthorizationError("decision does not contain a valid evaluated action")
    tool = action.get("tool")
    operation = action.get("operation")
    resource = action.get("target")
    arguments = action.get("arguments")
    if not isinstance(tool, str) or not tool:
        raise AuthorizationError("evaluated action is not bound to a tool")
    if not isinstance(operation, str) or not operation:
        raise AuthorizationError("evaluated action is not bound to an operation")
    if not isinstance(resource, str) or not resource:
        raise AuthorizationError("evaluated action is not bound to a resource")
    if not isinstance(arguments, dict):
        raise AuthorizationError("evaluated action arguments must be an object")
    return tool, operation, resource, arguments


def issue_capability(
    session: Session,
    signing_key: SigningProvider,
    *,
    tenant_id: str,
    decision: Decision,
    lifetime_seconds: int,
    requested_max_uses: int | None = None,
) -> tuple[Capability, str]:
    if decision.tenant_id != tenant_id:
        raise AuthorizationError("decision belongs to another tenant")
    if decision.outcome not in {"allow", "allow_with_limits", "redact_or_transform"}:
        raise AuthorizationError("decision outcome does not permit capability issuance")
    if decision.constraints.get("issue_capability") is False:
        raise AuthorizationError("policy explicitly prohibits capability issuance")
    if not decision.enforcement_plan.get("executable", False):
        raise AuthorizationError("decision enforcement plan is not executable")
    existing = session.scalar(
        select(Capability).where(
            Capability.tenant_id == tenant_id,
            Capability.decision_id == decision.id,
        )
    )
    if existing is not None:
        raise ConflictError("a capability has already been issued for this decision")

    now = datetime.now(UTC)
    decision_deadline = min(_aware(decision.expires_at), _aware(decision.created_at) + timedelta(minutes=5))
    if now >= decision_deadline:
        raise AuthorizationError("decision is too old for capability issuance")

    tool, operation, resource, arguments = bound_action(decision)
    policy_ttl = int(cast(int, decision.constraints.get("capability_ttl_seconds", 60)))
    policy_max_uses = int(cast(int, decision.constraints.get("max_capability_uses", 1)))
    effective_max_uses = policy_max_uses if requested_max_uses is None else min(requested_max_uses, policy_max_uses)
    remaining_seconds = max(0, int((decision_deadline - now).total_seconds()))
    effective_ttl = min(lifetime_seconds, policy_ttl, remaining_seconds)
    if effective_max_uses < 1 or effective_ttl < 5:
        raise AuthorizationError("policy limits do not permit a usable capability")

    expires = now + timedelta(seconds=effective_ttl)
    capability_id = "cap_" + secrets.token_urlsafe(16).replace("-", "").replace("_", "")
    arguments_hash = hash_object(arguments)
    constraints = dict(decision.constraints)
    claims = {
        "iss": "aifence",
        "sub": capability_id,
        "aud": "aifence-tool-broker",
        "tenant_id": tenant_id,
        "decision_id": decision.id,
        "agent_id": decision.agent_id,
        "trace_id": decision.trace_id,
        "tool": tool,
        "operation": operation,
        "resources": [resource],
        "constraints_hash": hash_object(constraints),
        "request_hash": decision.request_hash,
        "arguments_hash": arguments_hash,
        "max_uses": effective_max_uses,
        "jti": capability_id,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int(expires.timestamp()),
    }
    token = signing_key.issue_token(claims, headers={"typ": "AD-CAP"})
    capability = Capability(
        id=capability_id,
        tenant_id=tenant_id,
        decision_id=decision.id,
        agent_id=decision.agent_id,
        trace_id=decision.trace_id,
        tool=tool,
        operation=operation,
        resources=[resource],
        constraints=constraints,
        request_hash=decision.request_hash,
        arguments_hash=arguments_hash,
        token_hash=hashlib.sha256(token.encode()).hexdigest(),
        max_uses=effective_max_uses,
        use_count=0,
        status="active",
        not_before=now,
        expires_at=expires,
    )
    session.add(capability)
    session.flush()
    return capability, token


def consume_capability(
    session: Session,
    signing_key: SigningProvider,
    *,
    tenant_id: str,
    token: str,
    agent_id: str,
    trace_id: str,
    tool: str,
    operation: str,
    resource: str,
    execution: dict[str, Any],
) -> Capability:
    try:
        claims = signing_key.verify_token(
            token,
            audience="aifence-tool-broker",
            required=(
                "iss", "sub", "aud", "exp", "nbf", "iat", "jti", "tenant_id",
                "decision_id", "agent_id", "trace_id", "tool", "operation", "resources",
                "request_hash", "arguments_hash", "constraints_hash", "max_uses",
            ),
        )
    except jwt.PyJWTError as exc:
        raise AuthorizationError("capability token is invalid") from exc

    expected_arguments_hash = hash_object(execution)
    expected_claims = {
        "tenant_id": tenant_id,
        "agent_id": agent_id,
        "trace_id": trace_id,
        "tool": tool,
        "operation": operation,
        "arguments_hash": expected_arguments_hash,
    }
    for name, expected in expected_claims.items():
        if claims.get(name) != expected:
            raise AuthorizationError(f"capability is not bound to the supplied {name}")
    resources = claims.get("resources")
    if resources != [resource]:
        raise AuthorizationError("capability is not bound to the supplied resource")

    capability_id = str(claims["sub"])
    stmt = select(Capability).where(
        Capability.id == capability_id,
        Capability.tenant_id == tenant_id,
    )
    if session.bind and session.bind.dialect.name == "postgresql":
        stmt = stmt.with_for_update()
    capability = session.scalar(stmt)
    if capability is None:
        raise NotFoundError("capability does not exist")
    if capability.token_hash != hashlib.sha256(token.encode()).hexdigest():
        raise AuthorizationError("capability token hash does not match the issued token")

    decision = session.scalar(
        select(Decision).where(
            Decision.id == capability.decision_id,
            Decision.tenant_id == tenant_id,
        )
    )
    if decision is None:
        raise AuthorizationError("capability decision no longer exists")
    bound_tool, bound_operation, bound_resource, bound_arguments = bound_action(decision)
    if (
        capability.agent_id != agent_id
        or capability.trace_id != trace_id
        or capability.tool != tool
        or capability.operation != operation
        or capability.resources != [resource]
        or bound_tool != tool
        or bound_operation != operation
        or bound_resource != resource
        or bound_arguments != execution
        or capability.request_hash != decision.request_hash
        or capability.arguments_hash != expected_arguments_hash
        or claims.get("decision_id") != decision.id
        or claims.get("request_hash") != decision.request_hash
        or claims.get("max_uses") != capability.max_uses
        or claims.get("constraints_hash") != hash_object(capability.constraints)
    ):
        raise AuthorizationError("capability binding verification failed")

    now = datetime.now(UTC)
    if capability.status != "active" or _aware(capability.expires_at) <= now:
        raise AuthorizationError("capability is inactive or expired")
    if capability.use_count >= capability.max_uses:
        capability.status = "exhausted"
        raise ConflictError("capability use limit has been reached")
    capability.use_count += 1
    if capability.use_count >= capability.max_uses:
        capability.status = "exhausted"
    session.flush()
    return capability
