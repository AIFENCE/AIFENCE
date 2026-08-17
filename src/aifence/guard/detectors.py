# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import math
import re
from collections.abc import Iterable
from urllib.parse import urlparse

from .content_classes import classify_all
from .models import Agent
from .schemas import DecisionRequest, Finding

_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("aws_access_key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("github_token", re.compile(r"\b(?:ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{20,}\b")),
    ("generic_bearer", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{24,}\b", re.IGNORECASE)),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")),
    ("connection_string", re.compile(r"\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?)://[^\s]+", re.IGNORECASE)),
)

_PROMPT_INJECTION = (
    re.compile(r"\bignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions\b", re.IGNORECASE),
    re.compile(r"\breveal\s+(?:the\s+)?(?:system|developer)\s+(?:prompt|message|instructions)\b", re.IGNORECASE),
    re.compile(r"\bdisable\s+(?:security|monitoring|logging|policy|guardrails?)\b", re.IGNORECASE),
    re.compile(r"\bdo\s+not\s+(?:log|record|report|mention)\b", re.IGNORECASE),
    re.compile(r"\bact\s+as\s+root\b", re.IGNORECASE),
    re.compile(r"\boverride\s+(?:authorization|policy|safety|permissions?)\b", re.IGNORECASE),
)

_CONTROL_EVASION = (
    re.compile(r"\b(?:delete|truncate|alter)\b.{0,60}\b(?:audit|logs?|telemetry|events?)\b", re.IGNORECASE),
    re.compile(r"\b(?:bypass|evade|disable)\b.{0,60}\b(?:agentdance|monitor|policy|security)\b", re.IGNORECASE),
    re.compile(r"\bunset\b.{0,40}\b(?:OTEL|AUDIT|LOG)\b", re.IGNORECASE),
)

_DANGEROUS_COMMANDS = (
    re.compile(r"(?:^|\s)rm\s+-rf\s+(?:/|\*)", re.IGNORECASE),
    re.compile(r"\bmkfs(?:\.|\s)", re.IGNORECASE),
    re.compile(r"\bdd\s+if=.*\s+of=/dev/", re.IGNORECASE),
    re.compile(r"\bchmod\s+-R\s+777\b", re.IGNORECASE),
    re.compile(r"\bcurl\b.+\|\s*(?:sh|bash|zsh)\b", re.IGNORECASE),
    re.compile(r"\bwget\b.+\|\s*(?:sh|bash|zsh)\b", re.IGNORECASE),
    re.compile(r"\b(?:nc|netcat)\b.+\s-e\s", re.IGNORECASE),
    re.compile(r"\bpython\w*\s+-c\s+.+(?:socket|subprocess|base64)", re.IGNORECASE),
)

_SENSITIVE_CLASSES = {"secret", "credential", "authentication", "financial", "health", "biometric", "government_id"}


def _finding(
    detector: str,
    category: str,
    severity: str,
    confidence: float,
    evidence: str,
    **attributes: object,
) -> Finding:
    return Finding(
        detector=detector,
        category=category,
        severity=severity,  # type: ignore[arg-type]
        confidence=confidence,
        evidence=evidence[:2048],
        attributes=attributes,
    )


def run_detectors(request: DecisionRequest, registered_agent: Agent | None) -> list[Finding]:
    findings: list[Finding] = []
    text_parts = [request.objective.declared_goal]
    if request.security_context.content:
        text_parts.append(request.security_context.content)
    text_parts.extend(_flatten_strings(request.action.arguments))
    combined = "\n".join(text_parts)

    for secret_type, pattern in _SECRET_PATTERNS:
        if pattern.search(combined):
            findings.append(
                _finding(
                    "secret-detector",
                    "data.secret_exposure",
                    "critical",
                    0.98,
                    f"Content matched a {secret_type} credential pattern",
                    secret_type=secret_type,
                )
            )

    for pattern in _PROMPT_INJECTION:
        match = pattern.search(combined)
        if match:
            findings.append(
                _finding(
                    "prompt-injection-detector",
                    "prompt_injection.detected",
                    "high",
                    0.90,
                    f"Untrusted instruction pattern detected: {match.group(0)}",
                )
            )
            break

    for pattern in _CONTROL_EVASION:
        match = pattern.search(combined)
        if match:
            findings.append(
                _finding(
                    "control-evasion-detector",
                    "integrity.control_evasion",
                    "critical",
                    0.96,
                    f"Security control evasion pattern detected: {match.group(0)}",
                )
            )
            break

    if request.action.type in {"shell.execute", "code.execute", "process.spawn"}:
        for pattern in _DANGEROUS_COMMANDS:
            match = pattern.search(combined)
            if match:
                findings.append(
                    _finding(
                        "command-risk-detector",
                        "execution.dangerous_command",
                        "critical",
                        0.97,
                        f"Dangerous command pattern detected: {match.group(0)}",
                    )
                )
                break

    if registered_agent is None:
        findings.append(
            _finding(
                "agent-registry",
                "authorization.agent_unregistered",
                "critical",
                1.0,
                "The agent identity is not registered for this tenant",
            )
        )
    else:
        if registered_agent.status != "active":
            findings.append(
                _finding(
                    "agent-registry",
                    "authorization.agent_disabled",
                    "critical",
                    1.0,
                    "The registered agent is not active",
                )
            )
        if request.agent.instruction_hash != registered_agent.instruction_hash:
            findings.append(
                _finding(
                    "agent-integrity",
                    "integrity.instruction_drift",
                    "high",
                    1.0,
                    "The instruction hash differs from the registered agent version",
                )
            )
        if request.agent.version != registered_agent.version:
            findings.append(
                _finding(
                    "agent-integrity",
                    "integrity.version_drift",
                    "high",
                    1.0,
                    "The running agent version differs from the registered version",
                )
            )
        if request.action.tool and not _allowed(request.action.tool, registered_agent.allowed_tools):
            findings.append(
                _finding(
                    "tool-authorization",
                    "authorization.tool_not_allowed",
                    "critical",
                    1.0,
                    f"Tool {request.action.tool} is not in the agent allowlist",
                )
            )
        disallowed_data = set(request.security_context.data_classes) - set(
            registered_agent.allowed_data_classes
        )
        if disallowed_data:
            findings.append(
                _finding(
                    "data-authorization",
                    "authorization.scope_violation",
                    "critical",
                    1.0,
                    "The action requests data classes outside the registered scope",
                    data_classes=sorted(disallowed_data),
                )
            )

    target = request.action.target or ""
    approved = request.objective.approved_scope
    if target and approved and not _allowed(target, approved):
        findings.append(
            _finding(
                "objective-scope-detector",
                "authorization.scope_violation",
                "critical",
                0.99,
                f"Target {target} is outside the approved objective scope",
            )
        )

    # Data classes are caller-declared, so classify the payload itself: an agent
    # that under-declares must not thereby escape the exfiltration rules.
    observed_counts = classify_all(
        [request.security_context.content or "", *_flatten_strings(request.action.arguments)]
    )
    observed = set(observed_counts)
    undeclared = (observed & _SENSITIVE_CLASSES) - set(request.security_context.data_classes)
    if undeclared:
        findings.append(
            _finding(
                "content-classifier",
                "data.undeclared_sensitive",
                "high",
                0.9,
                "Content contains sensitive data classes the caller did not declare",
                # Counts only: the matched values are the sensitive data.
                data_classes=sorted(undeclared),
                observed_counts={k: observed_counts[k] for k in sorted(undeclared)},
            )
        )
    if observed & {"credential", "secret"}:
        findings.append(
            _finding(
                "content-classifier",
                "data.secret_exposure",
                "critical",
                0.93,
                "Credential or private key material was detected in the request content",
                data_classes=sorted(observed & {"credential", "secret"}),
            )
        )

    destination = request.security_context.network_destination
    declared = set(request.security_context.data_classes)
    sensitive = (declared | observed) & _SENSITIVE_CLASSES
    if destination and sensitive and not _is_private_destination(destination):
        findings.append(
            _finding(
                "exfiltration-detector",
                "data.exfiltration",
                "critical",
                0.94,
                "Sensitive data is being sent to a non-private destination",
                data_classes=sorted(sensitive),
                destination=destination,
            )
        )

    claim = (request.security_context.agent_claim or "").lower()
    facts = " ".join(request.security_context.observed_facts).lower()
    if claim and facts:
        denial_markers = ("did not", "never", "no ", "without accessing", "nothing was")
        action_markers = ("accessed", "executed", "sent", "deleted", "modified", "downloaded")
        if any(marker in claim for marker in denial_markers) and any(
            marker in facts for marker in action_markers
        ):
            findings.append(
                _finding(
                    "claim-action-consistency",
                    "deception.material_misrepresentation",
                    "high",
                    0.88,
                    "The agent claim materially conflicts with observed execution facts",
                )
            )

    evaluation_text = combined.lower()
    evaluation_patterns = (
        "edit the tests instead",
        "change the evaluator",
        "modify the benchmark",
        "mark the task as passed",
        "fake the test result",
        "bypass the grader",
    )
    if any(pattern in evaluation_text for pattern in evaluation_patterns):
        findings.append(
            _finding(
                "anti-cheat-detector",
                "cheat.evaluation_tampering",
                "critical",
                0.95,
                "The requested action attempts to alter evaluation rather than satisfy the objective",
            )
        )

    success_markers = ("completed", "succeeded", "passed", "finished successfully")
    failure_markers = ("failed", "error", "not executed", "timed out", "permission denied")
    if claim and facts and any(x in claim for x in success_markers) and any(x in facts for x in failure_markers):
        findings.append(
            _finding(
                "anti-cheat-detector",
                "cheat.fabricated_completion",
                "high",
                0.93,
                "The agent claimed successful completion despite observed failure evidence",
            )
        )

    if request.objective.delegation_depth > 4:
        findings.append(
            _finding(
                "delegation-depth-detector",
                "delegation.excessive_depth",
                "medium",
                min(0.99, 0.7 + request.objective.delegation_depth * 0.03),
                "The delegation chain is deeper than the baseline trust boundary",
            )
        )

    return _deduplicate(findings)


def calculate_risk(request: DecisionRequest, findings: list[Finding]) -> int:
    weights = {"info": 1, "low": 8, "medium": 22, "high": 45, "critical": 75}
    residual = 1.0
    for finding in findings:
        normalized = weights[finding.severity] / 100.0 * finding.confidence
        residual *= max(0.0, 1.0 - normalized)
    score = (1.0 - residual) * 100
    if request.action.destructive:
        score += 18
    if request.action.external_effect:
        score += 8
    if not request.action.reversible:
        score += 12
    if request.security_context.environment == "production":
        score += 5
    if request.action.amount_usd:
        score += min(15, 3 * math.log10(request.action.amount_usd + 1))
    if request.objective.delegation_depth:
        score += min(10, request.objective.delegation_depth * 1.5)
    return max(0, min(100, int(round(score))))


def _flatten_strings(value: object) -> list[str]:
    result: list[str] = []
    if isinstance(value, str):
        result.append(value)
    elif isinstance(value, dict):
        for key, item in value.items():
            result.append(str(key))
            result.extend(_flatten_strings(item))
    elif isinstance(value, list):
        for item in value:
            result.extend(_flatten_strings(item))
    return result


def _allowed(value: str, patterns: Iterable[str]) -> bool:
    import fnmatch

    return any(fnmatch.fnmatchcase(value.lower(), pattern.lower()) for pattern in patterns)


def _is_private_destination(destination: str) -> bool:
    parsed = urlparse(destination if "://" in destination else f"https://{destination}")
    host = (parsed.hostname or "").lower()
    if host in {"localhost", "127.0.0.1", "::1"}:
        return True
    if host.endswith((".internal", ".local", ".svc", ".cluster.local")):
        return True
    if host.startswith(("10.", "192.168.")):
        return True
    if host.startswith("172."):
        try:
            second = int(host.split(".")[1])
            return 16 <= second <= 31
        except (ValueError, IndexError):
            return False
    return False


def _deduplicate(findings: list[Finding]) -> list[Finding]:
    seen: set[tuple[str, str]] = set()
    result: list[Finding] = []
    for finding in findings:
        key = (finding.category, finding.evidence)
        if key not in seen:
            seen.add(key)
            result.append(finding)
    return result
