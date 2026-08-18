# AIFENCE Python client

Official synchronous and asynchronous Python client for the AIFENCE guard tier (the security control plane).

## Installation

For the release-candidate source tree:

```bash
pip install ./sdks/python
```

Published packages will use:

```bash
pip install aifence-client
```

## Usage

```python
from aifence_client import AifenceClient

with AifenceClient(
    "https://aifence.example.com/guard",
    api_key="replace-with-secret-manager-value",
) as client:
    decision = client.decide({
        "trace_id": "trc_example_0001",
        "principal": {"type": "human", "id": "operator-1"},
        "agent": {
            "id": "agt_example",
            "instance_id": "instance-1",
            "version": "1.0.0",
            "workload_identity": "spiffe://example.com/agent",
            "model": "provider/model",
            "instruction_hash": "a" * 64,
        },
        "objective": {"declared_goal": "Read approved record"},
        "action": {"type": "tool.call", "operation": "read"},
        "security_context": {"environment": "production"},
    })
    print(decision["outcome"])
```

The client requires HTTPS, disables redirects, supports mTLS, applies bounded retries to safe requests, and generates idempotency keys for decision and broker operations.

See the repository [SDK guide](../../docs/SDK.md) for the complete API and framework integrations.

## License

This SDK is licensed under the [Apache License 2.0](LICENSE).
