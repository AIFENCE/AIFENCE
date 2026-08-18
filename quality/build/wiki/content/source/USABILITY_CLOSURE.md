<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: USABILITY_CLOSURE
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->

# Usability Closure Standard
<!-- id: usability-closure.root -->

Purpose: close the remaining gap between feature-complete artifacts and interfaces that are immediately understandable, efficient, recoverable, and low-friction in real use.

This standard does **not** reward adding more controls. It rewards reducing unnecessary decisions while preserving task-critical information, state, accessibility, and domain specificity.


## Enabled-Control Closure
<!-- id: usability-closure.enabled-control-closure -->

Every rendered enabled control MUST resolve to an observable behavior class: navigation, state/action mutation, form/input behavior, disclosure/menu/dialog behavior, download/export, or explicit local/demo feedback. A control is not complete because it looks clickable.

Production/high-fidelity interactive acceptance requires a control inventory and direct exercise of every enabled visible control in its supported state. Any control with no observable intended effect is a dead control and MUST be implemented, removed, or explicitly disabled with a user-visible reason. Placeholder buttons, inert navigation tabs, period selectors, overflow menus, “More filters,” row action menus, and decorative anchors styled as controls are prohibited.

Disabled controls require a truthful reason or surrounding context when the user could reasonably expect availability. Do not mark unfinished functionality disabled merely to satisfy the gate when the requested production scope requires that functionality.

# Primary Task Orientation
<!-- id: usability-closure.primary-task-orientation -->

Every substantial screen or document interaction surface MUST make the following legible without exploratory clicking:

1. where the user is;
2. what state the work is in;
3. what the next meaningful action is;
4. what information is required before acting;
5. what will happen after the action;
6. how to recover if the action cannot complete.

The strongest visual element is not automatically the primary action. Priority follows user-job importance, risk, and current state.

# Task Friction Budget
<!-- id: usability-closure.friction-budget -->

For each P0/P1 user job, record a **Task Friction Trace**:

```text
Entry point
Orientation cue
Required decisions
Required inputs
Primary action
Confirmation / feedback
Recovery path
Exit / continuation
```

Reject avoidable friction such as:

- repeated decisions with no new information;
- mandatory fields that do not affect the task;
- hidden prerequisites;
- action labels that describe UI mechanics instead of user outcomes;
- context loss after filter, sort, selection, or validation;
- needless modal or navigation transitions;
- duplicated primary CTAs competing for attention;
- irreversible actions presented with the same visual weight as routine actions.

There is no universal click-count target. A longer path can be better when risk or evidence requires deliberate review. The acceptance criterion is **minimum justified friction**, not minimum interactions.

# Action Hierarchy & Progressive Disclosure
<!-- id: usability-closure.action-hierarchy -->

Classify actions as Primary, Secondary, Contextual, Destructive, Recovery, or Navigation.

- One task state SHOULD have one visually dominant Primary action unless the user genuinely faces a fork of equal importance.
- Contextual actions SHOULD remain near the object they affect.
- Rare actions SHOULD use progressive disclosure rather than permanent toolbar crowding.
- Destructive actions MUST be visually and behaviorally separated from routine continuation.
- Hidden overflow menus MUST NOT contain the only route to a P0 action unless the trigger clearly communicates the action family and remains accessible.

# Input & Decision Efficiency
<!-- id: usability-closure.input-decision-efficiency -->

Forms, filters, selectors, and decision controls MUST minimize memory load and re-entry.

Prefer visible defaults, preserved state, inline constraints, input grouping, useful examples, explicit optionality, and validation near the affected control. Do not clear user input after recoverable errors.

For dense workspaces, preserve search/filter/sort/selection context across detail views and recovery states.

# Feedback & Recovery Legibility
<!-- id: usability-closure.feedback-recovery -->

Every consequential action MUST produce feedback proportional to its effect:

- immediate local feedback for reversible UI changes;
- explicit pending/saving state for delayed actions;
- clear success state when completion changes user expectations;
- error feedback that states what failed, what was preserved, and what the user can do next;
- retry/reopen/undo paths when applicable;
- no silent dismissal of errors or state resets.

# Navigation & State Continuity
<!-- id: usability-closure.state-continuity -->

Users SHOULD retain orientation when moving between list/detail, filter/results, step/step, and error/recovery states. Breadcrumbs, selected-nav state, titles, step indicators, persistent filters, and return-focus behavior are evidence mechanisms—not decorative requirements.

# Touch, Pointer & Keyboard Efficiency
<!-- id: usability-closure.input-modalities -->

Task completion MUST remain efficient with keyboard, touch, and pointer where those modalities apply. Avoid hover-only discovery, tiny dense targets, focus traps, and mobile action layouts that require precision tapping or horizontal hunting.

# Usability Evidence Matrix
<!-- id: usability-closure.evidence-matrix -->

For each P0/P1 path, capture:

```text
Path ID
Entry cue visible? PASS/FAIL
Primary action unambiguous? PASS/FAIL
Required information adjacent? PASS/FAIL
State preserved? PASS/FAIL
Success feedback? PASS/FAIL/N/A
Error/recovery path? PASS/FAIL/N/A
Keyboard completion? PASS/FAIL/N/A
Touch/mobile completion? PASS/FAIL/N/A
Avoidable friction found
Repair applied
Revalidation evidence
```

# Acceptance
<!-- id: usability-closure.acceptance -->

Usability cannot PASS from feature count, a sampled subset of buttons, or lack of horizontal overflow alone. It requires exhaustive enabled-control closure plus direct task-path evidence showing orientation, action clarity, state continuity, efficient input, feedback, recovery, and 320/390 task preservation for applicable P0/P1 jobs.
