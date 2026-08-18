from __future__ import annotations

import argparse
import json
from pathlib import Path

from aifence.bus.protocol_spec import WirePacketV2
from aifence.bus.spec_models import SPEC_MODELS

ROOT = Path(__file__).resolve().parents[1]


def rendered(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def write_or_check(path: Path, payload: dict, check: bool) -> bool:
    expected = rendered(payload)
    if check:
        return path.exists() and path.read_text(encoding="utf-8") == expected
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(expected, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    repo = ROOT / "spec" / "schemas"
    packaged = ROOT / "src" / "aifence.bus" / "spec" / "schemas"
    mismatches: list[str] = []
    for name, model in SPEC_MODELS.items():
        payload = model.model_json_schema()
        filename = f"{name}-v0.2.schema.json"
        for path in (repo / filename, packaged / filename):
            if not write_or_check(path, payload, args.check):
                mismatches.append(str(path.relative_to(ROOT)))
    wire = WirePacketV2.model_json_schema(by_alias=True)
    for path in (repo / "wire-v2.schema.json", packaged / "wire-v2.schema.json"):
        if not write_or_check(path, wire, args.check):
            mismatches.append(str(path.relative_to(ROOT)))

    if mismatches:
        raise SystemExit("schema artifacts differ: " + ", ".join(sorted(mismatches)))
    if args.check:
        print("schema artifacts match generated source")


if __name__ == "__main__":
    main()
