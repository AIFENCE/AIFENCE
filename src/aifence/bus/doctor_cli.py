# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any, Protocol

import httpx

from . import __version__


class HttpClient(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        json: Any | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> httpx.Response: ...


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str
    hint: str | None = None


def _response_detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        text = response.text.strip()
        return text[:300] or f"HTTP {response.status_code}"
    if isinstance(payload, dict) and "detail" in payload:
        return str(payload["detail"])
    return json.dumps(payload, sort_keys=True)[:300]


def _expect_json(client: HttpClient, method: str, path: str, **kwargs: Any) -> Any:
    response = client.request(method, path, **kwargs)
    if response.is_error:
        raise RuntimeError(f"HTTP {response.status_code}: {_response_detail(response)}")
    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError("server returned a non-JSON response") from exc


def run_doctor(
    client: HttpClient,
    *,
    workspace: str = "default",
    check_flow: bool = True,
    agent_id: str | None = None,
) -> list[CheckResult]:
    results: list[CheckResult] = []

    try:
        live = _expect_json(client, "GET", "/health/live")
        if not isinstance(live, dict) or live.get("alive") is not True:
            raise RuntimeError(f"unexpected response: {live!r}")
        version = str(live.get("version", "unknown"))
        results.append(CheckResult("Service reachable", True, f"SAGE {version}"))
    except (httpx.HTTPError, RuntimeError) as exc:
        results.append(
            CheckResult(
                "Service reachable",
                False,
                str(exc),
                "Start SAGE and confirm --url points to the service from this machine or container.",
            )
        )
        return results

    try:
        ready_response = client.request("GET", "/v1/ready")
        if ready_response.status_code == 403:
            results.append(
                CheckResult(
                    "Database ready",
                    True,
                    "service-only readiness check skipped for an agent-scoped credential",
                )
            )
        else:
            if ready_response.is_error:
                raise RuntimeError(
                    f"HTTP {ready_response.status_code}: {_response_detail(ready_response)}"
                )
            ready = ready_response.json()
            if not isinstance(ready, dict) or ready.get("ready") is not True:
                raise RuntimeError(f"unexpected response: {ready!r}")
            results.append(CheckResult("Database ready", True, "database query succeeded"))
    except (httpx.HTTPError, RuntimeError, ValueError) as exc:
        hint = "Set --api-key or SAGE_API_KEY when authentication is enabled."
        results.append(CheckResult("Database ready", False, str(exc), hint))

    try:
        protocol = _expect_json(client, "GET", "/v1/protocol")
        if not isinstance(protocol, dict):
            raise RuntimeError(f"unexpected response: {protocol!r}")
        if protocol.get("protocol") != "sage/0.2" or protocol.get("wire_version") != 2:
            raise RuntimeError(f"unsupported protocol response: {protocol!r}")
        results.append(CheckResult("Protocol compatible", True, "sage/0.2, wire 2"))
    except (httpx.HTTPError, RuntimeError) as exc:
        results.append(
            CheckResult(
                "Protocol compatible",
                False,
                str(exc),
                "Use a SAGE v0.2.x server and provide the correct API key.",
            )
        )

    if not check_flow or any(not result.ok for result in results):
        return results

    suffix = uuid.uuid4().hex[:12]
    if agent_id:
        sender = agent_id
        receiver = agent_id
    else:
        sender = f"sage-doctor-sender-{suffix}"
        receiver = f"sage-doctor-receiver-{suffix}"
    message_id: str | None = None
    try:
        handoff = _expect_json(
            client,
            "POST",
            "/v1/bus/handoff",
            json={
                "sender": sender,
                "receiver": receiver,
                "workspace": workspace,
                "run_id": suffix,
                "content": {
                    "check": "sage-doctor",
                    "nonce": suffix,
                    "expected": "claim-and-ack",
                },
            },
        )
        if not isinstance(handoff, dict) or not isinstance(handoff.get("message_id"), str):
            raise RuntimeError(f"unexpected response: {handoff!r}")
        message_id = handoff["message_id"]
        results.append(CheckResult("Test handoff sent", True, message_id))
    except (httpx.HTTPError, RuntimeError) as exc:
        results.append(
            CheckResult(
                "Test handoff sent",
                False,
                str(exc),
                "Check authentication, workspace policy, and server logs.",
            )
        )
        return results

    try:
        context = _expect_json(
            client,
            "GET",
            f"/v1/bus/context/{receiver}",
            params={"workspace": workspace, "limit": 20, "budget_tokens": 1200},
        )
        if not isinstance(context, list):
            raise RuntimeError(f"unexpected response: {context!r}")
        claimed = next(
            (item for item in context if isinstance(item, dict) and item.get("message_id") == message_id),
            None,
        )
        if claimed is None:
            raise RuntimeError("the sent message was not returned by the context claim")
        results.append(CheckResult("Test context claimed", True, f"receiver={receiver}"))
    except (httpx.HTTPError, RuntimeError) as exc:
        results.append(
            CheckResult(
                "Test context claimed",
                False,
                str(exc),
                "Confirm the receiver and workspace are identical on send and receive.",
            )
        )
        return results

    try:
        acknowledged = _expect_json(
            client,
            "POST",
            "/v1/bus/ack-batch",
            json={"message_ids": [message_id], "receiver": receiver, "workspace": workspace},
        )
        if not isinstance(acknowledged, list) or not acknowledged:
            raise RuntimeError(f"unexpected response: {acknowledged!r}")
        results.append(CheckResult("Test message acknowledged", True, message_id))
    except (httpx.HTTPError, RuntimeError) as exc:
        results.append(
            CheckResult(
                "Test message acknowledged",
                False,
                str(exc),
                "Confirm the message was claimed by the same receiver before ACK.",
            )
        )
        return results

    try:
        remaining = _expect_json(
            client,
            "GET",
            f"/v1/bus/pull/{receiver}",
            params={"workspace": workspace, "limit": 20, "claim": "false"},
        )
        if not isinstance(remaining, list):
            raise RuntimeError(f"unexpected response: {remaining!r}")
        if any(isinstance(item, dict) and item.get("message_id") == message_id for item in remaining):
            raise RuntimeError("acknowledged message is still pending")
        results.append(CheckResult("Delivery lifecycle complete", True, "no pending copy remains"))
    except (httpx.HTTPError, RuntimeError) as exc:
        results.append(CheckResult("Delivery lifecycle complete", False, str(exc)))

    return results


def _print_results(results: list[CheckResult], *, json_output: bool) -> None:
    if json_output:
        print(
            json.dumps(
                {
                    "ok": all(result.ok for result in results),
                    "version": __version__,
                    "checks": [asdict(result) for result in results],
                },
                indent=2,
            )
        )
        return
    for result in results:
        marker = "OK" if result.ok else "FAIL"
        print(f"[{marker}] {result.name}: {result.detail}")
        if result.hint and not result.ok:
            print(f"       Fix: {result.hint}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a SAGE service and its durable delivery flow")
    parser.add_argument("--url", default=os.getenv("SAGE_URL", "http://127.0.0.1:8080"))
    parser.add_argument("--api-key", default=os.getenv("SAGE_API_KEY"))
    parser.add_argument("--workspace", default=os.getenv("SAGE_WORKSPACE", "default"))
    parser.add_argument(
        "--agent-id",
        default=os.getenv("SAGE_AGENT_ID"),
        help="use a self-addressed check suitable for an agent-scoped API key",
    )
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--no-flow", action="store_true", help="check health, database, and protocol only")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    headers = {"Authorization": f"Bearer {args.api_key}"} if args.api_key else {}
    try:
        with httpx.Client(base_url=args.url.rstrip("/"), headers=headers, timeout=args.timeout) as client:
            results = run_doctor(
                client,
                workspace=args.workspace,
                check_flow=not args.no_flow,
                agent_id=args.agent_id,
            )
    except (httpx.HTTPError, ValueError) as exc:
        results = [
            CheckResult(
                "Service reachable",
                False,
                str(exc),
                "Check --url, DNS, Docker networking, and whether the SAGE service is running.",
            )
        ]
    _print_results(results, json_output=args.json_output)
    if not all(result.ok for result in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
