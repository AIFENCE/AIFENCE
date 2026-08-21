# SPDX-License-Identifier: AGPL-3.0-or-later
"""Behavioural analysis across the quality, guard and bus tiers.

Each tier judges a single action in isolation. The quality tier asks whether an
artifact is sound; the guard tier asks whether an action is permitted. Neither
asks whether an agent is *becoming* less trustworthy.

Because all three tiers observe the same agent, the fence can watch a
trajectory — output degrading, intent escalating, untrusted input reaching an
effect — and act on a pattern that is invisible in any one request.

The signals here are deliberately few. Each one is validated against the
adversarial evaluation suite and must close a real detection gap without
blocking legitimate work. A behavioural signal that fires on intuition rather
than evidence is worse than none, because it spends operator trust on noise.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from .guard.schemas import Finding

#: Mirrors guard's closed severity vocabulary so findings type-check.
Severity = Literal["info", "low", "medium", "high", "critical"]

#: Repeated grounding lapses before the pattern is reported. One unsourced
#: figure is a drafting slip; a run of them is an agent asserting things its
#: sources do not support, which no single turn's threshold will ever catch.
GROUNDING_LAPSE_THRESHOLD = 2

#: Operations ordered by the damage they can do, used to detect escalation.
_OPERATION_SEVERITY = {
    "read": 0, "get": 0, "list": 0, "search": 0, "inspect": 0,
    "write": 1, "update": 1,
    "send": 2, "export": 2, "invoke": 2,
    "delete": 3, "purge": 3,
}


def _finding(
    detector: str, category: str, severity: Severity, confidence: float, evidence: str,
    **attributes: Any,
) -> Finding:
    from .guard.schemas import Finding

    return Finding(
        detector=detector,
        category=category,
        severity=severity,
        confidence=confidence,
        evidence=evidence,
        attributes=attributes,
    )


@dataclass
class ObservationWindow:
    """What one agent has done so far in a run.

    Cross-tier signals are properties of a *trajectory*, so they need somewhere
    to accumulate. This is that surface, and it is deliberately small: only the
    features a signal actually consumes are retained, never content.
    """

    quality_scores: list[int] = field(default_factory=list)
    operations: list[str] = field(default_factory=list)
    targets: list[str] = field(default_factory=list)
    destinations: list[str] = field(default_factory=list)
    observed_classes: set[str] = field(default_factory=set)
    #: Turns whose grounding check was worse than "pass". A single one is
    #: tolerable; a run of them is an agent persistently asserting figures its
    #: sources do not support.
    grounding_lapses: int = 0
    #: Untrusted external sources this agent has ingested content from. Anything
    #: it does afterwards is potentially acting on that content.
    untrusted_sources: list[str] = field(default_factory=list)
    turns_seen: int = 0

    def record(
        self,
        *,
        operation: str,
        target: str | None,
        destination: str | None,
        quality: dict[str, Any],
        observed: set[str],
        ingested_untrusted: str | None = None,
    ) -> None:
        self.turns_seen += 1
        self.quality_scores.append(int(quality.get("score", 0)))
        self.operations.append(operation)
        if target:
            self.targets.append(target)
        if destination:
            self.destinations.append(destination)
        self.observed_classes |= observed
        if ingested_untrusted:
            self.untrusted_sources.append(ingested_untrusted)
        for check in quality.get("checks", []):
            if check.get("check") == "grounding" and check.get("status") in {"warn", "fail"}:
                self.grounding_lapses += 1


#: Operations that change state somewhere outside the agent.
STATE_CHANGING = frozenset({"write", "update", "send", "export", "delete", "purge"})


def untrusted_source(operation: str, target: str | None, has_content: bool) -> str | None:
    """The external origin this turn ingested content from, if any.

    Content retrieved from a public address is attacker-controllable: it is data,
    never instructions. Recording where it came from is what lets a later action
    be recognised as acting on it.
    """
    from .guard.detectors import _is_private_destination

    if operation in STATE_CHANGING or not has_content:
        return None
    if not target or not target.startswith(("http://", "https://")):
        return None
    return None if _is_private_destination(target) else target


def behavioral_findings(
    *,
    operation: str,
    quality: dict[str, Any],
    window: ObservationWindow,
) -> list[Finding]:
    """Findings derived from the agent's history rather than this turn alone.

    ``window`` holds every prior turn; the current turn's quality result is
    passed separately because it has not been recorded yet.
    """
    findings: list[Finding] = []

    # --- signal: persistent ungrounded assertion ------------------------------
    # Counts this turn alongside the history, so a run of individually tolerable
    # warnings is caught at the turn that completes the pattern.
    current_lapse = any(
        check.get("check") == "grounding" and check.get("status") in {"warn", "fail"}
        for check in quality.get("checks", [])
    )
    lapses = window.grounding_lapses + (1 if current_lapse else 0)
    if lapses >= GROUNDING_LAPSE_THRESHOLD:
        findings.append(
            _finding(
                "behaviour-quality-trajectory",
                "integrity.behavioral_drift",
                "high",
                0.85,
                (
                    f"The agent has made unsupported numeric claims on {lapses} turns; "
                    "no single turn crossed the grounding threshold"
                ),
                signal="grounding_lapses",
                lapses=lapses,
                turns_seen=window.turns_seen + 1,
            )
        )

    # --- signal: intent escalation --------------------------------------------
    # Fires only on a *sustained* rise in operation severity, so a task that
    # legitimately reads for a while and then writes once does not trip it.
    history = [_OPERATION_SEVERITY.get(op, 1) for op in window.operations]
    current = _OPERATION_SEVERITY.get(operation, 1)
    if len(history) >= 2:
        baseline = max(history[:-1])
        if current >= 2 and current > baseline and history[-1] > min(history):
            findings.append(
                _finding(
                    "behaviour-intent-escalation",
                    "integrity.behavioral_drift",
                    "medium",
                    0.7,
                    (
                        f"Operation severity has risen across the run "
                        f"({'→'.join(window.operations[-3:])}→{operation})"
                    ),
                    signal="intent_escalation",
                    operations=[*window.operations[-3:], operation],
                )
            )

    # --- signal: untrusted content influencing a state change -----------------
    # The indirect prompt-injection shape: the agent retrieves attacker-
    # controllable content, then changes state. Neither turn is remarkable
    # alone, and the injected text need contain no keyword a matcher would
    # recognise — only the *flow* from untrusted input to effect gives it away.
    if operation in STATE_CHANGING and window.untrusted_sources:
        findings.append(
            _finding(
                "behaviour-untrusted-influence",
                "integrity.untrusted_influence",
                "high",
                0.8,
                (
                    "The agent changed state after ingesting untrusted external "
                    f"content from {window.untrusted_sources[-1]}"
                ),
                signal="untrusted_influence",
                operation=operation,
                sources=window.untrusted_sources[-3:],
            )
        )

    return findings


class AgentWindows:
    """Per-agent observation windows for the live request path.

    Cross-tier signals need an agent's recent history, so the fence keeps a
    bounded window per agent identity, expired by idle time.

    **Scope:** this store is per process. With multiple replicas an agent's turns
    may land on different instances and each will see only part of the
    trajectory, which weakens — never falsifies — a signal: a partial history
    produces fewer findings, not wrong ones. A shared store is the correct fix
    for multi-replica deployments and is deliberately left as follow-up rather
    than faked here.
    """

    def __init__(self, *, ttl_seconds: float = 3600.0, max_agents: int = 10_000) -> None:
        self._ttl = ttl_seconds
        self._max = max_agents
        self._windows: dict[str, tuple[float, ObservationWindow]] = {}
        self._lock = threading.Lock()

    def get(self, agent_key: str) -> ObservationWindow:
        now = time.monotonic()
        with self._lock:
            self._expire(now)
            entry = self._windows.get(agent_key)
            window = entry[1] if entry else ObservationWindow()
            self._windows[agent_key] = (now, window)
            if len(self._windows) > self._max:
                # Evict the least recently used rather than growing without bound.
                oldest = min(self._windows, key=lambda k: self._windows[k][0])
                del self._windows[oldest]
            return window

    def _expire(self, now: float) -> None:
        stale = [k for k, (seen, _) in self._windows.items() if now - seen >= self._ttl]
        for key in stale:
            del self._windows[key]

    def clear(self) -> None:
        with self._lock:
            self._windows.clear()
