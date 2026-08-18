from __future__ import annotations

import json
from typing import Any

import pytest

from aifence.bus import hermes_plugin


class Context:
    def __init__(self) -> None:
        self.schema: dict[str, Any] | None = None
        self.handler: Any = None

    def register_tool(self, **kwargs: Any) -> None:
        self.schema = kwargs["schema"]
        self.handler = kwargs["handler"]

    def register_hook(self, *_: Any, **__: Any) -> None:
        return None


def registered(monkeypatch: pytest.MonkeyPatch) -> tuple[Context, list[dict[str, Any]]]:
    sent: list[dict[str, Any]] = []

    def request(method: str, path: str, payload: Any | None = None) -> dict[str, bool]:
        assert method == "POST"
        assert path == "/v1/bus/handoff"
        assert isinstance(payload, dict)
        sent.append(payload)
        return {"ok": True}

    monkeypatch.setattr(hermes_plugin, "_request", request)
    ctx = Context()
    hermes_plugin.register(ctx)
    return ctx, sent


def test_handoff_schema_requires_structured_content(monkeypatch: pytest.MonkeyPatch) -> None:
    ctx, _ = registered(monkeypatch)
    assert ctx.schema is not None
    content = ctx.schema["parameters"]["properties"]["content"]
    assert content["type"] == "object"
    assert content["additionalProperties"] is True


def test_handoff_forwards_object(monkeypatch: pytest.MonkeyPatch) -> None:
    ctx, sent = registered(monkeypatch)
    result = json.loads(ctx.handler({"receiver": "peer", "content": {"value": 7}}))
    assert result == {"ok": True}
    assert sent[0]["content"] == {"value": 7}


def test_handoff_recovers_json_object_string(monkeypatch: pytest.MonkeyPatch) -> None:
    ctx, sent = registered(monkeypatch)
    ctx.handler({"receiver": "peer", "content": '{"value":7}'})
    assert sent[0]["content"] == {"value": 7}


def test_handoff_rejects_plain_text(monkeypatch: pytest.MonkeyPatch) -> None:
    ctx, _ = registered(monkeypatch)
    with pytest.raises(ValueError, match="JSON object, not plain text"):
        ctx.handler({"receiver": "peer", "content": "hello"})


def test_handoff_rejects_semantic_envelope(monkeypatch: pytest.MonkeyPatch) -> None:
    ctx, _ = registered(monkeypatch)
    content = {
        "concepts": [],
        "literals": [],
        "references": [],
        "provenance": {},
    }
    with pytest.raises(ValueError, match="encoded AIFENCE semantic envelope"):
        ctx.handler({"receiver": "peer", "content": content})
