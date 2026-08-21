#!/usr/bin/env python3
"""Benchmark the composed Quality -> Guard -> Bus fence on local SQLite."""
from __future__ import annotations

import argparse
import json
import math
import platform
import statistics
import tempfile
import time
from pathlib import Path

from fastapi.testclient import TestClient

from aifence.app import create_app
from aifence.core.config import CoreSettings
from aifence.guard.auth import FULL_ADMIN_SCOPES


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(q * len(ordered)) - 1))
    return ordered[index]


def run(iterations: int, warmup: int) -> dict[str, object]:
    artifact = (
        "# Deployment Readiness\n\n"
        "All required controls passed. The receiver should validate the deployment "
        "receipt and retain rollback ownership before proceeding to the next controlled stage."
    )
    with tempfile.TemporaryDirectory(prefix="aifence-bench-") as tmp:
        database = Path(tmp) / "bench.db"
        app = create_app(
            CoreSettings(
                environment="test",
                database_url=f"sqlite+pysqlite:///{database}",
            )
        )
        with app.state.session_factory() as session:
            _, _, token = app.state.guard_app.state.service.create_tenant_and_key(
                session,
                tenant_name="Benchmark",
                key_name="bench",
                scopes=FULL_ADMIN_SCOPES,
            )

        latencies: list[float] = []
        payload = {
            "artifact": artifact,
            "content_type": "text/markdown",
            "receiver": "benchmark-receiver",
            "action": {"operation": "read"},
            "risk_score": 10,
        }
        with TestClient(app, headers={"Authorization": f"Bearer {token}"}) as client:
            for _ in range(warmup):
                response = client.post("/v1/fence/submit", json=payload)
                response.raise_for_status()

            started = time.perf_counter()
            for _ in range(iterations):
                request_started = time.perf_counter()
                response = client.post("/v1/fence/submit", json=payload)
                response.raise_for_status()
                latencies.append((time.perf_counter() - request_started) * 1000)
            elapsed = time.perf_counter() - started
        app.state.engine.dispose()

    return {
        "benchmark": "composed-fence-v1",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "database": "SQLite",
            "client": "FastAPI/Starlette TestClient (in-process)",
            "quality_mode": "admission",
        },
        "iterations": iterations,
        "warmup": warmup,
        "elapsed_seconds": round(elapsed, 6),
        "throughput_rps": round(iterations / elapsed, 2),
        "latency_ms": {
            "min": round(min(latencies), 3),
            "mean": round(statistics.fmean(latencies), 3),
            "p50": round(percentile(latencies, 0.50), 3),
            "p95": round(percentile(latencies, 0.95), 3),
            "p99": round(percentile(latencies, 0.99), 3),
            "max": round(max(latencies), 3),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--warmup", type=int, default=10)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-p95-ms", type=float, default=500.0)
    args = parser.parse_args()
    if args.iterations < 1:
        raise SystemExit("iterations must be at least 1")
    if args.warmup < 0:
        raise SystemExit("warmup cannot be negative")

    report = run(args.iterations, args.warmup)
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    p95 = float(report["latency_ms"]["p95"])  # type: ignore[index]
    if p95 > args.max_p95_ms:
        raise SystemExit(f"benchmark regression: p95 {p95} ms > {args.max_p95_ms} ms")


if __name__ == "__main__":
    main()
