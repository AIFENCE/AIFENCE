# SPDX-License-Identifier: AGPL-3.0-or-later
"""Adversarial evaluation for the fence.

The question this package exists to answer is not "does the fence work on the
examples we thought of" but **what fraction of adversarial agent behaviour does
it actually catch, and how often does it cry wolf**. Those two numbers together
are the only honest description of a detection system; either alone is
marketing.

Three properties distinguish this from a unit-test corpus:

* **Traces, not requests.** An agent that has been compromised or has drifted
  reveals itself over a sequence of turns — scope creeps, claims start
  contradicting earlier ones, output quality decays. A single-request corpus
  cannot express that, and therefore cannot measure any detector that reasons
  over history.
* **Benign traces are mandatory.** A detector that blocks everything scores
  100% detection. Without a false-positive rate measured on realistic benign
  behaviour, a detection rate means nothing.
* **Bypasses are recorded, not hidden.** The report names every attack trace
  that got through, so the gaps are visible and regressions are catchable.
"""
from __future__ import annotations

from .corpus import Trace, Turn, load_corpus
from .report import EvaluationReport, FamilyResult, TraceResult
from .runner import evaluate_corpus, evaluate_trace

__all__ = [
    "EvaluationReport",
    "FamilyResult",
    "Trace",
    "TraceResult",
    "Turn",
    "evaluate_corpus",
    "evaluate_trace",
    "load_corpus",
]
