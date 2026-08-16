# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from .config import Settings


class Telemetry:
    def __init__(self, settings: Settings) -> None:
        self.enabled = settings.otel_enabled
        self._trace = None
        self._meter = None
        if self.enabled:
            try:
                from opentelemetry import metrics, trace
                self._trace = trace.get_tracer(settings.otel_service_name)
                self._meter = metrics.get_meter(settings.otel_service_name)
            except Exception:
                self.enabled = False
        self._counters: dict[str, Any] = {}

    @contextmanager
    def span(self, operation: str, **attrs: Any) -> Iterator[Any]:
        if not self.enabled or self._trace is None:
            yield None
            return
        parent_context = None
        traceparent = attrs.pop("traceparent", None)
        tracestate = attrs.pop("tracestate", None)
        if traceparent:
            try:
                from opentelemetry.propagate import extract
                carrier = {"traceparent": traceparent}
                if tracestate:
                    carrier["tracestate"] = tracestate
                parent_context = extract(carrier)
            except Exception:
                parent_context = None
        try:
            manager = self._trace.start_as_current_span(f"sage.{operation}", context=parent_context)
            span = manager.__enter__()
        except Exception:
            yield None
            return
        try:
            try:
                span.set_attribute("gen_ai.operation.name", operation)
                for key, value in attrs.items():
                    if value is not None and isinstance(value, (str, bool, int, float)):
                        span.set_attribute(f"sage.{key}", value)
            except Exception:
                pass
            try:
                yield span
            except BaseException as exc:
                try:
                    manager.__exit__(type(exc), exc, exc.__traceback__)
                except Exception:
                    pass
                raise
            else:
                try:
                    manager.__exit__(None, None, None)
                except Exception:
                    pass
        finally:
            pass

    def add(self, name: str, value: int | float, **attrs: Any) -> None:
        if not self.enabled or self._meter is None:
            return
        try:
            counter = self._counters.get(name)
            if counter is None:
                counter = self._meter.create_counter(f"sage.{name}")
                self._counters[name] = counter
            safe_attrs = {f"sage.{k}": v for k, v in attrs.items() if isinstance(v, (str, bool, int, float))}
            counter.add(value, safe_attrs)
        except Exception:
            return
