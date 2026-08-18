#!/usr/bin/env python
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Generate the shipped policy profiles from the mandatory baseline.

The baseline denies by default: anything outside a narrow allow-list falls to
``require_approval``. That is the right maximum-security posture, but measured
against realistic benign traffic it holds most production writes, which is an
adoption blocker rather than a security win.

A profile is the baseline plus additional *allow* rules. It never removes or
weakens a baseline rule — it is generated from the baseline every time, so a new
mandatory rule cannot be lost by a profile drifting out of date. Each added rule
is bounded by ``max_risk``, so any finding that raises risk above the bound
takes the action back out of the allowance.

Run: python tooling/generate-policy-profiles.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "src" / "aifence" / "guard" / "baseline_policy.json"
OUT = ROOT / "policies"

# Risk bounds are taken from measured traffic, not intuition: see
# `aifence-redteam` output and docs/evaluation.md. Each bound sits above the
# observed benign risk for that operation and below the risk any detector
# finding produces for it.
BALANCED_RULES = [
    {
        "id": "balanced-in-scope-reversible-write",
        "priority": 300,
        "description": (
            "Reversible, non-destructive, in-scope writes at low risk. Any detector "
            "finding raises risk above the bound and withdraws the allowance."
        ),
        "match": {
            "operations": ["write", "update"],
            "destructive": False,
            "reversible": True,
            "max_risk": 29,
        },
        "effect": {
            "outcome": "allow_with_limits",
            "reasons": ["Low-risk reversible write within the approved scope"],
            "constraints": {"read_only": False, "capability_ttl_seconds": 300},
        },
    },
    {
        "id": "balanced-low-risk-send",
        "priority": 300,
        "description": (
            "Outbound sends carrying nothing sensitive. Exfiltration and "
            "secret-exposure findings push risk far above this bound."
        ),
        "match": {"operations": ["send"], "destructive": False, "max_risk": 19},
        "effect": {
            "outcome": "allow_with_limits",
            "reasons": ["Low-risk send with no sensitive data class observed"],
            "constraints": {"capability_ttl_seconds": 300, "max_response_bytes": 1048576},
        },
    },
    {
        "id": "balanced-scoped-maintenance-delete",
        "priority": 300,
        "description": (
            "Destructive maintenance the agent is explicitly registered for, within "
            "its approved scope. Escalation beyond it raises risk and is withdrawn."
        ),
        "match": {"operations": ["delete"], "destructive": True, "max_risk": 39},
        "effect": {
            "outcome": "allow_with_limits",
            "reasons": ["Scoped destructive maintenance by a registered tool"],
            "constraints": {"capability_ttl_seconds": 120, "max_capability_uses": 1},
        },
    },
]


def main() -> int:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    OUT.mkdir(exist_ok=True)

    # strict == the baseline, shipped by name so a deployment can pin it.
    strict = dict(baseline)
    strict["version"] = f"{baseline['version']}+strict"
    (OUT / "strict.json").write_text(
        json.dumps(strict, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline=""
    )

    existing = {r["id"] for r in baseline["rules"]}
    balanced = dict(baseline)
    balanced["version"] = f"{baseline['version']}+balanced"
    balanced["rules"] = [*baseline["rules"], *(r for r in BALANCED_RULES if r["id"] not in existing)]
    (OUT / "balanced.json").write_text(
        json.dumps(balanced, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline=""
    )

    print(f"strict.json    {len(strict['rules'])} rules")
    print(f"balanced.json  {len(balanced['rules'])} rules (+{len(BALANCED_RULES)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
