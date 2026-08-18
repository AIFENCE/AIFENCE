# SAGE + A2A

SAGE does not replace the Agent2Agent lifecycle. It supplies the semantic payload carried by an A2A structured data part.

Python runtimes use `aifence.bus.a2a_adapter.pack_data_part` to create the data part and `aifence.bus.a2a_adapter.unpack_data_part` to recover the SAGE wire object. REST runtimes use `/v1/a2a/pack` and `/v1/a2a/unpack`.

Peers advertise the SAGE A2A extension identifier `urn:uuid:f81af17b-cc6a-5cdf-8a0f-51116b2e6a8d` when both sides support the binding. A2A continues to own agent cards, messages, tasks, streaming, cancellation, and collaboration lifecycle.
