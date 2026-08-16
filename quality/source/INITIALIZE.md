<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: INITIALIZE
Module-Version: 2
Last-Updated: 2026-08-09
-->

# Initialize Standards Pack
<!-- id: initialize.root -->

Locate and read `README.md` first.

Treat `README.md` as the authoritative operating and routing specification for this pack.

Follow its initialization, project-resolution, semantic-profile, lazy-loading, manifest-addressing, dependency, risk-trigger, precedence, validation, and output rules.

Do not preload the remaining files.

If `PROJECT.md` exists, process it according to `README.md`. Otherwise use the user's current prompt as the project request.

If the same user message already contains a creation request, continue immediately into classification/routing/execution after initialization; do not stop and ask the user to resubmit it.

Only when the user requested initialization with no creation task should the response be:

`Pack initialized. Ready for a creation request.`

# Control Plane Hook
<!-- id: initialize.control-plane-hook -->

Initialization is not complete for a creation task until the authoritative entry point is verified and the creation type is resolved far enough to identify the applicable control bundle in `CONTROL_INDEX.md`. Do not preload control shards during initialization; retrieve exact capability sections only when their decision point is reached.

# Control Plane Hooks
<!-- id: initialize.control-plane-hooks -->

When this module is active, use `CONTROL_INDEX.md` to retrieve only the capability sections relevant to the current decision. Applicable capabilities include:

- **Authoritative-entry verification** — `controls/01-initialization-precedence-and-agent-control.md` (BQ-0001–BQ-0005)
- **Initialization completion state** — `controls/01-initialization-precedence-and-agent-control.md` (BQ-0011–BQ-0015)

These hooks are routing pointers, not permission to preload the listed shards. Evidence Gates control pass/fail claims.
