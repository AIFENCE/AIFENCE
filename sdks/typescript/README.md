# AIFENCE TypeScript client

Official TypeScript client for the AIFENCE guard tier (the security control plane).

## Build from the repository

```bash
npm ci --ignore-scripts
npm run build
```

## Usage

```ts
import {AifenceClient} from "@aifence/client";

const client = new AifenceClient(
  "https://aifence.example.com/guard",
  process.env.AIFENCE_API_KEY!,
);

const decision = await client.decide({
  trace_id: "trc_example_0001",
  principal: {type: "human", id: "operator-1"},
  agent: {
    id: "agt_example",
    instance_id: "instance-1",
    version: "1.0.0",
    workload_identity: "spiffe://example.com/agent",
    model: "provider/model",
    instruction_hash: "a".repeat(64),
  },
  objective: {declared_goal: "Read approved record"},
  action: {type: "tool.call", operation: "read"},
  security_context: {environment: "production"},
});

console.log(decision.outcome);
```

See the repository [SDK guide](../../docs/SDK.md) for the complete API.

## License

This SDK is licensed under the [Apache License 2.0](LICENSE).
