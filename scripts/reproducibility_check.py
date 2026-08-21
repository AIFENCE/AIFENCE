#!/usr/bin/env python3
"""Build AIFENCE twice and require byte-identical release artifacts."""
from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(output: Path, epoch: str) -> dict[str, str]:
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = epoch
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/build_release.py"),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        env=env,
        check=True,
    )
    return {
        path.name: digest(path)
        for path in sorted(output.iterdir())
        if path.is_file()
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-date-epoch",
        default=os.getenv("SOURCE_DATE_EPOCH", "1704067200"),
    )
    args = parser.parse_args()

    with (
        tempfile.TemporaryDirectory(prefix="aifence-repro-a-") as first_dir,
        tempfile.TemporaryDirectory(prefix="aifence-repro-b-") as second_dir,
    ):
        first = build(Path(first_dir), args.source_date_epoch)
        second = build(Path(second_dir), args.source_date_epoch)

    if first != second:
        names = sorted(set(first) | set(second))
        details = [
            f"{name}: {first.get(name)} != {second.get(name)}"
            for name in names
            if first.get(name) != second.get(name)
        ]
        raise SystemExit("reproducibility check failed:\n" + "\n".join(details))

    print("reproducibility PASS")
    for name, sha256 in first.items():
        print(f"{sha256}  {name}")


if __name__ == "__main__":
    main()
