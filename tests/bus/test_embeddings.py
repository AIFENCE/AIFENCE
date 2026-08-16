import httpx

from aifence.bus.embeddings import OpenAICompatibleEmbeddingProvider, cosine


def test_openai_compatible_embedding_provider():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/embeddings"
        assert request.headers["authorization"] == "Bearer secret"
        return httpx.Response(200, json={"data": [{"embedding": [3.0, 4.0]}]})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OpenAICompatibleEmbeddingProvider(
        api_url="https://embedding.invalid/v1",
        api_key="secret",
        model="learned-embedding",
        client=client,
    )
    vector = provider.embed("refund requested")
    assert vector == [0.6, 0.8]
    assert cosine(vector, vector) == 1.0
