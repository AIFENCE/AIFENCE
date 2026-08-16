# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import argparse
import json
from typing import Any

from .db import SessionLocal
from .inspector import Inspector


def _print(value: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(value, ensure_ascii=False, indent=2, default=str))
        return
    if "packet_id" in value:
        print(f"Packet {value['packet_id']}")
        print(f"  original bytes: {value['original_bytes']}")
        print(f"  sent bytes:     {value['sent_bytes']}")
        print(f"  original tokens estimate: {value['estimated_original_tokens']}")
        print(f"  sent tokens estimate:     {value['estimated_sent_tokens']}")
        print(f"  semantic loss: {value['semantic_loss_score']:.6f}")
        print(f"  receiver-known ratio: {value['receiver_known_ratio']:.3f}")
        print(f"  patterns: {len(value['patterns'])}; refs: {len(value['refs'])}")
        return
    print(f"Run {value['run_id']}: {len(value['packets'])} packets")
    print(f"  original bytes: {value['original_bytes']}")
    print(f"  sent bytes:     {value['sent_bytes']}")
    print(f"  semantic loss max: {value['semantic_loss_max']:.6f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect SAGE packet/run compression and semantic decisions")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--packet", help="packet ID to inspect")
    group.add_argument("--run", help="run ID to inspect")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()
    with SessionLocal() as db:
        inspector = Inspector(db)
        try:
            value = inspector.packet(args.packet) if args.packet else inspector.run(args.run)
        except KeyError as exc:
            parser.error(f"not found: {exc.args[0]}")
    _print(value, args.json)


if __name__ == "__main__":
    main()
