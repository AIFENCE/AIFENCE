# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from fastapi import FastAPI
from sqlalchemy import Engine

from .config import Settings


def configure_telemetry(app: FastAPI, engine: Engine, settings: Settings) -> None:
    if not settings.otel_exporter_otlp_endpoint:
        return
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    from . import __version__

    provider = TracerProvider(resource=Resource.create({
        "service.name": settings.otel_service_name,
        "service.version": __version__,
        "deployment.environment.name": settings.environment,
        "service.namespace": "aifence",
    }))
    exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(
        app,
        excluded_urls="/health/live,/health/ready,/internal/health/ready,/internal/metrics",
    )
    SQLAlchemyInstrumentor().instrument(engine=engine)
