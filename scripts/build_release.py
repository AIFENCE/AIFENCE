from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

VERSION = "0.2.7"
SOURCE_NAME = f"sage-plugin-v{VERSION}.zip"
WHEEL_NAME = f"sage_agent_protocol-{VERSION}-py3-none-any.whl"
HERMES_NAME = f"sage-hermes-plugin-v{VERSION}.zip"
OPENCLAW_NAME = f"sage-agent-openclaw-sage-{VERSION}.tgz"
VERIFICATION_NAME = f"SAGE-v{VERSION}-VERIFICATION.md"
CHECKSUM_NAME = f"SAGE-v{VERSION}-SHA256SUMS.txt"
DEFAULT_SOURCE_DATE_EPOCH = 1_785_456_000  # 2026-07-31 00:00:00 UTC

EXCLUDED_PARTS = {
    ".git",
    ".github-release",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "node_modules",
}
EXCLUDED_NAMES = {".coverage", ".env", "sage.db", "ci-migration.db"}


def _epoch() -> int:
    return int(os.environ.get("SOURCE_DATE_EPOCH", str(DEFAULT_SOURCE_DATE_EPOCH)))


def _zip_datetime(epoch: int) -> tuple[int, int, int, int, int, int]:
    value = datetime.fromtimestamp(epoch, tz=UTC)
    year = max(1980, value.year)
    return (year, value.month, value.day, value.hour, value.minute, value.second)


def _include(path: Path, root: Path, output: Path) -> bool:
    relative = path.relative_to(root)
    if relative.parts and relative.parts[0] == "dist":
        return False
    if any(part in EXCLUDED_PARTS or part.endswith(".egg-info") for part in relative.parts):
        return False
    if path.name in EXCLUDED_NAMES or path.suffix in {".pyc", ".pyo"}:
        return False
    try:
        path.relative_to(output)
    except ValueError:
        pass
    else:
        return False
    return path.is_file()


def _write_zip_file(
    archive: zipfile.ZipFile,
    source: Path,
    name: str,
    *,
    epoch: int,
) -> None:
    info = zipfile.ZipInfo(str(PurePosixPath(name)), date_time=_zip_datetime(epoch))
    mode = source.stat().st_mode
    permissions = 0o755 if mode & stat.S_IXUSR else 0o644
    info.external_attr = (permissions & 0xFFFF) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build_source(root: Path, output: Path, epoch: int) -> Path:
    destination = output / SOURCE_NAME
    prefix = f"sage-plugin-v{VERSION}"
    files = sorted(path for path in root.rglob("*") if _include(path, root, output))
    with zipfile.ZipFile(destination, "w") as archive:
        for path in files:
            relative = path.relative_to(root).as_posix()
            _write_zip_file(archive, path, f"{prefix}/{relative}", epoch=epoch)
    return destination


def build_wheel(root: Path, output: Path, epoch: int) -> Path:
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = str(epoch)
    with tempfile.TemporaryDirectory(prefix="sage-wheel-") as temporary:
        temp = Path(temporary)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "wheel",
                ".",
                "--no-deps",
                "--no-build-isolation",
                "--wheel-dir",
                str(temp),
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=root,
            env=env,
        )
        if result.returncode != 0:
            raise SystemExit(
                f"pip wheel failed (exit {result.returncode}):\n{result.stdout}\n{result.stderr}"
            )
        wheels = list(temp.glob("*.whl"))
        if len(wheels) != 1:
            raise RuntimeError(f"expected one wheel, found {wheels}")
        destination = output / WHEEL_NAME
        shutil.copy2(wheels[0], destination)
    return destination


def build_hermes(root: Path, output: Path, epoch: int) -> Path:
    destination = output / HERMES_NAME
    source_root = root / "integrations" / "hermes"
    prefix = f"sage-hermes-plugin-v{VERSION}"
    required = [
        source_root / "README.md",
        source_root / "LICENSE",
        source_root / "install.sh",
        source_root / "install.ps1",
        source_root / "sage" / "__init__.py",
        source_root / "sage" / "plugin.yaml",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"Hermes release files missing: {missing}")
    with zipfile.ZipFile(destination, "w") as archive:
        for path in required:
            relative = path.relative_to(source_root).as_posix()
            _write_zip_file(archive, path, f"{prefix}/{relative}", epoch=epoch)
    return destination


def build_openclaw(root: Path, output: Path, epoch: int) -> Path:
    integration = root / "integrations" / "openclaw"
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = str(epoch)
    npm = shutil.which("npm")
    if npm is None:
        raise RuntimeError("npm is required to build the OpenClaw release package")
    with tempfile.TemporaryDirectory(prefix="sage-npm-cache-") as npm_cache:
        env["npm_config_cache"] = npm_cache
        env["npm_config_audit"] = "false"
        env["npm_config_fund"] = "false"
        env["npm_config_update_notifier"] = "false"
        subprocess.run(
            [npm, "pack", "--ignore-scripts", "--pack-destination", str(output)],
            cwd=integration,
            env=env,
            check=True,
        )
    candidates = sorted(output.glob("*.tgz"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not candidates:
        raise RuntimeError("npm pack did not produce a tarball")
    produced = next((path for path in candidates if path.name == OPENCLAW_NAME), candidates[0])
    destination = output / OPENCLAW_NAME
    if produced != destination:
        if destination.exists():
            destination.unlink()
        produced.replace(destination)
    return destination


def _validate_tar_paths(path: Path) -> None:
    with tarfile.open(path, "r:gz") as archive:
        for member in archive.getmembers():
            pure = PurePosixPath(member.name)
            if pure.is_absolute() or ".." in pure.parts:
                raise RuntimeError(f"unsafe archive path: {member.name}")


def write_supporting_assets(root: Path, output: Path, artifacts: list[Path]) -> list[Path]:
    verification = output / VERIFICATION_NAME
    shutil.copy2(root / "VERIFICATION.md", verification)
    checksum = output / CHECKSUM_NAME
    lines = []
    for path in sorted([*artifacts, verification], key=lambda item: item.name):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.name}")
    checksum.write_text("\n".join(lines) + "\n")
    return [verification, checksum]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build every SAGE GitHub release asset")
    parser.add_argument("--output", type=Path, default=Path("dist"))
    parser.add_argument("--skip-wheel", action="store_true")
    parser.add_argument("--skip-openclaw", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    for name in (
        SOURCE_NAME,
        WHEEL_NAME,
        HERMES_NAME,
        OPENCLAW_NAME,
        VERIFICATION_NAME,
        CHECKSUM_NAME,
    ):
        (output / name).unlink(missing_ok=True)

    epoch = _epoch()
    artifacts = [build_source(root, output, epoch), build_hermes(root, output, epoch)]
    if not args.skip_wheel:
        artifacts.append(build_wheel(root, output, epoch))
    if not args.skip_openclaw:
        openclaw = build_openclaw(root, output, epoch)
        _validate_tar_paths(openclaw)
        artifacts.append(openclaw)
    supporting = write_supporting_assets(root, output, artifacts)
    for path in [*artifacts, *supporting]:
        print(path)


if __name__ == "__main__":
    main()
