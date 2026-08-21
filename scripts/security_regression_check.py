#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/SECURITY_REGRESSIONS.md"
PATTERN = re.compile(r"`((?:tests|scripts)/[^`]+)`")


def main() -> None:
    if not LEDGER.is_file():
        raise SystemExit("security regression ledger missing")

    refs = sorted(set(PATTERN.findall(LEDGER.read_text(encoding="utf-8"))))
    missing = [ref for ref in refs if not (ROOT / ref.split("::", 1)[0]).exists()]
    if missing:
        raise SystemExit(
            "security regression ledger has missing test references:\n" + "\n".join(missing)
        )
    if len(refs) < 8:
        raise SystemExit(f"security regression ledger is too small ({len(refs)} refs)")

    print(f"security regression ledger PASS ({len(refs)} regression references)")


if __name__ == "__main__":
    main()
