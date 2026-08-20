#!/usr/bin/env python3
"""Reject protocol/TCK fixture drift between the canonical Bus package and adapters."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "src/aifence/bus/tck/vectors/core.json"
COPIES = [ROOT / "integrations/openclaw/tck/core.json"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    canonical = CANONICAL.read_bytes()
    # Parse once so a byte-identical but invalid fixture cannot pass this gate.
    parsed = json.loads(canonical)
    if not isinstance(parsed, dict) or not parsed.get("valid") or not parsed.get("invalid"):
        failures.append("canonical TCK fixture is empty or malformed")
    for path in COPIES:
        if not path.is_file():
            failures.append(f"missing adapter TCK copy: {path.relative_to(ROOT)}")
        elif path.read_bytes() != canonical:
            failures.append(
                f"adapter TCK drift: {path.relative_to(ROOT)} "
                f"({sha(path)[:12]} != {sha(CANONICAL)[:12]})"
            )
    if failures:
        print("protocol fixture check failed:\n- " + "\n- ".join(failures))
        return 1
    print(json.dumps({"ok": True, "sha256": sha(CANONICAL), "copies": len(COPIES)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
