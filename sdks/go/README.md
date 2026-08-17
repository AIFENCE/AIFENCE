# AIFENCE Go client

Official Go client for the AIFENCE guard tier (the security control plane).

```go
client, err := agentdance.NewClient(
    "https://aifence.example.com/guard",
    os.Getenv("AIFENCE_API_KEY"),
    nil,
)
if err != nil {
    log.Fatal(err)
}
```

The client requires HTTPS, applies bounded request behavior, and exposes the core decision, capability, broker, lifecycle, protocol, and audit APIs.

See the repository [SDK guide](../../docs/SDK.md) for the complete integration model.

## License

This SDK is licensed under the [Apache License 2.0](LICENSE).
