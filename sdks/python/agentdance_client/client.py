# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import asyncio
import secrets
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx

_RETRYABLE_STATUS_CODES = {429, 502, 503, 504}


class AgentDanceError(RuntimeError):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(f"{code}: {message}")
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


def _path(value: str) -> str:
    return quote(value, safe="")


def _retry_delay(response: httpx.Response | None, attempt: int) -> float:
    retry_after = response.headers.get("Retry-After") if response is not None else None
    if retry_after:
        try:
            delay = float(retry_after)
            if delay > 0:
                return min(delay, 60)
        except ValueError:
            pass
    return min(2**attempt, 8)


def _raise_for_error(response: httpx.Response) -> None:
    if not response.is_error:
        return
    try:
        payload = response.json()
        error = payload.get("error", {}) if isinstance(payload, dict) else {}
    except ValueError:
        error = {}
    raise AgentDanceError(
        response.status_code,
        str(error.get("code", "http_error")),
        str(error.get("message", response.text)),
        error.get("details") if isinstance(error.get("details"), dict) else {},
    )


class AgentDanceClient:
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        *,
        timeout_seconds: float = 30,
        verify: bool | str = True,
        cert: str | tuple[str, str] | None = None,
        max_retries: int = 3,
    ) -> None:
        if not base_url.startswith("https://"):
            raise ValueError("AGENTDANCE base_url must use HTTPS")
        if not api_key and cert is None:
            raise ValueError("AGENTDANCE requires an API key or mTLS client certificate")
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        self.max_retries = max_retries
        headers = {"Accept": "application/json", "User-Agent": "agentdance-python/1.0.0-rc.5"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            headers=headers,
            timeout=timeout_seconds,
            verify=verify,
            cert=cert,
            follow_redirects=False,
            trust_env=False,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> AgentDanceClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def create_api_key(self, request: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", "/v1/api-keys", json=request)

    def list_api_keys(self) -> list[dict[str, Any]]:
        return self._json("GET", "/v1/api-keys", retryable=True)

    def revoke_api_key(self, key_id: str, reason: str) -> dict[str, Any]:
        return self._json("POST", f"/v1/api-keys/{_path(key_id)}/revoke", json={"reason": reason})

    def register_agent(self, registration: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", "/v1/agents/register", json=registration)

    def get_agent(self, agent_id: str) -> dict[str, Any]:
        return self._json("GET", f"/v1/agents/{_path(agent_id)}", retryable=True)

    def revoke_agent(self, agent_id: str, reason: str) -> dict[str, Any]:
        return self._json("POST", f"/v1/agents/{_path(agent_id)}/revoke", json={"reason": reason})

    def decide(self, request: dict[str, Any], *, idempotency_key: str | None = None) -> dict[str, Any]:
        body = dict(request)
        body.setdefault("idempotency_key", idempotency_key or f"sdk_{secrets.token_urlsafe(18)}")
        return self._json("POST", "/v1/decisions", json=body, retryable=True)

    def get_decision(self, decision_id: str) -> dict[str, Any]:
        return self._json("GET", f"/v1/decisions/{_path(decision_id)}", retryable=True)

    def ingest_event(self, event: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", "/v1/events", json=event)

    def get_trace(self, trace_id: str) -> list[dict[str, Any]]:
        return self._json("GET", f"/v1/traces/{_path(trace_id)}", retryable=True)

    def list_policies(self) -> list[dict[str, Any]]:
        return self._json("GET", "/v1/policies", retryable=True)

    def publish_policy(self, request: dict[str, Any]) -> dict[str, Any]:
        body = dict(request)
        body["activate"] = False
        return self._json("POST", "/v1/policies", json=body)

    def activate_policy(self, policy_id: str, reason: str) -> dict[str, Any]:
        return self._json("POST", f"/v1/policies/{_path(policy_id)}/activate", json={"reason": reason})

    def list_approvals(self, *, status: str | None = None) -> list[dict[str, Any]]:
        params = {"status": status} if status is not None else None
        return self._json("GET", "/v1/approvals", params=params, retryable=True)

    def get_approval(self, approval_id: str) -> dict[str, Any]:
        return self._json("GET", f"/v1/approvals/{_path(approval_id)}", retryable=True)

    def decide_approval(self, approval_id: str, decision: str, reason: str) -> dict[str, Any]:
        return self._json(
            "POST",
            f"/v1/approvals/{_path(approval_id)}/decision",
            json={"decision": decision, "reason": reason},
        )

    def issue_capability(
        self,
        decision_id: str,
        *,
        lifetime_seconds: int = 60,
    ) -> dict[str, Any]:
        return self._json(
            "POST",
            "/v1/capabilities",
            json={
                "decision_id": decision_id,
                "lifetime_seconds": lifetime_seconds,
            },
        )

    def consume_capability(self, request: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", "/v1/capabilities/consume", json=request)

    def revoke_capability(self, capability_id: str, reason: str) -> dict[str, Any]:
        return self._json(
            "POST",
            f"/v1/capabilities/{_path(capability_id)}/revoke",
            json={"reason": reason},
        )

    def scan_artifact(self, trace_id: str, path: str | Path, media_type: str) -> dict[str, Any]:
        artifact = Path(path)
        with artifact.open("rb") as handle:
            return self._json(
                "POST",
                "/v1/artifacts/scan",
                data={"trace_id": trace_id},
                files={"artifact": (artifact.name, handle, media_type)},
            )

    def get_artifact(self, artifact_id: str) -> dict[str, Any]:
        return self._json("GET", f"/v1/artifacts/{_path(artifact_id)}", retryable=True)

    def download_artifact(self, artifact_id: str) -> bytes:
        response = self._request(
            "GET",
            f"/v1/artifacts/{_path(artifact_id)}/content",
            retryable=True,
        )
        return response.content

    def list_incidents(self, *, status: str | None = None) -> list[dict[str, Any]]:
        params = {"status": status} if status is not None else None
        return self._json("GET", "/v1/incidents", params=params, retryable=True)

    def create_incident(self, request: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", "/v1/incidents", json=request)

    def get_incident(self, incident_id: str) -> dict[str, Any]:
        return self._json("GET", f"/v1/incidents/{_path(incident_id)}", retryable=True)

    def update_incident(self, incident_id: str, status: str, reason: str) -> dict[str, Any]:
        return self._json(
            "POST",
            f"/v1/incidents/{_path(incident_id)}/status",
            json={"status": status, "reason": reason},
        )

    def list_providers(self) -> list[dict[str, Any]]:
        return self._json("GET", "/v1/providers", retryable=True)

    def register_provider(self, request: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", "/v1/providers", json=request)

    def revoke_provider(self, provider_id: str, reason: str) -> dict[str, Any]:
        return self._json("POST", f"/v1/providers/{_path(provider_id)}/revoke", json={"reason": reason})

    def invoke_provider(
        self,
        provider_id: str,
        request: dict[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        body = dict(request)
        body.setdefault("idempotency_key", idempotency_key or f"sdk_{secrets.token_urlsafe(18)}")
        return self._json(
            "POST", f"/v1/providers/{_path(provider_id)}/invoke", json=body, retryable=True
        )

    def list_tools(self) -> list[dict[str, Any]]:
        return self._json("GET", "/v1/tools", retryable=True)

    def register_tool(self, request: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", "/v1/tools", json=request)

    def revoke_tool(self, tool_id: str, reason: str) -> dict[str, Any]:
        return self._json("POST", f"/v1/tools/{_path(tool_id)}/revoke", json={"reason": reason})

    def execute_tool(
        self,
        tool_id: str,
        request: dict[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        body = dict(request)
        body.setdefault("idempotency_key", idempotency_key or f"sdk_{secrets.token_urlsafe(18)}")
        return self._json(
            "POST", f"/v1/tools/{_path(tool_id)}/execute", json=body, retryable=True
        )

    def verify_audit(self) -> dict[str, Any]:
        return self._json("GET", "/v1/audit/verify", retryable=True)

    def list_audit_checkpoints(self, *, limit: int = 100) -> list[dict[str, Any]]:
        return self._json(
            "GET", "/v1/audit/checkpoints", params={"limit": limit}, retryable=True
        )

    def get_execution(self, execution_id: str) -> dict[str, Any]:
        return self._json("GET", f"/v1/executions/{_path(execution_id)}", retryable=True)

    def reconcile_execution(
        self,
        execution_id: str,
        request: dict[str, Any],
    ) -> dict[str, Any]:
        return self._json(
            "POST", f"/v1/executions/{_path(execution_id)}/reconcile", json=request
        )

    def recover_stale_executions(self, *, limit: int = 100) -> dict[str, Any]:
        return self._json(
            "POST", "/v1/executions/recover-stale", params={"limit": limit}
        )

    def create_workload_identity(self, request: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", "/v1/workload-identities", json=request)

    def list_workload_identities(self) -> list[dict[str, Any]]:
        return self._json("GET", "/v1/workload-identities", retryable=True)

    def revoke_workload_identity(self, binding_id: str, reason: str) -> dict[str, Any]:
        return self._json("POST", f"/v1/workload-identities/{_path(binding_id)}/revoke", json={"reason": reason})

    def validate_policy(self, document: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", "/v1/policies/validate", json={"document": document})

    def simulate_policy(self, document: dict[str, Any], cases: list[dict[str, Any]]) -> dict[str, Any]:
        return self._json("POST", "/v1/policies/simulate", json={"document": document, "cases": cases})

    def diff_policy(self, current_document: dict[str, Any], proposed_document: dict[str, Any], *, cases: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        return self._json("POST", "/v1/policies/diff", json={"current_document": current_document, "proposed_document": proposed_document, "cases": cases or []})

    def replay_policy(self, policy_id: str, *, limit: int = 100) -> dict[str, Any]:
        return self._json("POST", f"/v1/policies/{_path(policy_id)}/replay", params={"limit": limit})

    def canary_policy(self, policy_id: str, percentage: int, reason: str) -> dict[str, Any]:
        return self._json("POST", f"/v1/policies/{_path(policy_id)}/canary", json={"percentage": percentage, "reason": reason})

    def shadow_policy(self, policy_id: str, reason: str) -> dict[str, Any]:
        return self._json("POST", f"/v1/policies/{_path(policy_id)}/shadow", json={"reason": reason})

    def rollback_policy(self, policy_id: str, reason: str) -> dict[str, Any]:
        return self._json("POST", f"/v1/policies/{_path(policy_id)}/rollback", json={"reason": reason})

    def anchor_audit(self, destination: str = "file") -> dict[str, Any]:
        return self._json("POST", "/v1/audit/anchors", json={"destination": destination})

    def verify_audit_anchor(self, anchor_id: str) -> dict[str, Any]:
        return self._json("POST", f"/v1/audit/anchors/{_path(anchor_id)}/verify")

    def anchor_audit_batch(self, destinations: list[str], *, required_quorum: int = 1) -> dict[str, Any]:
        return self._json("POST", "/v1/audit/anchors/batch",
                          json={"destinations": destinations, "required_quorum": required_quorum})

    def audit_anchor_quorum(self, *, sequence: int | None = None,
                            required_quorum: int | None = None) -> dict[str, Any]:
        params = {k: v for k, v in {"sequence": sequence, "required_quorum": required_quorum}.items()
                  if v is not None}
        return self._json("GET", "/v1/audit/anchors/quorum", params=params, retryable=True)

    def write_memory(self, request: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", "/v1/memory", json=request)

    def read_memory(self, memory_id: str, *, include_content: bool = False) -> dict[str, Any]:
        return self._json("GET", f"/v1/memory/{_path(memory_id)}", params={"include_content": str(include_content).lower()}, retryable=True)

    def update_memory_status(self, memory_id: str, status: str, reason: str) -> dict[str, Any]:
        return self._json("POST", f"/v1/memory/{_path(memory_id)}/status", json={"status": status, "reason": reason})

    def create_delegation(self, request: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", "/v1/delegations", json=request)

    def revoke_delegation(self, grant_id: str, reason: str) -> dict[str, Any]:
        return self._json("POST", f"/v1/delegations/{_path(grant_id)}/revoke", json={"reason": reason})

    def create_budget(self, request: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", "/v1/budgets", json=request)

    def reserve_budget(self, budget_id: str, request: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", f"/v1/budgets/{_path(budget_id)}/reserve", json=request)

    def settle_budget(self, reservation_id: str, request: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", f"/v1/budget-reservations/{_path(reservation_id)}/settle", json=request)

    def request_tenant_lifecycle(self, request: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", "/v1/tenant/lifecycle", json=request)

    def get_tenant_lifecycle(self, job_id: str) -> dict[str, Any]:
        return self._json("GET", f"/v1/tenant/lifecycle/{_path(job_id)}", retryable=True)

    def download_tenant_export(self, job_id: str) -> bytes:
        return self._request("GET", f"/v1/tenant/lifecycle/{_path(job_id)}/content",
                             retryable=True).content

    def reconcile_tenant_lifecycle(self, job_id: str, request: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", f"/v1/tenant/lifecycle/{_path(job_id)}/reconcile", json=request)

    def create_legal_hold(self, request: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", "/v1/tenant/legal-holds", json=request)

    def list_legal_holds(self) -> list[dict[str, Any]]:
        return self._json("GET", "/v1/tenant/legal-holds", retryable=True)

    def release_legal_hold(self, hold_id: str, reason: str) -> dict[str, Any]:
        return self._json("POST", f"/v1/tenant/legal-holds/{_path(hold_id)}/release",
                          json={"reason": reason})

    def register_protocol(self, request: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", "/v1/protocols", json=request)

    def list_protocol_manifest_versions(self, registration_id: str) -> list[dict[str, Any]]:
        return self._json("GET", f"/v1/protocols/{_path(registration_id)}/manifest-versions",
                          retryable=True)

    def authorize_a2a(self, registration_id: str, request: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", f"/v1/protocols/a2a/{_path(registration_id)}/authorize", json=request)

    def call_mcp_tool(self, registration_id: str, request: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", f"/v1/protocols/mcp/{_path(registration_id)}/tools/call", json=request)

    def run_dispatcher(self, *, limit: int = 20) -> dict[str, Any]:
        return self._json("POST", "/v1/dispatch/run", params={"limit": limit})

    def _request(self, method: str, path: str, *, retryable: bool = False, **kwargs: Any) -> httpx.Response:
        response: httpx.Response | None = None
        attempts = self.max_retries + 1 if retryable else 1
        for attempt in range(attempts):
            try:
                response = self._client.request(method, path, **kwargs)
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout):
                if attempt + 1 >= attempts:
                    raise
                time.sleep(_retry_delay(None, attempt))
                continue
            if response.status_code not in _RETRYABLE_STATUS_CODES or attempt + 1 >= attempts:
                break
            time.sleep(_retry_delay(response, attempt))
        if response is None:
            raise RuntimeError("AGENTDANCE request did not produce a response")
        _raise_for_error(response)
        return response

    def _json(self, method: str, path: str, *, retryable: bool = False, **kwargs: Any) -> Any:
        return self._request(method, path, retryable=retryable, **kwargs).json()


class AsyncAgentDanceClient:
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        *,
        timeout_seconds: float = 30,
        verify: bool | str = True,
        cert: str | tuple[str, str] | None = None,
        max_retries: int = 3,
    ) -> None:
        if not base_url.startswith("https://"):
            raise ValueError("AGENTDANCE base_url must use HTTPS")
        if not api_key and cert is None:
            raise ValueError("AGENTDANCE requires an API key or mTLS client certificate")
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        self.max_retries = max_retries
        headers = {"Accept": "application/json", "User-Agent": "agentdance-python/1.0.0-rc.5"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers=headers,
            timeout=timeout_seconds,
            verify=verify,
            cert=cert,
            follow_redirects=False,
            trust_env=False,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncAgentDanceClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def create_api_key(self, request: dict[str, Any]) -> dict[str, Any]:
        return await self._json("POST", "/v1/api-keys", json=request)

    async def list_api_keys(self) -> list[dict[str, Any]]:
        return await self._json("GET", "/v1/api-keys", retryable=True)

    async def revoke_api_key(self, key_id: str, reason: str) -> dict[str, Any]:
        return await self._json("POST", f"/v1/api-keys/{_path(key_id)}/revoke", json={"reason": reason})

    async def register_agent(self, registration: dict[str, Any]) -> dict[str, Any]:
        return await self._json("POST", "/v1/agents/register", json=registration)

    async def get_agent(self, agent_id: str) -> dict[str, Any]:
        return await self._json("GET", f"/v1/agents/{_path(agent_id)}", retryable=True)

    async def revoke_agent(self, agent_id: str, reason: str) -> dict[str, Any]:
        return await self._json("POST", f"/v1/agents/{_path(agent_id)}/revoke", json={"reason": reason})

    async def decide(self, request: dict[str, Any], *, idempotency_key: str | None = None) -> dict[str, Any]:
        body = dict(request)
        body.setdefault("idempotency_key", idempotency_key or f"sdk_{secrets.token_urlsafe(18)}")
        return await self._json("POST", "/v1/decisions", json=body, retryable=True)

    async def get_decision(self, decision_id: str) -> dict[str, Any]:
        return await self._json("GET", f"/v1/decisions/{_path(decision_id)}", retryable=True)

    async def ingest_event(self, event: dict[str, Any]) -> dict[str, Any]:
        return await self._json("POST", "/v1/events", json=event)

    async def get_trace(self, trace_id: str) -> list[dict[str, Any]]:
        return await self._json("GET", f"/v1/traces/{_path(trace_id)}", retryable=True)

    async def list_policies(self) -> list[dict[str, Any]]:
        return await self._json("GET", "/v1/policies", retryable=True)

    async def publish_policy(self, request: dict[str, Any]) -> dict[str, Any]:
        body = dict(request)
        body["activate"] = False
        return await self._json("POST", "/v1/policies", json=body)

    async def activate_policy(self, policy_id: str, reason: str) -> dict[str, Any]:
        return await self._json("POST", f"/v1/policies/{_path(policy_id)}/activate", json={"reason": reason})

    async def list_approvals(self, *, status: str | None = None) -> list[dict[str, Any]]:
        params = {"status": status} if status is not None else None
        return await self._json("GET", "/v1/approvals", params=params, retryable=True)

    async def get_approval(self, approval_id: str) -> dict[str, Any]:
        return await self._json("GET", f"/v1/approvals/{_path(approval_id)}", retryable=True)

    async def decide_approval(self, approval_id: str, decision: str, reason: str) -> dict[str, Any]:
        return await self._json(
            "POST",
            f"/v1/approvals/{_path(approval_id)}/decision",
            json={"decision": decision, "reason": reason},
        )

    async def issue_capability(
        self,
        decision_id: str,
        *,
        lifetime_seconds: int = 60,
    ) -> dict[str, Any]:
        return await self._json(
            "POST",
            "/v1/capabilities",
            json={
                "decision_id": decision_id,
                "lifetime_seconds": lifetime_seconds,
            },
        )

    async def consume_capability(self, request: dict[str, Any]) -> dict[str, Any]:
        return await self._json("POST", "/v1/capabilities/consume", json=request)

    async def revoke_capability(self, capability_id: str, reason: str) -> dict[str, Any]:
        return await self._json(
            "POST",
            f"/v1/capabilities/{_path(capability_id)}/revoke",
            json={"reason": reason},
        )

    async def scan_artifact(self, trace_id: str, path: str | Path, media_type: str) -> dict[str, Any]:
        artifact = Path(path)
        content = await asyncio.to_thread(artifact.read_bytes)
        return await self._json(
            "POST",
            "/v1/artifacts/scan",
            data={"trace_id": trace_id},
            files={"artifact": (artifact.name, content, media_type)},
        )

    async def get_artifact(self, artifact_id: str) -> dict[str, Any]:
        return await self._json("GET", f"/v1/artifacts/{_path(artifact_id)}", retryable=True)

    async def download_artifact(self, artifact_id: str) -> bytes:
        response = await self._request(
            "GET",
            f"/v1/artifacts/{_path(artifact_id)}/content",
            retryable=True,
        )
        return response.content

    async def list_incidents(self, *, status: str | None = None) -> list[dict[str, Any]]:
        params = {"status": status} if status is not None else None
        return await self._json("GET", "/v1/incidents", params=params, retryable=True)

    async def create_incident(self, request: dict[str, Any]) -> dict[str, Any]:
        return await self._json("POST", "/v1/incidents", json=request)

    async def get_incident(self, incident_id: str) -> dict[str, Any]:
        return await self._json("GET", f"/v1/incidents/{_path(incident_id)}", retryable=True)

    async def update_incident(self, incident_id: str, status: str, reason: str) -> dict[str, Any]:
        return await self._json(
            "POST",
            f"/v1/incidents/{_path(incident_id)}/status",
            json={"status": status, "reason": reason},
        )

    async def list_providers(self) -> list[dict[str, Any]]:
        return await self._json("GET", "/v1/providers", retryable=True)

    async def register_provider(self, request: dict[str, Any]) -> dict[str, Any]:
        return await self._json("POST", "/v1/providers", json=request)

    async def revoke_provider(self, provider_id: str, reason: str) -> dict[str, Any]:
        return await self._json("POST", f"/v1/providers/{_path(provider_id)}/revoke", json={"reason": reason})

    async def invoke_provider(
        self,
        provider_id: str,
        request: dict[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        body = dict(request)
        body.setdefault("idempotency_key", idempotency_key or f"sdk_{secrets.token_urlsafe(18)}")
        return await self._json(
            "POST", f"/v1/providers/{_path(provider_id)}/invoke", json=body, retryable=True
        )

    async def list_tools(self) -> list[dict[str, Any]]:
        return await self._json("GET", "/v1/tools", retryable=True)

    async def register_tool(self, request: dict[str, Any]) -> dict[str, Any]:
        return await self._json("POST", "/v1/tools", json=request)

    async def revoke_tool(self, tool_id: str, reason: str) -> dict[str, Any]:
        return await self._json("POST", f"/v1/tools/{_path(tool_id)}/revoke", json={"reason": reason})

    async def execute_tool(
        self,
        tool_id: str,
        request: dict[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        body = dict(request)
        body.setdefault("idempotency_key", idempotency_key or f"sdk_{secrets.token_urlsafe(18)}")
        return await self._json(
            "POST", f"/v1/tools/{_path(tool_id)}/execute", json=body, retryable=True
        )

    async def verify_audit(self) -> dict[str, Any]:
        return await self._json("GET", "/v1/audit/verify", retryable=True)

    async def list_audit_checkpoints(self, *, limit: int = 100) -> list[dict[str, Any]]:
        return await self._json(
            "GET", "/v1/audit/checkpoints", params={"limit": limit}, retryable=True
        )

    async def get_execution(self, execution_id: str) -> dict[str, Any]:
        return await self._json(
            "GET", f"/v1/executions/{_path(execution_id)}", retryable=True
        )

    async def reconcile_execution(
        self,
        execution_id: str,
        request: dict[str, Any],
    ) -> dict[str, Any]:
        return await self._json(
            "POST", f"/v1/executions/{_path(execution_id)}/reconcile", json=request
        )

    async def recover_stale_executions(self, *, limit: int = 100) -> dict[str, Any]:
        return await self._json(
            "POST", "/v1/executions/recover-stale", params={"limit": limit}
        )

    async def create_workload_identity(self, request: dict[str, Any]) -> dict[str, Any]:
        return await self._json("POST", "/v1/workload-identities", json=request)

    async def list_workload_identities(self) -> list[dict[str, Any]]:
        return await self._json("GET", "/v1/workload-identities", retryable=True)

    async def revoke_workload_identity(self, binding_id: str, reason: str) -> dict[str, Any]:
        return await self._json("POST", f"/v1/workload-identities/{_path(binding_id)}/revoke", json={"reason": reason})

    async def validate_policy(self, document: dict[str, Any]) -> dict[str, Any]:
        return await self._json("POST", "/v1/policies/validate", json={"document": document})

    async def simulate_policy(self, document: dict[str, Any], cases: list[dict[str, Any]]) -> dict[str, Any]:
        return await self._json("POST", "/v1/policies/simulate", json={"document": document, "cases": cases})

    async def diff_policy(self, current_document: dict[str, Any], proposed_document: dict[str, Any], *, cases: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        return await self._json("POST", "/v1/policies/diff", json={"current_document": current_document, "proposed_document": proposed_document, "cases": cases or []})

    async def replay_policy(self, policy_id: str, *, limit: int = 100) -> dict[str, Any]:
        return await self._json("POST", f"/v1/policies/{_path(policy_id)}/replay", params={"limit": limit})

    async def canary_policy(self, policy_id: str, percentage: int, reason: str) -> dict[str, Any]:
        return await self._json("POST", f"/v1/policies/{_path(policy_id)}/canary", json={"percentage": percentage, "reason": reason})

    async def shadow_policy(self, policy_id: str, reason: str) -> dict[str, Any]:
        return await self._json("POST", f"/v1/policies/{_path(policy_id)}/shadow", json={"reason": reason})

    async def rollback_policy(self, policy_id: str, reason: str) -> dict[str, Any]:
        return await self._json("POST", f"/v1/policies/{_path(policy_id)}/rollback", json={"reason": reason})

    async def anchor_audit(self, destination: str = "file") -> dict[str, Any]:
        return await self._json("POST", "/v1/audit/anchors", json={"destination": destination})

    async def verify_audit_anchor(self, anchor_id: str) -> dict[str, Any]:
        return await self._json("POST", f"/v1/audit/anchors/{_path(anchor_id)}/verify")

    async def anchor_audit_batch(self, destinations: list[str], *, required_quorum: int = 1) -> dict[str, Any]:
        return await self._json("POST", "/v1/audit/anchors/batch",
                                json={"destinations": destinations, "required_quorum": required_quorum})

    async def audit_anchor_quorum(self, *, sequence: int | None = None,
                                  required_quorum: int | None = None) -> dict[str, Any]:
        params = {k: v for k, v in {"sequence": sequence, "required_quorum": required_quorum}.items()
                  if v is not None}
        return await self._json("GET", "/v1/audit/anchors/quorum", params=params, retryable=True)

    async def write_memory(self, request: dict[str, Any]) -> dict[str, Any]:
        return await self._json("POST", "/v1/memory", json=request)

    async def read_memory(self, memory_id: str, *, include_content: bool = False) -> dict[str, Any]:
        return await self._json("GET", f"/v1/memory/{_path(memory_id)}", params={"include_content": str(include_content).lower()}, retryable=True)

    async def update_memory_status(self, memory_id: str, status: str, reason: str) -> dict[str, Any]:
        return await self._json("POST", f"/v1/memory/{_path(memory_id)}/status", json={"status": status, "reason": reason})

    async def create_delegation(self, request: dict[str, Any]) -> dict[str, Any]:
        return await self._json("POST", "/v1/delegations", json=request)

    async def revoke_delegation(self, grant_id: str, reason: str) -> dict[str, Any]:
        return await self._json("POST", f"/v1/delegations/{_path(grant_id)}/revoke", json={"reason": reason})

    async def create_budget(self, request: dict[str, Any]) -> dict[str, Any]:
        return await self._json("POST", "/v1/budgets", json=request)

    async def reserve_budget(self, budget_id: str, request: dict[str, Any]) -> dict[str, Any]:
        return await self._json("POST", f"/v1/budgets/{_path(budget_id)}/reserve", json=request)

    async def settle_budget(self, reservation_id: str, request: dict[str, Any]) -> dict[str, Any]:
        return await self._json("POST", f"/v1/budget-reservations/{_path(reservation_id)}/settle", json=request)

    async def request_tenant_lifecycle(self, request: dict[str, Any]) -> dict[str, Any]:
        return await self._json("POST", "/v1/tenant/lifecycle", json=request)

    async def get_tenant_lifecycle(self, job_id: str) -> dict[str, Any]:
        return await self._json("GET", f"/v1/tenant/lifecycle/{_path(job_id)}", retryable=True)

    async def download_tenant_export(self, job_id: str) -> bytes:
        return (await self._request("GET", f"/v1/tenant/lifecycle/{_path(job_id)}/content",
                                    retryable=True)).content

    async def reconcile_tenant_lifecycle(self, job_id: str, request: dict[str, Any]) -> dict[str, Any]:
        return await self._json("POST", f"/v1/tenant/lifecycle/{_path(job_id)}/reconcile", json=request)

    async def create_legal_hold(self, request: dict[str, Any]) -> dict[str, Any]:
        return await self._json("POST", "/v1/tenant/legal-holds", json=request)

    async def list_legal_holds(self) -> list[dict[str, Any]]:
        return await self._json("GET", "/v1/tenant/legal-holds", retryable=True)

    async def release_legal_hold(self, hold_id: str, reason: str) -> dict[str, Any]:
        return await self._json("POST", f"/v1/tenant/legal-holds/{_path(hold_id)}/release",
                                json={"reason": reason})

    async def register_protocol(self, request: dict[str, Any]) -> dict[str, Any]:
        return await self._json("POST", "/v1/protocols", json=request)

    async def list_protocol_manifest_versions(self, registration_id: str) -> list[dict[str, Any]]:
        return await self._json("GET", f"/v1/protocols/{_path(registration_id)}/manifest-versions",
                                retryable=True)

    async def authorize_a2a(self, registration_id: str, request: dict[str, Any]) -> dict[str, Any]:
        return await self._json("POST", f"/v1/protocols/a2a/{_path(registration_id)}/authorize", json=request)

    async def call_mcp_tool(self, registration_id: str, request: dict[str, Any]) -> dict[str, Any]:
        return await self._json("POST", f"/v1/protocols/mcp/{_path(registration_id)}/tools/call", json=request)

    async def run_dispatcher(self, *, limit: int = 20) -> dict[str, Any]:
        return await self._json("POST", "/v1/dispatch/run", params={"limit": limit})

    async def _request(
        self,
        method: str,
        path: str,
        *,
        retryable: bool = False,
        **kwargs: Any,
    ) -> httpx.Response:
        response: httpx.Response | None = None
        attempts = self.max_retries + 1 if retryable else 1
        for attempt in range(attempts):
            try:
                response = await self._client.request(method, path, **kwargs)
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout):
                if attempt + 1 >= attempts:
                    raise
                await asyncio.sleep(_retry_delay(None, attempt))
                continue
            if response.status_code not in _RETRYABLE_STATUS_CODES or attempt + 1 >= attempts:
                break
            await asyncio.sleep(_retry_delay(response, attempt))
        if response is None:
            raise RuntimeError("AGENTDANCE request did not produce a response")
        _raise_for_error(response)
        return response

    async def _json(self, method: str, path: str, *, retryable: bool = False, **kwargs: Any) -> Any:
        response = await self._request(method, path, retryable=retryable, **kwargs)
        return response.json()
