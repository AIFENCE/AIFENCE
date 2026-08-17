# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol


class DecisionClient(Protocol):
    def decide(self, request: dict[str, Any], *, idempotency_key: str | None = None) -> dict[str, Any]: ...
    def ingest_event(self, event: dict[str, Any]) -> dict[str, Any]: ...


@dataclass(frozen=True)
class AgentManifest:
    id: str
    instance_id: str
    version: str
    workload_identity: str
    model: str
    instruction_hash: str


@dataclass
class AgentDanceGuard:
    """Framework-neutral interceptor used by OpenAI Agents, LangGraph, Semantic Kernel,
    AutoGen, CrewAI, and custom tool runtimes without importing those frameworks.
    """

    client: DecisionClient
    principal: dict[str, Any]
    manifest: AgentManifest
    objective: dict[str, Any]
    security_context: dict[str, Any]
    trace_id: str
    event_sink: Callable[[dict[str, Any]], None] | None = None
    _sequence: int = field(default=0, init=False)

    def authorize_tool(
        self,
        *,
        tool: str,
        operation: str,
        target: str | None,
        arguments: dict[str, Any],
        destructive: bool = False,
        reversible: bool = True,
        external_effect: bool = True,
        amount_usd: float | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        request = {
            "trace_id": self.trace_id,
            "principal": self.principal,
            "agent": self.manifest.__dict__,
            "objective": self.objective,
            "action": {
                "type": "tool.call",
                "tool": tool,
                "operation": operation,
                "target": target,
                "arguments": arguments,
                "destructive": destructive,
                "reversible": reversible,
                "external_effect": external_effect,
                "amount_usd": amount_usd,
            },
            "security_context": self.security_context,
        }
        decision = self.client.decide(request, idempotency_key=idempotency_key)
        self.record("framework.tool_authorized", {"tool": tool, "operation": operation, "decision": decision})
        if decision["outcome"] in {"deny", "quarantine_and_terminate", "require_approval"}:
            raise PermissionError(f"AGENTDANCE blocked tool call: {decision['outcome']}")
        return decision

    def record(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._sequence += 1
        event = {"trace_id": self.trace_id, "event_type": event_type, "payload": {**payload, "framework_sequence": self._sequence}}
        result = self.client.ingest_event(event)
        if self.event_sink:
            self.event_sink(result)
        return result

    def openai_agents_hooks(self) -> dict[str, Callable[..., Any]]:
        return self._hooks("openai_agents")

    def langgraph_hooks(self) -> dict[str, Callable[..., Any]]:
        return self._hooks("langgraph")

    def semantic_kernel_hooks(self) -> dict[str, Callable[..., Any]]:
        return self._hooks("semantic_kernel")

    def autogen_hooks(self) -> dict[str, Callable[..., Any]]:
        return self._hooks("autogen")

    def crewai_hooks(self) -> dict[str, Callable[..., Any]]:
        return self._hooks("crewai")

    def _hooks(self, framework: str) -> dict[str, Callable[..., Any]]:
        def on_model_start(*, model: str, input: Any, **_: Any) -> dict[str, Any]:
            return self.record(f"{framework}.model_start", {"model": model, "input_hash": _hash(input)})

        def on_model_end(*, output: Any, **_: Any) -> dict[str, Any]:
            return self.record(f"{framework}.model_end", {"output_hash": _hash(output)})

        def on_handoff(*, target_agent: str, payload: Any, **_: Any) -> dict[str, Any]:
            return self.record(f"{framework}.handoff", {"target_agent": target_agent, "payload_hash": _hash(payload)})

        def before_tool(**kwargs: Any) -> dict[str, Any]:
            return self.authorize_tool(
                tool=str(kwargs["tool"]),
                operation=str(kwargs.get("operation", "execute")),
                target=kwargs.get("target"),
                arguments=dict(kwargs.get("arguments", {})),
                destructive=bool(kwargs.get("destructive", False)),
                reversible=bool(kwargs.get("reversible", True)),
                external_effect=bool(kwargs.get("external_effect", True)),
                amount_usd=kwargs.get("amount_usd"),
                idempotency_key=kwargs.get("idempotency_key"),
            )

        return {
            "on_model_start": on_model_start,
            "on_model_end": on_model_end,
            "on_handoff": on_handoff,
            "before_tool": before_tool,
        }


def _hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(encoded).hexdigest()
