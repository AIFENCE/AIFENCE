# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import argparse
import json

from .integrations import config_for, profiles


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate vendor-neutral SAGE integration configuration")
    parser.add_argument("platform", nargs="?", choices=[p.id for p in profiles()])
    parser.add_argument("--url", default="http://localhost:8080")
    parser.add_argument("--agent-id", default="agent")
    parser.add_argument("--workspace", default="default")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    if args.list or args.platform is None:
        print(json.dumps([p.model_dump() for p in profiles()], indent=2))
        return
    print(json.dumps(config_for(args.platform, args.url, args.agent_id, args.workspace).model_dump(), indent=2))


if __name__ == "__main__":
    main()
