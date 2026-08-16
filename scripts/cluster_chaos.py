from __future__ import annotations

import argparse
import json
import ssl
import subprocess
import time
from urllib import parse, request


def api(base: str, key: str, method: str, path: str, payload: dict | None = None, ca_cert: str | None = None) -> tuple[int, dict]:
    body = json.dumps(payload).encode() if payload is not None else None
    req = request.Request(base.rstrip("/") + path, method=method, data=body)
    req.add_header("Authorization", f"Bearer {key}")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        context = ssl.create_default_context(cafile=ca_cert) if ca_cert else None
        with request.urlopen(req, timeout=10, context=context) as response:
            return response.status, json.loads(response.read() or b"{}")
    except Exception as exc:
        return 0, {"error": type(exc).__name__}


def compose(file: str, *args: str) -> None:
    subprocess.run(["docker", "compose", "-f", file, *args], check=True, timeout=120)


def verify_round_trip(base: str, key: str, workspace: str, suffix: str, ca_cert: str | None = None) -> str:
    receiver = f"chaos-{suffix}"
    handoff = {
        "receiver": receiver,
        "sender": "chaos-controller",
        "workspace": workspace,
        "content": {"suffix": suffix, "status": "ready"},
        "idempotency_key": f"chaos-{suffix}",
        "ordering_key": "chaos-stream",
    }

    def attempt() -> tuple[int, str]:
        status, sent = api(base, key, "POST", "/v1/bus/handoff", handoff, ca_cert)
        if status != 200:
            return status, f"handoff failed: {sent}"
        status, repeated = api(base, key, "POST", "/v1/bus/handoff", handoff, ca_cert)
        if status != 200 or repeated.get("message_id") != sent.get("message_id"):
            return 599, "idempotent handoff failed"
        query = parse.urlencode({"workspace": workspace, "claim": "true", "limit": 1})
        status, rows = api(base, key, "GET", f"/v1/bus/pull/{parse.quote(receiver)}?{query}", ca_cert=ca_cert)
        if status != 200 or not isinstance(rows, list) or len(rows) != 1:
            return 599, "claim failed"
        message_id = rows[0]["message_id"]
        status, ack = api(base, key, "POST", f"/v1/bus/{parse.quote(message_id)}/ack", {"message_id": message_id, "receiver": receiver, "workspace": workspace}, ca_cert)
        if status != 200 or ack.get("status") != "acked":
            return 599, "ack failed"
        return 200, message_id

    # A paused/killed worker can leave one in-flight request hanging on the
    # load balancer while it fails over (nginx 499/502/504). Retry transient
    # transport failures so the assertion is cluster recovery, not scheduling.
    last: tuple[int, str] = (0, "no attempt")
    for _ in range(5):
        status, detail = attempt()
        if status == 200:
            return detail
        last = (status, detail)
        time.sleep(2)
    raise RuntimeError(f"round trip failed after retries: {last}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--compose-file", required=True)
    parser.add_argument("--workspace", default="chaos")
    parser.add_argument("--disrupt-postgres", action="store_true")
    parser.add_argument("--ca-cert")
    args = parser.parse_args()

    verify_round_trip(args.url, args.api_key, args.workspace, "baseline", args.ca_cert)
    # Stop (not pause) the worker: a paused process keeps TCP alive so the load
    # balancer waits on it; a stopped worker fails over via connection refusal.
    compose(args.compose_file, "stop", "sage-b")
    try:
        verify_round_trip(args.url, args.api_key, args.workspace, "worker-stopped", args.ca_cert)
    finally:
        compose(args.compose_file, "start", "sage-b")

    if args.disrupt_postgres:
        compose(args.compose_file, "stop", "postgres")
        time.sleep(2)
        failed_status, _ = api(args.url, args.api_key, "GET", "/v1/ready", ca_cert=args.ca_cert)
        if failed_status == 200:
            raise RuntimeError("readiness stayed healthy with PostgreSQL stopped")
        compose(args.compose_file, "start", "postgres")
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            status, _ = api(args.url, args.api_key, "GET", "/v1/ready", ca_cert=args.ca_cert)
            if status == 200:
                break
            time.sleep(1)
        else:
            raise RuntimeError("service did not recover after PostgreSQL restart")
        verify_round_trip(args.url, args.api_key, args.workspace, "postgres-recovered", args.ca_cert)

    print(json.dumps({"ok": True, "worker_failover": True, "postgres_recovery": args.disrupt_postgres}, sort_keys=True))


if __name__ == "__main__":
    main()
