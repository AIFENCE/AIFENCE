# SPDX-License-Identifier: AGPL-3.0-or-later
"""Latency budgets, fail-open/fail-closed paradigms, and breaker tripping."""
from __future__ import annotations

import time

import pytest

from aifence.core.config import CoreSettings
from aifence.resilience import BreakerPolicy, CircuitBreaker, TierUnavailable

CLOSED = BreakerPolicy(timeout_seconds=0.5, failure_threshold=2, recovery_seconds=0.2)
OPEN = BreakerPolicy(
    timeout_seconds=0.5, failure_threshold=2, recovery_seconds=0.2, paradigm="fail_open"
)


def _boom() -> str:
    raise RuntimeError("tier exploded")


def _hang() -> str:
    time.sleep(5)
    return "never"


# --- happy path ---

def test_successful_call_returns_the_value() -> None:
    breaker = CircuitBreaker("quality", CLOSED)
    outcome = breaker.call(lambda: "verdict")
    assert outcome.ok is True
    assert outcome.value == "verdict"
    assert outcome.state == "closed"
    breaker.close()


# --- fail closed: the safe default ---

def test_fail_closed_raises_on_error() -> None:
    breaker = CircuitBreaker("guard", CLOSED)
    with pytest.raises(TierUnavailable) as excinfo:
        breaker.call(_boom)
    assert excinfo.value.tier == "guard"
    assert excinfo.value.reason == "error"
    breaker.close()


def test_fail_closed_raises_on_timeout() -> None:
    breaker = CircuitBreaker("guard", BreakerPolicy(timeout_seconds=0.05, failure_threshold=2))
    with pytest.raises(TierUnavailable) as excinfo:
        breaker.call(_hang)
    assert excinfo.value.reason == "timeout"
    breaker.close()


# --- fail open: explicit opt-in ---

def test_fail_open_degrades_instead_of_raising() -> None:
    breaker = CircuitBreaker("quality", OPEN)
    outcome = breaker.call(_boom)
    assert outcome.ok is False
    assert outcome.degraded is True
    assert outcome.value is None
    assert outcome.reason == "error"
    breaker.close()


def test_fail_open_degrades_on_timeout() -> None:
    breaker = CircuitBreaker(
        "quality",
        BreakerPolicy(timeout_seconds=0.05, failure_threshold=2, paradigm="fail_open"),
    )
    outcome = breaker.call(_hang)
    assert outcome.ok is False
    assert outcome.reason == "timeout"
    breaker.close()


# --- tripping and recovery ---

def test_breaker_trips_after_threshold_and_short_circuits() -> None:
    breaker = CircuitBreaker("quality", OPEN)
    for _ in range(2):
        breaker.call(_boom)
    assert breaker.state == "open"

    # Once open the tier is not called at all: the outcome is immediate.
    called = False

    def _tier() -> str:
        nonlocal called
        called = True
        return "value"

    outcome = breaker.call(_tier)
    assert outcome.reason == "open"
    assert called is False, "an open breaker must not invoke the tier"
    breaker.close()


def test_breaker_probes_again_after_the_recovery_window() -> None:
    breaker = CircuitBreaker("quality", OPEN)
    for _ in range(2):
        breaker.call(_boom)
    assert breaker.state == "open"

    time.sleep(0.25)  # exceeds recovery_seconds
    assert breaker.state == "half_open"
    outcome = breaker.call(lambda: "recovered")
    assert outcome.ok is True
    assert breaker.state == "closed", "a success must reset the breaker"
    breaker.close()


def test_success_resets_the_failure_count() -> None:
    breaker = CircuitBreaker("quality", OPEN)
    breaker.call(_boom)
    breaker.call(lambda: "ok")
    breaker.call(_boom)
    assert breaker.state == "closed", "one isolated failure must not trip the breaker"
    breaker.close()


# --- configuration guards ---

def test_guard_tier_cannot_be_configured_to_fail_open() -> None:
    with pytest.raises(ValueError, match="may only contain"):
        CoreSettings(flow_fail_open_tiers=("guard",)).validate()


def test_quality_and_bus_may_fail_open() -> None:
    CoreSettings(flow_fail_open_tiers=("quality", "bus")).validate()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"flow_quality_timeout_seconds": 0},
        {"flow_failure_threshold": 0},
        {"flow_recovery_seconds": -1},
    ],
)
def test_invalid_breaker_settings_are_rejected(kwargs: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        CoreSettings(**kwargs).validate()  # type: ignore[arg-type]
