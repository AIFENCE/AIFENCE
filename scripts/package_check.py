from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import tomllib
import zipfile
from email.parser import Parser
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
VERSION = str(tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"])


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"package check failed: {message}")


def safe_name(name: str) -> bool:
    path = PurePosixPath(name)
    return not path.is_absolute() and ".." not in path.parts


def check_source(path: Path) -> dict[str, object]:
    require(path.is_file(), f"source archive missing: {path}")
    prefix = f"aifence-v{VERSION}/"
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        require(all(safe_name(name) for name in names), "source archive contains unsafe paths")
        files = {name for name in names if not name.endswith("/")}
        require(files and all(name.startswith(prefix) for name in files), "source archive lacks a single versioned root")
        required = {
            f"{prefix}README.md", f"{prefix}LICENSE", f"{prefix}pyproject.toml",
            f"{prefix}compose.yaml", f"{prefix}SECURITY.md", f"{prefix}docs/QUICKSTART.md",
            f"{prefix}src/aifence/versions.py", f"{prefix}scripts/release_check.py",
        }
        require(not (required - files), f"source archive missing: {sorted(required - files)}")
        require(not any(name.startswith(f"{prefix}quality/build/") for name in files), "generated quality/build leaked into source archive")
    return {"ok": True, "source": path.name, "entries": len(files)}


def _check_record(archive: zipfile.ZipFile, names: set[str]) -> None:
    record_name = next((name for name in names if name.endswith(".dist-info/RECORD")), None)
    require(record_name is not None, "wheel RECORD missing")
    rows = csv.reader(io.StringIO(archive.read(record_name).decode()))
    for name, digest_field, size_field in rows:
        require(name in names, f"RECORD references missing file: {name}")
        if name == record_name:
            continue
        payload = archive.read(name)
        require(size_field == str(len(payload)), f"RECORD size mismatch: {name}")
        algorithm, sep, encoded = digest_field.partition("=")
        require(sep == "=" and algorithm == "sha256", f"unsupported RECORD digest: {name}")
        expected = base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).rstrip(b"=").decode()
        require(encoded == expected, f"RECORD digest mismatch: {name}")


def check_wheel(path: Path) -> dict[str, object]:
    require(path.is_file(), f"wheel missing: {path}")
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        require(all(safe_name(name) for name in names), "wheel contains unsafe paths")
        metadata_name = next((name for name in names if name.endswith(".dist-info/METADATA")), None)
        entry_name = next((name for name in names if name.endswith(".dist-info/entry_points.txt")), None)
        require(metadata_name is not None, "wheel METADATA missing")
        require(entry_name is not None, "wheel entry points missing")
        metadata = Parser().parsestr(archive.read(metadata_name).decode())
        require(metadata.get("Version") == VERSION, "wheel version drift")
        required = {
            "aifence/py.typed",
            "aifence/bus/py.typed",
            "aifence/bus/spec/AIFENCE-0.2.md",
            "aifence/bus/spec/aifence-v0.2.proto",
            "aifence/bus/spec/schemas/wire-v2.schema.json",
            "aifence/bus/tck/implementations.json",
            "aifence/bus/tck/vectors/core.json",
            "aifence/cli.py",
            "aifence/versions.py",
            "aifence/quality/control_registry.csv",
        }
        require(not (required - names), f"wheel missing: {sorted(required - names)}")
        entries = archive.read(entry_name).decode()
        for command in ("aifence =", "aifence-doctor =", "aifence-demo =", "aifence-redteam ="):
            require(command in entries, f"wheel entry point missing: {command}")
        _check_record(archive, names)
    return {"ok": True, "wheel": path.name, "entries": len(names)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate built AIFENCE release artifacts")
    parser.add_argument("--source", type=Path)
    parser.add_argument("--wheel", type=Path)
    args = parser.parse_args()
    require(bool(args.source or args.wheel), "provide --source and/or --wheel")
    result: dict[str, object] = {"ok": True}
    if args.source:
        result["source"] = check_source(args.source)
    if args.wheel:
        result["wheel"] = check_wheel(args.wheel)
    import json
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
