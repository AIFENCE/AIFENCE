"""Regression tests for the sealed direct-symbolic ACTUAL packet rendering
(issue #22, stage 2).

Covers (issue #22, stage 2):

* rendering determinism: ``_render_actual_packet`` is byte-identical across
  calls and across fresh re-encodes for the same (variant, turn);
* the REAL packet structure: v09 packets carry act/atoms/bindings/cb/id/
  meta/prov/receiver/refs/sender/v with code+cv atoms and a ``bindings``
  legend mapping every atom's ``code:cv`` to its non-empty canonical clause;
  v11 state variants are reference/delta packets (refs + ``meta.state`` on
  the reference turn, chained ``base`` + ``delta`` ops afterwards); v12
  ACKed packets are full semantic packets whose atoms carry code/cv/literal
  and whose ACKed receiver knowledge grows after turn 0 (a PACKET-level
  fact -- the rendering's meta strips non-wire keys, so the growth is
  verified at the codec level); v10's learned-pattern identifier lands in
  an ATOM (a ``cv > 1`` code whose binding is the EXPANDED pattern
  canonical), never in ``meta``;
* wire-meta whitelist: the rendering's ``meta`` carries ONLY the wire
  codec's export keys ``{state, revision, budget_exceeded, memory_tier}``
  -- ``strategy`` / ``codebook_fingerprint`` / ``receiver_known_code_count``
  are ABSENT, so the rendering equals the real wire packet plus the
  ``bindings`` legend (no evaluator-side decoder metadata crosses the
  sealed boundary);
* NO stage-1 proxy shape: sealed direct-symbolic AIFENCE packets never carry
  ``strategy_note`` / ``canonicals``;
* wire-byte honesty: ``_render_aifence_variant_packets`` reproduces the
  benchmark's recorded ``wire_bytes_json`` / ``wire_bytes_msgpack`` AND the
  accumulated reconstruction for every (variant, turn) of v09/v10/v11/v12
  (the v10 pattern warm-up turn -1 is skipped);
* round-trip: ``Packet.model_validate`` of the rendering, decoded by the
  REAL codec in a replay of the benchmark's per-variant session, reproduces
  the benchmark's recorded reconstruction for that (variant, turn)
  (refs/states persist because encode commits -- cross-session round-trips
  work);
* sealed payload integration: an end-to-end ``--sealed`` CLI run whose
  wrapper fake adapter dumps its stdin to files under the fake HOME shows
  ``model_facing_packet`` carrying atoms/bindings for AIFENCE variants and NO
  leak keys;
* non-sealed byte identity: default-OFF artifacts carry no
  ``evaluation_boundary`` and no packet-rendering fields, and sealed
  decoder-assisted / full-expansion modes (plus non-AIFENCE direct-symbolic)
  still use the reconstruction path;
* sealed determinism: two fresh CLI sealed runs over AIFENCE variants produce
  JSON-identical artifacts modulo latency keys and byte-identical printed
  tables.

All tests are deterministic (fixed inputs, no network, no real model) and
write their output directories under ``/opt/data/aifence/scratch/`` -- never
``/tmp``.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
HARNESS_SCRIPT = ROOT / "scripts" / "model_eval_harness.py"
SCRATCH_ROOT = Path(os.environ.get("AIFENCE_BUS_SCRATCH_ROOT", "/opt/data/aifence/scratch")) / "stage22-packet-tests"

#: AIFENCE variants whose sealed direct-symbolic packets are rendered for real.
AIFENCE_BUS_VARIANTS = ("v09", "v10", "v11", "v12")

#: Evaluator-only fields the sealed payload must NEVER carry.
LEAK_KEYS = ("content", "expected", "change_markers", "receiver_prior", "examples")

#: The stage-1 proxy shape that stage-2 rendering must NOT contain.
PROXY_KEYS = ("strategy_note", "canonicals")

#: The ONLY packet ``meta`` keys the wire codec exports (mirror of the
#: whitelist in ``WireCodec.compact``, src/aifence/bus/wire_codec.py) -- the
#: rendering's ``meta`` must be exactly this subset.
WIRE_META_KEYS = frozenset({"state", "revision", "budget_exceeded", "memory_tier"})

#: Sealed fake adapter: replies with a fixed task_response plus the required
#: token/cost numbers (the sealed contract's reply shape).
FAKE_ADAPTER_SEALED = (
    "import json,sys; p=json.load(sys.stdin); "
    "print(json.dumps({'task_response': 'Project Phoenix is blocked because three integration tests failed.', "
    "'input_tokens': 7, 'output_tokens': 5, 'provider_cost_usd': 0.0012}))"
)

#: WRAPPER fake adapter: dumps its full stdin payload to a file under the
#: (fake) HOME named after the payload's variant/turn/receiver_state, then
#: replies with the sealed contract shape.  Proves what the sealed payload
#: really carries end-to-end through the CLI.
FAKE_ADAPTER_DUMP_STDIN = (
    "import json,sys,os; p=json.load(sys.stdin); "
    "fn=os.path.join(os.path.expanduser('~'), "
    "'aifence_bus_adapter_dump_%s_%s_%s.json' % (p['variant'], p['turn'], p['receiver_state'])); "
    "open(fn,'w').write(json.dumps(p)); "
    "print(json.dumps({'task_response': 'Project Phoenix is blocked because three integration tests failed.', "
    "'input_tokens': 7, 'output_tokens': 5, 'provider_cost_usd': 0.0012}))"
)

#: Unsealed fake adapter (mirrors test_model_eval_harness / sealed tests) --
#: for the default-OFF byte-identity check.
FAKE_ADAPTER_OK = (
    "import json,sys; p=json.load(sys.stdin); "
    "print(json.dumps({'task_success': 1.0 if p.get('receiver_state') == 'warm' else 0.5, "
    "'input_tokens': 7, 'output_tokens': 5, 'provider_cost_usd': 0.0012, 'critical_fact_recall': 0.8}))"
)


def _load_harness() -> Any:
    spec = importlib.util.spec_from_file_location("model_eval_harness", HARNESS_SCRIPT)
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def h() -> Any:
    return _load_harness()


@pytest.fixture(scope="module")
def cb(h: Any) -> Any:
    return h._load_compression_benchmark()


@pytest.fixture()
def scratch_dir() -> Iterator[Path]:
    """A scratch output directory under /opt/data/aifence/scratch (never /tmp)."""
    path = SCRATCH_ROOT / uuid.uuid4().hex[:12]
    path.mkdir(parents=True, exist_ok=True)
    yield path
    shutil.rmtree(path, ignore_errors=True)


def _run_cli_subprocess(argv: list[str], fake_home: Path) -> subprocess.CompletedProcess:
    """Run the harness CLI in a FRESH subprocess (fake HOME + provider env)."""
    env = {**os.environ, "HOME": str(fake_home), "AIFENCE_BUS_BENCH_LLM_PROVIDER": "fake"}
    env.pop("AIFENCE_BUS_DATABASE_URL", None)
    return subprocess.run(
        [sys.executable, str(HARNESS_SCRIPT), *argv],
        capture_output=True,
        text=True,
        timeout=600,
        env=env,
    )


def _exchange(turn: int, variant: str = "v05") -> dict[str, Any]:
    return {
        "variant": variant,
        "variant_name": "x",
        "turn": turn,
        "phase": "update",
        "aifence": False,
        "wire_bytes": 10,
    }


def _recorded_turns(cb: Any) -> dict[str, dict[int, dict[str, Any]]]:
    """The benchmark's recorded per-variant turn records (warm-up turn -1 skipped)."""
    benchmark = cb.run_benchmark(out_dir=None)
    recorded: dict[str, dict[int, dict[str, Any]]] = {}
    for row in benchmark["variants"]:
        recorded[row["variant_id"]] = {turn["turn"]: turn for turn in row["turns"] if turn["turn"] >= 0}
    return recorded


def _render_all(cb: Any, h: Any) -> dict[str, dict[int, dict[str, Any]]]:
    """Per-variant stage-2 re-encode results (rendering + wire bytes + reconstruction)."""
    return {
        vid: h._render_aifence_variant_packets(cb, h._aifence_variant_spec(cb, vid))
        for vid in AIFENCE_BUS_VARIANTS
    }


def _replay_rendering_roundtrip(cb: Any, h: Any, spec: dict[str, Any]) -> dict[int, str]:
    """Replay the variant through the REAL codec, decoding the RENDERING itself.

    Mirrors the benchmark's per-variant session (schema reset, spec settings,
    codebook registration in order, pinned ids, v10 warm-up, per-turn
    encode) but every turn's decode consumes ``Packet.model_validate`` of the
    canonical rendering produced by ``_render_packet_json`` instead of the
    raw packet -- proving the rendering round-trips.  Returns the accumulated
    reconstruction per turn, which must equal the benchmark's recorded one.
    """
    from sqlalchemy import select

    from aifence.bus import db as db_module
    from aifence.bus.codec import AifenceCodec
    from aifence.bus.config import Settings
    from aifence.bus.db import SessionLocal
    from aifence.bus.db_models import LearnedPattern
    from aifence.bus.schemas import Packet

    db_module.init_db()
    cb._reset_schema(db_module)
    settings = Settings(
        auth_required=False,
        database_url=os.environ.get("AIFENCE_BUS_DATABASE_URL", "sqlite://"),
        context_accounting_enabled=True,
        learning_mode="managed",
        **spec.get("settings", {}),
    )
    reconstruction = ""
    per_turn: dict[int, str] = {}
    with SessionLocal() as db:
        codec = AifenceCodec(db, settings)
        for canonical in spec["codebook"]:
            codec.codebook.register("global", canonical)
        db.commit()

        warmup = spec.get("warmup")
        if warmup is not None:
            cb._pin_packet_id(codec, spec["id"], "warmup")
            codec.encode(cb._aifence_request(warmup, auto_learn=True, record_learning=True))
            pattern = db.scalar(select(LearnedPattern))
            if pattern is not None:
                codec.patterns.set_status(pattern.pattern_id, "active")
                db.commit()

        base_id: str | None = None
        for turn in range(6):
            cb._pin_packet_id(codec, spec["id"], turn)
            content = spec["content_fn"](turn)
            base_state = base_id if (turn > 0 and spec.get("chain_states")) else None
            inline_limit = spec.get("inline_limit") if turn == 0 else None
            encoded = codec.encode(
                cb._aifence_request(
                    content,
                    use_receiver_knowledge=spec.get("ack", False),
                    use_patterns=spec.get("patterns", True),
                    base_state=base_state,
                    inline_limit=inline_limit,
                )
            )
            rendered = h._render_packet_json(codec, encoded.packet)
            parsed = Packet.model_validate(json.loads(rendered))
            decoded = codec.decode(
                parsed,
                resolve_refs=spec.get("resolve_refs", False),
                receiver="bob",
                acknowledge=spec.get("ack", False),
            )
            piece = spec["render_fn"](decoded)
            reconstruction = f"{reconstruction} {piece}".strip()
            if spec.get("chain_states") and encoded.packet.meta.get("state"):
                base_id = str(encoded.packet.meta["state"])
            per_turn[turn] = reconstruction
    return per_turn


def _acked_receiver_known_counts(cb: Any, h: Any, spec: dict[str, Any]) -> dict[int, int]:
    """Replay an ACKed variant through the REAL codec, returning each turn's
    RAW packet ``meta.receiver_known_code_count``.

    The wire codec strips this key from its export and the rendering's meta
    is filtered to exactly the wire whitelist, so the ACK-growth is only
    observable at the PACKET level.  Mirrors the benchmark's per-variant
    session (schema reset, spec settings, codebook registration, pinned ids,
    per-turn encode + ACKed decode).
    """
    from aifence.bus import db as db_module
    from aifence.bus.codec import AifenceCodec
    from aifence.bus.config import Settings
    from aifence.bus.db import SessionLocal

    db_module.init_db()
    cb._reset_schema(db_module)
    settings = Settings(
        auth_required=False,
        database_url=os.environ.get("AIFENCE_BUS_DATABASE_URL", "sqlite://"),
        context_accounting_enabled=True,
        learning_mode="managed",
        **spec.get("settings", {}),
    )
    counts: dict[int, int] = {}
    base_id: str | None = None
    with SessionLocal() as db:
        codec = AifenceCodec(db, settings)
        for canonical in spec["codebook"]:
            codec.codebook.register("global", canonical)
        db.commit()
        for turn in range(6):
            cb._pin_packet_id(codec, spec["id"], turn)
            content = spec["content_fn"](turn)
            base_state = base_id if (turn > 0 and spec.get("chain_states")) else None
            inline_limit = spec.get("inline_limit") if turn == 0 else None
            encoded = codec.encode(
                cb._aifence_request(
                    content,
                    use_receiver_knowledge=spec.get("ack", False),
                    use_patterns=spec.get("patterns", True),
                    base_state=base_state,
                    inline_limit=inline_limit,
                )
            )
            counts[turn] = int(encoded.packet.meta.get("receiver_known_code_count", 0))
            codec.decode(
                encoded.packet,
                resolve_refs=spec.get("resolve_refs", False),
                receiver="bob",
                acknowledge=spec.get("ack", False),
            )
            if spec.get("chain_states") and encoded.packet.meta.get("state"):
                base_id = str(encoded.packet.meta["state"])
    return counts


def _sealed_adapters_config(command_tail: str = FAKE_ADAPTER_SEALED) -> dict[str, Any]:
    return {
        "acme-gpt-4o": {
            "family": "acme",
            "version": "gpt-4o-2026-05",
            "command": [sys.executable, "-c", command_tail],
        },
        "nebula-sonnet": {
            "family": "nebula",
            "version": "sonnet-2026-07",
            "command": [sys.executable, "-c", command_tail],
        },
    }


# ---------------------------------------------------------------------------
# Rendering determinism
# ---------------------------------------------------------------------------


def test_render_actual_packet_deterministic(cb, h):
    spec = h._aifence_variant_spec(cb, "v09")
    first = h._render_actual_packet(cb, spec, 1)
    second = h._render_actual_packet(cb, spec, 1)  # served from the cache
    assert first == second  # byte-identical strings
    # ... and a FRESH re-encode (new schema, new session) is byte-identical too
    fresh = h._render_aifence_variant_packets(cb, spec)[1]["rendering"]
    assert fresh == first
    assert isinstance(first, str) and json.loads(first)["bindings"]


# ---------------------------------------------------------------------------
# Real-packet structure
# ---------------------------------------------------------------------------


def test_real_packet_structure_v09(cb, h):
    entries = _render_all(cb, h)["v09"]
    rendered = json.loads(entries[0]["rendering"])
    assert set(rendered) == {
        "act", "atoms", "bindings", "cb", "id", "meta", "prov", "receiver", "refs", "sender", "v",
    }
    atoms = rendered["atoms"]
    assert atoms
    for atom in atoms:
        assert atom["code"] and "cv" in atom
    # every atom's code:cv maps to a non-empty canonical clause in the legend
    bindings = rendered["bindings"]
    assert bindings
    for atom in atoms:
        key = f"{atom['code']}:{atom['cv']}"
        assert key in bindings
        assert isinstance(bindings[key], str) and bindings[key]
    # spot-check the legend against the codebook's canonicals
    assert bindings["C00000001:1"] == "12"
    assert bindings["C00000002:1"] == "database_migrations_must_be_reviewed_by_the_platform_team"
    # the strategy is a codec-level fact, NOT part of the wire meta: the
    # rendering's meta is filtered to the wire whitelist (see
    # test_rendered_meta_is_wire_whitelist_only)
    assert entries[0]["strategy"] == "semantic"
    assert set(rendered["meta"]) <= WIRE_META_KEYS
    # the reconstruction is the recorded benchmark reconstruction (honesty)
    recorded = _recorded_turns(cb)["v09"]
    assert entries[0]["reconstruction"] == recorded[0]["reconstruction"]


def test_real_packet_structure_v11_state_reference_and_delta(cb, h):
    entries = _render_all(cb, h)["v11"]
    t0 = json.loads(entries[0]["rendering"])
    # reference packet: refs + meta.state, no atoms, no base/delta
    assert t0["refs"], "v11 turn 0 is a reference packet"
    assert all(str(ref).startswith("aifence:sha256:") for ref in t0["refs"])
    assert t0["meta"]["state"]
    assert entries[0]["strategy"] == "reference"
    assert t0["atoms"] == []
    assert t0["bindings"] == {}
    # delta packets: chained base + delta ops, state revision grows
    t1 = json.loads(entries[1]["rendering"])
    assert t1["base"] == t0["meta"]["state"]
    assert t1["delta"] and all("op" in op and "path" in op for op in t1["delta"])
    assert t1["meta"]["state"] and t1["meta"]["state"] != t0["meta"]["state"]
    assert t1["meta"]["revision"] == 2
    assert entries[1]["strategy"] == "delta"
    assert t1["refs"] == []
    assert t1["atoms"] == []
    # every turn still carries the full packet identity fields
    for turn in (0, 1, 5):
        packet = json.loads(entries[turn]["rendering"])
        for key in ("act", "cb", "id", "meta", "prov", "receiver", "sender", "v"):
            assert key in packet


def test_real_packet_structure_v12_acked(cb, h):
    entries = _render_all(cb, h)["v12"]
    t0 = json.loads(entries[0]["rendering"])
    atoms = t0["atoms"]
    assert atoms
    for atom in atoms:
        assert atom["code"] and "cv" in atom and "literal" in atom
    assert entries[0]["strategy"] == "semantic"
    assert t0["meta"]["state"]
    assert t0["refs"] == []
    # ACKed receiver knowledge grows after turn 0 -- a PACKET-level fact the
    # rendering cannot carry (the wire codec strips the key from its export
    # and the rendering's meta is filtered to exactly that whitelist), so the
    # growth is verified at the codec level
    counts = _acked_receiver_known_counts(cb, h, h._aifence_variant_spec(cb, "v12"))
    assert counts[0] == 0
    assert counts[1] > counts[0]
    t1 = json.loads(entries[1]["rendering"])
    assert t1["meta"]["revision"] == 2
    # bindings legend covers every atom
    for turn in (0, 1):
        packet = json.loads(entries[turn]["rendering"])
        for atom in packet["atoms"]:
            key = f"{atom['code']}:{atom['cv']}"
            assert key in packet["bindings"]
            assert packet["bindings"][key]


def test_real_packet_structure_v10_pattern_identifier_in_atoms(cb, h):
    entries = _render_all(cb, h)["v10"]
    t0 = json.loads(entries[0]["rendering"])
    # the learned-pattern identifier lands in an ATOM: a cv > 1 code whose
    # binding is the EXPANDED pattern canonical (multi-clause join)
    pattern_atoms = [atom for atom in t0["atoms"] if atom["cv"] > 1]
    assert pattern_atoms, "v10 turn 0 must reference the learned pattern via a cv>1 atom"
    for atom in pattern_atoms:
        binding = t0["bindings"][f"{atom['code']}:{atom['cv']}"]
        assert isinstance(binding, str) and binding
        assert " + " in binding, "pattern binding must be the expanded multi-clause canonical"
    # ... and NOT in meta (the rendering's meta is filtered to the wire
    # whitelist; v10's packets carry no wire-meta fields at all)
    assert t0["meta"] == {}
    assert set(t0["meta"]) <= WIRE_META_KEYS
    # later turns reference ordinary canonicals
    t1 = json.loads(entries[1]["rendering"])
    for atom in t1["atoms"]:
        assert atom["cv"] == 1
        assert t1["bindings"][f"{atom['code']}:{atom['cv']}"]


# ---------------------------------------------------------------------------
# Wire-meta whitelist (issue #22 stage-2 hardening): the rendering's meta
# must carry ONLY the keys the wire codec exports, so the rendering equals
# the real wire packet plus the bindings legend.
# ---------------------------------------------------------------------------


def test_rendered_meta_is_wire_whitelist_only(cb, h):
    for vid in AIFENCE_BUS_VARIANTS:
        entries = h._render_aifence_variant_packets(cb, h._aifence_variant_spec(cb, vid))
        for turn in range(6):
            packet = json.loads(entries[turn]["rendering"])
            meta = packet["meta"]
            non_wire = set(meta) - WIRE_META_KEYS
            assert set(meta) <= WIRE_META_KEYS, f"{vid} turn {turn}: meta carries non-wire keys {sorted(non_wire)}"
            for banned in ("codebook_fingerprint", "strategy", "receiver_known_code_count"):
                assert banned not in meta, f"{vid} turn {turn}: meta carries {banned!r}"


# ---------------------------------------------------------------------------
# NO stage-1 proxy shape
# ---------------------------------------------------------------------------


def test_sealed_aifence_packets_have_no_proxy_shape(cb, h):
    for vid in AIFENCE_BUS_VARIANTS:
        for turn in (0, 1):
            packet = json.loads(h._render_actual_packet(cb, h._aifence_variant_spec(cb, vid), turn))
            for key in PROXY_KEYS:
                assert key not in packet, f"{vid} turn {turn} carries proxy key {key!r}"
                assert key not in packet.get("meta", {}), f"{vid} turn {turn} meta carries {key!r}"
            assert "packet" not in packet, "stage-1 proxy's 'packet' id field must not leak"


# ---------------------------------------------------------------------------
# Wire-byte honesty vs the recorded benchmark
# ---------------------------------------------------------------------------


def test_wire_bytes_and_reconstruction_match_recorded_benchmark(cb, h):
    recorded = _recorded_turns(cb)
    for vid in AIFENCE_BUS_VARIANTS:
        entries = _render_all(cb, h)[vid]
        for turn in range(6):
            entry = entries[turn]
            rec = recorded[vid][turn]
            assert entry["wire_bytes_json"] == rec["wire_bytes_json"], (
                f"{vid} turn {turn}: rendered wire_bytes_json {entry['wire_bytes_json']} "
                f"!= recorded {rec['wire_bytes_json']}"
            )
            assert entry["wire_bytes_msgpack"] == rec["wire_bytes_msgpack"], (
                f"{vid} turn {turn}: rendered wire_bytes_msgpack {entry['wire_bytes_msgpack']} "
                f"!= recorded {rec['wire_bytes_msgpack']}"
            )
            assert entry["reconstruction"] == rec["reconstruction"], (
                f"{vid} turn {turn}: rendered reconstruction differs from recorded"
            )
            assert entry["note"] == rec["note"]


# ---------------------------------------------------------------------------
# Round-trip: rendering -> Packet.model_validate -> real codec decode
# ---------------------------------------------------------------------------


def test_rendering_roundtrip_reproduces_recorded_reconstruction(cb, h):
    recorded = _recorded_turns(cb)
    for vid in AIFENCE_BUS_VARIANTS:
        per_turn = _replay_rendering_roundtrip(cb, h, h._aifence_variant_spec(cb, vid))
        for turn in range(6):
            assert per_turn[turn] == recorded[vid][turn]["reconstruction"], (
                f"{vid} turn {turn}: round-tripped reconstruction {per_turn[turn]!r} "
                f"!= recorded {recorded[vid][turn]['reconstruction']!r}"
            )


# ---------------------------------------------------------------------------
# Sealed payload integration: wrapper adapter dumps its stdin end-to-end
# ---------------------------------------------------------------------------


def test_sealed_aifence_payload_integration_adapter_stdin(scratch_dir):
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_sealed_adapters_config(FAKE_ADAPTER_DUMP_STDIN)))
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    out_dir = scratch_dir / "out"
    completed = _run_cli_subprocess(
        ["--sealed", "--adapters", str(cfg), "--output", str(out_dir), "--variants", "v09,v12"],
        fake_home,
    )
    assert completed.returncode == 0, completed.stderr

    artifact = json.loads((out_dir / "model_eval_harness.json").read_text())
    assert artifact["evaluation_boundary"] == "sealed"
    assert artifact["rows"]

    dumped: dict[tuple[str, int], dict[str, Any]] = {}
    for path in fake_home.glob("aifence_bus_adapter_dump_*.json"):
        payload = json.loads(path.read_text())
        dumped[(payload["variant"], payload["turn"])] = payload

    for vid in ("v09", "v12"):
        for turn in range(6):
            payload = dumped[(vid, turn)]
            # sealed contract: no evaluator-only fields
            for key in LEAK_KEYS:
                assert key not in payload, f"{vid} turn {turn} leaked {key!r}"
            # the model-facing packet is the RENDERED ACTUAL packet
            packet = json.loads(payload["model_facing_packet"])
            assert packet["atoms"], f"{vid} turn {turn}: rendering has no atoms"
            assert packet["bindings"], f"{vid} turn {turn}: rendering has no bindings"
            for key in PROXY_KEYS:
                assert key not in packet
            assert "task" in payload and "allowed_decoder_metadata" in payload


# ---------------------------------------------------------------------------
# Non-sealed byte identity + sealed non-direct-symbolic reconstruction path
# ---------------------------------------------------------------------------


def test_non_sealed_and_other_modes_unchanged(h, cb, monkeypatch):
    monkeypatch.setenv("AIFENCE_BUS_BENCH_LLM_PROVIDER", "fake")

    # default-OFF run over a AIFENCE variant: no boundary, no packet-rendering fields
    results = h.run_harness(_sealed_adapters_config(FAKE_ADAPTER_OK), variants=["v09"])
    assert "evaluation_boundary" not in results
    for row in results["rows"]:
        assert "sealed" not in row
        assert "task_response" not in row
        assert "model_facing_packet" not in row
        assert "receiver_prior" in row  # unsealed rows keep the prior field

    # the unsealed AIFENCE representation is still the stage-1 proxy (byte-identical)
    aifence_bus_exchange = {
        **_exchange(1, variant="v09"),
        "variant": "v09",
        "representation": '{"packet": "P...", "strategy_note": "aifence strategy: semantic", "canonicals": ["x"]}',
        "reconstruction": "RECON-09",
        "wire_bytes": 182,
        "content": "SOURCE",
        "expected": {"qa": {}},
        "change_markers": [],
        "aifence": True,
    }
    payload = h._build_payload(cb, aifence_bus_exchange, "cold", "direct-symbolic", False)
    assert "strategy_note" in payload["representation"]  # proxy preserved for unsealed

    # sealed non-direct-symbolic modes still use the reconstruction path
    for mode in ("decoder-assisted", "full-expansion"):
        sealed = h._build_sealed_payload(cb, aifence_bus_exchange, "cold", mode, {"family": "a", "version": "1"})
        assert sealed["model_facing_packet"] == "RECON-09"
    # sealed direct-symbolic for a NON-AIFENCE variant still uses reconstruction
    plain_exchange = {**_exchange(1, variant="v05"), "reconstruction": "RECON-05", "aifence": False}
    sealed = h._build_sealed_payload(cb, plain_exchange, "cold", "direct-symbolic", {"family": "a", "version": "1"})
    assert sealed["model_facing_packet"] == "RECON-05"
    # ... and for a AIFENCE variant it is the rendered packet, not the proxy/reconstruction
    sealed = h._build_sealed_payload(cb, aifence_bus_exchange, "cold", "direct-symbolic", {"family": "a", "version": "1"})
    rendered = json.loads(sealed["model_facing_packet"])
    assert rendered["atoms"] and rendered["bindings"]
    assert sealed["model_facing_packet"] not in ("RECON-09", aifence_bus_exchange["representation"])


# ---------------------------------------------------------------------------
# Sealed determinism across two fresh CLI runs (AIFENCE variants)
# ---------------------------------------------------------------------------


def test_sealed_aifence_determinism_two_runs(scratch_dir):
    cfg = scratch_dir / "adapters.json"
    cfg.write_text(json.dumps(_sealed_adapters_config()))
    fake_home = scratch_dir / "fakehome"
    fake_home.mkdir()
    out_a = scratch_dir / "run-a"
    out_b = scratch_dir / "run-b"
    run_a = _run_cli_subprocess(
        ["--sealed", "--adapters", str(cfg), "--output", str(out_a), "--variants", "v09,v12"],
        fake_home,
    )
    assert run_a.returncode == 0, run_a.stderr
    run_b = _run_cli_subprocess(
        ["--sealed", "--adapters", str(cfg), "--output", str(out_b), "--variants", "v09,v12"],
        fake_home,
    )
    assert run_b.returncode == 0, run_b.stderr

    def _printed_table(run: subprocess.CompletedProcess, out_dir: Path) -> str:
        return run.stdout.split(f"Artifacts written to {out_dir}")[0]

    assert _printed_table(run_a, out_a) == _printed_table(run_b, out_b)

    def _strip_latency(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: _strip_latency(item) for key, item in value.items() if "latency" not in key}
        if isinstance(value, list):
            return [_strip_latency(item) for item in value]
        return value

    art_a = json.loads((out_a / "model_eval_harness.json").read_text())
    art_b = json.loads((out_b / "model_eval_harness.json").read_text())
    assert any("latency_ms" in row for row in art_a["rows"])
    assert _strip_latency(art_a) == _strip_latency(art_b)
    assert json.dumps(_strip_latency(art_a), sort_keys=True).encode("utf-8") == json.dumps(
        _strip_latency(art_b), sort_keys=True
    ).encode("utf-8")
    assert (out_a / "model_eval_harness.md").read_bytes() == (out_b / "model_eval_harness.md").read_bytes()
