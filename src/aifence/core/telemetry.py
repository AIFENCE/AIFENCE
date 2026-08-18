# SPDX-License-Identifier: AGPL-3.0-or-later
"""Optional OpenTelemetry wiring for the composed application.

A no-op unless ``AIFENCE_OTEL_EXPORTER_OTLP_ENDPOINT`` is set. The heavy
OpenTelemetry imports are deferred into the function body so the ``otel`` extra
stays optional.
"""
from __future__ import annotations

from typing import Protocol

from fastapi import FastAPI
from sqlalchemy import Engine


class TelemetryConfig(Protocol):
    """Settings surface needed to configure tracing.

    Declared as read-only properties so frozen settings dataclasses satisfy it.
    """

    @property
    def otel_exporter_otlp_endpoint(self) -> str: ...

    @property
    def otel_service_name(self) -> str: ...

    @property
    def environment(self) -> str: ...


def configure_telemetry(app: FastAPI, engine: Engine, settings: TelemetryConfig) -> None:
    if not settings.otel_exporter_otlp_endpoint:
        return
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    from .. import __version__

    provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": settings.otel_service_name,
                "service.version": __version__,
                "deployment.environment.name": settings.environment,
                "service.namespace": "aifence",
            }
        )
    )
    exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(
        app,
        excluded_urls="/health/live,/health/ready,/metrics",
    )
    SQLAlchemyInstrumentor().instrument(engine=engine)
