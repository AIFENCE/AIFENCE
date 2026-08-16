# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from .api_helpers import bus_response
from .bus import SemanticBus
from .checkpoints import CheckpointStore
from .codebook_releases import CodebookReleaseStore
from .config import get_settings
from .db import get_db
from .db_models import Contradiction
from .economics import run_sage_economics_benchmark, score_observed_runs
from .evals import run_eval
from .facts import FactStore
from .federation import FederationStore
from .inspector import Inspector
from .inspector_ui import render_inspector
from .maintenance import cleanup
from .merkle import CodebookMerkle
from .reliability import ModelIdentityStore, ReliabilityMonitor
from .routing import SemanticPubSub, SemanticRouter
from .schemas import (
    AgentCapabilityRequest,
    BusMessageResponse,
    CheckpointResponse,
    CodebookReleaseRequest,
    ContradictionResolveRequest,
    EconomicsBenchmarkRequest,
    EvalRequest,
    FactInvalidateRequest,
    FactPutRequest,
    FactResponse,
    FederationImportRequest,
    FederationPeerRequest,
    MerkleSyncRequest,
    ModelIdentityRequest,
    ModelIdentityResponse,
    NativeTokenGateRequest,
    NativeTokenGateResponse,
    ObservedEconomicsRequest,
    PublishRequest,
    ReliabilityResponse,
    RouteRequest,
    SubscriptionRequest,
)
from .security import current_principal, enforce_agent_scope
from .state import StateStore

router = APIRouter()

settings = get_settings()

@router.post("/facts", response_model=FactResponse)
def put_fact(req: FactPutRequest, db: Session = Depends(get_db)) -> FactResponse:
    source = enforce_agent_scope(actor=req.source, workspace=req.workspace)
    store = FactStore(db)
    item = store.put(workspace=req.workspace, subject=req.subject, predicate=req.predicate, object=req.object, epistemic_type=req.epistemic_type, source=source, confidence=req.confidence, provenance=req.provenance.model_dump() if req.provenance else {}, depends_on=req.depends_on, sensitivity=req.sensitivity)
    db.commit()
    return FactResponse.model_validate(store.response(item))

@router.get("/facts/{fact_id}", response_model=FactResponse)
def get_fact(fact_id: str, workspace: str = Query(default="default"), db: Session = Depends(get_db)) -> FactResponse:
    enforce_agent_scope(actor=None, workspace=workspace)
    store = FactStore(db)
    item = store.get(fact_id, workspace=workspace)
    if item is None:
        raise HTTPException(404, "fact not found")
    return FactResponse.model_validate(store.response(item))

@router.post("/facts/{fact_id}/invalidate")
def invalidate_fact(fact_id: str, req: FactInvalidateRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    enforce_agent_scope(actor=None, workspace=req.workspace)
    store = FactStore(db)
    fact = store.get(fact_id, workspace=req.workspace)
    if fact is None:
        raise HTTPException(404, "fact not found")
    try:
        ids = store.invalidate(fact_id, reason=req.reason)
    except KeyError as exc:
        raise HTTPException(404, "fact not found") from exc
    db.commit()
    return {"invalidated": ids}

@router.post("/contradictions/{contradiction_id}/resolve")
def resolve_contradiction(contradiction_id: str, req: ContradictionResolveRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    enforce_agent_scope(actor=None, workspace=req.workspace)
    existing = db.get(Contradiction, contradiction_id)
    if existing is None or existing.workspace != req.workspace:
        raise HTTPException(404, "contradiction not found")
    try:
        item = FactStore(db).resolve_contradiction(contradiction_id, req.winner_fact_id, req.note)
    except KeyError as exc:
        raise HTTPException(404, "contradiction not found") from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    db.commit()
    return {"contradiction_id": item.id, "status": item.status, "resolution": item.resolution}

@router.post("/subscriptions")
def subscribe(req: SubscriptionRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    agent = enforce_agent_scope(actor=req.agent, workspace=req.workspace) or req.agent
    item = SemanticPubSub(db, settings).subscribe(workspace=req.workspace, agent=agent, concepts=req.concepts, filters=req.filters, min_confidence=req.min_confidence)
    db.commit()
    return {"subscription_id": item.id, "agent": item.agent, "concepts": item.concepts}

@router.post("/publish")
def publish(req: PublishRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    sender = enforce_agent_scope(actor=req.sender, workspace=req.workspace)
    recipients = SemanticPubSub(db, settings).publish(content=req.content, workspace=req.workspace, sender=sender, confidence=req.confidence, source_ids=req.source_ids)
    db.commit()
    return {"recipients": recipients, "count": len(recipients)}

@router.post("/routing/agents")
def register_agent_capability(req: AgentCapabilityRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    item = SemanticRouter(db, settings).register_agent(workspace=req.workspace, agent=req.agent, capabilities=req.capabilities, authority=req.authority, cost_score=req.cost_score, latency_ms=req.latency_ms, available=req.available, metadata=req.metadata)
    db.commit()
    return {"agent": item.agent, "capabilities": item.capabilities, "authority": item.authority, "available": item.available}

@router.post("/routing/choose")
def route_choose(req: RouteRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    sender = enforce_agent_scope(actor=req.sender, workspace=req.workspace)
    try:
        winner, score = SemanticRouter(db, settings).choose(content=req.content, workspace=req.workspace, capability=req.capability, authority=req.authority, exclude={sender} if sender else None)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {"agent": winner.agent, "score": score}

@router.post("/routing/send", response_model=BusMessageResponse)
def route_send(req: RouteRequest, db: Session = Depends(get_db)) -> BusMessageResponse:
    sender = enforce_agent_scope(actor=req.sender, workspace=req.workspace)
    try:
        winner, _ = SemanticRouter(db, settings).choose(content=req.content, workspace=req.workspace, capability=req.capability, authority=req.authority, exclude={sender} if sender else None)
        item = SemanticBus(db, settings).handoff(receiver=winner.agent, content=req.content, sender=sender, act="route", workspace=req.workspace)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    db.commit()
    return bus_response(item)

@router.post("/federation/peers")
def federation_peer(req: FederationPeerRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        item = FederationStore(db, settings).register_peer(workspace=req.workspace, name=req.name, base_url=req.base_url, public_key_b64=req.public_key_b64, allowed_namespaces=req.allowed_namespaces, enabled=req.enabled)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    db.commit()
    return {"peer_id": item.id, "name": item.name, "allowed_namespaces": item.allowed_namespaces}

@router.get("/federation/export/{namespace}")
def federation_export(namespace: str, source: str = Query(default="local"), db: Session = Depends(get_db)) -> dict[str, Any]:
    return FederationStore(db, settings).export_bundle(namespace, source=source)

@router.post("/federation/import")
def federation_import(req: FederationImportRequest, db: Session = Depends(get_db)) -> dict[str, int]:
    try:
        result = FederationStore(db, settings).import_bundle(req.bundle, workspace=req.workspace)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    db.commit()
    return result

@router.post("/evals/run")
def eval_run(req: EvalRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    return run_eval(db, settings, req)

@router.post("/benchmarks/economics")
def economics_benchmark(req: EconomicsBenchmarkRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Measure model-token/cost economics across raw, JSON, refs, SAGE, and supplied RAG/summary baselines."""
    try:
        return run_sage_economics_benchmark(db, settings, req)
    except RuntimeError as exc:
        raise HTTPException(422, str(exc)) from exc
    except (ValueError, httpx.HTTPError) as exc:
        raise HTTPException(422, str(exc)) from exc

@router.post("/benchmarks/economics/observed")
def economics_observed(req: ObservedEconomicsRequest) -> dict[str, Any]:
    """Score actual recorded provider usage as cost per successful task."""
    return score_observed_runs([row.model_dump(exclude_none=True) for row in req.observations], req.price.model_dump())

@router.post("/native-token-gate", response_model=NativeTokenGateResponse)
def native_token_gate(req: NativeTokenGateRequest) -> NativeTokenGateResponse:
    allowed = req.eval_score >= settings.native_token_min_eval_score
    return NativeTokenGateResponse(
        allowed=allowed,
        required_score=settings.native_token_min_eval_score,
        reason=(
            "semantic fidelity threshold met; native-token experimentation may proceed behind a feature flag"
            if allowed
            else "native semantic tokens are intentionally gated until eval fidelity meets the configured threshold"
        ),
    )

@router.get("/bus/backpressure")
def bus_backpressure(workspace: str = "default", db: Session = Depends(get_db)) -> dict[str, Any]:
    enforce_agent_scope(actor=None, workspace=workspace)
    return SemanticBus(db, settings).backpressure(workspace=workspace)

@router.post("/receivers/model-identity", response_model=ModelIdentityResponse)
def receiver_model_identity(req: ModelIdentityRequest, db: Session = Depends(get_db)) -> ModelIdentityResponse:
    enforce_agent_scope(actor=req.receiver, workspace=req.workspace)
    item = ModelIdentityStore(db).register(
        workspace=req.workspace, receiver=req.receiver, provider=req.provider, model=req.model,
        model_version=req.model_version, runtime=req.runtime, runtime_version=req.runtime_version,
        configuration=req.configuration,
    )
    db.commit()
    return ModelIdentityResponse.model_validate({
        "receiver": item.receiver, "workspace": item.workspace, "provider": item.provider, "model": item.model,
        "model_version": item.model_version, "runtime": item.runtime, "runtime_version": item.runtime_version,
        "config_hash": item.config_hash, "identity_hash": item.identity_hash, "active": item.active,
    })

@router.get("/receivers/{receiver}/reliability", response_model=ReliabilityResponse)
def receiver_reliability(receiver: str, model_identity_hash: str, workspace: str = "default", pattern_db_id: int | None = None, task_family: str = "*", db: Session = Depends(get_db)) -> ReliabilityResponse:
    enforce_agent_scope(actor=receiver, workspace=workspace)
    report = ReliabilityMonitor(db, settings).latest_status(workspace=workspace, receiver=receiver, model_identity_hash=model_identity_hash, pattern_id=pattern_db_id, task_family=task_family)
    return ReliabilityResponse.model_validate(report)

@router.get("/codebooks/{namespace}/merkle")
def codebook_merkle(namespace: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    manifest = CodebookMerkle(db).manifest(namespace)
    return {"namespace": manifest.namespace, "root": manifest.root, "partitions": manifest.partitions, "entries": manifest.entries}

@router.post("/codebooks/sync")
def codebook_sync(req: MerkleSyncRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    store = CodebookMerkle(db)
    manifest = store.manifest(req.namespace)
    return {"namespace": req.namespace, "root": manifest.root, **store.diff(manifest, req.remote)}

@router.post("/codebooks/releases")
def codebook_release(req: CodebookReleaseRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    if not current_principal().is_service:
        raise HTTPException(403, "service credential required")
    if settings.packet_signing_private_key is None:
        raise HTTPException(503, "signing key is not configured")
    try:
        item = CodebookReleaseStore(db).create(req.namespace, req.release, settings.packet_signing_private_key.get_secret_value(), settings.packet_signing_key_id)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    db.commit()
    return {"id": item.id, "namespace": item.namespace, "release": item.release, "merkle_root": item.merkle_root, "key_id": item.key_id, "signature": item.signature}

@router.post("/states/{state_id}/checkpoint", response_model=CheckpointResponse)
def state_checkpoint(state_id: str, workspace: str = "default", db: Session = Depends(get_db)) -> CheckpointResponse:
    state = StateStore(db, settings).get(state_id, workspace=workspace)
    if state is None:
        raise HTTPException(404, "state not found")
    item = CheckpointStore(db, settings).create(state)
    db.commit()
    return CheckpointResponse(checkpoint_id=item.id, state_id=item.state_id, revision=item.revision, payload_hash=item.payload_hash)

@router.get("/inspect/ui/{packet_id}", response_class=HTMLResponse)
def inspect_ui(packet_id: str, db: Session = Depends(get_db)) -> HTMLResponse:
    principal = current_principal()
    workspace = principal.workspace if principal.kind == "agent" else None
    actor = principal.agent if principal.kind == "agent" else None
    try:
        report = Inspector(db).packet(packet_id, workspace=workspace, actor=actor)
    except KeyError as exc:
        raise HTTPException(404, "packet not found") from exc
    return HTMLResponse(
        render_inspector(report),
        headers={"Cache-Control": "no-store", "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'"},
    )

@router.post("/maintenance/cleanup")
def maintenance_cleanup(db: Session = Depends(get_db)) -> dict[str, int]:
    return cleanup(db, settings)

@router.get("/ready")
def ready(db: Session = Depends(get_db)) -> dict[str, bool]:
    db.execute(text("SELECT 1"))
    return {"ready": True}
