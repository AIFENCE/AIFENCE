from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_performance_check_initializes_complete_bus_schema() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/performance_check.py"),
            "--iterations",
            "20",
            "--core-encode-p95-ms",
            "10000",
            "--core-decode-p95-ms",
            "10000",
            "--http-send-p95-ms",
            "10000",
            "--http-receive-p95-ms",
            "10000",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout.strip().splitlines()[-1])
    assert report["ok"] is True
    assert report["iterations"] == 20
