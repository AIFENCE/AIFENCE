# Fence Flow: Executable Product Contract

```mermaid
flowchart LR
    A[Authenticated agent] --> Q[Quality admission]
    Q -->|stable findings + score| G[Guard policy]
    G -->|matched rule + reason codes| B[Durable Bus handoff]
    B --> R[Receiving agent]
    Q -. correlation .-> O[Telemetry]
    G -. signed decision evidence .-> O
    B -. message metadata .-> O
    B --> AU[fence.completed audit event]
```

The critical distinction is that each stage adds a different property: Quality establishes admissibility, Guard establishes authority, and Bus establishes durable minimum-sufficient transfer. No tier inherits the trust conclusion of another tier.
