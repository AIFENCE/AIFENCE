# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import argparse
import json

from .config import get_settings
from .db import SessionLocal
from .patterns import PatternStore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codebook")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    settings = get_settings()
    with SessionLocal() as db:
        store = PatternStore(db, settings)
        patterns = store.promote_ready_candidates(codebook=args.codebook, limit=args.limit)
        db.commit()
        print(json.dumps({"promoted": [store.response(item) for item in patterns]}, sort_keys=True))


if __name__ == "__main__":
    main()
