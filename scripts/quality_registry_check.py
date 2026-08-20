#!/usr/bin/env python3
"""Verify the wheel-vendored Quality registry matches the canonical source pack."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "quality/source/control_registry.csv"
VENDORED = ROOT / "src/aifence/quality/control_registry.csv"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    missing = [str(p.relative_to(ROOT)) for p in (CANONICAL, VENDORED) if not p.is_file()]
    if missing:
        print("FAIL: missing Quality registry: " + ", ".join(missing))
        return 1
    if CANONICAL.read_bytes() != VENDORED.read_bytes():
        print("FAIL: vendored Quality registry is stale")
        print(f"  canonical sha256={digest(CANONICAL)}")
        print(f"  vendored  sha256={digest(VENDORED)}")
        return 1
    print(f"PASS: Quality registry synchronized ({digest(CANONICAL)[:16]}..., {CANONICAL.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
