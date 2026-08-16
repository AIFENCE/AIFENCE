# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from .api_helpers import concept_response
from .codebook import Codebook
from .config import get_settings
from .db import get_db
from .db_models import Concept
from .references import ReferenceAccessError, ReferenceExpiredError, ReferenceStore
from .resilience import QuotaExceededError
from .schemas import (
    ConceptAliasRequest,
    ConceptDeprecateRequest,
    ConceptRegisterRequest,
    ConceptResponse,
    MemoryTier,
    RefGrantRequest,
    RefPolicyRequest,
    ResolveRequest,
    StateCreateRequest,
    StatePatchRequest,
    StateResponse,
    StoreRequest,
    StoreResponse,
)
from .security import current_principal, enforce_agent_scope
from .state import StateStore

router = APIRouter()

settings = get_settings()

@router.post("/refs", response_model=StoreResponse)
def store_ref(req: StoreRequest, db: Session = Depends(get_db)) -> StoreResponse:
    req.owner = enforce_agent_scope(actor=req.owner, workspace=req.workspace)
    try:
        item = ReferenceStore(db, settings).put(
            req.value,
            req.media_type,
            workspace=req.workspace,
            owner=req.owner,
            acl=req.acl,
            allowed_paths=req.allowed_paths,
            tier=req.tier,
            ttl_seconds=req.ttl_seconds,
            encrypt=req.encrypt,
            provenance=req.provenance.model_dump() if req.provenance else {},
            sensitivity=req.sensitivity,
        )
    except QuotaExceededError as exc:
        raise HTTPException(429, str(exc), headers={"Retry-After": "1"}) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    grant = ReferenceStore(db, settings).grant_metadata(item.id, actor=req.owner, workspace=req.workspace, privileged=current_principal().is_service)
    db.commit()
    expires = grant.expires_at.isoformat() if grant.expires_at else None
    return StoreResponse(
        ref=item.id,
        byte_size=item.byte_size,
        tier=cast(MemoryTier, grant.tier),
        encrypted=item.ciphertext is not None,
        expires_at=expires,
    )

@router.post("/refs/resolve")
def resolve_ref(req: ResolveRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    req.actor = enforce_agent_scope(actor=req.actor, workspace=req.workspace)
    store = ReferenceStore(db, settings)
    try:
        item = store.get(req.ref, actor=req.actor, workspace=req.workspace)
    except (ReferenceAccessError, ReferenceExpiredError) as exc:
        raise HTTPException(403 if isinstance(exc, ReferenceAccessError) else 410, str(exc)) from exc
    if item is None:
        raise HTTPException(404, "reference not found")
    grant = store.grant_metadata(item.id, actor=req.actor, workspace=req.workspace)
    return {
        "ref": item.id, "media_type": item.media_type,
        "value": store.resolve(item.id, actor=req.actor, workspace=req.workspace, fields=req.fields),
        "byte_size": item.byte_size, "tier": grant.tier, "provenance": grant.provenance,
        "allowed_paths": grant.allowed_paths, "expires_at": grant.expires_at.isoformat() if grant.expires_at else None,
    }

@router.get("/refs/{ref_id}")
def get_ref(
    ref_id: str,
    actor: str | None = Query(default=None),
    workspace: str = Query(default="default"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return resolve_ref(ResolveRequest(ref=ref_id, actor=actor, workspace=workspace), db)

@router.post("/refs/{ref_id}/policy")
def ref_policy(ref_id: str, req: RefPolicyRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    req.actor = enforce_agent_scope(actor=req.actor, workspace=req.workspace)
    try:
        item = ReferenceStore(db, settings).policy(
            ref_id,
            actor=req.actor,
            workspace=req.workspace,
            tier=req.tier,
            ttl_seconds=req.ttl_seconds,
            invalidate=req.invalidate,
        )
    except ReferenceAccessError as exc:
        raise HTTPException(403, str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(404, "reference not found") from exc
    grant = ReferenceStore(db, settings).grant_metadata(item.id, actor=req.actor, workspace=req.workspace)
    db.commit()
    return {"ref": item.id, "tier": grant.tier, "invalidated": grant.invalidated_at is not None, "expires_at": grant.expires_at.isoformat() if grant.expires_at else None}

@router.post("/refs/{ref_id}/grant")
def ref_grant(ref_id: str, req: RefGrantRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    req.actor = enforce_agent_scope(actor=req.actor, workspace=req.workspace)
    store = ReferenceStore(db, settings)
    try:
        principal = current_principal()
        current = store.grant_metadata(
            ref_id,
            actor=req.actor,
            workspace=req.workspace,
            privileged=principal.is_service,
        )
        if not principal.is_service and current.owner != req.actor:
            raise ReferenceAccessError("only the owner or a service credential can delegate reference access")
        grant = store.grant(ref_id, workspace=req.workspace, owner=current.owner, acl=list(set(current.acl) | set(req.acl) | ({req.grantee} if req.grantee else set())), allowed_paths=req.allowed_paths or current.allowed_paths, tier=req.tier, ttl_seconds=req.ttl_seconds, provenance=current.provenance)
    except ReferenceAccessError as exc:
        raise HTTPException(403, str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(404, "reference not found") from exc
    db.commit()
    return {"ref": ref_id, "workspace": grant.workspace, "owner": grant.owner, "acl": grant.acl, "allowed_paths": grant.allowed_paths}

@router.post("/states", response_model=StateResponse)
def create_state(req: StateCreateRequest, db: Session = Depends(get_db)) -> StateResponse:
    req.created_by = enforce_agent_scope(actor=req.created_by, workspace=req.workspace)
    item = StateStore(db).create(
        req.value,
        workspace=req.workspace,
        created_by=req.created_by,
        provenance=req.provenance.model_dump() if req.provenance else {},
    )
    db.commit()
    return StateResponse(
        state=item.id,
        revision=item.revision,
        value=item.payload,
        parent=item.parent_id,
        provenance=item.provenance,
    )

@router.get("/states/{state_id}", response_model=StateResponse)
def get_state(
    state_id: str,
    workspace: str = Query(default="default"),
    db: Session = Depends(get_db),
) -> StateResponse:
    enforce_agent_scope(actor=None, workspace=workspace)
    item = StateStore(db).get(state_id, workspace=workspace)
    if item is None:
        raise HTTPException(404, "state not found")
    return StateResponse(
        state=item.id,
        revision=item.revision,
        value=item.payload,
        parent=item.parent_id,
        provenance=item.provenance,
    )

@router.get("/states/{state_id}/lineage")
def state_lineage(
    state_id: str,
    workspace: str = Query(default="default"),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    enforce_agent_scope(actor=None, workspace=workspace)
    lineage = StateStore(db).lineage(state_id, workspace=workspace)
    if not lineage:
        raise HTTPException(404, "state not found")
    return [
        {"state": item.id, "revision": item.revision, "parent": item.parent_id, "value": item.payload}
        for item in lineage
    ]

@router.post("/states/transition", response_model=StateResponse)
def transition(req: StatePatchRequest, db: Session = Depends(get_db)) -> StateResponse:
    req.created_by = enforce_agent_scope(actor=req.created_by, workspace=req.workspace)
    try:
        item, patch = StateStore(db).transition(
            req.base,
            req.value,
            is_patch=req.mode == "patch",
            workspace=req.workspace,
            created_by=req.created_by,
            provenance=req.provenance.model_dump() if req.provenance else {},
        )
    except KeyError as exc:
        raise HTTPException(404, "base state not found") from exc
    db.commit()
    return StateResponse(
        state=item.id,
        revision=item.revision,
        value=item.payload,
        parent=item.parent_id,
        delta=patch,
        provenance=item.provenance,
    )

@router.post("/concepts", response_model=ConceptResponse)
def register_concept(req: ConceptRegisterRequest, db: Session = Depends(get_db)) -> ConceptResponse:
    try:
        item = Codebook(db, settings).register(
            req.codebook or settings.codebook,
            req.canonical,
            req.description,
            req.aliases,
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    db.commit()
    return concept_response(item, db)

@router.post("/concepts/{code}/aliases")
def add_alias(code: str, req: ConceptAliasRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        item = Codebook(db, settings).add_alias(code, req.alias)
    except KeyError as exc:
        raise HTTPException(404, "concept not found") from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    db.commit()
    return {"code": code, "alias": item.alias}

@router.post("/concepts/{code}/deprecate", response_model=ConceptResponse)
def deprecate_concept(code: str, req: ConceptDeprecateRequest, db: Session = Depends(get_db)) -> ConceptResponse:
    cb = Codebook(db, settings)
    try:
        concept_id = int(code[1:], 16)
    except (ValueError, IndexError) as exc:
        raise HTTPException(404, "concept not found") from exc
    raw = db.get(Concept, concept_id)
    if raw is None:
        raise HTTPException(404, "concept not found")
    try:
        item = cb.deprecate(code, req.replacement_code)
    except (KeyError, ValueError) as exc:
        raise HTTPException(422, str(exc)) from exc
    db.commit()
    return concept_response(item, db)

@router.get("/concepts", response_model=list[ConceptResponse])
def list_concepts(
    codebook: str | None = None,
    limit: int = 100,
    include_deprecated: bool = False,
    db: Session = Depends(get_db),
) -> list[ConceptResponse]:
    limit = max(1, min(limit, 1000))
    cb = codebook or settings.codebook
    stmt = select(Concept).where(Concept.codebook == cb)
    if not include_deprecated:
        stmt = stmt.where(Concept.status == "active")
    items = db.scalars(stmt.order_by(Concept.id).limit(limit))
    return [concept_response(c, db) for c in items]
