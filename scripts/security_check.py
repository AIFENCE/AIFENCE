from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = [ROOT / "src", ROOT / "scripts"]


def fail(message: str) -> None:
    raise SystemExit(f"security check failed: {message}")


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


def main() -> None:
    failures: list[str] = []
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
                names = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module or ""]
                if any(name.split(".", 1)[0] in forbidden_imports for name in names):
                    failures.append(f"{path.relative_to(ROOT)}:{node.lineno}: unsafe serialization import")
            if isinstance(node, ast.Call):
                name = call_name(node)
                if name in forbidden_calls:
                    failures.append(f"{path.relative_to(ROOT)}:{node.lineno}: forbidden call {name}")
                if name.startswith("subprocess."):
                    for kw in node.keywords:
                        if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                            failures.append(f"{path.relative_to(ROOT)}:{node.lineno}: subprocess shell=True")
                if name in {"requests.get", "requests.post", "requests.request", "httpx.get", "httpx.post", "httpx.request"}:
                    for kw in node.keywords:
                        if kw.arg == "verify" and isinstance(kw.value, ast.Constant) and kw.value.value is False:
                            failures.append(f"{path.relative_to(ROOT)}:{node.lineno}: TLS verification disabled")

    for compose_path in [ROOT / "docker-compose.yml", ROOT / "deploy" / "staging" / "compose.yml"]:
        compose = compose_path.read_text(encoding="utf-8")
        label = str(compose_path.relative_to(ROOT))
        if re.search(r"^\s*POSTGRES_PASSWORD:\s*(?!\$\{)[^\s]+", compose, re.MULTILINE):
            failures.append(f"{label}: embedded PostgreSQL password")
        if 'SAGE_AUTH_REQUIRED: "false"' in compose:
            failures.append(f"{label}: production auth disabled")


    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    if re.search(r"^USER\s+root\s*$", dockerfile, re.MULTILINE):
        failures.append("Dockerfile: final runtime user is root")
    if "USER sage" not in dockerfile:
        failures.append("Dockerfile: non-root runtime user missing")

    plugin = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    if plugin.get("repository") != "https://github.com/NeuralBinary/SAGE":
        failures.append("plugin.json: repository identity mismatch")

    if failures:
        fail("; ".join(failures))
    print(json.dumps({"ok": True, "python_files": len(python_files()), "checks": ["ast", "tls", "compose", "container", "metadata"]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
