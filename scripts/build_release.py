from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
VERSION = str(PROJECT["version"])
SOURCE_NAME = f"aifence-v{VERSION}-source.zip"
CHECKSUM_NAME = f"AIFENCE-v{VERSION}-SHA256SUMS.txt"
DEFAULT_SOURCE_DATE_EPOCH = 1_704_067_200  # 2024-01-01 UTC; stable default for reproducible local builds.
EXCLUDED_PARTS = {
    ".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".hypothesis", ".mutmut-cache",
    ".nox", ".tox", ".venv", "__pycache__", "node_modules", "dist", "build", "mutants",
}
EXCLUDED_NAMES = {
    ".coverage", ".env", "aifence.db", "ci-migration.db", "coverage.json", "coverage.xml",
}


def _epoch() -> int:
    return int(os.environ.get("SOURCE_DATE_EPOCH", str(DEFAULT_SOURCE_DATE_EPOCH)))


def _zip_datetime(epoch: int) -> tuple[int, int, int, int, int, int]:
    value = datetime.fromtimestamp(epoch, tz=UTC)
    return (max(1980, value.year), value.month, value.day, value.hour, value.minute, value.second)


def _include(path: Path, output: Path) -> bool:
    relative = path.relative_to(ROOT)
    if any(part in EXCLUDED_PARTS or part.endswith(".egg-info") for part in relative.parts):
        return False
    if relative.parts[:2] == ("quality", "build"):
        return False
    if path.name in EXCLUDED_NAMES or path.suffix in {".pyc", ".pyo"}:
        return False
    try:
        path.relative_to(output)
        return False
    except ValueError:
        return path.is_file()


def _write_zip_file(archive: zipfile.ZipFile, source: Path, name: str, epoch: int) -> None:
    info = zipfile.ZipInfo(str(PurePosixPath(name)), date_time=_zip_datetime(epoch))
    permissions = 0o755 if source.stat().st_mode & stat.S_IXUSR else 0o644
    info.external_attr = (permissions & 0xFFFF) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build_source(output: Path, epoch: int) -> Path:
    destination = output / SOURCE_NAME
    prefix = f"aifence-v{VERSION}"
    files = sorted(path for path in ROOT.rglob("*") if _include(path, output))
    with zipfile.ZipFile(destination, "w") as archive:
        for path in files:
            _write_zip_file(archive, path, f"{prefix}/{path.relative_to(ROOT).as_posix()}", epoch)
    return destination


def build_wheel(output: Path, epoch: int) -> Path:
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = str(epoch)
    with tempfile.TemporaryDirectory(prefix="aifence-wheel-") as temporary:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "wheel", ".", "--no-deps", "--no-build-isolation", "--wheel-dir", temporary],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            raise SystemExit(f"wheel build failed:\n{result.stdout}\n{result.stderr}")
        wheels = list(Path(temporary).glob("aifence-*.whl"))
        if len(wheels) != 1:
            raise SystemExit(f"expected one AIFENCE wheel, found {wheels}")
        destination = output / wheels[0].name
        shutil.copy2(wheels[0], destination)
        return destination


def write_checksums(output: Path, artifacts: list[Path]) -> Path:
    path = output / CHECKSUM_NAME
    lines = [f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.name}" for item in sorted(artifacts)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build reproducible AIFENCE source and wheel artifacts")
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument("--skip-wheel", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    epoch = _epoch()
    artifacts = [build_source(output, epoch)]
    if not args.skip_wheel:
        artifacts.append(build_wheel(output, epoch))
    artifacts.append(write_checksums(output, artifacts))
    for path in artifacts:
        print(path)


if __name__ == "__main__":
    main()
