#!/usr/bin/env python3
"""Detect backwards-incompatible removals from a frozen OpenAPI baseline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from aifence.app import create_app
from aifence.core.config import CoreSettings

ROOT = Path(__file__).resolve().parents[1]
HTTP_METHODS = {"get", "put", "post", "delete", "patch", "options", "head", "trace"}


def current() -> dict:
    app = create_app(
        CoreSettings(
            environment="test",
            database_url="sqlite+pysqlite:///:memory:",
            docs_enabled=True,
        )
    )
    return app.openapi()


def compare(old: dict, new: dict) -> list[str]:
    failures: list[str] = []
    old_paths = old.get("paths", {})
    new_paths = new.get("paths", {})

    for path, methods in old_paths.items():
        if path not in new_paths:
            failures.append(f"removed path: {path}")
            continue
        for method in methods:
            if method.lower() in HTTP_METHODS and method not in new_paths[path]:
                failures.append(f"removed operation: {method.upper()} {path}")

    old_schemas = old.get("components", {}).get("schemas", {})
    new_schemas = new.get("components", {}).get("schemas", {})
    for name, schema in old_schemas.items():
        if name not in new_schemas:
            failures.append(f"removed schema: {name}")
            continue

        old_required = set(schema.get("required", []))
        new_required = set(new_schemas[name].get("required", []))
        added_required = new_required - old_required
        if added_required:
            failures.append(f"new required fields in {name}: {sorted(added_required)}")

        old_properties = set(schema.get("properties", {}))
        new_properties = set(new_schemas[name].get("properties", {}))
        removed = old_properties - new_properties
        if removed:
            failures.append(f"removed fields in {name}: {sorted(removed)}")

    return failures


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--baseline",
        type=Path,
        default=ROOT / "compat/openapi-platform-0.1.0.json",
    )
    parser.add_argument("--write-current", type=Path)
    args = parser.parse_args()

    document = current()
    if args.write_current:
        args.write_current.parent.mkdir(parents=True, exist_ok=True)
        args.write_current.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(args.write_current)
        return

    if not args.baseline.is_file():
        raise SystemExit(f"OpenAPI baseline missing: {args.baseline}")

    failures = compare(
        json.loads(args.baseline.read_text(encoding="utf-8")),
        document,
    )
    if failures:
        raise SystemExit("OpenAPI compatibility failed:\n- " + "\n- ".join(failures))
    print(f"OpenAPI compatibility PASS against {args.baseline.name}")


if __name__ == "__main__":
    main()
