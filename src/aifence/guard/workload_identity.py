# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import fnmatch
import ipaddress
import re
from dataclasses import dataclass
from urllib.parse import unquote

from fastapi import Request
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from .auth import AuthContext
from .config import Settings
from .db import set_tenant_context
from .errors import AuthenticationError
from .metrics import WORKLOAD_AUTH_EVENTS
from .models import Agent, Tenant, WorkloadIdentityBinding

_SPIFFE_RE = re.compile(r"^spiffe://([a-z0-9.-]{1,255})(/[A-Za-z0-9._~!$&'()*+,;=:@%/-]+)$")


def parse_spiffe_id(value: str) -> tuple[str, str]:
    normalized = unquote(value.strip())
    match = _SPIFFE_RE.fullmatch(normalized)
    if not match or ".." in match.group(2).split("/"):
        raise AuthenticationError("invalid SPIFFE identity")
    return normalized, match.group(1).lower()


@dataclass(frozen=True)
class WorkloadAssertion:
    spiffe_id: str
    instance_id: str | None = None


def request_from_trusted_proxy(request: Request, settings: Settings) -> bool:
    host = request.client.host if request.client is not None else ""
    if host == "testclient" and settings.environment == "test":
        host = "127.0.0.1"
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return False
    for cidr in settings.trusted_proxy_cidrs:
        try:
            if address in ipaddress.ip_network(cidr, strict=False):
                return True
        except ValueError as exc:
            raise ValueError(f"invalid trusted proxy CIDR: {cidr}") from exc
    return False


def extract_workload_assertion(request: Request, settings: Settings) -> WorkloadAssertion | None:
    direct = request.headers.get(settings.workload_identity_direct_header)
    forwarded = request.headers.get(settings.workload_identity_header)
    value = direct or forwarded
    if not value:
        return None
    if not settings.workload_auth_enabled:
        raise AuthenticationError("workload authentication is disabled")
    if not request_from_trusted_proxy(request, settings):
        WORKLOAD_AUTH_EVENTS.labels("untrusted_proxy").inc()
        raise AuthenticationError("workload identity assertion came from an untrusted proxy")
    # Identity-aware proxies may forward a full XFCC document. Accept only a single URI field.
    if "URI=" in value:
        candidates = [part.split("URI=", 1)[1].split(";", 1)[0].strip('" ') for part in value.split(",")]
        if len(candidates) != 1:
            raise AuthenticationError("ambiguous forwarded workload identity")
        value = candidates[0]
    spiffe_id, _ = parse_spiffe_id(value)
    return WorkloadAssertion(spiffe_id, request.headers.get("X-Aifence-Instance-ID"))


def authenticate_workload(session: Session, assertion: WorkloadAssertion, settings: Settings) -> AuthContext:
    spiffe_id, trust_domain = parse_spiffe_id(assertion.spiffe_id)
    if settings.workload_trust_domains and trust_domain not in settings.workload_trust_domains:
        raise AuthenticationError("workload trust domain is not allowed")
    if session.get_bind().dialect.name == "postgresql":
        session.execute(
            text("SELECT set_config('aifence.spiffe_id', :value, true)"),
            {"value": spiffe_id},
        )
    session.info["spiffe_id"] = spiffe_id
    binding = session.scalar(select(WorkloadIdentityBinding).where(
        WorkloadIdentityBinding.spiffe_id == spiffe_id,
        WorkloadIdentityBinding.status == "active",
    ))
    if binding is None:
        raise AuthenticationError("workload identity is not registered")
    set_tenant_context(session, binding.tenant_id)
    tenant = session.get(Tenant, binding.tenant_id)
    if tenant is None or tenant.status != "active":
        raise AuthenticationError("workload tenant is inactive")
    if binding.instance_pattern and not assertion.instance_id:
        raise AuthenticationError("workload instance identity is required")
    if binding.instance_pattern and not fnmatch.fnmatchcase(assertion.instance_id or "", binding.instance_pattern):
        raise AuthenticationError("workload instance does not match its binding")
    agent = session.scalar(select(Agent).where(
        Agent.tenant_id == binding.tenant_id,
        Agent.id == binding.agent_id,
        Agent.status == "active",
    ))
    if agent is None or agent.workload_identity != spiffe_id:
        raise AuthenticationError("workload binding no longer matches an active immutable agent")
    WORKLOAD_AUTH_EVENTS.labels("succeeded").inc()
    return AuthContext(
        tenant_id=binding.tenant_id,
        key_id=binding.id,
        scopes=frozenset(binding.scopes),
        bound_agent_id=binding.agent_id,
        bound_workload_identity=spiffe_id,
        bound_instance_id=assertion.instance_id if binding.instance_pattern else None,
        bound_principal_type=binding.principal_type,
        bound_principal_id=binding.principal_id,
    )
