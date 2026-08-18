// SPDX-License-Identifier: AGPL-3.0-or-later
// SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
// Contact sage@digitalacre.org for commercial licensing.
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";

/**
 * SAGE JavaScript TCK conformance runner.
 *
 * Implements the SAGE wire-format canonicalization, MessagePack-style
 * encoding, and validation rules, then verifies every vector in the TCK
 * corpus. Used by `npm run tck` and the three-runtime conformance matrix.
 */

type WireValue = null | boolean | number | string | WireValue[] | { [key: string]: WireValue };

type Vector = {
  name: string;
  wire: Record<string, WireValue>;
  canonical_json?: string;
  canonical_msgpack_hex?: string;
  canonical_sha256?: string;
};

type Corpus = {
  protocol: string;
  wire_version: number;
  valid: Vector[];
  invalid: Vector[];
};

function normalize(value: WireValue): WireValue {
  if (Array.isArray(value)) return value.map(normalize);
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return Object.fromEntries(
      Object.keys(value as Record<string, WireValue>)
        .sort()
        .map((key) => [key, normalize((value as Record<string, WireValue>)[key])]),
    );
  }
  if (typeof value === "number" && !Number.isFinite(value)) throw new Error("non-finite number");
  return value;
}

function prefix(code: number, value: number, bytes: 1 | 2 | 4): Buffer {
  const out = Buffer.alloc(1 + bytes);
  out[0] = code;
  if (bytes === 1) out.writeUInt8(value, 1);
  else if (bytes === 2) out.writeUInt16BE(value, 1);
  else out.writeUInt32BE(value, 1);
  return out;
}

function encodeInteger(value: number): Buffer {
  if (value >= 0) {
    if (value <= 0x7f) return Buffer.from([value]);
    if (value <= 0xff) return prefix(0xcc, value, 1);
    if (value <= 0xffff) return prefix(0xcd, value, 2);
    if (value <= 0xffffffff) return prefix(0xce, value, 4);
    const out = Buffer.alloc(9);
    out[0] = 0xcf;
    out.writeBigUInt64BE(BigInt(value), 1);
    return out;
  }
  if (value >= -32) return Buffer.from([0x100 + value]);
  if (value >= -128) {
    const out = Buffer.alloc(2);
    out[0] = 0xd0;
    out.writeInt8(value, 1);
    return out;
  }
  if (value >= -32768) {
    const out = Buffer.alloc(3);
    out[0] = 0xd1;
    out.writeInt16BE(value, 1);
    return out;
  }
  if (value >= -2147483648) {
    const out = Buffer.alloc(5);
    out[0] = 0xd2;
    out.writeInt32BE(value, 1);
    return out;
  }
  const out = Buffer.alloc(9);
  out[0] = 0xd3;
  out.writeBigInt64BE(BigInt(value), 1);
  return out;
}

function encodeString(value: string): Buffer {
  const body = Buffer.from(value, "utf8");
  let head: Buffer;
  if (body.length <= 31) head = Buffer.from([0xa0 | body.length]);
  else if (body.length <= 0xff) head = prefix(0xd9, body.length, 1);
  else if (body.length <= 0xffff) head = prefix(0xda, body.length, 2);
  else head = prefix(0xdb, body.length, 4);
  return Buffer.concat([head, body]);
}

function encode(value: WireValue): Buffer {
  if (value === null) return Buffer.from([0xc0]);
  if (value === false) return Buffer.from([0xc2]);
  if (value === true) return Buffer.from([0xc3]);
  if (typeof value === "number") {
    if (Number.isSafeInteger(value)) return encodeInteger(value);
    const out = Buffer.alloc(9);
    out[0] = 0xcb;
    out.writeDoubleBE(value, 1);
    return out;
  }
  if (typeof value === "string") return encodeString(value);
  if (Array.isArray(value)) {
    const head =
      value.length <= 15
        ? Buffer.from([0x90 | value.length])
        : value.length <= 0xffff
          ? prefix(0xdc, value.length, 2)
          : prefix(0xdd, value.length, 4);
    return Buffer.concat([head, ...value.map(encode)]);
  }
  if (value && typeof value === "object") {
    const entries = Object.entries(normalize(value) as Record<string, WireValue>);
    const head =
      entries.length <= 15
        ? Buffer.from([0x80 | entries.length])
        : entries.length <= 0xffff
          ? prefix(0xde, entries.length, 2)
          : prefix(0xdf, entries.length, 4);
    return Buffer.concat([head, ...entries.flatMap(([key, item]) => [encodeString(key), encode(item)])]);
  }
  throw new Error(`unsupported type: ${typeof value}`);
}

function validate(wire: Record<string, WireValue>): void {
  const top = new Set(["v", "c", "a", "i", "s", "r", "x", "R", "b", "d", "p", "m", "g", "z"]);
  if (!wire || typeof wire !== "object" || Array.isArray(wire)) throw new Error("wire object required");
  if (wire.v !== 2) throw new Error("wire version");
  if (typeof wire.c !== "string") throw new Error("codebook");
  for (const key of Object.keys(wire)) if (!top.has(key)) throw new Error("unknown top-level key");
  const provenance = wire.p as Record<string, WireValue> | undefined;
  if (provenance?.q !== undefined && (typeof provenance.q !== "number" || provenance.q < 0 || provenance.q > 1)) {
    throw new Error("provenance confidence");
  }
  if (wire.x !== undefined) {
    if (!Array.isArray(wire.x)) throw new Error("atoms");
    const atomKeys = new Set(["c", "v", "l", "h", "p", "q", "e"]);
    for (const atom of wire.x as Record<string, WireValue>[]) {
      for (const key of Object.keys(atom)) if (!atomKeys.has(key)) throw new Error("unknown atom key");
      if (atom.q !== undefined && (typeof atom.q !== "number" || atom.q < 0 || atom.q > 1)) throw new Error("atom confidence");
      if (atom.e !== undefined && typeof atom.e !== "string") throw new Error("epistemic type");
    }
  }
  const sig = wire.g as Record<string, WireValue> | undefined;
  if (sig !== undefined && sig.alg !== "Ed25519") throw new Error("signature algorithm");
  const trace = wire.z as Record<string, WireValue> | undefined;
  if (trace !== undefined) {
    if (typeof trace.p !== "string" || !/^[0-9a-f]{2}-[0-9a-f]{32}-[0-9a-f]{16}-[0-9a-f]{2}$/.test(trace.p)) {
      throw new Error("traceparent");
    }
    if (trace.s !== undefined && typeof trace.s !== "string") throw new Error("tracestate");
  }
}

const file = process.argv[2] ?? new URL("../tck/core.json", import.meta.url);
const vectors = JSON.parse(readFileSync(file, "utf8")) as Corpus;
const failures: string[] = [];
let total = 0;
for (const test of vectors.valid) {
  total += 1;
  try {
    validate(test.wire);
    const canonical = normalize(test.wire);
    const json = JSON.stringify(canonical);
    const packed = encode(canonical);
    const digest = `sha256:${createHash("sha256").update(packed).digest("hex")}`;
    if (typeof test.canonical_json === "string" && json !== test.canonical_json) throw new Error("canonical JSON mismatch");
    if (packed.toString("hex") !== test.canonical_msgpack_hex) throw new Error("canonical MessagePack mismatch");
    if (digest !== test.canonical_sha256) throw new Error("digest mismatch");
  } catch (error) {
    failures.push(`${test.name}: ${error instanceof Error ? error.message : String(error)}`);
  }
}
for (const test of vectors.invalid) {
  total += 1;
  try {
    validate(test.wire);
    failures.push(`${test.name}: invalid vector accepted`);
  } catch {
    // expected rejection
  }
}
const result = { ok: failures.length === 0, total, passed: total - failures.length, failures };
console.log(JSON.stringify(result));
if (!result.ok) process.exitCode = 1;
