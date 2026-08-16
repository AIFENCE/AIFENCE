# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from collections.abc import Sequence
from typing import Protocol

import httpx


class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> list[float]: ...


def _normalize(vector: Sequence[float]) -> list[float]:
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [float(v) / norm for v in vector]


class HashEmbeddingProvider:
    """Dependency-free deterministic feature hashing for local/offline operation.

    It is intentionally not presented as a learned semantic model. Production
    deployments that need semantic clustering can switch to the OpenAI-compatible
    learned embedding provider below without changing the codec API.
    """

    def __init__(self, dimensions: int = 96) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        tokens = re.findall(r"[a-z0-9_]+", text.lower())
        features: Counter[int] = Counter()
        for token in tokens:
            grams = [token] + [token[i : i + 3] for i in range(max(0, len(token) - 2))]
            for gram in grams:
                digest = hashlib.blake2b(gram.encode(), digest_size=8).digest()
                raw = int.from_bytes(digest, "big")
                idx = raw % self.dimensions
                sign = 1 if ((raw >> 8) & 1) else -1
                features[idx] += sign
        return _normalize([float(features[i]) for i in range(self.dimensions)])


class OpenAICompatibleEmbeddingProvider:
    """Learned embedding provider using the OpenAI-compatible `/embeddings` API."""

    def __init__(
        self,
        *,
        api_url: str,
        api_key: str,
        model: str,
        timeout_seconds: float = 10.0,
        client: httpx.Client | None = None,
    ) -> None:
        if not api_url.strip():
            raise ValueError("embedding_api_url is required for learned embeddings")
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._owned_client = client is None
        self.client = client or httpx.Client(timeout=timeout_seconds)

    def embed(self, text: str) -> list[float]:
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        response = self.client.post(
            f"{self.api_url}/embeddings",
            headers=headers,
            json={"model": self.model, "input": text},
        )
        response.raise_for_status()
        payload = response.json()
        try:
            vector = payload["data"][0]["embedding"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("embedding service returned an invalid response") from exc
        if not isinstance(vector, list) or not vector:
            raise ValueError("embedding service returned an empty vector")
        return _normalize([float(v) for v in vector])

    def close(self) -> None:
        if self._owned_client:
            self.client.close()


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return float(sum(x * y for x, y in zip(a, b, strict=True)))
