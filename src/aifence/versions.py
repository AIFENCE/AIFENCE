# SPDX-License-Identifier: AGPL-3.0-or-later
"""Canonical version inventory for the AIFENCE monorepo.

AIFENCE deliberately versions the platform, individual subsystems, public SDKs,
and the Bus wire protocol independently.  Keeping those values in one small
module makes the distinction explicit and gives release tooling one stable
source of truth.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

PLATFORM_VERSION = "0.1.0"
GUARD_VERSION = "1.0.0rc5"
BUS_VERSION = "0.2.7"
QUALITY_VERSION = "2.0.0"
SDK_VERSION = "1.0.0rc5"
BUS_PROTOCOL = "aifence/0.2"
BUS_WIRE_VERSION = 2


@dataclass(frozen=True)
class VersionInventory:
    platform: str = PLATFORM_VERSION
    guard: str = GUARD_VERSION
    bus: str = BUS_VERSION
    quality: str = QUALITY_VERSION
    sdk: str = SDK_VERSION
    bus_protocol: str = BUS_PROTOCOL
    bus_wire: int = BUS_WIRE_VERSION

    def to_dict(self) -> dict[str, str | int]:
        return asdict(self)


def version_inventory() -> dict[str, str | int]:
    """Return the public monorepo version matrix as JSON-friendly data."""
    return VersionInventory().to_dict()
