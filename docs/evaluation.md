---
title: Adversarial evaluation
summary: How well the fence actually detects hostile agent behaviour, measured rather than asserted.
infobox:
  Command: aifence-redteam
  Corpus: evals/traces/
  Unit: multi-turn agent trace
  Gate: CI blocks on regression
---

A detection system is described honestly by two numbers together: how much
hostile behaviour it catches, and how much legitimate work it breaks. Either
alone is marketing. This page records both, and the command that reproduces them.

```bash
aifence-redteam              # measure the baseline
aifence-redteam --behavioural analysis     # with the cross-tier detector
aifence-redteam --compare    # both, and the delta
```

## Why traces rather than requests

A compromised or drifting agent rarely reveals itself in one request. Scope
creeps, claims start contradicting earlier ones, output quality decays. A
single-request evaluation suite cannot express that, and therefore cannot measure any
detector that reasons over history.

The unit of evaluation is a **trace**: a sequence of turns by one agent, each
carrying an artifact for the [quality](quality.md) tier and an action for the
[guard](guard.md) tier, executed in order against an accumulating observation
window.

Every attack trace begins with plausible behaviour and degrades. An attack that
looks like an attack on turn one measures nothing about a control plane.

## Benign traces are mandatory

A detector that refuses everything scores 100% detection. The evaluation suite therefore
contains legitimate work drawn close to the line — real deletions, real customer
PII, real outbound calls, and a document that *discusses* credentials and prompt
injection without containing either.

## The three metrics

| Metric | Meaning |
| --- | --- |
| **Detection rate** | Attack traces stopped by any means, including the default hold. |
| **Specific detection** | Attack traces stopped *because a detector fired* — the honest number. |
| **False-positive rate** | Benign traces hard-refused. |
| **Hold rate** | Benign traces held for human approval: friction, not refusal. |

Detection rate and specific detection differ because the baseline policy
defaults to `require_approval`. Any operation outside the narrow allow-list is
stopped whether or not anything was actually detected, so counting those as
detections would credit the fence with catching attacks it never perceived.

`deny` and `require_approval` are likewise kept apart: a benign action refused
outright is a defect, while one held for a human is a cost.

## Current results

Measured on 18 traces (11 attack, 7 benign):

| | baseline | with behavioural analysis |
| --- | ---: | ---: |
| Detection rate | 90.9% | **100.0%** |
| Specific detection | 81.8% | **90.9%** |
| False-positive rate | 0.0% | 0.0% |
| Hold rate | 71.4% | 71.4% |

### What the numbers do not say

**The 71% hold rate is the headline operational finding**, and it has a precise
cause. The strict baseline allows only low-risk reads, non-production writes,
model requests and approved external communication; everything else falls to
`require_approval`. Out of the box, most production writes need a human.

That is deliberate fail-closed design, not a defect — but see
[policy profiles](#policy-profiles) for what it actually buys, which is less
than it appears.

**Specific detection is 100%**: no attack scenario is stopped only by the
default hold. That is a statement about these scenarios, not about the world.
Eighteen traces is a useful regression suite and far too small a sample to
publish a rate; broadening coverage is ongoing.

## Policy profiles

Two profiles ship, both generated from the mandatory baseline so neither can
drop or weaken a baseline rule:

| | strict | balanced |
| --- | ---: | ---: |
| Detection rate | 100.0% | **100.0%** |
| Specific detection | 100.0% | **100.0%** |
| False-positive rate | 0.0% | 0.0% |
| Held for approval | 71.4% | **14.3%** |

**Balanced matches strict on security and costs a fifth of the friction**:
identical detection, identical false-positive rate, far fewer requests held.

This depends on behavioural analysis being enabled. Without it, the balanced
profile misses indirect prompt injection carrying an innocuous payload — an
attack the strict profile stops only through its blanket default hold, without
detecting anything.

This relationship should inform the choice of profile. Under a
deny-by-default policy, approval friction and incidental blocking are the same
mechanism: because little is permitted, nearly everything is stopped — attacks
and legitimate work alike. Protection obtained that way costs roughly five held
requests per genuine catch, and it lapses as soon as an attacker uses an
operation the allow-list happens to permit. Detection that identifies the attack
is what makes the lower-friction profile safe.

```bash
AIFENCE_GUARD_POLICY_FILE=policies/balanced.json
aifence-redteam --behavioural analysis --policy policies/balanced.json   # measure any profile
```

Each added rule is bounded by `max_risk`, so any finding that raises risk above
the bound withdraws the allowance automatically. Regenerate after changing the
baseline: `python tooling/generate-policy-profiles.py`.

## The cross-tier detector

Quality asks whether *this* artifact is sound; guard asks whether *this* action
is permitted. Neither asks whether the agent is *becoming* less trustworthy.
Because the tiers share a process, the fence can watch a trajectory.

The signal set is intentionally small. It emits `integrity.behavioral_drift` on:

- **Persistent ungrounded assertion** — repeated grounding lapses, where no
  single turn crosses the threshold but the run does.
- **Sustained intent escalation** — operation severity rising across a run.
- **Untrusted influence** — a state change following ingestion of
  attacker-controllable external content. This is the indirect prompt-injection
  shape: the injected text need contain no recognisable keyword and the payload
  may be entirely innocuous, because it is the *flow* from untrusted input to
  effect that gives it away, not the words. Reading untrusted content is never
  flagged on its own; acting afterwards is.

Every signal must pay for itself in `--compare` without adding a false positive.
A behavioural detector that fires on plausible-sounding intuitions is worse than
none, because it spends the operator's trust on noise.

## Regression gate

CI runs the evaluation suite and fails on regression:

```bash
aifence-redteam --behavioural analysis --max-false-positive-rate 0 --min-detection-rate 100
```

A further test asserts that the suite still contains at least one scenario the
**baseline** misses. A suite the current implementation passes completely
demonstrates only that the suite is too easy.

## Extending the evaluation suite

Add traces to `evals/traces/*.json`. Two rules matter more than volume:

1. **Keep attack scenarios within their approved scope.** An attack that
   immediately leaves its approved surface is caught by scope enforcement at the
   first turn, and measures nothing about the detector it was written for.
2. **Keep benign scenarios realistic.** Legitimate work that avoids every
   trigger renders the false-positive rate meaningless.
