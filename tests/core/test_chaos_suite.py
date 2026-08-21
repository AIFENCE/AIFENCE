from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_chaos_suite_handles_workloads_larger_than_pull_batch() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/chaos_suite.py"),
            "--messages",
            "128",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout.strip().splitlines()[-1])
    assert report == {
        "idempotent_writes": 1,
        "messages": 128,
        "recovered_after_lease": 64,
    }
