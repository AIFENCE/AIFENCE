# SPDX-License-Identifier: AGPL-3.0-or-later
"""Shared HTTP request metrics for the composed application.

This module owns only the generic per-request counter/histogram and the
``/metrics`` response. Subsystem-specific counters (guard decision outcomes,
bus compression waterfalls, …) are declared in each subsystem's own metrics
module but export through this one Prometheus registry.
"""
from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware

REQUESTS = Counter(
    "aifence_http_requests_total",
    "HTTP requests handled by AIFENCE",
    ("method", "route", "status"),
)
LATENCY = Histogram(
    "aifence_http_request_duration_seconds",
    "HTTP request duration",
    ("method", "route"),
)

FENCE_STAGE_CALLS = Counter(
    "aifence_fence_stage_calls_total",
    "Fence tier calls by result and breaker state",
    ("tier", "result", "breaker_state"),
)
FENCE_STAGE_LATENCY = Histogram(
    "aifence_fence_stage_duration_seconds",
    "Fence tier call duration",
    ("tier",),
)
FENCE_OUTCOMES = Counter(
    "aifence_fence_outcomes_total",
    "Final fence outcomes",
    ("outcome", "allowed"),
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
