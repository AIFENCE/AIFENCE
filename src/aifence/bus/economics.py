# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.parse import urlparse

import httpx

from .protocol_spec import canonical_json_bytes


class TokenCounter(Protocol):
    name: str
    exact: bool

    def count(self, text: str) -> int: ...


@dataclass
class EstimateTokenCounter:
    chars_per_token: float = 4.0
    name: str = "character-estimate"
    exact: bool = False

    def count(self, text: str) -> int:
        return math.ceil(len(text) / self.chars_per_token)


class TiktokenCounter:
    exact = True

    def __init__(self, *, model: str | None = None, encoding: str | None = None) -> None:
        try:
            import tiktoken
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("install SAGE with the 'bench' extra for tiktoken counting") from exc
        if encoding:
            self._enc = tiktoken.get_encoding(encoding)
            self.name = f"tiktoken:{encoding}"
        elif model:
            self._enc = tiktoken.encoding_for_model(model)
            self.name = f"tiktoken:{model}"
        else:
            raise ValueError("tiktoken counter requires model or encoding")

    def count(self, text: str) -> int:
        return len(self._enc.encode(text))


class HttpTokenCounter:
    exact = True

    def __init__(self, *, endpoint: str, model: str = "", bearer_token: str | None = None, timeout: float = 10.0) -> None:
        if not endpoint.startswith(("http://", "https://")):
            raise ValueError("HTTP tokenizer endpoint must be http(s)")
        self.endpoint = endpoint
        self.model = model
        self.bearer_token = bearer_token
        self.timeout = timeout
        self.name = f"http:{model or endpoint}"

    def count(self, text: str) -> int:
        headers = {"authorization": f"Bearer {self.bearer_token}"} if self.bearer_token else {}
        response = httpx.post(
            self.endpoint,
            json={"text": text, "model": self.model},
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        body = response.json()
        tokens = body.get("tokens")
        if not isinstance(tokens, int) or tokens < 0:
            raise ValueError("tokenizer endpoint must return {'tokens': nonnegative integer}")
        return tokens


def make_counter(spec: dict[str, Any], *, chars_per_token: float = 4.0) -> TokenCounter:
    kind = str(spec.get("kind", "estimate"))
    if kind == "tiktoken":
        return TiktokenCounter(model=spec.get("model"), encoding=spec.get("encoding"))
    if kind == "http":
        return HttpTokenCounter(
            endpoint=str(spec.get("endpoint", "")),
            model=str(spec.get("model", "")),
            bearer_token=spec.get("bearer_token"),
            timeout=float(spec.get("timeout_seconds", 10.0)),
        )
    if kind == "estimate":
        return EstimateTokenCounter(chars_per_token=float(spec.get("chars_per_token", chars_per_token)))
    raise ValueError(f"unsupported tokenizer kind: {kind}")


def text_for_representation(value: Any) -> str:
    if isinstance(value, str):
        return value
    return canonical_json_bytes(value).decode("utf-8")


def strategy_cost(*, input_tokens: int, output_tokens: int, input_per_million: float, output_per_million: float) -> float:
    return (input_tokens / 1_000_000) * input_per_million + (output_tokens / 1_000_000) * output_per_million


def score_observation(observation: dict[str, Any], price: dict[str, float]) -> dict[str, Any]:
    input_tokens = int(observation.get("input_tokens", 0))
    output_tokens = int(observation.get("output_tokens", 0))
    success = observation.get("task_success")
    model_cost = observation.get("provider_cost_usd")
    if model_cost is None:
        model_cost = strategy_cost(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_per_million=float(price.get("input_per_million", 0.0)),
            output_per_million=float(price.get("output_per_million", 0.0)),
        )
    model_cost = float(model_cost)
    infrastructure_cost = float(observation.get("infrastructure_cost_usd", 0.0) or 0.0)
    retrieval_cost = float(observation.get("retrieval_cost_usd", 0.0) or 0.0)
    retry_cost = float(observation.get("retry_cost_usd", 0.0) or 0.0)
    cost = model_cost + infrastructure_cost + retrieval_cost + retry_cost
    wire_bytes = observation.get("wire_bytes")
    bits = int(wire_bytes) * 8 if wire_bytes is not None else None
    return {
        **observation,
        "model_cost": model_cost,
        "cost": cost,
        "successful_tasks_per_dollar": (
            float(success) / cost if success is not None and cost > 0 else None
        ),
        "task_utility_per_bit": (float(success) / bits if success is not None and bits and bits > 0 else None),
    }


def benchmark_representations(
    *,
    representations: dict[str, Any],
    tokenizer: dict[str, Any],
    task_success: dict[str, float] | None = None,
    price: dict[str, float] | None = None,
    chars_per_token: float = 4.0,
) -> dict[str, Any]:
    counter = make_counter(tokenizer, chars_per_token=chars_per_token)
    task_success = task_success or {}
    price = price or {"input_per_million": 0.0, "output_per_million": 0.0}
    rows: list[dict[str, Any]] = []
    for strategy, representation in representations.items():
        text = text_for_representation(representation)
        tokens = counter.count(text)
        row = score_observation(
            {
                "strategy": strategy,
                "input_tokens": tokens,
                "output_tokens": 0,
                "wire_bytes": len(text.encode("utf-8")),
                "task_success": task_success.get(strategy),
            },
            price,
        )
        rows.append(row)
    baseline = next((row for row in rows if row["strategy"] == "raw_history"), None)
    if baseline is not None:
        for row in rows:
            row["net_savings_vs_raw_history"] = float(baseline["cost"]) - float(row["cost"])
            baseline_bytes = int(baseline.get("wire_bytes") or 0)
            row_bytes = int(row.get("wire_bytes") or 0)
            row["wire_reduction_vs_raw_history"] = (1.0 - row_bytes / baseline_bytes) if baseline_bytes else None
    return {
        "tokenizer": {"name": counter.name, "exact": counter.exact},
        "price": price,
        "strategies": rows,
        "warning": None if counter.exact else "token counts are estimates; do not use them as provider billing proof",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Score recorded SAGE strategy economics")
    parser.add_argument("input", help="JSON file containing observations and price")
    args = parser.parse_args()
    payload = json.loads(open(args.input, encoding="utf-8").read())
    price = payload.get("price", {})
    rows = [score_observation(row, price) for row in payload.get("observations", [])]
    print(json.dumps({"price": price, "observations": rows}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


def run_sage_economics_benchmark(db: Any, settings: Any, request: Any) -> dict[str, Any]:
    """Compare model-token economics for the protocol's required baselines.

    The harness produces raw history, JSON state, state+ref, structural SAGE,
    SAGE with the current learned codebook, and SAGE with receiver knowledge.
    Summary/RAG representations are included only when supplied by a real caller;
    SAGE never fabricates model or retriever outputs. Task success is caller-observed.
    """
    from .codec import SageCodec
    from .references import ReferenceStore
    from .schemas import Budget, EncodeRequest

    content = request.content
    representations: dict[str, Any] = {
        "raw_history": request.raw_history if request.raw_history is not None else content,
        "json_state": content,
    }
    if request.summarized_history is not None:
        representations["summarized_history"] = request.summarized_history
    if request.rag is not None:
        representations["rag"] = request.rag

    ref = ReferenceStore(db, settings).put(
        content,
        workspace=request.workspace,
        owner="benchmark",
        acl=[request.receiver],
        tier="hot",
        encrypt=False,
    )
    db.flush()
    representations["state_refs"] = {"ref": ref.id}

    common = dict(
        content=content,
        sender="benchmark",
        receiver=request.receiver,
        workspace=request.workspace,
        budget=Budget(max_tokens=request.budget_tokens),
        use_cache=False,
        auto_learn=False,
        record_learning=False,
    )

    plain_settings = settings.model_copy(
        update={
            "codebook": "__benchmark_empty__",
            "core_codebook": "__benchmark_empty_core__",
        }
    )
    plain_codec = SageCodec(db, plain_settings)
    plain_result = plain_codec.encode(
        EncodeRequest(
            **common,
            codebook="__benchmark_empty__",
            use_receiver_knowledge=False,
        )
    )
    representations["sage"] = plain_codec.compact(plain_result.packet)

    learned_codec = SageCodec(db, settings)
    learned_result = learned_codec.encode(
        EncodeRequest(
            **common,
            codebook=settings.codebook,
            use_receiver_knowledge=False,
            use_patterns=False,
        )
    )
    representations["sage_learned"] = learned_codec.compact(learned_result.packet)

    pattern_codec = SageCodec(db, settings)
    pattern_result = pattern_codec.encode(
        EncodeRequest(
            **common,
            codebook=settings.codebook,
            use_receiver_knowledge=False,
            use_patterns=True,
        )
    )
    representations["sage_patterns"] = pattern_codec.compact(pattern_result.packet)

    receiver_codec = SageCodec(db, settings)
    receiver_result = receiver_codec.encode(
        EncodeRequest(
            **common,
            codebook=settings.codebook,
            use_receiver_knowledge=True,
        )
    )
    representations["sage_receiver"] = receiver_codec.compact(receiver_result.packet)

    tokenizer_spec = request.tokenizer.model_dump(exclude_none=True)
    if tokenizer_spec.get("kind") == "http":
        endpoint = str(tokenizer_spec.get("endpoint", ""))
        host = (urlparse(endpoint).hostname or "").lower()
        allowed_hosts = {h.lower() for h in settings.benchmark_tokenizer_allowed_hosts}
        if settings.env == "production" and not allowed_hosts:
            raise ValueError("production HTTP tokenizer requires SAGE_BENCHMARK_TOKENIZER_ALLOWED_HOSTS")
        if allowed_hosts and host not in allowed_hosts:
            raise ValueError(f"tokenizer host is not allowlisted: {host}")
        if settings.benchmark_tokenizer_api_key is not None:
            tokenizer_spec["bearer_token"] = settings.benchmark_tokenizer_api_key.get_secret_value()

    report = benchmark_representations(
        representations=representations,
        tokenizer=tokenizer_spec,
        task_success=request.task_success,
        price=request.price.model_dump(),
        chars_per_token=settings.chars_per_token_estimate,
    )
    report["sage_variants"] = {
        "sage": {
            "strategy": plain_result.strategy,
            "packet_id": plain_result.packet.id,
            "wire_msgpack_bytes": plain_result.output_bytes_msgpack,
            "estimated_tokens": plain_result.estimated_tokens,
        },
        "sage_learned": {
            "strategy": learned_result.strategy,
            "packet_id": learned_result.packet.id,
            "wire_msgpack_bytes": learned_result.output_bytes_msgpack,
            "estimated_tokens": learned_result.estimated_tokens,
        },
        "sage_patterns": {
            "strategy": pattern_result.strategy,
            "packet_id": pattern_result.packet.id,
            "wire_msgpack_bytes": pattern_result.output_bytes_msgpack,
            "estimated_tokens": pattern_result.estimated_tokens,
        },
        "sage_receiver": {
            "strategy": receiver_result.strategy,
            "packet_id": receiver_result.packet.id,
            "wire_msgpack_bytes": receiver_result.output_bytes_msgpack,
            "estimated_tokens": receiver_result.estimated_tokens,
        },
    }
    report["methodology"] = {
        "token_scope": "input representation only; submit observed provider usage for end-to-end economics",
        "task_success": "caller-observed; omitted values remain null",
        "summary_rag": "included only when caller supplies actual outputs",
        "state_refs": "counts the ref pointer, not a later dereference; record dereference tokens separately when a task requires them",
        "sage": "structural SAGE with an empty benchmark codebook and receiver knowledge disabled",
        "sage_learned": "current learned/registered codebook with receiver knowledge disabled",
        "sage_receiver": "current learned/registered codebook plus receiver knowledge/capability state",
        "learning_side_effects": "disabled for benchmark encodes",
    }
    db.commit()
    return report


def score_observed_runs(observations: list[dict[str, Any]], price: dict[str, float]) -> dict[str, Any]:
    rows = [score_observation(row, price) for row in observations]
    by_strategy: dict[str, dict[str, float]] = {}
    for row in rows:
        strategy = str(row.get("strategy", "unknown"))
        bucket = by_strategy.setdefault(
            strategy,
            {
                "runs": 0.0,
                "cost": 0.0,
                "success": 0.0,
                "input_tokens": 0.0,
                "output_tokens": 0.0,
                "latency_ms": 0.0,
                "latency_samples": 0.0,
                "retrievals": 0.0,
                "retrieval_samples": 0.0,
                "wire_bits": 0.0,
            },
        )
        bucket["runs"] += 1
        bucket["cost"] += float(row["cost"])
        bucket["input_tokens"] += float(row.get("input_tokens", 0))
        bucket["output_tokens"] += float(row.get("output_tokens", 0))
        if row.get("wire_bytes") is not None:
            bucket["wire_bits"] += float(row["wire_bytes"]) * 8.0
        if row.get("task_success") is not None:
            bucket["success"] += float(row["task_success"])
        if row.get("latency_ms") is not None:
            bucket["latency_ms"] += float(row["latency_ms"])
            bucket["latency_samples"] += 1
        if row.get("retrievals") is not None:
            bucket["retrievals"] += float(row["retrievals"])
            bucket["retrieval_samples"] += 1
    summary: dict[str, dict[str, Any]] = {}
    for strategy, values in by_strategy.items():
        summary[strategy] = {
            "runs": int(values["runs"]),
            "cost": values["cost"],
            "success": values["success"],
            "input_tokens": int(values["input_tokens"]),
            "output_tokens": int(values["output_tokens"]),
            "cost_per_success": (values["cost"] / values["success"] if values["success"] > 0 else None),
            "successful_tasks_per_dollar": (values["success"] / values["cost"] if values["cost"] > 0 else None),
            "avg_latency_ms": (values["latency_ms"] / values["latency_samples"] if values["latency_samples"] > 0 else None),
            "avg_retrievals": (values["retrievals"] / values["retrieval_samples"] if values["retrieval_samples"] > 0 else None),
            "task_utility_per_bit": (values["success"] / values["wire_bits"] if values["wire_bits"] > 0 else None),
        }
    return {"price": price, "observations": rows, "summary": summary}
