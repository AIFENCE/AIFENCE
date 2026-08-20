#!/usr/bin/env python3
"""Generate a deterministic CycloneDX-compatible inventory of installed Python packages."""
from __future__ import annotations

import argparse
import json
from importlib import metadata
from pathlib import Path


def components() -> list[dict[str, object]]:
    seen: set[tuple[str, str]] = set()
    result: list[dict[str, object]] = []
    for dist in metadata.distributions():
        name = str(dist.metadata.get("Name") or "").strip()
        version = str(dist.version or "").strip()
        if not name or not version:
            continue
        key = (name.lower(), version)
        if key in seen:
            continue
        seen.add(key)
        normalized = name.lower().replace("_", "-")
        result.append(
            {
                "type": "library",
                "name": name,
                "version": version,
                "purl": f"pkg:pypi/{normalized}@{version}",
            }
        )
    return sorted(result, key=lambda item: (str(item["name"]).lower(), str(item["version"])))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an AIFENCE Python dependency SBOM")
    parser.add_argument("--output", type=Path, default=Path("dist/aifence-python-sbom.cdx.json"))
    args = parser.parse_args()
    payload = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {"component": {"type": "application", "name": "aifence"}},
        "components": components(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
