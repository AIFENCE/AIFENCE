"""Held-out scenario fixture for the sealed evaluation harness (issue #22, stage 3).

This module is the UNSEEN conversation for ``--held-out`` mode: a NEW project
("Orion") that the codebook-establishment phase has never seen, structured in
parallel to the RFC Phoenix fixture so the same deterministic scoring machinery
(``compression_benchmark``'s ``read_state`` / ``evaluate_turn`` /
``ground_truth_answers`` / ``fidelity_critical``) applies unchanged.

Phases (mirrors the RFC Phoenix fixture but with distinct names and facts;
the compiled establishment canonicals are NOT all distinct from Phoenix --
2 of the 5 are shared: '12' (the bare number split out of "Python 3.12.")
and 'database_migrations_must_be_reviewed_by_the_platform_team' (the
generic migration-review sentence kept verbatim for the fidelity checker);
the held-out UPDATE canonicals are fully disjoint from Phoenix):

* Phase 1 -- establishment: ``ESTABLISHMENT_SHARED_CONTEXT`` is transmitted
  once.  In held-out mode this is the ONLY material the SAGE variants'
  FROZEN codebook is compiled from (see ``establishment_canonicals``); the
  held-out updates below are deliberately NOT part of it.
* Phase 2 -- five held-out updates (``HELDOUT_UPDATES[0:5]``) mutate the
  project state; ``HELDOUT_STATE_DICTS`` tracks the state after each one
  (turn 0 = establishment state, turns 1-5 = after updates 1-5) and
  ``HELDOUT_CHANGE_MARKERS`` carries the per-turn "what changed" markers.
* Phase 3 -- the downstream task is scored against the embedded ground-truth
  answer key exactly as in the standard scenario.

Content-type coverage (issue #22 section C): the fixture contains at least one
update per required content type, each tagged in a comment below:

  1. paraphrased concept      -- U1 restates the deploy gate / failure in new
                                 words ("cannot deploy until the suite is
                                 green" style, not the establishment sentence);
  2. unseen value             -- U2 introduces Python 3.13, a value never seen
                                 during establishment (3.12 was);
  3. new combination of known concepts -- U3 composes billing service +
                                 Commerce team + integration tests + platform
                                 team + migration review in a NEW relation;
  4. changed state            -- U4 flips ``failed_tests`` 3 -> 1;
  5. contradiction            -- U5 approves the migration DESPITE the
                                 remaining test failure (failure vs approval);
  6. negation                 -- U6 negates a fact ("No ... failures");
  7. numeric constraint       -- U7 pins a deploy gate threshold ("at least
                                 80 percent ... to pass");
  8. delayed-relevance        -- U8 plants a fact that only matters later
                                 ("will require ... later this year").

The harness machinery is frozen at six turns (turn 0 = shared context, turns
1-5 = updates), so ``HELDOUT_STATE_DICTS``/``HELDOUT_CHANGE_MARKERS`` cover the
first five updates; updates 6-8 complete the content-type coverage of the
fixture itself (the FROZEN-CODEBOOK-PROOF and coverage tests compile every
update).

The module is fully embedded and deterministic: constants only, no RNG, no
timestamps, no external files, and ``sage_plugin`` is NEVER imported at module
import time (``establishment_canonicals`` imports the compiler lazily so the
fixture stays importable before ``SAGE_DATABASE_URL`` is bound).
"""

from __future__ import annotations

from typing import Any

#: Phase-1 establishment context for the held-out project.  Genuinely UNSEEN
#: relative to Phoenix: distinct project, distinct service ownership fact and
#: a reworded deploy gate, so the compiled canonical clauses differ from the
#: standard scenario (the generic constraint sentences keep the exact phrases
#: the deterministic fidelity checker keys on -- "production deployment" /
#: "integration test" / "pass" and "migration" / "review" / "platform team").
ESTABLISHMENT_SHARED_CONTEXT = (
    "Project Orion uses Python 3.12. "
    "Every production deployment requires the integration test suite to pass. "
    "The billing service is owned by the Commerce team. "
    "Database migrations must be reviewed by the platform team."
)

#: Held-out updates.  The harness consumes the first five (turns 1-5); updates
#: 6-8 complete the issue section-C content-type coverage of the fixture.
HELDOUT_UPDATES = [
    # (1) paraphrased concept: the deploy gate / failure restated in new words.
    "Project Orion is blocked because three of its integration tests failed.",
    # (2) unseen value: Python 3.13 was never mentioned during establishment.
    "The Commerce team upgraded Project Orion to Python 3.13.",
    # (3) new combination of known concepts: billing service + Commerce team +
    #     integration tests + platform team + migration review in a NEW gate.
    "Deploying the billing service now requires the Commerce team's integration tests to pass and the platform team's migration review; one database migration failure remains.",
    # (4) changed state: failed_tests 3 -> 1.
    "The Commerce team fixed two integration test failures.",
    # (5) contradiction: the migration is approved DESPITE the remaining test
    #     failure (approval vs failure).
    "The platform team approved the migration despite the remaining test failure.",
    # (6) negation: a fact is negated.
    "No new integration test failures were introduced by the Python upgrade.",
    # (7) numeric constraint: the deploy gate is pinned to a threshold.
    "Orion's deploy gate requires at least 80 percent of the integration test suite to pass.",
    # (8) delayed-relevance: a fact that only matters later.
    "The billing service's Q3 quota migration will require a new platform review later this year.",
]

#: Per-turn state after each consumed update (turn 0 = establishment state;
#: turns 1-5 = after updates 1-5).  Keeps the scoring machinery's fields
#: (deployment_allowed / failed_tests / migration_approved / blocker) plus the
#: project identity and python version consistent with the update arc:
#: blocked (3 failing tests) -> Python 3.13 -> migration failure joins the
#: gate -> two test failures fixed -> migration approved despite the leftover
#: test failure.
HELDOUT_STATE_DICTS = [
    {"project": "orion", "python_version": "3.12", "deployment_allowed": False, "failed_tests": 0, "migration_approved": False, "blocker": "none"},
    {"project": "orion", "python_version": "3.12", "deployment_allowed": False, "failed_tests": 3, "migration_approved": False, "blocker": "integration_tests"},
    {"project": "orion", "python_version": "3.13", "deployment_allowed": False, "failed_tests": 3, "migration_approved": False, "blocker": "integration_tests"},
    {"project": "orion", "python_version": "3.13", "deployment_allowed": False, "failed_tests": 3, "migration_approved": False, "blocker": "migration"},
    {"project": "orion", "python_version": "3.13", "deployment_allowed": False, "failed_tests": 1, "migration_approved": False, "blocker": "migration"},
    {"project": "orion", "python_version": "3.13", "deployment_allowed": False, "failed_tests": 1, "migration_approved": True, "blocker": "integration_tests"},
]

#: Per-turn "what changed since the previous update?" markers, normalized on
#: BOTH sides per the proven convention (``evaluate_turn`` matches
#: ``_norm(marker) in _norm(text)``): natural-language phrases and/or rendered
#: state forms.
HELDOUT_CHANGE_MARKERS: dict[int, list[str]] = {
    1: ["integration tests failed", "blocked", "blocker: integration_tests"],
    2: ["python 3.13", "python_version: 3.13"],
    3: ["billing service", "migration failure remains", "blocker: migration"],
    4: ["fixed two", "failed_tests: 1"],
    5: ["approved the migration", "migration_approved"],
}


def establishment_canonicals(cb: Any | None = None) -> list[str]:
    """The FROZEN codebook source: canonical clauses of the ESTABLISHMENT
    material ONLY, sorted and deduplicated (the exact shape the SAGE variants'
    codebook registration order needs -- deterministic).

    ``cb`` is the loaded ``compression_benchmark`` module (the harness passes
    it for symmetry with ``cb._sage_specs()``); ``compile_content`` is
    imported LAZILY so this module never imports ``sage_plugin`` at import
    time (the standalone CLI binds ``SAGE_DATABASE_URL`` before any
    ``sage_plugin`` import).
    """
    from aifence.bus.compiler import compile_content  # lazy (see module docstring)

    compile_fn = getattr(cb, "compile_content", compile_content)
    return sorted({unit.canonical for unit in compile_fn(ESTABLISHMENT_SHARED_CONTEXT)})
