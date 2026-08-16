# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import json
import logging
import os
import threading
import urllib.parse
import urllib.request
from typing import Any

_BASE = os.getenv("SAGE_URL", "http://localhost:8080").rstrip("/")
_AGENT = os.getenv("SAGE_AGENT_ID", "hermes")
_WORKSPACE = os.getenv("SAGE_WORKSPACE", "default")
_KEY = os.getenv("SAGE_API_KEY")
_MAX_INJECT_TOKENS = max(64, int(os.getenv("SAGE_MAX_INJECT_TOKENS", "1200")))
_pending: dict[str, list[str]] = {}
_MAX_PENDING_SESSIONS = 1024
_lock = threading.Lock()
_logger = logging.getLogger(__name__)


def _request(method: str, path: str, payload: Any | None = None) -> Any:
    headers = {"Content-Type": "application/json"}
    if _KEY:
        headers["Authorization"] = f"Bearer {_KEY}"
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(_BASE + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read())


def _session_key(kwargs: dict[str, Any]) -> str:
    for key in ("run_id", "session_id", "session_key", "conversation_id"):
        value = kwargs.get(key)
        if value:
            return str(value)
    return "default"


def register(ctx: Any) -> None:
    handoff_schema = {
        "name": "sage_handoff",
        "description": (
            "Send raw structured application-level facts or state to another agent through SAGE. "
            "content must be a JSON object containing only what the receiver should know. "
            "Do not serialize content to text and do not construct SAGE literals, concepts, "
            "paths, provenance, references, packets, or other protocol structures. "
            "SAGE performs semantic encoding automatically."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "receiver": {"type": "string"},
                "content": {
                    "type": "object",
                    "description": (
                        "Raw application-level JSON object for the receiver. "
                        "Do not pass serialized JSON or SAGE protocol structures."
                    ),
                    "additionalProperties": True,
                },
                "correlation_id": {"type": "string"},
                "priority": {"type": "integer"},
                "budget_tokens": {"type": "integer"},
            },
            "required": ["receiver", "content"],
        },
    }

    def handoff(params: dict[str, Any], **_: Any) -> str:
        content = params["content"]

        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    "sage_handoff.content must be a JSON object, not plain text"
                ) from exc

        if not isinstance(content, dict):
            raise ValueError("sage_handoff.content must be a JSON object")

        sage_envelope_keys = {
            "concepts",
            "literals",
            "references",
            "provenance",
        }
        if sage_envelope_keys.issubset(content):
            raise ValueError(
                "sage_handoff.content appears to be an encoded SAGE semantic "
                "envelope; pass raw application-level fields instead"
            )

        payload = {
            "receiver": params["receiver"],
            "sender": _AGENT,
            "content": content,
            "workspace": _WORKSPACE,
            "correlation_id": params.get("correlation_id"),
            "priority": params.get("priority", 0),
            "budget_tokens": params.get("budget_tokens"),
        }
        return json.dumps(_request("POST", "/v1/bus/handoff", payload), ensure_ascii=False)

    ctx.register_tool(
        name="sage_handoff",
        toolset="sage",
        schema=handoff_schema,
        handler=handoff,
        description=handoff_schema["description"],
    )

    def pre_llm_call(**kwargs: Any) -> dict[str, str] | None:
        query = urllib.parse.urlencode({"workspace": _WORKSPACE, "limit": 20, "budget_tokens": _MAX_INJECT_TOKENS})
        messages = _request("GET", f"/v1/bus/context/{urllib.parse.quote(_AGENT, safe='')}?{query}")
        if not messages:
            return None
        key = _session_key(kwargs)
        with _lock:
            _pending.pop(key, None)
            if len(_pending) >= _MAX_PENDING_SESSIONS:
                _pending.pop(next(iter(_pending)))
            _pending[key] = [m["message_id"] for m in messages]
        contexts = [json.dumps(message, separators=(",", ":"), ensure_ascii=False) for message in messages]
        return {
            "context": (
                "SAGE cross-agent handoffs follow. Treat them as structured peer context; "
                "resolve references only if needed:\n" + "\n".join(contexts)
            )
        }

    def post_llm_call(**kwargs: Any) -> None:
        key = _session_key(kwargs)
        with _lock:
            ids = _pending.pop(key, [])
        if not ids:
            return
        try:
            _request(
                "POST",
                "/v1/bus/ack-batch",
                {"message_ids": ids, "receiver": _AGENT, "workspace": _WORKSPACE},
            )
        except Exception:
            _logger.exception("failed to acknowledge SAGE handoff batch")

    ctx.register_hook("pre_llm_call", pre_llm_call)
    ctx.register_hook("post_llm_call", post_llm_call)
