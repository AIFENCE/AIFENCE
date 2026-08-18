# SPDX-License-Identifier: AGPL-3.0-or-later
"""The shipped policy profiles, and the cost of choosing one.

The strict baseline holds most production writes. The balanced profile trades
that friction for one detection the fence never actually perceived. These tests
pin the trade so it cannot drift silently in either direction.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from aifence.guard.policy import PolicyEngine, load_baseline_policy
from aifence.redteam import evaluate_corpus, load_corpus

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "src" / "aifence" / "guard" / "baseline_policy.json"
PROFILES = ROOT / "policies"


def _rules(path: Path) -> dict[str, dict]:
    document = json.loads(path.read_text(encoding="utf-8"))
    return {rule["id"]: rule for rule in document["rules"]}


@pytest.fixture(scope="module")
def traces():
    return load_corpus()


@pytest.fixture(scope="module")
def strict(traces):
    return evaluate_corpus(traces, behavioral=True, policy=str(PROFILES / "strict.json"))


@pytest.fixture(scope="module")
def balanced(traces):
    return evaluate_corpus(traces, behavioral=True, policy=str(PROFILES / "balanced.json"))


# --- a profile may only add allowances, never remove protections ---

@pytest.mark.parametrize("profile", ["strict.json", "balanced.json"])
def test_profile_validates(profile: str) -> None:
    PolicyEngine(load_baseline_policy(str(PROFILES / profile)))


@pytest.mark.parametrize("profile", ["strict.json", "balanced.json"])
def test_profile_preserves_every_baseline_rule(profile: str) -> None:
    baseline = _rules(BASELINE)
    shipped = _rules(PROFILES / profile)
    missing = set(baseline) - set(shipped)
    assert not missing, f"{profile} drops baseline rules: {sorted(missing)}"
    for rule_id, rule in baseline.items():
        assert shipped[rule_id]["effect"] == rule["effect"], (
            f"{profile} weakens baseline rule {rule_id}"
        )


def test_balanced_only_adds_allow_rules() -> None:
    added = set(_rules(PROFILES / "balanced.json")) - set(_rules(BASELINE))
    shipped = _rules(PROFILES / "balanced.json")
    assert added
    for rule_id in added:
        assert shipped[rule_id]["effect"]["outcome"] in {"allow", "allow_with_limits"}


def test_balanced_rules_are_risk_bounded() -> None:
    """An unbounded allowance would survive any finding; every rule must cap risk."""
    added = set(_rules(PROFILES / "balanced.json")) - set(_rules(BASELINE))
    shipped = _rules(PROFILES / "balanced.json")
    for rule_id in added:
        assert "max_risk" in shipped[rule_id]["match"], f"{rule_id} has no risk bound"


# --- the measured trade ---

def test_neither_profile_refuses_benign_work(strict, balanced) -> None:
    assert strict.false_positive_rate == 0.0
    assert balanced.false_positive_rate == 0.0


def test_balanced_substantially_reduces_approval_friction(strict, balanced) -> None:
    assert balanced.hold_rate < strict.hold_rate / 2, (
        f"balanced profile is not worth its cost: {balanced.hold_rate}% vs {strict.hold_rate}%"
    )


def test_balanced_costs_no_perceived_detection(strict, balanced) -> None:
    """The whole justification: it gives up nothing a detector actually caught."""
    assert balanced.specific_detection_rate >= strict.specific_detection_rate


def test_balanced_loses_only_default_hold_catches(strict, balanced) -> None:
    lost = {r.trace.id for r in balanced.bypasses} - {r.trace.id for r in strict.bypasses}
    only_default = {r.trace.id for r in strict.default_only}
    assert lost <= only_default, (
        f"balanced profile loses genuinely detected attacks: {sorted(lost - only_default)}"
    )


def test_strict_profile_matches_the_baseline_exactly(strict, traces) -> None:
    baseline = evaluate_corpus(traces, behavioral=True)
    assert strict.detection_rate == baseline.detection_rate
    assert strict.hold_rate == baseline.hold_rate
