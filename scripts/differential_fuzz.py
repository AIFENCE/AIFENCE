from __future__ import annotations

import argparse
import copy
import json
import random
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from aifence.bus.protocol_spec import (
    canonical_digest,
    canonical_msgpack_bytes,
    validate_wire_v2,
)


def _random_scalar(rng: random.Random) -> Any:
    values: list[Any] = [None, True, False, rng.randint(-100000, 100000), round(rng.random(), 8)]
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789-_"
    values.append("".join(rng.choice(alphabet) for _ in range(rng.randint(1, 24))))
    return rng.choice(values)


def _wire(rng: random.Random, index: int) -> dict[str, Any]:
    atoms = []
    for atom_index in range(rng.randint(0, 5)):
        atom: dict[str, Any] = {"p": f"$.f{atom_index}"}
        if rng.random() < 0.5:
            atom["c"] = f"C{rng.randint(1, 65535):08X}"
            atom["v"] = rng.randint(1, 20)
        if rng.random() < 0.8:
            atom["h"] = 1
            atom["l"] = _random_scalar(rng)
        if rng.random() < 0.3:
            atom["q"] = round(rng.random(), 6)
        if rng.random() < 0.25:
            atom["e"] = rng.choice(["fact", "observation", "inference", "constraint"])
        atoms.append(atom)
    wire: dict[str, Any] = {
        "v": 2,
        "c": rng.choice(["global", "core", "software.deploy"]),
        "a": rng.choice(["report", "handoff", "update"]),
        "i": f"DF{index:08d}",
        "p": {},
    }
    if atoms:
        wire["x"] = atoms
    if rng.random() < 0.4:
        wire["m"] = {"n": rng.randint(0, 100), "flag": rng.choice([True, False])}
    if rng.random() < 0.25:
        wire["z"] = {"p": "00-" + f"{index + 1:032x}"[-32:] + "-" + f"{index + 1:016x}"[-16:] + "-01"}
    validate_wire_v2(wire)
    return wire


def _vector(name: str, wire: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "wire": wire,
        "canonical_msgpack_hex": canonical_msgpack_bytes(wire).hex(),
        "canonical_sha256": canonical_digest(wire),
    }


def _invalid(wire: dict[str, Any], index: int) -> dict[str, Any]:
    mutated = copy.deepcopy(wire)
    if index % 4 == 0:
        mutated["v"] = 3
    elif index % 4 == 1:
        mutated["unknown"] = True
    elif index % 4 == 2:
        mutated["x"] = "invalid"
    else:
        mutated["z"] = {"p": "invalid"}
    return mutated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20260731)
    args = parser.parse_args()
    if args.iterations < 1:
        raise SystemExit("iterations must be positive")
    rng = random.Random(args.seed)
    valid = [_vector(f"diff-{i}", _wire(rng, i)) for i in range(args.iterations)]
    invalid = [{"name": f"invalid-{i}", "wire": _invalid(valid[i]["wire"], i)} for i in range(args.iterations)]
    suite = {"suite": "aifence-differential/0.2", "protocol": "aifence/0.2", "wire_version": 2, "valid": valid, "invalid": invalid}
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "vectors.json"
        path.write_text(json.dumps(suite, separators=(",", ":")))
        commands = [
            ["node", "integrations/openclaw/dist/conformance.js", str(path)],
            ["go", "run", "integrations/go/conformance.go", str(path)],
        ]
        results = []
        for command in commands:
            executable = shutil.which(command[0])
            if executable is None:
                raise SystemExit(f"required runtime unavailable: {command[0]}")
            command[0] = executable
            completed = subprocess.run(command, check=False, capture_output=True, text=True)
            if completed.returncode != 0:
                raise SystemExit(completed.stdout + completed.stderr)
            results.append(json.loads(completed.stdout))
    print(json.dumps({"ok": all(item.get("ok") for item in results), "iterations": args.iterations, "implementations": results}, sort_keys=True))


if __name__ == "__main__":
    main()
