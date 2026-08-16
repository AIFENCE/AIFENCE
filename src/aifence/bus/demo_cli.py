# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from typing import Any

import httpx

from .doctor_cli import HttpClient, _expect_json


def run_demo(
    client: HttpClient,
    *,
    workspace: str,
    content: dict[str, Any],
    single_agent: bool,
    sender: str | None = None,
    receiver: str | None = None,
) -> dict[str, Any]:
    suffix = uuid.uuid4().hex[:10]
    if single_agent:
        agent = sender or receiver or f"sage-demo-{suffix}"
        sender_id = agent
        receiver_id = agent
    else:
        sender_id = sender or f"sage-demo-a-{suffix}"
        receiver_id = receiver or f"sage-demo-b-{suffix}"

    handoff = _expect_json(
        client,
        "POST",
        "/v1/bus/handoff",
        json={
            "sender": sender_id,
            "receiver": receiver_id,
            "workspace": workspace,
            "run_id": suffix,
            "content": content,
        },
    )
    if not isinstance(handoff, dict) or not isinstance(handoff.get("message_id"), str):
        raise RuntimeError(f"unexpected handoff response: {handoff!r}")
    message_id = handoff["message_id"]

    context = _expect_json(
        client,
        "GET",
        f"/v1/bus/context/{receiver_id}",
        params={"workspace": workspace, "limit": 20, "budget_tokens": 1200},
    )
    if not isinstance(context, list):
        raise RuntimeError(f"unexpected context response: {context!r}")
    received = next(
        (item for item in context if isinstance(item, dict) and item.get("message_id") == message_id),
        None,
    )
    if received is None:
        raise RuntimeError("the demo handoff was not returned by the receiver")

    ack = _expect_json(
        client,
        "POST",
        "/v1/bus/ack-batch",
        json={"message_ids": [message_id], "receiver": receiver_id, "workspace": workspace},
    )
    if not isinstance(ack, list) or not ack:
        raise RuntimeError(f"unexpected ACK response: {ack!r}")

    return {
        "mode": "single-agent" if single_agent else "two-agent",
        "workspace": workspace,
        "sender": sender_id,
        "receiver": receiver_id,
        "sent": content,
        "message_id": message_id,
        "received": received,
        "acknowledged": True,
    }


def _parse_content(value: str | None) -> dict[str, Any]:
    if value is None:
        return {
            "task": "prepare_release",
            "status": "ready",
            "constraints": ["preserve meaning", "acknowledge after consumption"],
            "next_action": "publish verified artifacts",
        }
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"--content must be valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError("--content must be a JSON object")
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a visible end-to-end SAGE handoff demo")
    parser.add_argument("--url", default=os.getenv("SAGE_URL", "http://127.0.0.1:8080"))
    parser.add_argument("--api-key", default=os.getenv("SAGE_API_KEY"))
    parser.add_argument("--workspace", default=os.getenv("SAGE_WORKSPACE", "default"))
    parser.add_argument("--sender")
    parser.add_argument("--receiver")
    parser.add_argument("--single-agent", action="store_true")
    parser.add_argument("--content", help="raw JSON object to send")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    try:
        content = _parse_content(args.content)
        headers = {"Authorization": f"Bearer {args.api_key}"} if args.api_key else {}
        with httpx.Client(base_url=args.url.rstrip("/"), headers=headers, timeout=args.timeout) as client:
            result = run_demo(
                client,
                workspace=args.workspace,
                content=content,
                single_agent=args.single_agent,
                sender=args.sender,
                receiver=args.receiver,
            )
    except (httpx.HTTPError, RuntimeError, ValueError) as exc:
        print(f"SAGE demo failed: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.json_output:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    print(f"Mode: {result['mode']}")
    print(f"Route: {result['sender']} -> {result['receiver']} ({result['workspace']})")
    print(f"Message: {result['message_id']}")
    print("Sent raw application data:")
    print(json.dumps(result["sent"], indent=2, ensure_ascii=False))
    print("Received decoded SAGE context:")
    print(json.dumps(result["received"], indent=2, ensure_ascii=False))
    print("[OK] Message acknowledged")


if __name__ == "__main__":
    main()
