# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import logging
import random
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import Session, sessionmaker

from .audit import append_event
from .auth import AuthContext
from .db import set_tenant_context
from .errors import AgentDanceError, AuthorizationError, ConflictError, DependencyUnavailableError
from .ids import new_id
from .metrics import DISPATCH_LATENCY, OUTBOX_BACKLOG, OUTBOX_EVENTS
from .models import (
    AgentProtocolRegistration,
    DispatchClaim,
    Execution,
    OutboxMessage,
    Tool,
)
from .network import ValidatedEndpoint, pin_validated_target, validate_endpoint
from .service import AgentDanceService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DispatchResult:
    claimed: int = 0
    succeeded: int = 0
    retried: int = 0
    failed: int = 0
    outcome_unknown: int = 0
    dead_lettered: int = 0
    execution_ids: tuple[str, ...] = ()

    def add(self, *, execution_id: str | None = None, **updates: int) -> DispatchResult:
        values = {
            "claimed": self.claimed,
            "succeeded": self.succeeded,
            "retried": self.retried,
            "failed": self.failed,
            "outcome_unknown": self.outcome_unknown,
            "dead_lettered": self.dead_lettered,
            "execution_ids": self.execution_ids,
        }
        for key, value in updates.items():
            values[key] += value
        if execution_id is not None:
            values["execution_ids"] = (*self.execution_ids, execution_id)
        return DispatchResult(**values)


class DispatchWorker:
    """Lease-based outbox dispatcher.

    PostgreSQL deployments claim work through the SECURITY DEFINER function
    installed by the RC3 migration. SQLite uses an equivalent transaction-local
    implementation for development and deterministic tests.
    """

    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
        service: AgentDanceService,
        client: httpx.AsyncClient,
        worker_id: str,
    ) -> None:
        self.session_factory = session_factory
        self.service = service
        self.client = client
        self.worker_id = worker_id
        self.settings = service.settings
        self._closed = False

    async def close(self) -> None:
        self._closed = True

    def _internal_auth(self, tenant_id: str) -> AuthContext:
        return AuthContext(tenant_id=tenant_id, key_id=f"worker:{self.worker_id}", scopes=frozenset({"*"}))

    def claim(self, *, limit: int | None = None) -> list[tuple[str, str, int]]:
        requested = max(limit or self.settings.worker_batch_size, 1)
        batch = min(requested, self.settings.worker_concurrency, 1000)
        lease_seconds = self.settings.execution_lease_seconds
        now = datetime.now(UTC)
        with self.session_factory() as session:
            if session.get_bind().dialect.name == "postgresql":
                rows = session.execute(
                    text(
                        "SELECT outbox_id, tenant_id, fencing_token FROM agentdance_claim_dispatch("
                        ":worker_id, :batch_size, :lease_seconds)"
                    ),
                    {
                        "worker_id": self.worker_id,
                        "batch_size": batch,
                        "lease_seconds": lease_seconds,
                    },
                ).all()
                session.commit()
                return [(str(row[0]), str(row[1]), int(row[2])) for row in rows]

            statement = (
                select(DispatchClaim)
                .where(
                    DispatchClaim.status.in_(["pending", "retry", "leased"]),
                    DispatchClaim.available_at <= now,
                    or_(
                        DispatchClaim.status.in_(["pending", "retry"]),
                        DispatchClaim.lease_expires_at.is_(None),
                        DispatchClaim.lease_expires_at <= now,
                    ),
                    DispatchClaim.attempts < DispatchClaim.max_attempts,
                )
                .order_by(
                    DispatchClaim.priority.asc(),
                    DispatchClaim.available_at.asc(),
                    DispatchClaim.created_at.asc(),
                    DispatchClaim.outbox_id.asc(),
                )
                .limit(batch)
            )
            claims = list(session.scalars(statement))
            claimed: list[tuple[str, str, int]] = []
            for claim in claims:
                claim.status = "leased"
                claim.lease_owner = self.worker_id
                claim.lease_expires_at = now + timedelta(seconds=lease_seconds)
                claim.attempts += 1
                claim.fencing_token += 1
                claimed.append((claim.outbox_id, claim.tenant_id, claim.fencing_token))
            session.commit()
            return claimed

    async def run_once(self, *, limit: int | None = None) -> DispatchResult:
        result = DispatchResult()
        claimed = self.claim(limit=limit)
        OUTBOX_EVENTS.labels("claimed").inc(len(claimed))
        outcomes = await asyncio.gather(
            *(self._process_claim(outbox_id, tenant_id, fencing_token)
              for outbox_id, tenant_id, fencing_token in claimed),
            return_exceptions=True,
        )
        for item in outcomes:
            result = result.add(claimed=1)
            if isinstance(item, Exception):
                logger.error("dispatcher claim failed", exc_info=(type(item), item, item.__traceback__))
                outcome, execution_id = "failed", None
            else:
                outcome, execution_id = item
            OUTBOX_EVENTS.labels(outcome).inc()
            result = result.add(execution_id=execution_id, **{outcome: 1})
        with self.session_factory() as session:
            backlog = session.scalar(
                select(func.count()).select_from(DispatchClaim).where(
                    DispatchClaim.status.in_(["pending", "retry", "leased"])
                )
            )
            OUTBOX_BACKLOG.set(int(backlog or 0))
        return result

    async def run_forever(self) -> None:
        while not self._closed:
            result = await self.run_once()
            if result.claimed == 0:
                await asyncio.sleep(self.settings.worker_poll_milliseconds / 1000.0)

    async def _process_claim(
        self, outbox_id: str, tenant_id: str, fencing_token: int
    ) -> tuple[str, str | None]:
        with self.session_factory() as session:
            claim = session.get(DispatchClaim, outbox_id)
            if (claim is None or claim.status != "leased" or claim.lease_owner != self.worker_id
                    or claim.fencing_token != fencing_token):
                return "failed", None
            set_tenant_context(session, tenant_id)
            message = session.scalar(
                select(OutboxMessage).where(
                    OutboxMessage.tenant_id == tenant_id,
                    OutboxMessage.id == outbox_id,
                )
            )
            if message is None:
                claim.status = "dead_lettered"
                claim.lease_owner = None
                claim.lease_expires_at = None
                claim.processed_at = datetime.now(UTC)
                session.commit()
                return "dead_lettered", None
            message.status = "leased"
            message.lease_owner = self.worker_id
            message.fencing_token = fencing_token
            message.lease_expires_at = claim.lease_expires_at
            message.attempts = claim.attempts
            execution = session.scalar(
                select(Execution).where(
                    Execution.tenant_id == tenant_id,
                    Execution.id == message.aggregate_id,
                )
            )
            if execution is None:
                message.status = "dead_lettered"
                message.last_error = "execution_missing"
                message.lease_owner = None
                message.lease_expires_at = None
                message.processed_at = datetime.now(UTC)
                claim.status = "dead_lettered"
                claim.lease_owner = None
                claim.lease_expires_at = None
                claim.processed_at = message.processed_at
                session.commit()
                return "dead_lettered", None
            if execution.state == "succeeded":
                message.status = "processed"
                message.lease_owner = None
                message.lease_expires_at = None
                message.processed_at = datetime.now(UTC)
                claim.status = "processed"
                claim.lease_owner = None
                claim.lease_expires_at = None
                claim.processed_at = message.processed_at
                session.commit()
                return "succeeded", execution.id
            if execution.state == "outcome_unknown":
                message.status = "processed"
                message.lease_owner = None
                message.lease_expires_at = None
                message.processed_at = datetime.now(UTC)
                claim.status = "processed"
                claim.lease_owner = None
                claim.lease_expires_at = None
                claim.processed_at = message.processed_at
                session.commit()
                return "outcome_unknown", execution.id
            execution.state = "dispatching"
            execution.attempt_count = max(execution.attempt_count + 1, message.attempts)
            execution.lease_owner = self.worker_id
            execution.fencing_token = fencing_token
            execution.lease_expires_at = message.lease_expires_at
            execution.updated_at = datetime.now(UTC)
            append_event(
                session,
                self.service.signing_key,
                event_id=new_id("evt"),
                tenant_id=tenant_id,
                trace_id=execution.trace_id,
                parent_event_id=None,
                event_type="execution.dispatching",
                payload={
                    "execution_id": execution.id,
                    "worker_id": self.worker_id,
                    "attempt_count": execution.attempt_count,
                    "fencing_token": fencing_token,
                },
            )
            session.commit()
            execution_id = execution.id

        stop_renewal = asyncio.Event()
        renewal_task = asyncio.create_task(
            self._renew_lease(outbox_id, tenant_id, execution_id, fencing_token, stop_renewal)
        )
        try:
            response, response_body, response_headers = await self._dispatch(
                tenant_id, execution_id, fencing_token
            )
        except Exception as exc:  # converted into durable execution state below
            return self._handle_dispatch_error(
                outbox_id, tenant_id, execution_id, fencing_token, exc
            ), execution_id
        finally:
            stop_renewal.set()
            await renewal_task

        with self.session_factory() as session:
            set_tenant_context(session, tenant_id)
            auth = self._internal_auth(tenant_id)
            self.service.finalize_execution_success(
                session,
                auth,
                execution_id,
                status_code=response.status_code,
                headers=response_headers,
                body=response_body,
                response_hash=hashlib.sha256(response.content).hexdigest(),
                expected_fencing_token=fencing_token,
            )
        return "succeeded", execution_id

    async def _renew_lease(
        self, outbox_id: str, tenant_id: str, execution_id: str, fencing_token: int,
        stop: asyncio.Event,
    ) -> None:
        interval = self.settings.worker_lease_renewal_seconds
        while True:
            try:
                await asyncio.wait_for(stop.wait(), timeout=interval)
                return
            except TimeoutError:
                pass
            now = datetime.now(UTC)
            expires = now + timedelta(seconds=self.settings.execution_lease_seconds)
            with self.session_factory() as session:
                claim = session.get(DispatchClaim, outbox_id)
                if (claim is None or claim.status != "leased"
                        or claim.lease_owner != self.worker_id
                        or claim.fencing_token != fencing_token):
                    return
                set_tenant_context(session, tenant_id)
                message = session.scalar(select(OutboxMessage).where(
                    OutboxMessage.tenant_id == tenant_id, OutboxMessage.id == outbox_id
                ))
                execution = session.scalar(select(Execution).where(
                    Execution.tenant_id == tenant_id, Execution.id == execution_id
                ))
                if (message is None or execution is None
                        or message.lease_owner != self.worker_id
                        or execution.lease_owner != self.worker_id
                        or message.fencing_token != fencing_token
                        or execution.fencing_token != fencing_token):
                    return
                claim.lease_expires_at = expires
                message.lease_expires_at = expires
                execution.lease_expires_at = expires
                execution.updated_at = now
                session.commit()

    async def _dispatch(
        self, tenant_id: str, execution_id: str, fencing_token: int
    ) -> tuple[httpx.Response, Any, dict[str, str]]:
        with self.session_factory() as session:
            set_tenant_context(session, tenant_id)
            execution = session.scalar(
                select(Execution).where(
                    Execution.tenant_id == tenant_id,
                    Execution.id == execution_id,
                )
            )
            if execution is None:
                raise ConflictError("leased execution disappeared")
            if (execution.lease_owner != self.worker_id
                    or execution.fencing_token != fencing_token):
                raise ConflictError("dispatcher lease is stale")
            request_json = dict(execution.request_json)
            method = str(request_json.get("method", "POST")).upper()
            path = str(request_json.get("path", "/"))
            body = request_json.get("body")
            query_raw = request_json.get("query", {})
            if not isinstance(query_raw, dict):
                raise AuthorizationError("queued execution query is invalid")
            query = {str(key): str(value) for key, value in query_raw.items()}
            if execution.broker_type == "provider":
                broker = self.service.get_provider(session, tenant_id, execution.broker_id)
                target, endpoint = self.service.validate_provider_path(broker, path)
                auth_header = broker.auth_header_name
                auth_value = self.service.provider_auth(session, broker)
            elif execution.broker_type == "tool":
                broker = self.service.get_tool(session, tenant_id, execution.broker_id)
                operation = self._tool_operation(execution.controls_applied)
                target, endpoint = self.service.validate_tool_call(broker, operation, method, path)
                auth_header = broker.auth_header_name
                auth_value = self.service.tool_auth(session, broker)
            elif execution.broker_type in {"mcp", "a2a"}:
                registration = session.scalar(select(AgentProtocolRegistration).where(
                    AgentProtocolRegistration.tenant_id == tenant_id,
                    AgentProtocolRegistration.id == execution.broker_id,
                    AgentProtocolRegistration.protocol == execution.broker_type,
                    AgentProtocolRegistration.status == "active",
                ))
                if registration is None:
                    raise AuthorizationError("queued protocol registration is inactive")
                allowed = (self.settings.tool_allowed_hosts if execution.broker_type == "mcp"
                           else self.settings.provider_allowed_hosts)
                endpoint = validate_endpoint(
                    registration.endpoint, allowed_hosts=allowed, network_zone="public",
                    require_resolution=self.settings.environment in {"staging", "production"},
                    resolution_timeout_seconds=self.settings.dns_resolution_timeout_seconds,
                )
                target = endpoint.canonical_url
                auth_header, auth_value = self.service.protocol_auth(session, registration)
            else:
                raise AuthorizationError("queued execution references an unsupported broker type")
            max_response_bytes = self._response_limit(execution.controls_applied)
            upstream_idempotency_key = execution.upstream_idempotency_key
            broker_type = execution.broker_type

        started = time.perf_counter()
        try:
            response = await self._forward_json(
                target=target,
                endpoint=endpoint,
                method=method,
                body=body,
                query=query,
                auth_header=auth_header,
                auth_value=auth_value,
                upstream_idempotency_key=upstream_idempotency_key,
                execution_id=execution_id,
                max_response_bytes=max_response_bytes,
            )
        except Exception:
            DISPATCH_LATENCY.labels(broker_type, "failed").observe(time.perf_counter() - started)
            raise
        DISPATCH_LATENCY.labels(broker_type, "succeeded").observe(time.perf_counter() - started)
        response_body, response_headers = self._parse_response(response)
        return response, response_body, response_headers

    async def _forward_json(
        self,
        *,
        target: str,
        endpoint: ValidatedEndpoint,
        method: str,
        body: object,
        query: dict[str, str],
        auth_header: str | None,
        auth_value: str | None,
        upstream_idempotency_key: str,
        execution_id: str,
        max_response_bytes: int,
    ) -> httpx.Response:
        pinned_target, host_header, request_extensions = pin_validated_target(target, endpoint)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "AGENTDANCE-Dispatcher/1.0.0-rc.5",
            "X-Agentdance-Execution-ID": execution_id,
            "Idempotency-Key": upstream_idempotency_key,
        }
        headers["Host"] = host_header
        if auth_header and auth_value:
            headers[auth_header] = auth_value
        try:
            async with self.client.stream(
                method, pinned_target, json=body, params=query, headers=headers,
                extensions=request_extensions,
            ) as upstream:
                chunks: list[bytes] = []
                total = 0
                async for chunk in upstream.aiter_bytes():
                    total += len(chunk)
                    if total > max_response_bytes:
                        raise ConflictError("broker response exceeds the configured size limit")
                    chunks.append(chunk)
                return httpx.Response(
                    upstream.status_code,
                    headers=upstream.headers,
                    content=b"".join(chunks),
                    request=upstream.request,
                    extensions=upstream.extensions,
                )
        except httpx.RequestError as exc:
            raise DependencyUnavailableError("broker upstream request failed") from exc

    def _handle_dispatch_error(
        self, outbox_id: str, tenant_id: str, execution_id: str,
        fencing_token: int, exc: Exception
    ) -> str:
        with self.session_factory() as session:
            set_tenant_context(session, tenant_id)
            execution = session.scalar(
                select(Execution).where(
                    Execution.tenant_id == tenant_id,
                    Execution.id == execution_id,
                )
            )
            message = session.scalar(
                select(OutboxMessage).where(
                    OutboxMessage.tenant_id == tenant_id,
                    OutboxMessage.id == outbox_id,
                )
            )
            claim = session.get(DispatchClaim, outbox_id)
            if execution is None or message is None or claim is None:
                return "failed"
            if (execution.fencing_token != fencing_token
                    or message.fencing_token != fencing_token
                    or claim.fencing_token != fencing_token
                    or claim.lease_owner != self.worker_id):
                return "failed"
            code = exc.code if isinstance(exc, AgentDanceError) else "unexpected_dispatch_failure"
            error_message = (
                exc.message if isinstance(exc, AgentDanceError) else str(exc) or type(exc).__name__
            )[:4096]
            request_method = str(execution.request_json.get("method", "POST")).upper()
            operation = self._tool_operation(execution.controls_applied, required=False)
            retryable = self._is_retryable(
                execution=execution,
                method=request_method,
                operation=operation,
                exc=exc,
                session=session,
            )
            now = datetime.now(UTC)
            if retryable and claim.attempts < claim.max_attempts:
                delay = self._backoff_seconds(claim.attempts)
                execution.state = "authorized"
                execution.last_error_code = code
                execution.last_error_message = error_message
                execution.lease_owner = None
                execution.lease_expires_at = None
                execution.next_attempt_at = now + timedelta(seconds=delay)
                execution.updated_at = now
                message.status = "retry"
                message.available_at = execution.next_attempt_at
                message.lease_owner = None
                message.lease_expires_at = None
                message.last_error = error_message
                claim.status = "retry"
                claim.available_at = execution.next_attempt_at
                claim.lease_owner = None
                claim.lease_expires_at = None
                append_event(
                    session,
                    self.service.signing_key,
                    event_id=new_id("evt"),
                    tenant_id=tenant_id,
                    trace_id=execution.trace_id,
                    parent_event_id=None,
                    event_type="execution.retry_scheduled",
                    payload={
                        "execution_id": execution.id,
                        "attempt_count": execution.attempt_count,
                        "next_attempt_at": execution.next_attempt_at.isoformat(),
                        "error_code": code,
                    },
                )
                session.commit()
                return "retried"

            uncertain = isinstance(exc, DependencyUnavailableError) and not self._declared_idempotent(
                execution, request_method, operation, session
            )
            auth = self._internal_auth(tenant_id)
            finalized = self.service.finalize_execution_failure(
                session,
                auth,
                execution_id,
                error_code=code,
                error_message=error_message,
                outcome_unknown=uncertain,
                expected_fencing_token=fencing_token,
            )
            # Preserve terminal outbox evidence instead of losing it as merely processed.
            terminal = session.scalar(
                select(OutboxMessage).where(
                    OutboxMessage.tenant_id == tenant_id,
                    OutboxMessage.id == outbox_id,
                )
            )
            terminal_claim = session.get(DispatchClaim, outbox_id)
            if terminal is not None:
                terminal.status = "processed" if finalized.state == "outcome_unknown" else "dead_lettered"
                terminal.last_error = error_message
                terminal.lease_owner = None
                terminal.lease_expires_at = None
                terminal.processed_at = datetime.now(UTC)
                if terminal_claim is not None:
                    terminal_claim.status = terminal.status
                    terminal_claim.lease_owner = None
                    terminal_claim.lease_expires_at = None
                    terminal_claim.processed_at = terminal.processed_at
                session.commit()
            return "outcome_unknown" if uncertain else "dead_lettered"

    def _is_retryable(
        self,
        *,
        execution: Execution,
        method: str,
        operation: str | None,
        exc: Exception,
        session: Session,
    ) -> bool:
        if isinstance(exc, (AuthorizationError, ConflictError)):
            return False
        return self._declared_idempotent(execution, method, operation, session)

    def _declared_idempotent(
        self, execution: Execution, method: str, operation: str | None, session: Session
    ) -> bool:
        if method in {"GET", "HEAD", "PUT", "DELETE"}:
            return True
        if execution.broker_type in {"mcp", "a2a"}:
            return bool(execution.upstream_idempotency_key)
        if execution.broker_type != "tool" or operation is None:
            return False
        tool = session.scalar(
            select(Tool).where(
                Tool.tenant_id == execution.tenant_id,
                Tool.id == execution.broker_id,
            )
        )
        if tool is None:
            return False
        rule = tool.allowed_operations.get(operation)
        return isinstance(rule, dict) and bool(rule.get("idempotent", False))

    def _backoff_seconds(self, attempts: int) -> float:
        cap = max(float(self.settings.worker_retry_base_seconds) * 64.0, 1.0)
        base = min(float(self.settings.worker_retry_base_seconds) * (2 ** max(attempts - 1, 0)), cap)
        return min(base + random.uniform(0, min(base * 0.2, 2.0)), cap)

    def _response_limit(self, controls: list[dict[str, Any]]) -> int:
        limits = [self.settings.max_broker_response_bytes]
        for control in controls:
            if control.get("type") != "max_response_bytes" or control.get("status") != "applied":
                continue
            value = control.get("parameters", {}).get("value")
            try:
                parsed = int(value)
            except (TypeError, ValueError) as exc:
                raise AuthorizationError("max_response_bytes enforcement control is invalid") from exc
            if parsed < 1:
                raise AuthorizationError("max_response_bytes enforcement control is invalid")
            limits.append(parsed)
        return min(limits)

    @staticmethod
    def _tool_operation(controls: list[dict[str, Any]], *, required: bool = True) -> str | None:
        for control in controls:
            if control.get("type") != "capability_binding":
                continue
            evidence = control.get("evidence", {})
            operation = evidence.get("operation") if isinstance(evidence, dict) else None
            if isinstance(operation, str) and operation:
                return operation
        if required:
            raise AuthorizationError("queued tool execution lacks a bound operation")
        return None

    @staticmethod
    def _parse_response(response: httpx.Response) -> tuple[Any, dict[str, str]]:
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                body: Any = response.json()
            except json.JSONDecodeError:
                body = {"encoding": "base64", "data": base64.b64encode(response.content).decode()}
        elif content_type.startswith("text/"):
            body = response.text
        else:
            body = {"encoding": "base64", "data": base64.b64encode(response.content).decode()}
        headers = {
            key: value
            for key, value in response.headers.items()
            if key.lower() in {"content-type", "x-request-id", "retry-after", "request-id"}
        }
        return body, headers
