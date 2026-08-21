#!/usr/bin/env python3
"""Connectivity smoke for optional broker fan-out backends.

The durable database remains the delivery authority; this check only proves that
configured optional transports can establish a connection and publish the
content-free handoff event used by AIFENCE.
"""
from __future__ import annotations

import argparse
import json

from aifence.bus.transport import HandoffEvent, build_transport

EVENT = HandoffEvent(
    message_id="compat-smoke",
    receiver="compat-receiver",
    sender="compat-sender",
    workspace="compat",
    correlation_id="compat-smoke",
    wire_bytes=0,
    strategy="smoke",
)


def publish(backend: str, url: str) -> dict[str, object]:
    transport = build_transport(backend, url=url, topic="aifence.compatibility")
    try:
        transport.publish(EVENT)
    finally:
        transport.close()
    return {"backend": backend, "published": True}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--redis", required=True)
    parser.add_argument("--kafka", required=True)
    parser.add_argument("--rabbitmq", required=True)
    args = parser.parse_args()
    result = [
        publish("redis", args.redis),
        publish("kafka", args.kafka),
        publish("rabbitmq", args.rabbitmq),
    ]
    print(json.dumps({"ok": True, "transports": result}, sort_keys=True))


if __name__ == "__main__":
    main()
