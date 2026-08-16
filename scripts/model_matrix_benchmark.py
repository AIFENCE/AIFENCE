from __future__ import annotations

import argparse
import json
import subprocess
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

from aifence.bus.corpus import read_jsonl


def _invoke(command: list[str], payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        input=json.dumps(payload, separators=(",", ":")),
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    latency_ms = (time.perf_counter() - started) * 1000
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "benchmark adapter failed")
    result = json.loads(completed.stdout)
    result.setdefault("latency_ms", latency_ms)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", required=True)
    parser.add_argument("--adapters", required=True)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    adapters = json.loads(Path(args.adapters).read_text())
    if not isinstance(adapters, dict) or not adapters:
        raise SystemExit("adapter configuration must be a non-empty object")
    rows: list[dict[str, Any]] = []
    for record in read_jsonl(args.corpus):
        for strategy in record.strategies:
            for model_identity, spec in adapters.items():
                command = spec.get("command")
                if not isinstance(command, list) or not command or not all(isinstance(x, str) for x in command):
                    raise SystemExit(f"invalid command for adapter {model_identity}")
                payload = {
                    "record_id": record.record_id,
                    "task_family": record.task_family,
                    "task": record.task,
                    "receiver_prior": record.receiver_prior,
                    "representation": strategy.representation,
                    "expected": record.expected,
                    "strategy": strategy.name,
                }
                result = _invoke(command, payload, args.timeout)
                success = result.get("task_success")
                if success is None:
                    raise RuntimeError(f"adapter {model_identity} did not report task_success")
                provider_cost = float(result.get("provider_cost_usd", 0.0))
                infrastructure_cost = float(result.get("infrastructure_cost_usd", 0.0))
                retrieval_cost = float(result.get("retrieval_cost_usd", 0.0))
                retry_cost = float(result.get("retry_cost_usd", 0.0))
                component_total = provider_cost + infrastructure_cost + retrieval_cost + retry_cost
                total_cost = float(result["cost_usd"]) if "cost_usd" in result else component_total
                rows.append({
                    "record_id": record.record_id,
                    "model_identity": model_identity,
                    "strategy": strategy.name,
                    "task_success": float(success),
                    "input_tokens": int(result.get("input_tokens", 0)),
                    "output_tokens": int(result.get("output_tokens", 0)),
                    "latency_ms": float(result["latency_ms"]),
                    "retrievals": int(result.get("retrievals", 0)),
                    "tool_calls": int(result.get("tool_calls", 0)),
                    "retries": int(result.get("retries", 0)),
                    "semantic_loss": float(result.get("semantic_loss", 0.0)),
                    "provider_cost_usd": provider_cost,
                    "infrastructure_cost_usd": infrastructure_cost,
                    "retrieval_cost_usd": retrieval_cost,
                    "retry_cost_usd": retry_cost,
                    "cost_usd": total_cost,
                    "wire_bytes": strategy.wire_bytes,
                })
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["model_identity"], row["strategy"])].append(row)
    summary = []
    baseline: dict[str, tuple[float, float]] = {}
    for (model, strategy), items in grouped.items():
        if strategy == "raw_history":
            baseline[model] = (sum(item["cost_usd"] for item in items), sum(item["task_success"] for item in items) / len(items))
    for (model, strategy), items in sorted(grouped.items()):
        total_bits = sum(max(0, int(item.get("wire_bytes") or 0)) * 8 for item in items)
        utility = sum(item["task_success"] for item in items)
        total_cost = sum(item["cost_usd"] for item in items)
        success_mean = utility / len(items)
        baseline_cost, baseline_success = baseline.get(model, (0.0, 0.0))
        summary.append({
            "model_identity": model,
            "strategy": strategy,
            "tasks": len(items),
            "task_success_mean": success_mean,
            "input_tokens": sum(item["input_tokens"] for item in items),
            "output_tokens": sum(item["output_tokens"] for item in items),
            "provider_cost_usd": sum(item["provider_cost_usd"] for item in items),
            "infrastructure_cost_usd": sum(item["infrastructure_cost_usd"] for item in items),
            "retrieval_cost_usd": sum(item["retrieval_cost_usd"] for item in items),
            "retry_cost_usd": sum(item["retry_cost_usd"] for item in items),
            "cost_usd": total_cost,
            "latency_ms_mean": sum(item["latency_ms"] for item in items) / len(items),
            "semantic_loss_max": max(item["semantic_loss"] for item in items),
            "task_utility_per_bit": utility / total_bits if total_bits else None,
            "net_success_per_usd": utility / total_cost if total_cost else None,
            "cost_savings_vs_raw_history_usd": baseline_cost - total_cost if model in baseline else None,
            "task_success_delta_vs_raw_history": success_mean - baseline_success if model in baseline else None,
        })
    Path(args.output).write_text(json.dumps({"rows": rows, "summary": summary}, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
