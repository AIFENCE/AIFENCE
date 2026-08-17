# SPDX-License-Identifier: AGPL-3.0-or-later
"""Latency budgets and circuit breakers for the fence tiers.

Each tier of the fence can be slow or unavailable, and the right response is not
the same for all of them:

* **Fail closed** — if the tier cannot render a verdict, refuse the request. This
  is the only safe default for enforcement: an unavailable guard must never become
  an open door.
* **Fail open** — if the tier cannot render a verdict, continue without it. This
  is a legitimate choice for advisory tiers where availability outweighs the
  signal, and it is always an explicit opt-in.

A tier that keeps failing is *tripped*: the breaker stops calling it for a
recovery window and applies the configured paradigm immediately, so one sick
dependency cannot consume the latency budget of every subsequent request.
"""
from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from dataclasses import dataclass
from typing import Literal

_logger = logging.getLogger(__name__)

Paradigm = Literal["fail_open", "fail_closed"]
BreakerState = Literal["closed", "open", "half_open"]


class TierUnavailable(Exception):
    """A tier could not produce a verdict and its paradigm is fail-closed."""

    def __init__(self, tier: str, reason: str) -> None:
        super().__init__(f"{tier} tier unavailable: {reason}")
        self.tier = tier
        self.reason = reason


@dataclass(frozen=True)
class BreakerPolicy:
    """How one tier behaves under latency and failure."""

    timeout_seconds: float = 5.0
    #: Consecutive failures before the breaker trips open.
    failure_threshold: int = 5
    #: How long the breaker stays open before probing the tier again.
    recovery_seconds: float = 30.0
    paradigm: Paradigm = "fail_closed"

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.failure_threshold < 1:
            raise ValueError("failure_threshold must be at least 1")
        if self.recovery_seconds < 0:
            raise ValueError("recovery_seconds cannot be negative")


@dataclass
class TierOutcome[T]:
    """The result of calling a tier through its breaker."""

    value: T | None
    ok: bool
    state: BreakerState
    #: Set when the tier did not produce a value: "timeout", "error", or "open".
    reason: str | None = None
    elapsed_ms: float = 0.0

    @property
    def degraded(self) -> bool:
        """True when the tier was skipped or failed and the flow continued."""
        return not self.ok


class CircuitBreaker:
    """A per-tier circuit breaker with a latency budget.

    Thread-safe: the composed application serves requests from a thread pool, so
    breaker state is shared and guarded by a lock.
    """

    def __init__(self, tier: str, policy: BreakerPolicy | None = None) -> None:
        self.tier = tier
        self.policy = policy or BreakerPolicy()
        self._lock = threading.Lock()
        self._failures = 0
        self._opened_at: float | None = None
        # A dedicated worker so a hung tier cannot occupy the request thread.
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix=f"fence-{tier}")

    @property
    def state(self) -> BreakerState:
        with self._lock:
            return self._state_locked()

    def _state_locked(self) -> BreakerState:
        if self._opened_at is None:
            return "closed"
        if (time.monotonic() - self._opened_at) >= self.policy.recovery_seconds:
            return "half_open"
        return "open"

    def _record_success(self) -> None:
        with self._lock:
            self._failures = 0
            self._opened_at = None

    def _record_failure(self) -> None:
        with self._lock:
            self._failures += 1
            if self._failures >= self.policy.failure_threshold and self._opened_at is None:
                self._opened_at = time.monotonic()
                _logger.warning(
                    "circuit breaker opened for the %s tier after %d consecutive failures",
                    self.tier,
                    self._failures,
                )

    def call[T](self, operation: Callable[[], T]) -> TierOutcome[T]:
        """Run ``operation`` under the tier's latency budget and breaker state.

        Returns a :class:`TierOutcome`; raises :class:`TierUnavailable` only when
        the tier fails and its paradigm is fail-closed.
        """
        with self._lock:
            state = self._state_locked()
            if state == "open":
                return self._degrade("open", state, 0.0)

        started = time.monotonic()
        future = self._executor.submit(operation)
        try:
            value = future.result(timeout=self.policy.timeout_seconds)
        except FutureTimeout:
            future.cancel()
            self._record_failure()
            return self._degrade("timeout", self.state, (time.monotonic() - started) * 1000)
        except Exception as exc:
            self._record_failure()
            _logger.exception("%s tier raised", self.tier, exc_info=exc)
            return self._degrade("error", self.state, (time.monotonic() - started) * 1000)
        self._record_success()
        return TierOutcome(
            value=value, ok=True, state="closed", elapsed_ms=(time.monotonic() - started) * 1000
        )

    def _degrade[T](self, reason: str, state: BreakerState, elapsed_ms: float) -> TierOutcome[T]:
        if self.policy.paradigm == "fail_closed":
            raise TierUnavailable(self.tier, reason)
        _logger.warning("%s tier degraded (%s); failing open by policy", self.tier, reason)
        return TierOutcome(value=None, ok=False, state=state, reason=reason, elapsed_ms=elapsed_ms)

    def close(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)
