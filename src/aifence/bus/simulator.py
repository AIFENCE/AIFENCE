# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .config import get_settings
from .db import SessionLocal, init_db
from .evals import run_eval
from .schemas import EvalCase, EvalRequest


def load_cases(path: Path) -> list[EvalCase]:
    if path.suffix.lower() == ".jsonl":
        rows: list[EvalCase] = []
        for line in path.read_text().splitlines():
            if line.strip():
                rows.append(EvalCase.model_validate(json.loads(line)))
        return rows
    data: Any = json.loads(path.read_text())
    if isinstance(data, dict) and "cases" in data:
        data = data["cases"]
    if not isinstance(data, list):
        raise ValueError("eval input must be a JSON list, {cases:[...]}, or JSONL")
    return [EvalCase.model_validate(row) for row in data]


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline SAGE communication simulator/evaluator")
    parser.add_argument("input", type=Path, help="JSON/JSONL eval cases")
    parser.add_argument("--budget-tokens", type=int, default=1200)
    parser.add_argument("--workspace", default="simulator")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    init_db()
    request = EvalRequest(
        cases=load_cases(args.input),
        budget_tokens=args.budget_tokens,
        workspace=args.workspace,
    )
    with SessionLocal() as db:
        report = run_eval(db, get_settings(), request)
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(text + "\n")
    else:
        print(text)


if __name__ == "__main__":
    main()
