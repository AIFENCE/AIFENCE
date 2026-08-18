# SAGE for Claude

SAGE remains outside the model provider. Claude clients with remote MCP support connect to the deployed SAGE `/mcp` endpoint using the service authentication policy configured by the operator.

Peer-to-peer agent runtimes may carry compact SAGE wire data through the A2A binding exposed by `/v1/a2a/pack` and `/v1/a2a/unpack`.

SAGE persistence, receiver knowledge, codebooks, references, delivery state, authorization, and semantic-learning state remain owned by the SAGE runtime.
