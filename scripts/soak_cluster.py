from __future__ import annotations

import argparse
import concurrent.futures
import json
import secrets
import ssl
import statistics
import time
from collections import Counter
from urllib import parse, request


def call(url: str, key: str, method: str, path: str, payload: dict | None = None, ca_cert: str | None = None) -> tuple[int, float, dict]:
    body = json.dumps(payload).encode() if payload is not None else None
    req = request.Request(url.rstrip("/") + path, data=body, method=method)
    req.add_header("Authorization", f"Bearer {key}")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    started = time.perf_counter()
    try:
        context = ssl.create_default_context(cafile=ca_cert) if ca_cert else None
        with request.urlopen(req, timeout=30, context=context) as response:
            data = json.loads(response.read() or b"{}")
            return response.status, (time.perf_counter() - started) * 1000, data
    except Exception as exc:
        return 0, (time.perf_counter() - started) * 1000, {"error": type(exc).__name__}


def worker(base: str, key: str, workspace: str, index: int, ca_cert: str | None = None) -> tuple[bool, float]:
    receiver = f"soak-r-{index}"
    idem = "soak-" + secrets.token_hex(16)
    status, send_latency, result = call(base, key, "POST", "/v1/bus/handoff", {
        "content": {"sequence": index, "status": "active"}, "receiver": receiver,
        "sender": f"soak-s-{index % 32}", "workspace": workspace, "idempotency_key": idem,
        "ordering_key": f"stream-{index % 128}",
    }, ca_cert)
    message_id = result.get("message_id")
    if status != 200 or not message_id:
        return False, send_latency
    query = parse.urlencode({"workspace": workspace, "limit": 1, "claim": "true"})
    pull_status, pull_latency, pulled = call(base, key, "GET", f"/v1/bus/pull/{parse.quote(receiver)}?{query}", ca_cert=ca_cert)
    if pull_status != 200 or not isinstance(pulled, list) or len(pulled) != 1 or pulled[0].get("message_id") != message_id:
        return False, send_latency + pull_latency
    ack_status, ack_latency, acked = call(base, key, "POST", f"/v1/bus/{parse.quote(message_id)}/ack", {
        "message_id": message_id, "receiver": receiver, "workspace": workspace,
    }, ca_cert)
    return ack_status == 200 and acked.get("status") == "acked", send_latency + pull_latency + ack_latency


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--workspace", default="soak")
    parser.add_argument("--duration-seconds", type=int, default=86400)
    parser.add_argument("--workers", type=int, default=64)
    parser.add_argument("--rate", type=int, default=100)
    parser.add_argument("--ca-cert")
    args = parser.parse_args()
    deadline = time.monotonic() + args.duration_seconds
    latencies: list[float] = []
    outcomes = Counter()
    sequence = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        while time.monotonic() < deadline:
            batch_start = time.monotonic()
            futures = [pool.submit(worker, args.url, args.api_key, args.workspace, sequence + i, args.ca_cert) for i in range(args.rate)]
            sequence += args.rate
            for future in futures:
                ok, latency = future.result()
                outcomes["ok" if ok else "failed"] += 1
                latencies.append(latency)
            delay = 1.0 - (time.monotonic() - batch_start)
            if delay > 0:
                time.sleep(delay)
    ordered = sorted(latencies)
    def pct(q: float) -> float:
        return ordered[min(len(ordered) - 1, max(0, int(q * len(ordered)) - 1))] if ordered else 0.0
    report = {"requests": sum(outcomes.values()), "outcomes": dict(outcomes), "latency_ms": {"p50": pct(.5), "p95": pct(.95), "p99": pct(.99), "mean": statistics.mean(latencies) if latencies else 0.0}}
    print(json.dumps(report, sort_keys=True))
    if outcomes["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
