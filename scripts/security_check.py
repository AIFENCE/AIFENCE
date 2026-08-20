from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = [ROOT / "src", ROOT / "scripts"]
TEXT_SCAN_ROOTS = [ROOT / "src", ROOT / "sdks", ROOT / "integrations", ROOT / "deploy"]


def fail(messages: list[str]) -> None:
    if messages:
        raise SystemExit("security check failed:\n- " + "\n- ".join(messages))


def python_files() -> list[Path]:
    files: list[Path] = []
    for root in SOURCE_ROOTS:
        files.extend(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)
    return sorted(files)


def call_name(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        parts = [func.attr]
        value = func.value
        while isinstance(value, ast.Attribute):
            parts.append(value.attr)
            value = value.value
        if isinstance(value, ast.Name):
            parts.append(value.id)
        return ".".join(reversed(parts))
    return ""


def scan_python(failures: list[str]) -> None:
    forbidden_calls = {"eval", "exec", "os.system"}
    forbidden_imports = {"pickle", "marshal"}
    for path in python_files():
        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            failures.append(f"{path.relative_to(ROOT)}: syntax error: {exc}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = (
                    [alias.name for alias in node.names]
                    if isinstance(node, ast.Import)
                    else [node.module or ""]
                )
                if any(name.split(".", 1)[0] in forbidden_imports for name in names):
                    failures.append(f"{path.relative_to(ROOT)}:{node.lineno}: unsafe serialization import")
            if not isinstance(node, ast.Call):
                continue
            name = call_name(node)
            if name in forbidden_calls:
                failures.append(f"{path.relative_to(ROOT)}:{node.lineno}: forbidden call {name}")
            if name.startswith("subprocess."):
                for kw in node.keywords:
                    if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                        failures.append(f"{path.relative_to(ROOT)}:{node.lineno}: subprocess shell=True")
            if name in {
                "requests.get", "requests.post", "requests.request",
                "httpx.get", "httpx.post", "httpx.request",
            }:
                for kw in node.keywords:
                    if kw.arg == "verify" and isinstance(kw.value, ast.Constant) and kw.value.value is False:
                        failures.append(f"{path.relative_to(ROOT)}:{node.lineno}: TLS verification disabled")


def scan_deployment(failures: list[str]) -> None:
    compose_paths = [ROOT / "compose.yaml", ROOT / "deploy" / "qualification" / "compose.yaml"]
    existing = [path for path in compose_paths if path.is_file()]
    if not existing:
        failures.append("no supported compose configuration found")
    for compose_path in existing:
        compose = compose_path.read_text(encoding="utf-8")
        label = str(compose_path.relative_to(ROOT))
        # The qualification stack is an isolated, disposable test fixture and
        # deliberately uses fixed non-production credentials so it can boot
        # unattended. Deployment-facing compose files must resolve secrets from
        # the environment instead.
        is_qualification = compose_path == ROOT / "deploy" / "qualification" / "compose.yaml"
        if (
            not is_qualification
            and re.search(r"^\s*POSTGRES_PASSWORD:\s*(?!\$\{)[^\s]+", compose, re.MULTILINE)
        ):
            failures.append(f"{label}: embedded PostgreSQL password")
        if re.search(r"AIFENCE_(?:BUS_)?AUTH_REQUIRED:\s*[\"']?false", compose, re.IGNORECASE):
            failures.append(f"{label}: authentication disabled")

    dockerfile_path = ROOT / "Dockerfile"
    if not dockerfile_path.is_file():
        failures.append("Dockerfile missing")
        return
    dockerfile = dockerfile_path.read_text(encoding="utf-8")
    user_lines = re.findall(r"^USER\s+([^\s]+)\s*$", dockerfile, re.MULTILINE)
    if not user_lines:
        failures.append("Dockerfile: final runtime user is not declared")
    elif user_lines[-1].lower() in {"root", "0", "0:0"}:
        failures.append("Dockerfile: final runtime user is root")


def scan_repository_identity(failures: list[str]) -> None:
    stale = "github.com/NeuralBinary/AIFENCE"
    for root in TEXT_SCAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or any(part in {"node_modules", "build"} for part in path.parts):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if stale in text:
                failures.append(f"{path.relative_to(ROOT)}: stale repository identity")


def main() -> None:
    failures: list[str] = []
    scan_python(failures)
    scan_deployment(failures)
    scan_repository_identity(failures)
    fail(failures)
    print(json.dumps({
        "ok": True,
        "python_files": len(python_files()),
        "checks": ["ast", "tls", "subprocess", "compose", "container-user", "repository-identity"],
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
