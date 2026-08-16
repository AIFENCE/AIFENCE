# SPDX-License-Identifier: AGPL-3.0-or-later
"""ASGI entrypoint for the composed AIFENCE application.

``app`` is built here from environment configuration. The ``aifence-api``
console script runs this module under uvicorn.
"""
from __future__ import annotations

from .app import create_app
from .core.config import CoreSettings

app = create_app()


def run() -> None:
    import uvicorn

    settings = CoreSettings.from_env()
    uvicorn.run("aifence.main:app", host=settings.bind_host, port=settings.bind_port)


if __name__ == "__main__":
    run()
