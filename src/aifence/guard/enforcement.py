# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import copy
import fnmatch
import re
from typing import Any
from urllib.parse import urlsplit

from .crypto import hash_object

_SECRET_KEY = re.compile(
    r"(?:api[_-]?key|access[_-]?token|refresh[_-]?token|authorization|password|passwd|secret|credential|private[_-]?key|client[_-]?secret)",
    re.IGNORECASE,
)
_SECRET_VALUE_PATTERNS = (
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+\-/]+=*", re.IGNORECASE),
    re.compile(r"\b(?:sk|pk|rk|ghp|github_pat)_[A-Za-z0-9_\-]{12,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----.*?-----END (?:RSA |EC |OPENSSH |)PRIVATE KEY-----", re.DOTALL),
)
_REDACTED = "[REDACTED_BY_AIFENCE]"

# Every baseline policy constraint must be represented here. Unknown constraints fail closed.
_SUPPORTED_CONTROLS = frozenset(
    {
        "approval_id",
        "approved_by_key_id",
        "allowed_destinations",
        "allowed_recipients",
        "allowed_resources",
        "approval_ttl_seconds",
        "bind_amount",
        "buffered_response_required",
        "capability_ttl_seconds",
        "dual_control",
        "isolate_untrusted_content",
        "issue_capability",
        "max_amount_usd",
        "max_capability_uses",
        "max_messages",
        "max_recipients",
        "max_records",
        "max_response_bytes",
        "open_incident",
        "quarantine_artifact",
        "read_only",
        "redact_secrets",
        "required_controls",
        "require_reregistration",
        "retry_after_dependency_recovery",
        "revoke_capabilities",
        "revoke_exposed_credentials",
        "sandbox_required",
        "terminate_descendants",
    }
)


def _redact_string(value: str) -> tuple[str, int]:
    redactions = 0
    result = value
    for pattern in _SECRET_VALUE_PATTERNS:
        result, count = pattern.subn(_REDACTED, result)
        redactions += count
    return result, redactions


def redact_value(value: Any) -> tuple[Any, int]:
    if isinstance(value, dict):
        output: dict[str, Any] = {}
        redactions = 0
        for key, item in value.items():
            if _SECRET_KEY.search(str(key)):
                output[str(key)] = _REDACTED
                redactions += 1
            else:
                output[str(key)], count = redact_value(item)
                redactions += count
        return output, redactions
    if isinstance(value, list):
        output_list: list[Any] = []
        redactions = 0
        for item in value:
            transformed, count = redact_value(item)
            output_list.append(transformed)
            redactions += count
        return output_list, redactions
    if isinstance(value, str):
        return _redact_string(value)
    return value, 0


def _control(
    name: str,
    value: Any,
    *,
    status: str = "applied",
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "type": name,
        "required": True,
        "parameters": {"value": value},
        "status": status,
        "evidence": evidence or {},
    }


def _matches_any(value: str, patterns: list[str]) -> bool:
    candidates = {value}
    parsed = urlsplit(value)
    if parsed.hostname:
        candidates.add(parsed.hostname.lower())
        candidates.add(f"{parsed.hostname.lower()}{parsed.path or '/'}")
    return any(fnmatch.fnmatchcase(candidate, pattern) for candidate in candidates for pattern in patterns)


def _argument_values(arguments: dict[str, Any], key: str) -> list[str]:
    value = arguments.get(key)
    if value is None and isinstance(arguments.get("body"), dict):
        value = arguments["body"].get(key)
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return list(value)
    return ["<invalid>"]


def build_enforcement_plan(
    request_document: dict[str, Any],
    *,
    outcome: str,
    constraints: dict[str, Any],
    runtime_attestation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compile policy constraints into an executable, evidence-bearing plan.

    The compiler is intentionally conservative. A required control that cannot be
    deterministically applied marks the plan non-executable, causing the broker to
    fail closed.
    """

    original_hash = hash_object(request_document)
    transformed_action = copy.deepcopy(request_document.get("action", {}))
    controls: list[dict[str, Any]] = []
    executable = outcome in {"allow", "allow_with_limits", "redact_or_transform"}

    unknown = sorted(set(constraints) - _SUPPORTED_CONTROLS)
    for name in unknown:
        controls.append(
            _control(
                name,
                constraints[name],
                status="failed",
                evidence={"reason": "unsupported_required_control"},
            )
        )
        executable = False

    for name, value in sorted(constraints.items()):
        if name in unknown:
            continue
        if name == "allowed_destinations":
            patterns = list(value)
            destination = (
                request_document.get("security_context", {}).get("network_destination")
                or transformed_action.get("target")
                or ""
            )
            matched = isinstance(destination, str) and bool(destination) and _matches_any(destination, patterns)
            controls.append(
                _control(name, value, status="applied" if matched else "failed", evidence={"destination": destination})
            )
            if not matched:
                executable = False
        elif name == "allowed_resources":
            patterns = list(value)
            resource = transformed_action.get("target") or ""
            matched = isinstance(resource, str) and bool(resource) and _matches_any(resource, patterns)
            controls.append(
                _control(name, value, status="applied" if matched else "failed", evidence={"resource": resource})
            )
            if not matched:
                executable = False
        elif name == "allowed_recipients":
            arguments = transformed_action.get("arguments", {})
            recipients = _argument_values(arguments if isinstance(arguments, dict) else {}, "recipients")
            prohibited = [recipient for recipient in recipients if not _matches_any(recipient, list(value))]
            status = "applied" if recipients and not prohibited else "failed"
            controls.append(
                _control(name, value, status=status, evidence={"recipients": recipients, "prohibited": prohibited})
            )
            if status == "failed":
                executable = False
        elif name == "max_amount_usd":
            amount = transformed_action.get("amount_usd")
            valid = amount is not None and float(amount) <= float(value)
            controls.append(
                _control(name, value, status="applied" if valid else "failed", evidence={"amount_usd": amount})
            )
            if not valid:
                executable = False
        elif name == "max_response_bytes":
            controls.append(_control(name, value, evidence={"effective_limit": int(value)}))
        elif name == "read_only" and bool(value):
            arguments = transformed_action.get("arguments", {})
            method = arguments.get("method") if isinstance(arguments, dict) else None
            operation = str(transformed_action.get("operation", "")).lower()
            read_operations = {"read", "get", "list", "search", "inspect", "head"}
            valid = (
                not bool(transformed_action.get("destructive"))
                and operation in read_operations
                and (method is None or str(method).upper() in {"GET", "HEAD"})
            )
            controls.append(
                _control(name, value, status="applied" if valid else "failed", evidence={"operation": operation, "method": method})
            )
            if not valid:
                executable = False
        elif name == "sandbox_required" and bool(value):
            attestation = runtime_attestation or {}
            verified = attestation.get("sandbox_attestation") == "verified"
            controls.append(
                _control(name, value, status="applied" if verified else "failed", evidence={"attestation": attestation.get("sandbox_attestation")})
            )
            if not verified:
                executable = False
        elif name == "redact_secrets" and bool(value):
            arguments, argument_redactions = redact_value(transformed_action.get("arguments", {}))
            transformed_action["arguments"] = arguments
            controls.append(
                _control(
                    name,
                    value,
                    evidence={"redactions": argument_redactions},
                )
            )
        elif name == "max_records":
            limit = int(value)
            arguments = transformed_action.setdefault("arguments", {})
            if not isinstance(arguments, dict):
                controls.append(
                    _control(name, value, status="failed", evidence={"reason": "arguments_not_object"})
                )
                executable = False
                continue
            # Broker actions wrap HTTP parameters under query/body; direct tool
            # actions use the arguments object itself. Apply the limit at the
            # narrowest executable location so the transformed hash describes
            # exactly what will be dispatched.
            target = arguments
            if isinstance(arguments.get("query"), dict):
                target = arguments["query"]
            elif isinstance(arguments.get("body"), dict):
                target = arguments["body"]
            candidate_keys = ("limit", "page_size", "max_records")
            existing_key = next((key for key in candidate_keys if key in target), None)
            query_target = target is arguments.get("query")
            if existing_key is not None:
                try:
                    requested = int(target[existing_key])
                except (TypeError, ValueError):
                    controls.append(
                        _control(
                            name, value, status="failed",
                            evidence={"reason": f"invalid_{existing_key}"},
                        )
                    )
                    executable = False
                    continue
                bounded = min(requested, limit)
                target[existing_key] = str(bounded) if query_target else bounded
                effective = bounded
            else:
                target["limit"] = str(limit) if query_target else limit
                effective = limit
            controls.append(_control(name, value, evidence={"effective_limit": effective}))
        elif name in {"max_recipients", "max_messages"}:
            arguments = transformed_action.get("arguments", {})
            key = "recipients" if name == "max_recipients" else "messages"
            values = arguments.get(key) if isinstance(arguments, dict) else None
            if values is not None and isinstance(values, list) and len(values) > int(value):
                controls.append(
                    _control(
                        name,
                        value,
                        status="failed",
                        evidence={"observed": len(values), "reason": "limit_exceeded"},
                    )
                )
                executable = False
            else:
                observed = len(values) if isinstance(values, list) else 0
                controls.append(_control(name, value, evidence={"observed": observed}))
        elif name == "bind_amount" and bool(value):
            amount = transformed_action.get("amount_usd")
            if amount is None:
                controls.append(_control(name, value, status="failed", evidence={"reason": "amount_missing"}))
                executable = False
            else:
                controls.append(_control(name, value, evidence={"amount_usd": amount}))
        elif name == "buffered_response_required":
            controls.append(_control(name, value, evidence={"streaming_allowed": not bool(value)}))
        elif name == "isolate_untrusted_content":
            # Isolation is represented as a hard non-executable plan for external effects.
            status = "failed" if bool(value) and transformed_action.get("external_effect") else "not_applicable"
            controls.append(_control(name, value, status=status))
            if status == "failed":
                executable = False
        elif name in {
            "approval_id",
            "approved_by_key_id",
            "approval_ttl_seconds",
            "capability_ttl_seconds",
            "dual_control",
            "issue_capability",
            "max_capability_uses",
        }:
            controls.append(_control(name, value))
        elif name == "required_controls":
            # Resolve after the primary controls are compiled below.
            controls.append(_control(name, value, status="planned"))
        elif name in {
            "open_incident",
            "quarantine_artifact",
            "require_reregistration",
            "retry_after_dependency_recovery",
            "revoke_capabilities",
            "revoke_exposed_credentials",
            "terminate_descendants",
        }:
            controls.append(_control(name, value, status="planned"))

    required = constraints.get("required_controls", [])
    if isinstance(required, list):
        aliases = {"audit": "audit", "redaction": "redact_secrets", "sandbox": "sandbox_required"}
        available = {str(control.get("type")): control for control in controls}
        missing: list[str] = []
        for requested in required:
            control_name = aliases.get(str(requested), str(requested))
            if control_name == "audit":
                if "audit" not in available:
                    audit_control = _control("audit", True, status="planned")
                    controls.append(audit_control)
                    available["audit"] = audit_control
                continue
            control = available.get(control_name)
            if control is None or control.get("status") == "failed":
                missing.append(str(requested))
        for control in controls:
            if control.get("type") == "required_controls":
                control["status"] = "applied" if not missing else "failed"
                control["evidence"] = {"missing": missing}
        if missing:
            executable = False

    transformed_request = copy.deepcopy(request_document)
    transformed_request["action"] = transformed_action
    transformed_hash = hash_object(transformed_request)
    return {
        "version": "aifence.enforcement.v1",
        "original_request_hash": original_hash,
        "transformed_request_hash": transformed_hash,
        "transformed_action": transformed_action,
        "controls": controls,
        "executable": executable,
    }


def mark_control_applied(
    plan: dict[str, Any], control_type: str, evidence: dict[str, Any] | None = None
) -> None:
    for control in plan.get("controls", []):
        if control.get("type") == control_type:
            control["status"] = "applied"
            if evidence:
                control.setdefault("evidence", {}).update(evidence)
