# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
from typing import Any

import httpx

from .errors import ConflictError, DependencyUnavailableError
from .network import ValidatedEndpoint, pin_validated_target


def discover_protocol_manifest(*, protocol: str, endpoint: str, auth_header_name: str | None,
                               auth_value: str | None, proxy_url: str,
                               max_response_bytes: int,
                               validated_endpoint: ValidatedEndpoint | None = None
                               ) -> tuple[dict[str, Any], str, dict[str, Any]]:
    headers = {"Accept": "application/json", "User-Agent": "AGENTDANCE-Protocol-Discovery/1.0.0-rc.5"}
    if auth_header_name and auth_value:
        headers[auth_header_name] = auth_value
    if protocol == "mcp":
        target = endpoint
    elif protocol == "a2a":
        target = endpoint.rstrip("/") + "/.well-known/agent-card.json"
    else:
        raise ConflictError("unsupported agent protocol")
    request_extensions: dict[str, str] = {}
    if validated_endpoint is not None:
        target, host_header, request_extensions = pin_validated_target(target, validated_endpoint)
        headers["Host"] = host_header
    try:
        with httpx.Client(timeout=30, verify=True, follow_redirects=False, trust_env=False,
                          proxy=proxy_url or None) as client:
            if protocol == "mcp":
                response = client.post(target, headers={**headers, "Content-Type": "application/json"},
                    json={"jsonrpc": "2.0", "id": "agentdance-discovery", "method": "tools/list", "params": {}},
                    extensions=request_extensions)
            else:
                response = client.get(target, headers=headers, extensions=request_extensions)
            response.raise_for_status()
            if len(response.content) > max_response_bytes:
                raise ConflictError("protocol manifest response exceeds the configured limit")
            document = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise DependencyUnavailableError("protocol manifest discovery failed") from exc
    if not isinstance(document, dict):
        raise ConflictError("protocol manifest discovery returned a non-object")
    if protocol == "mcp":
        result = document.get("result")
        if not isinstance(result, dict) or not isinstance(result.get("tools"), list):
            raise ConflictError("MCP tools/list response is invalid")
        tools: list[dict[str, Any]] = []
        for item in result["tools"]:
            if not isinstance(item, dict) or not isinstance(item.get("name"), str):
                raise ConflictError("MCP tool descriptor is invalid")
            descriptor = {
                "name": item["name"],
                "description": str(item.get("description", ""))[:4096],
                "inputSchema": item.get("inputSchema", {"type": "object"}),
            }
            tools.append(descriptor)
        protocol_version = str(response.headers.get("MCP-Protocol-Version", "2025-06-18"))
        manifest = {"protocol": "mcp", "protocolVersion": protocol_version, "tools": tools}
    else:
        protocol_version = str(document.get("protocolVersion", document.get("version", "0.3")))
        manifest = document
    verification = {
        "source": "native-discovery",
        "http_status": response.status_code,
        "content_type": response.headers.get("content-type", ""),
        "content_length": len(response.content),
        "canonical_json_bytes": len(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()),
    }
    return manifest, protocol_version, verification
