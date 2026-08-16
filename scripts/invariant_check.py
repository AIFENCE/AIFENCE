from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    catalog = json.loads((ROOT / "spec" / "invariants.json").read_text())
    ids: set[str] = set()
    missing: list[str] = []
    for item in catalog.get("invariants", []):
        ident = item.get("id")
        if not isinstance(ident, str) or not ident or ident in ids:
            raise SystemExit("invalid or duplicate invariant id")
        ids.add(ident)
        checks = item.get("checks") or []
        if not checks:
            raise SystemExit(f"invariant has no checks: {ident}")
        for check in checks:
            target = str(check).split("::", 1)[0]
            if not (ROOT / target).is_file():
                missing.append(f"{ident}:{target}")
    if missing:
        raise SystemExit("missing invariant checks: " + ", ".join(missing))
    print(json.dumps({"ok": True, "protocol": catalog["version"], "invariants": len(ids)}, sort_keys=True))


if __name__ == "__main__":
    main()
