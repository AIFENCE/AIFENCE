#!/usr/bin/env python3
"""Pure release-event/version validation used by Actions and unit tests."""
from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def project_version() -> str:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    return str(project["version"])


def resolve(*, ref_type: str, ref_name: str, version: str) -> dict[str, object]:
    expected = f"v{version}"
    if ref_type == "tag":
        if ref_name != expected:
            raise ValueError(
                f"Release tag {ref_name} does not match pyproject.toml version {expected}."
            )
        return {"version": version, "tag": ref_name, "publish": True}
    if ref_type in {"branch", ""}:
        return {"version": version, "tag": "", "publish": False}
    raise ValueError(f"unsupported GitHub ref type: {ref_type}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref-type", default="")
    parser.add_argument("--ref-name", default="")
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()

    try:
        result = resolve(
            ref_type=args.ref_type,
            ref_name=args.ref_name,
            version=project_version(),
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as handle:
            for key in ("version", "tag", "publish"):
                value = result[key]
                rendered = str(value).lower() if isinstance(value, bool) else value
                handle.write(f"{key}={rendered}\n")

    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
