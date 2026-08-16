from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "tck" / "implementations.json").read_text())
    env = os.environ.copy()
    src = str(root / "src")
    env["PYTHONPATH"] = src + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    results: list[dict[str, object]] = []
    failed = False
    for item in manifest["implementations"]:
        command = shlex.split(item["command"])
        if command and command[0] in {"python", "python3"}:
            command[0] = sys.executable
        try:
            proc = subprocess.run(command, cwd=root, env=env, text=True, capture_output=True, timeout=120, check=False)
            ok = proc.returncode == 0
            result = {
                "id": item["id"],
                "required": bool(item.get("required", False)),
                "ok": ok,
                "returncode": proc.returncode,
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
            }
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            ok = False
            result = {
                "id": item["id"],
                "required": bool(item.get("required", False)),
                "ok": False,
                "error": str(exc),
            }
        results.append(result)
        if item.get("required", False) and not ok:
            failed = True
    print(json.dumps({"suite": manifest["suite"], "ok": not failed, "implementations": results}, separators=(",", ":")))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
