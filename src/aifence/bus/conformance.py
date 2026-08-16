# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import argparse
import copy
import json
import random
from dataclasses import dataclass
from importlib.resources import files
from typing import Any, cast

from .a2a_adapter import pack_data_part, unpack_data_part
from .protocol_spec import (
    canonical_digest,
    canonical_json_bytes,
    canonical_msgpack_bytes,
    validate_wire_v2,
)


@dataclass(frozen=True)
class TckResult:
    total: int
    passed: int
    failures: list[str]

    @property
    def ok(self) -> bool:
        return self.total == self.passed

    def as_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "total": self.total, "passed": self.passed, "failures": self.failures}


def _load_vectors() -> dict[str, Any]:
    resource = files("aifence.bus").joinpath("tck/vectors/core.json")
    return cast(dict[str, Any], json.loads(resource.read_text(encoding="utf-8")))


def run_tck() -> TckResult:
    vectors = _load_vectors()
    failures: list[str] = []
    total = 0

    for case in vectors["valid"]:
        total += 1
        name = case["name"]
        wire = case["wire"]
        try:
            validate_wire_v2(wire)
            digest = canonical_digest(wire)
            if digest != case["canonical_sha256"]:
                failures.append(f"{name}: digest {digest} != {case['canonical_sha256']}")
                continue
            if canonical_json_bytes(wire).decode("utf-8") != case["canonical_json"]:
                failures.append(f"{name}: canonical JSON mismatch")
                continue
            if canonical_msgpack_bytes(wire).hex() != case["canonical_msgpack_hex"]:
                failures.append(f"{name}: canonical MessagePack mismatch")
                continue
            if unpack_data_part(pack_data_part(wire)) != wire:
                failures.append(f"{name}: A2A data-part round trip mismatch")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{name}: {type(exc).__name__}: {exc}")

    for case in vectors["invalid"]:
        total += 1
        try:
            validate_wire_v2(case["wire"])
        except Exception:  # noqa: BLE001
            continue
        failures.append(f"{case['name']}: invalid vector was accepted")

    return TckResult(total=total, passed=total - len(failures), failures=failures)



def run_wire_fuzz(iterations: int = 100, seed: int = 1) -> TckResult:
    """Deterministic mutation suite for the frozen v0.2 wire validator.

    Mutations deliberately violate protocol invariants and must be rejected. It is not
    a replacement for a dedicated coverage-guided fuzzer, but it ships a repeatable
    conformance safety check that every implementation can run in CI.
    """
    if iterations < 1:
        raise ValueError("iterations must be >= 1")
    vectors = _load_vectors()
    valid = vectors["valid"]
    rng = random.Random(seed)
    failures: list[str] = []
    total = 0
    mutators = [
        lambda wire: wire.__setitem__("v", 999),
        lambda wire: wire.__setitem__("x", "not-a-list"),
        lambda wire: wire.__setitem__("R", "not-a-list"),
        lambda wire: wire.__setitem__("p", "not-an-object"),
        lambda wire: wire.__setitem__("g", "not-an-object"),
    ]
    for idx in range(iterations):
        total += 1
        wire = copy.deepcopy(rng.choice(valid)["wire"])
        rng.choice(mutators)(wire)
        try:
            validate_wire_v2(wire)
        except Exception:
            continue
        failures.append(f"mutation-{idx}: malformed wire accepted")
    return TckResult(total=total, passed=total - len(failures), failures=failures)

def main() -> None:
    parser = argparse.ArgumentParser(description="Run SAGE 0.2 conformance checks")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--fuzz", type=int, default=0, metavar="N", help="run N deterministic malformed-wire mutations")
    parser.add_argument("--seed", type=int, default=1, help="mutation seed")
    args = parser.parse_args()
    tck = run_tck()
    fuzz = run_wire_fuzz(args.fuzz, args.seed) if args.fuzz else None
    combined_failures = list(tck.failures) + (list(fuzz.failures) if fuzz else [])
    result = {
        "ok": not combined_failures,
        "tck": tck.as_dict(),
        "wire_fuzz": fuzz.as_dict() if fuzz else None,
        "failures": combined_failures,
    }
    if args.json:
        print(json.dumps(result, separators=(",", ":")))
    else:
        print(f"SAGE TCK: {tck.passed}/{tck.total} passed")
        if fuzz:
            print(f"SAGE wire mutations: {fuzz.passed}/{fuzz.total} rejected as expected")
        for failure in combined_failures:
            print(f"FAIL: {failure}")
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
