# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware

REQUESTS = Counter(
    "aifence_guard_http_requests_total",
    "HTTP requests handled by AIFENCE",
    ("method", "route", "status"),
)
LATENCY = Histogram(
    "aifence_guard_http_request_duration_seconds",
    "HTTP request duration",
    ("method", "route"),
)
DECISIONS = Counter(
    "aifence_guard_decisions_total",
    "Security decisions by outcome",
    ("outcome",),
)
BROKER_CALLS = Counter(
    "aifence_guard_broker_calls_total",
    "Broker calls by type and status",
    ("broker", "status"),
)

CONTROL_APPLICATIONS = Counter(
    "aifence_guard_control_applications_total",
    "Mandatory enforcement controls by type and final status",
    ("control", "status"),
)
CAPABILITY_EVENTS = Counter(
    "aifence_guard_capability_events_total",
    "Capability lifecycle events",
    ("event",),
)
APPROVAL_EVENTS = Counter(
    "aifence_guard_approval_events_total",
    "Approval lifecycle events",
    ("event",),
)
EXECUTION_TRANSITIONS = Counter(
    "aifence_guard_execution_transitions_total",
    "Execution state transitions",
    ("from_state", "to_state"),
)
OUTBOX_EVENTS = Counter(
    "aifence_guard_outbox_events_total",
    "Outbox claim and delivery lifecycle events",
    ("event",),
)
OUTBOX_BACKLOG = Gauge(
    "aifence_guard_outbox_backlog",
    "Current number of dispatch claims awaiting completion",
)
AUDIT_ANCHOR_EVENTS = Counter(
    "aifence_guard_audit_anchor_events_total",
    "External audit anchoring lifecycle events",
    ("event", "destination"),
)
MEMORY_EVENTS = Counter(
    "aifence_guard_memory_events_total",
    "Memory provenance and quarantine events",
    ("event", "status"),
)
BUDGET_EVENTS = Counter(
    "aifence_guard_budget_events_total",
    "Runtime budget lifecycle events",
    ("event",),
)
POLICY_ROLLOUT_EVENTS = Counter(
    "aifence_guard_policy_rollout_events_total",
    "Policy rollout lifecycle events",
    ("event",),
)
DISPATCH_LATENCY = Histogram(
    "aifence_guard_dispatch_duration_seconds",
    "End-to-end broker dispatch duration",
    ("broker", "result"),
)
DEPENDENCY_LATENCY = Histogram(
    "aifence_guard_dependency_duration_seconds",
    "Latency of security dependencies",
    ("dependency", "operation"),
)
WORKLOAD_AUTH_EVENTS = Counter(
    "aifence_guard_workload_auth_events_total",
    "Workload authentication outcomes",
    ("result",),
)
DELEGATION_EVENTS = Counter(
    "aifence_guard_delegation_events_total",
    "Agent delegation lifecycle events",
    ("event",),
)
TENANT_LIFECYCLE_EVENTS = Counter(
    "aifence_guard_tenant_lifecycle_events_total",
    "Tenant lifecycle operations",
    ("event", "status"),
)
PROTOCOL_EVENTS = Counter(
    "aifence_guard_protocol_events_total",
    "MCP and A2A gateway lifecycle events",
    ("protocol", "event"),
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        route = request.scope.get("route")
        route_path = getattr(route, "path", request.url.path)
        REQUESTS.labels(request.method, route_path, str(response.status_code)).inc()
        LATENCY.labels(request.method, route_path).observe(time.perf_counter() - start)
        return response


def metrics_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
