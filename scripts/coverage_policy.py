#!/usr/bin/env python3
"""Enforce risk-weighted line and branch coverage from coverage.py JSON output."""
from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _percent(covered: int, total: int) -> float:
    return 100.0 if total == 0 else (covered / total) * 100.0


def _metrics(summary: dict[str, Any]) -> tuple[float, float]:
    line = _percent(int(summary.get("covered_lines", 0)), int(summary.get("num_statements", 0)))
    branch = _percent(int(summary.get("covered_branches", 0)), int(summary.get("num_branches", 0)))
    return line, branch


def _normalize_coverage_path(path: str) -> str:
    """Normalize coverage.py file keys across Windows and POSIX runners."""
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _check(label: str, actual: float, required: float, failures: list[str]) -> None:
    status = "PASS" if actual + 1e-9 >= required else "FAIL"
    print(f"{status:4} {label:<52} {actual:6.2f}% >= {required:6.2f}%")
    if status == "FAIL":
        failures.append(f"{label}: {actual:.2f}% < {required:.2f}%")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", "--coverage-json", dest="coverage", type=Path, default=Path("coverage.json"))
    parser.add_argument("--policy", type=Path, default=ROOT / "coverage-policy.toml")
    parser.add_argument("--profile", choices=["ci", "release", "nightly"], default="ci")
    args = parser.parse_args()

    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    policy = tomllib.loads(args.policy.read_text(encoding="utf-8"))
    profile = policy["profiles"][args.profile]
    failures: list[str] = []

    total_line, total_branch = _metrics(coverage["totals"])
    _check(f"overall line ({args.profile})", total_line, float(profile["line"]), failures)
    _check(f"overall branch ({args.profile})", total_branch, float(profile["branch"]), failures)

    files: dict[str, Any] = {
        _normalize_coverage_path(path): entry
        for path, entry in coverage.get("files", {}).items()
    }
    for path, thresholds in policy.get("modules", {}).items():
        entry = files.get(_normalize_coverage_path(path))
        if entry is None:
            failures.append(f"missing coverage entry: {path}")
            print(f"FAIL {path:<52} missing")
            continue
        line, branch = _metrics(entry["summary"])
        _check(f"{path} line", line, float(thresholds["line"]), failures)
        _check(f"{path} branch", branch, float(thresholds["branch"]), failures)

    if failures:
        print("\nCoverage policy failures:")
        for failure in failures:
            print(f" - {failure}")
        raise SystemExit(1)
    print("\nCoverage policy satisfied.")


if __name__ == "__main__":
    main()
