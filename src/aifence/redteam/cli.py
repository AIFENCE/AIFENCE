# SPDX-License-Identifier: AGPL-3.0-or-later
"""``aifence-redteam`` — run the adversarial corpus and report the numbers."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .corpus import load_corpus
from .runner import evaluate_corpus


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="aifence-redteam",
        description="Measure detection rate and false-positive rate on multi-turn agent traces.",
    )
    parser.add_argument("--corpus", type=Path, default=None, help="trace directory")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument(
        "--behavioral", action="store_true", help="enable cross-tier behavioural analysis"
    )
    parser.add_argument(
        "--policy", default=None, help="policy document to evaluate against (default: baseline)"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="run with and without behavioural analysis and show the difference",
    )
    parser.add_argument(
        "--max-false-positive-rate",
        type=float,
        default=None,
        help="exit non-zero if the benign false-positive rate exceeds this percentage",
    )
    parser.add_argument(
        "--min-detection-rate",
        type=float,
        default=None,
        help="exit non-zero if the attack detection rate falls below this percentage",
    )
    args = parser.parse_args(argv)

    traces = load_corpus(args.corpus)
    if not traces:
        print("no traces found", file=sys.stderr)
        return 2

    if args.compare:
        baseline = evaluate_corpus(traces, behavioral=False, policy=args.policy)
        analysed = evaluate_corpus(traces, behavioral=True, policy=args.policy)
        if args.json:
            print(json.dumps({"baseline": baseline.to_dict(), "behavioral": analysed.to_dict()}, indent=2))
        else:
            print(baseline.render())
            print()
            print(analysed.render())
            print()
            print("delta")
            print("=" * 58)
            print(
                f"detection rate      {baseline.detection_rate:5.1f}% -> "
                f"{analysed.detection_rate:5.1f}%  "
                f"({analysed.detection_rate - baseline.detection_rate:+.1f})"
            )
            print(
                f"false-positive rate {baseline.false_positive_rate:5.1f}% -> "
                f"{analysed.false_positive_rate:5.1f}%  "
                f"({analysed.false_positive_rate - baseline.false_positive_rate:+.1f})"
            )
            closed = {r.trace.id for r in baseline.bypasses} - {r.trace.id for r in analysed.bypasses}
            opened = {r.trace.id for r in analysed.bypasses} - {r.trace.id for r in baseline.bypasses}
            print(f"bypasses closed     {sorted(closed) or 'none'}")
            if opened:
                print(f"bypasses OPENED     {sorted(opened)}")
        report = analysed
    else:
        report = evaluate_corpus(traces, behavioral=args.behavioral, policy=args.policy)
        print(json.dumps(report.to_dict(), indent=2) if args.json else report.render())

    failed = False
    if args.min_detection_rate is not None and report.detection_rate < args.min_detection_rate:
        print(
            f"\nFAIL: detection rate {report.detection_rate:.1f}% "
            f"< {args.min_detection_rate:.1f}%",
            file=sys.stderr,
        )
        failed = True
    if (
        args.max_false_positive_rate is not None
        and report.false_positive_rate > args.max_false_positive_rate
    ):
        print(
            f"\nFAIL: false-positive rate {report.false_positive_rate:.1f}% "
            f"> {args.max_false_positive_rate:.1f}%",
            file=sys.stderr,
        )
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
