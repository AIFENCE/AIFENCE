from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from aifence.bus.protocol_spec import SAGE_PROTOCOL, SAGE_WIRE_VERSION, WirePacketV2

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "spec" / "generated"


def render_typescript() -> str:
    schema = WirePacketV2.model_json_schema(by_alias=True)
    keys = sorted(schema["properties"])
    lines = ["export type SageWireV2 = {", "  v: 2;", "  c: string;"]
    for key in keys:
        if key in {"v", "c"}:
            continue
        lines.append(f"  {json.dumps(key)}?: unknown;")
    lines.extend(["};", "", f"export const SAGE_PROTOCOL = {json.dumps(SAGE_PROTOCOL)} as const;", f"export const SAGE_WIRE_VERSION = {SAGE_WIRE_VERSION} as const;", ""])
    return "\n".join(lines)


def render_go() -> str:
    schema = WirePacketV2.model_json_schema(by_alias=True)
    keys = sorted(schema["properties"])
    lines = ["package sagewire", "", "const Protocol = \"sage/0.2\"", "const WireVersion = 2", "", "type Packet map[string]any", "", "var WireKeys = map[string]struct{}{",]
    lines.extend(f"\t{json.dumps(key)}: {{}}," for key in keys)
    lines.extend(["}", ""])
    return "\n".join(lines)


def render_field_table() -> str:
    schema = WirePacketV2.model_json_schema(by_alias=True)
    required = set(schema.get("required", []))
    lines = ["# Generated wire fields", "", "This file is generated from `sage_plugin.protocol_spec.WirePacketV2`.", "", "| Field | Required |", "|---|---|" ]
    for key in sorted(schema["properties"]):
        lines.append(f"| `{key}` | {'yes' if key in required else 'no'} |")
    lines.append("")
    return "\n".join(lines)



def render_proto() -> str:
    return 'syntax = "proto3";\n\npackage sage.v02;\n\nimport "google/protobuf/struct.proto";\n\n// Optional transport binding for SAGE 0.2. Canonical SAGE digests are defined\n// over canonical MessagePack, not protobuf serialization.\n\nmessage Provenance {\n  repeated string source_ids = 1;\n  optional string observed_at = 2;\n  optional double confidence = 3;\n  optional string derivation = 4;\n  optional string producer = 5;\n}\n\nmessage Atom {\n  optional string code = 1;\n  optional uint32 code_version = 2;\n  google.protobuf.Value literal = 3;\n  bool has_literal = 4;\n  optional string path = 5;\n  optional double confidence = 6;\n  optional string epistemic_type = 7;\n}\n\nmessage TraceContext {\n  string traceparent = 1;\n  optional string tracestate = 2;\n}\n\nmessage Packet {\n  uint32 wire_version = 1; // MUST be 2.\n  string codebook = 2;\n  string act = 3;\n  optional string packet_id = 4;\n  optional string sender = 5;\n  optional string receiver = 6;\n  repeated Atom atoms = 7;\n  repeated string refs = 8;\n  optional string base_state = 9;\n  google.protobuf.Value delta = 10;\n  Provenance provenance = 11;\n  google.protobuf.Struct meta = 12;\n  google.protobuf.Struct signature = 13;\n  TraceContext trace = 14;\n}\n\nmessage Ref {\n  string ref = 1;\n  string media_type = 2;\n  uint64 byte_size = 3;\n  string digest = 4;\n  string tier = 5;\n  optional string expires_at = 6;\n  Provenance provenance = 7;\n}\n\nmessage State {\n  string state = 1;\n  uint64 revision = 2;\n  optional string parent = 3;\n  string value_digest = 4;\n  Provenance provenance = 5;\n}\n\nmessage DeltaOp {\n  string op = 1; // add | remove | replace\n  string path = 2;\n  google.protobuf.Value value = 3;\n}\n\nmessage Delta {\n  string base = 1;\n  optional string target = 2;\n  repeated DeltaOp ops = 3;\n}\n\nmessage Concept {\n  string code = 1;\n  uint32 version = 2;\n  string codebook = 3;\n  string canonical = 4;\n  string description = 5;\n  string status = 6;\n  optional string replacement_code = 7;\n  double confidence = 8;\n}\n\n\nmessage Pattern {\n  string pattern_id = 1;\n  string concept_code = 2;\n  uint32 concept_version = 3;\n  uint32 version = 4;\n  string codebook = 5;\n  string signature = 6;\n  string canonical = 7;\n  repeated google.protobuf.Struct composition = 8;\n  google.protobuf.Struct relation_structure = 9;\n  string status = 10;\n  double confidence = 11;\n  double semantic_variance = 12;\n  double utility_score = 13;\n  double ambiguity_score = 14;\n  double interoperability_score = 15;\n  uint64 use_count = 16;\n  repeated string children = 17;\n  double calibrated_reliability = 18;\n  string trust_scope = 19;\n  uint32 source_diversity = 20;\n  double dominant_source_share = 21;\n  double trust_score = 22;\n}\n\nmessage Capabilities {\n  repeated string protocol_versions = 1; // MUST contain sage/0.2.\n  repeated string codebooks = 2;\n  uint64 max_packet_bytes = 3;\n  bool supports_refs = 4;\n  bool supports_deltas = 5;\n  repeated string latent_spaces = 6;\n  repeated string fallback_modes = 7;\n  bool supports_patterns = 8;\n}\n\nmessage Capability {\n  string protocol = 1; // MUST be sage/0.2.\n  Capabilities capabilities = 2;\n  map<string, string> codebook_fingerprints = 3;\n}\n\nmessage Ack {\n  string message_id = 1;\n  string packet_id = 2;\n  string receiver = 3;\n  string workspace = 4;\n  string status = 5; // acked | nacked\n  string observed_at = 6;\n}\n\nmessage Error {\n  string code = 1;\n  string message = 2;\n  bool retryable = 3;\n  optional string packet_id = 4;\n  google.protobuf.Struct details = 5;\n}\n'


def artifacts() -> dict[Path, str]:
    return {
        OUT / "wire-v2.ts": render_typescript(),
        OUT / "wire-v2.go": render_go(),
        OUT / "WIRE-FIELDS.md": render_field_table(),
        ROOT / "spec" / "sage-v0.2.proto": render_proto(),
        ROOT / "src" / "sage_plugin" / "spec" / "sage-v0.2.proto": render_proto(),
    }


def digest_map(values: dict[Path, str]) -> dict[str, str]:
    return {
        path.relative_to(ROOT).as_posix(): hashlib.sha256(text.encode()).hexdigest()
        for path, text in sorted(values.items(), key=lambda item: item[0].as_posix())
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    values = artifacts()
    manifest = {"protocol": SAGE_PROTOCOL, "wire": SAGE_WIRE_VERSION, "artifacts": digest_map(values)}
    values[OUT / "manifest.json"] = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, content in values.items() if not path.exists() or path.read_text() != content]
        if stale:
            raise SystemExit("stale generated protocol artifacts: " + ", ".join(stale))
        print(json.dumps({"ok": True, "files": len(values)}, sort_keys=True))
        return
    for path, content in values.items():
        path.write_text(content)
    print(json.dumps({"ok": True, "files": len(values)}, sort_keys=True))


if __name__ == "__main__":
    main()
