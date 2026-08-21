# Benchmarks

`scripts/benchmark_fence.py` measures the complete in-process `POST /v1/fence/submit` lifecycle on an isolated SQLite database, including Quality admission, Guard evaluation, durable Bus handoff and tamper-evident audit completion.

The benchmark reports throughput plus min/mean/p50/p95/p99/max latency. The nightly workflow stores JSON results as an artifact and applies a deliberately loose p95 regression ceiling to catch catastrophic regressions without pretending GitHub-hosted runners are stable laboratory hardware.

`scripts/performance_check.py` remains the lower-level Bus encode/decode and HTTP performance regression check. Release decisions should consider both the composed-fence benchmark and the lower-level protocol benchmark.
