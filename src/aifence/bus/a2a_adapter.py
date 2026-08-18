# SPDX-License-Identifier: AGPL-3.0-or-later
# AIFENCE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import uuid
from typing import Any

from .protocol_spec import (
    AIFENCE_MEDIA_TYPE_JSON,
    AIFENCE_PROTOCOL,
    AIFENCE_SUPPORTED_PROTOCOLS,
    AIFENCE_WIRE_VERSION,
    validate_wire_v2,
)

AIFENCE_EXTENSION_URI = "urn:uuid:f81af17b-cc6a-5cdf-8a0f-51116b2e6a8d"
AIFENCE_MEDIA_TYPE = AIFENCE_MEDIA_TYPE_JSON
A2A_PROTOCOL_VERSION = "1.0"


def pack_data_part(wire: dict[str, Any]) -> dict[str, Any]:
    """Wrap a AIFENCE wire packet as an A2A 1.0 DataPart.

    A2A owns Message/Task lifecycle. AIFENCE is only the structured data carried by a
    Part, which keeps the semantic protocol independent of an A2A SDK or binding.
    """
    validate_wire_v2(wire)
    return {
        "data": {"aifenceProtocol": AIFENCE_PROTOCOL, "wire": wire},
        "mediaType": AIFENCE_MEDIA_TYPE,
    }


def unpack_data_part(part: dict[str, Any]) -> dict[str, Any]:
    media_type = part.get("mediaType")
    if media_type not in {None, "application/json", AIFENCE_MEDIA_TYPE}:
        raise ValueError(f"unsupported A2A part mediaType: {media_type}")
    data = part.get("data")
    if not isinstance(data, dict):
        raise ValueError("A2A DataPart must contain a data object")

    protocol = data.get("aifenceProtocol")
    if protocol != AIFENCE_PROTOCOL:
        raise ValueError(f"A2A DataPart must declare {AIFENCE_PROTOCOL}")

    wire = data.get("wire")
    if not isinstance(wire, dict):
        raise ValueError("A2A DataPart does not contain a AIFENCE wire packet")
    validate_wire_v2(wire)
    return wire


def pack_message(
    wire: dict[str, Any],
    *,
    message_id: str | None = None,
    role: str = "ROLE_USER",
    context_id: str | None = None,
    task_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an A2A 1.0 Message carrying AIFENCE as one structured Part."""
    if role not in {"ROLE_USER", "ROLE_AGENT", "ROLE_UNSPECIFIED"}:
        raise ValueError(f"unsupported A2A role: {role}")
    message: dict[str, Any] = {
        "mesaifenceId": message_id or str(uuid.uuid4()),
        "role": role,
        "parts": [pack_data_part(wire)],
        "extensions": [AIFENCE_EXTENSION_URI],
    }
    if context_id:
        message["contextId"] = context_id
    if task_id:
        message["taskId"] = task_id
    if metadata:
        message["metadata"] = metadata
    return message


def unpack_message(message: dict[str, Any]) -> dict[str, Any]:
    """Extract the first AIFENCE DataPart from an A2A 1.0 Message."""
    parts = message.get("parts")
    if not isinstance(parts, list):
        raise ValueError("A2A Message must contain parts")
    for part in parts:
        if isinstance(part, dict) and "data" in part:
            try:
                return unpack_data_part(part)
            except ValueError:
                continue
    raise ValueError("A2A Message does not contain a AIFENCE DataPart")


def agent_card_extension() -> dict[str, Any]:
    return {
        "uri": AIFENCE_EXTENSION_URI,
        "description": "AIFENCE semantic payload transport for compact shared context between agents.",
        "required": False,
        "params": {
            "mediaType": AIFENCE_MEDIA_TYPE,
            "protocolVersions": list(AIFENCE_SUPPORTED_PROTOCOLS),
            "wireVersion": AIFENCE_WIRE_VERSION,
        },
    }


def agent_card(
    *,
    name: str,
    description: str,
    url: str,
    version: str = "1.0.0",
    protocol_binding: str = "HTTP+JSON",
    tenant: str | None = None,
    default_input_modes: list[str] | None = None,
    default_output_modes: list[str] | None = None,
    skills: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build an A2A 1.0 AgentCard advertising the AIFENCE extension.

    A2A 1.0 requires default input/output modes and a skills array, so the
    helper emits a valid minimal card rather than an incomplete fragment.
    """
    interface: dict[str, Any] = {
        "url": url,
        "protocolBinding": protocol_binding,
        "protocolVersion": A2A_PROTOCOL_VERSION,
    }
    if tenant:
        interface["tenant"] = tenant
    input_modes = default_input_modes or [AIFENCE_MEDIA_TYPE]
    output_modes = default_output_modes or [AIFENCE_MEDIA_TYPE]
    advertised_skills = skills or [
        {
            "id": "aifence-semantic-handoff",
            "name": "AIFENCE semantic handoff",
            "description": "Exchange AIFENCE 0.2 structured semantic payloads with peer agents.",
            "tags": ["aifence", "semantic-context", "agent-handoff"],
            "inputModes": input_modes,
            "outputModes": output_modes,
        }
    ]
    return {
        "name": name,
        "description": description,
        "version": version,
        "supportedInterfaces": [interface],
        "capabilities": {"extensions": [agent_card_extension()]},
        "defaultInputModes": input_modes,
        "defaultOutputModes": output_modes,
        "skills": advertised_skills,
    }
