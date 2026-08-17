# SPDX-License-Identifier: AGPL-3.0-or-later
"""JSON validity, schema conformance, and grounding checks in the quality gate."""
from __future__ import annotations

import pytest

from aifence.quality.gate import QualityGate

SOURCES = ["Q3 revenue was 4.2 million dollars, up 12 percent, across 1500 accounts."]
GROUNDED = (
    "Revenue reached 4.2 million, a 12 percent rise over 1500 accounts, a strong "
    "quarter for the whole team."
)
FABRICATED = (
    "Revenue reached 9.9 million, up 87 percent, across 4200 accounts and 350 new "
    "logos in the period overall."
)
SCHEMA = {
    "type": "object",
    "required": ["title", "total"],
    "properties": {"title": {"type": "string"}, "total": {"type": "number"}},
}


def _check(decision, name: str):
    return next(c for c in decision.checks if c.check == name)


# --- structured output ---

def test_valid_json_passes() -> None:
    decision = QualityGate().evaluate('{"title": "Report", "total": 42}', "application/json")
    assert _check(decision, "json_validity").status == "pass"
    assert decision.outcome == "accept"


def test_malformed_json_is_rejected() -> None:
    decision = QualityGate().evaluate('{"title": "Report",,}', "application/json")
    assert decision.outcome == "reject"
    assert any("json_validity" in v for v in decision.violations)


def test_json_checks_skipped_for_prose() -> None:
    decision = QualityGate().evaluate("Just some prose.", "text/plain")
    assert not any(c.check == "json_validity" for c in decision.checks)


# --- schema conformance ---

def test_conforming_document_passes_schema() -> None:
    decision = QualityGate().evaluate(
        '{"title": "Report", "total": 42}', "application/json", schema=SCHEMA
    )
    assert _check(decision, "schema_conformance").status == "pass"


def test_missing_required_property_is_rejected() -> None:
    decision = QualityGate().evaluate('{"title": "Report"}', "application/json", schema=SCHEMA)
    assert decision.outcome == "reject"
    assert any("total" in v for v in decision.violations)


def test_wrong_property_type_is_rejected() -> None:
    decision = QualityGate().evaluate(
        '{"title": "Report", "total": "lots"}', "application/json", schema=SCHEMA
    )
    assert decision.outcome == "reject"


# --- grounding ---

def test_grounded_claims_pass() -> None:
    decision = QualityGate().evaluate(GROUNDED, "text/markdown", sources=SOURCES)
    assert _check(decision, "grounding").status == "pass"
    assert decision.passed is True


def test_fabricated_figures_are_rejected() -> None:
    decision = QualityGate().evaluate(FABRICATED, "text/markdown", sources=SOURCES)
    assert decision.outcome == "reject", "a cluster of unsourced figures must not pass"
    assert any("grounding" in v for v in decision.violations)


def test_single_unsourced_figure_is_only_a_warning() -> None:
    text = "Revenue reached 4.2 million, a 12 percent rise over 1500 accounts, plus 77 new logos."
    decision = QualityGate().evaluate(text, "text/markdown", sources=SOURCES)
    assert _check(decision, "grounding").status == "warn"
    assert decision.passed is True


def test_grounding_skipped_without_sources() -> None:
    decision = QualityGate().evaluate(FABRICATED, "text/markdown")
    assert not any(c.check == "grounding" for c in decision.checks)


@pytest.mark.parametrize("value", ["1,500", "$4,200.00", "12.5"])
def test_formatted_numbers_match_their_sources(value: str) -> None:
    decision = QualityGate().evaluate(
        f"The figure was {value} for the period under review here.",
        "text/plain",
        sources=[f"Reported {value} in the filing."],
    )
    assert _check(decision, "grounding").status == "pass"
