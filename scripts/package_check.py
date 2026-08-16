from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import tarfile
import zipfile
from email.parser import Parser
from pathlib import Path, PurePosixPath

VERSION = "0.2.7"
AUTHOR = "NeuralBinary"
SOURCE_PREFIX = f"sage-plugin-v{VERSION}/"
HERMES_PREFIX = f"sage-hermes-plugin-v{VERSION}/"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"package check failed: {message}")


def safe_name(name: str) -> bool:
    path = PurePosixPath(name)
    return not path.is_absolute() and ".." not in path.parts and "" not in path.parts


def require_safe_names(names: set[str]) -> None:
    unsafe = sorted(name for name in names if not safe_name(name))
    require(not unsafe, f"unsafe archive paths: {unsafe[:5]}")


def check_source(path: Path) -> dict[str, object]:
    require(path.is_file(), f"source archive missing: {path}")
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        require_safe_names(names)
        files = {name for name in names if not name.endswith("/")}
        require(files and all(name.startswith(SOURCE_PREFIX) for name in files), "source archive must extract into one versioned directory")
        required = {
            f"{SOURCE_PREFIX}README.md",
            f"{SOURCE_PREFIX}LICENSE",
            f"{SOURCE_PREFIX}.env.example",
            f"{SOURCE_PREFIX}quickstart.sh",
            f"{SOURCE_PREFIX}quickstart.ps1",
            f"{SOURCE_PREFIX}docker-compose.quickstart.yml",
            f"{SOURCE_PREFIX}pyproject.toml",
            f"{SOURCE_PREFIX}CONTRIBUTING.md",
            f"{SOURCE_PREFIX}CONTRIBUTOR_LICENSE_AGREEMENT.md",
            f"{SOURCE_PREFIX}SECURITY.md",
            f"{SOURCE_PREFIX}SUPPORT.md",
            f"{SOURCE_PREFIX}CODE_OF_CONDUCT.md",
            f"{SOURCE_PREFIX}.github/dependabot.yml",
            f"{SOURCE_PREFIX}scripts/build_release.py",
            f"{SOURCE_PREFIX}src/sage_plugin/doctor_cli.py",
            f"{SOURCE_PREFIX}src/sage_plugin/demo_cli.py",
        }
        missing = sorted(required - files)
        require(not missing, f"source content missing: {missing}")
        pyproject = archive.read(f"{SOURCE_PREFIX}pyproject.toml").decode()
        require(f'version = "{VERSION}"' in pyproject, "source version drift")
        require("sage-doctor" in pyproject and "sage-demo" in pyproject, "quick-start CLI entries missing")
    return {"source": path.name, "entries": len(files), "ok": True}


def check_record(archive: zipfile.ZipFile, names: set[str]) -> None:
    record_name = next((name for name in names if name.endswith(".dist-info/RECORD")), None)
    require(record_name is not None, "wheel RECORD missing")
    rows = csv.reader(io.StringIO(archive.read(record_name).decode()))
    for name, digest_field, size_field in rows:
        require(name in names, f"RECORD references missing file: {name}")
        if name == record_name:
            continue
        payload = archive.read(name)
        require(size_field == str(len(payload)), f"RECORD size mismatch: {name}")
        algorithm, separator, encoded = digest_field.partition("=")
        require(separator == "=" and algorithm == "sha256", f"unsupported RECORD digest: {name}")
        expected = base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).rstrip(b"=").decode()
        require(encoded == expected, f"RECORD digest mismatch: {name}")


def check_wheel(path: Path) -> dict[str, object]:
    require(path.is_file(), f"wheel missing: {path}")
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        require_safe_names(names)
        metadata_name = next((name for name in names if name.endswith(".dist-info/METADATA")), None)
        entry_name = next((name for name in names if name.endswith(".dist-info/entry_points.txt")), None)
        require(metadata_name is not None, "wheel METADATA missing")
        require(entry_name is not None, "wheel entry points missing")
        metadata = Parser().parsestr(archive.read(metadata_name).decode())
        require(metadata.get("Version") == VERSION, "wheel version drift")
        require(metadata.get("Author") == AUTHOR, "wheel author drift")
        required = {
            "sage_plugin/py.typed",
            "sage_plugin/spec/SAGE-0.2.md",
            "sage_plugin/spec/sage-v0.2.proto",
            "sage_plugin/spec/schemas/wire-v2.schema.json",
            "sage_plugin/spec/schemas/pattern-v0.2.schema.json",
            "sage_plugin/tck/implementations.json",
            "sage_plugin/tck/vectors/core.json",
            "sage_plugin/doctor_cli.py",
            "sage_plugin/demo_cli.py",
        }
        missing = sorted(required - names)
        require(not missing, f"wheel content missing: {missing}")
        entries = archive.read(entry_name).decode()
        require("[hermes_agent.plugins]" in entries and "sage = sage_plugin.hermes_plugin" in entries, "Hermes entry point missing")
        require("sage-doctor = sage_plugin.doctor_cli:main" in entries, "sage-doctor entry point missing")
        require("sage-demo = sage_plugin.demo_cli:main" in entries, "sage-demo entry point missing")
        check_record(archive, names)
    return {"wheel": path.name, "entries": len(names), "ok": True}


def check_hermes(path: Path) -> dict[str, object]:
    require(path.is_file(), f"Hermes package missing: {path}")
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        require_safe_names(names)
        files = {name for name in names if not name.endswith("/")}
        require(files and all(name.startswith(HERMES_PREFIX) for name in files), "Hermes ZIP must extract into one versioned directory")
        required = {
            f"{HERMES_PREFIX}README.md",
            f"{HERMES_PREFIX}LICENSE",
            f"{HERMES_PREFIX}install.sh",
            f"{HERMES_PREFIX}install.ps1",
            f"{HERMES_PREFIX}sage/__init__.py",
            f"{HERMES_PREFIX}sage/plugin.yaml",
        }
        missing = sorted(required - files)
        require(not missing, f"Hermes content missing: {missing}")
        manifest = archive.read(f"{HERMES_PREFIX}sage/plugin.yaml").decode()
        require(f'version: "{VERSION}"' in manifest, "Hermes version drift")
        source_adapter = Path("integrations/hermes/sage/__init__.py")
        if source_adapter.is_file():
            require(
                archive.read(f"{HERMES_PREFIX}sage/__init__.py") == source_adapter.read_bytes(),
                "Hermes adapter differs from repository source",
            )
    return {"hermes": path.name, "entries": len(files), "ok": True}


def check_openclaw(path: Path) -> dict[str, object]:
    require(path.is_file(), f"OpenClaw package missing: {path}")
    with tarfile.open(path, "r:gz") as archive:
        names = set(archive.getnames())
        require_safe_names(names)
        required = {
            "package/package.json",
            "package/openclaw.plugin.json",
            "package/dist/index.js",
            "package/dist/conformance.js",
            "package/tck/core.json",
            "package/README.md",
            "package/LICENSE",
        }
        missing = sorted(required - names)
        require(not missing, f"OpenClaw content missing: {missing}")
        package_member = archive.extractfile("package/package.json")
        require(package_member is not None, "OpenClaw package metadata unreadable")
        package = json.loads(package_member.read())
        require(package.get("version") == VERSION, "OpenClaw version drift")
        require(package.get("author") == AUTHOR, "OpenClaw author drift")
        require(package.get("contributors") == ["NeuralBinary", "ro0ti"], "OpenClaw credits drift")
        require(package.get("license") == "AGPL-3.0-or-later", "OpenClaw license metadata drift")
        license_member = archive.extractfile("package/LICENSE")
        require(license_member is not None, "OpenClaw license unreadable")
        license_text = license_member.read().decode()
        require("SPDX: AGPL-3.0-or-later" in license_text, "OpenClaw AGPL license payload drift")
        require(not license_text.startswith("MIT License"), "OpenClaw package still contains MIT license")
    return {"openclaw": path.name, "entries": len(names), "ok": True}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path)
    parser.add_argument("--wheel", type=Path)
    parser.add_argument("--hermes", type=Path)
    parser.add_argument("--openclaw", type=Path)
    args = parser.parse_args()
    require(any((args.source, args.wheel, args.hermes, args.openclaw)), "at least one package path is required")
    result: dict[str, object] = {"ok": True}
    if args.source is not None:
        result["source"] = check_source(args.source)
    if args.wheel is not None:
        result["python"] = check_wheel(args.wheel)
    if args.hermes is not None:
        result["hermes"] = check_hermes(args.hermes)
    if args.openclaw is not None:
        result["openclaw"] = check_openclaw(args.openclaw)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
