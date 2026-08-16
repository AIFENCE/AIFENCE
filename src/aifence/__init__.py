# SPDX-License-Identifier: AGPL-3.0-or-later
# AIFENCE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# See LICENSING.md. Contact aifence@digitalacre.org for commercial licensing.
"""AIFENCE — one governed fence around AI agents.

AIFENCE unifies three tiers into a single control plane:

* ``aifence.bus``     — semantic communication runtime (formerly SAGE).
* ``aifence.guard``   — security control & enforcement plane (formerly AGENTDANCE).
* ``aifence.quality`` — production quality gate for AI output (bridge to BizIQ).

The tiers compose into one logical flow: a request is quality-gated, then
policy/capability-enforced, then carried as minimal semantic state — under one
identity, one audit chain, and one telemetry pipeline.
"""
from __future__ import annotations

__version__ = "0.1.0"

__all__ = ["__version__"]
