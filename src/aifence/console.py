# SPDX-License-Identifier: AGPL-3.0-or-later
"""The operator console: one view of what the fence is actually doing.

A JSON status API plus a server-rendered page. Two constraints shape it:

* **Authenticated like everything else.** The console reads tenant-scoped
  operational data, so it requires the same API-key identity the rest of the
  fence uses — there is no separate, weaker console login.
* **CSP-safe.** The application sends a strict Content-Security-Policy, so the
  page carries no inline script and no external assets. It is rendered
  server-side and refreshes with a plain meta refresh rather than fetch loops.
"""
from __future__ import annotations

import html
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select

from .security import IdentityDep

router = APIRouter(prefix="/v1/console", tags=["console"])


def _breaker_view(app_state: Any) -> list[dict[str, Any]]:
    breakers = app_state.flow_breakers
    return [
        {
            "tier": tier,
            "state": breaker.state,
            "paradigm": breaker.policy.paradigm,
            "timeout_seconds": breaker.policy.timeout_seconds,
        }
        for tier, breaker in (
            ("quality", breakers.quality),
            ("guard", breakers.guard),
            ("bus", breakers.bus),
        )
    ]


def _bus_view(request: Request, tenant_id: str) -> dict[str, Any]:
    """Handoff counts by status, scoped to the durable bus."""
    from .bus.db_models import BusMessage

    del tenant_id  # bus messages are workspace-scoped, not tenant-scoped
    counts: dict[str, int] = {}
    with request.app.state.session_factory() as session:
        rows = session.execute(
            select(BusMessage.status, func.count(BusMessage.id)).group_by(BusMessage.status)
        ).all()
        for status, count in rows:
            counts[str(status)] = int(count)
    return {"messages_by_status": counts, "total": sum(counts.values())}


def _approvals_view(request: Request, tenant_id: str) -> dict[str, Any]:
    """Pending approvals awaiting a human decision, for this tenant only."""
    from .guard.models import Approval

    with request.app.state.session_factory() as session:
        pending = session.execute(
            select(func.count(Approval.id)).where(
                Approval.tenant_id == tenant_id, Approval.status == "pending"
            )
        ).scalar_one()
    return {"pending": int(pending)}


@router.get("/status", summary="Operational status across every fence tier")
def status(request: Request, identity: IdentityDep) -> dict[str, Any]:
    identity.require("decisions:read")
    state = request.app.state
    return {
        "version": state.version,
        "environment": state.settings.environment,
        "region": state.settings.region or None,
        "subsystems": state.subsystems,
        "breakers": _breaker_view(state),
        "bus": _bus_view(request, identity.tenant_id),
        "approvals": _approvals_view(request, identity.tenant_id),
        "transport": {"backend": state.bus_transport.name},
        "quality": _quality_view(),
    }


def _quality_view() -> dict[str, Any]:
    from .quality.controls import registry_summary

    summary = registry_summary()
    return {"controls": summary.get("total_controls", 0), "loaded": summary.get("loaded", False)}


_STYLE = """
:root{color-scheme:light dark}
body{font:14px/1.5 ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
margin:0;padding:2rem;background:#0f1115;color:#e6e8ee}
h1{font-size:1.25rem;margin:0 0 .25rem}
p.sub{color:#8b93a7;margin:0 0 1.5rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:1rem}
.card{background:#171a21;border:1px solid #242936;border-radius:10px;padding:1rem}
.card h2{font-size:.75rem;text-transform:uppercase;letter-spacing:.08em;
color:#8b93a7;margin:0 0 .6rem}
.metric{font-size:1.6rem;font-weight:600}
table{width:100%;border-collapse:collapse;margin-top:.25rem}
td{padding:.25rem 0;border-bottom:1px solid #242936}
td:last-child{text-align:right;color:#aab2c5}
.pill{display:inline-block;padding:.1rem .5rem;border-radius:999px;font-size:.75rem}
.ok{background:#10331f;color:#5ddc9a}.warn{background:#3a2f10;color:#e8c34a}
.bad{background:#3a1414;color:#ff8080}
footer{margin-top:1.5rem;color:#6b7488;font-size:.75rem}
"""


def _pill(state: str) -> str:
    cls = {"closed": "ok", "half_open": "warn", "open": "bad"}.get(state, "warn")
    return f'<span class="pill {cls}">{html.escape(state)}</span>'


def _rows(pairs: list[tuple[str, str]]) -> str:
    return "".join(
        f"<tr><td>{html.escape(k)}</td><td>{v}</td></tr>" for k, v in pairs
    ) or "<tr><td>none</td><td>&mdash;</td></tr>"


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def console(request: Request, identity: IdentityDep) -> HTMLResponse:
    data = status(request, identity)
    breakers = _rows([(b["tier"], _pill(str(b["state"]))) for b in data["breakers"]])
    bus_counts = _rows(
        [(k, str(v)) for k, v in sorted(data["bus"]["messages_by_status"].items())]
    )
    subsystems = _rows([(s.replace("aifence.", ""), _pill("closed")) for s in data["subsystems"]])
    body = f"""<!-- server-rendered: the app sends a strict CSP, so no inline script -->
<h1>AIFENCE operator console</h1>
<p class="sub">{html.escape(str(data['environment']))}
&middot; v{html.escape(str(data['version']))}
&middot; tenant {html.escape(identity.tenant_id)}</p>
<div class="grid">
  <div class="card"><h2>Handoffs</h2>
    <div class="metric">{data['bus']['total']}</div>
    <table>{bus_counts}</table></div>
  <div class="card"><h2>Approvals pending</h2>
    <div class="metric">{data['approvals']['pending']}</div></div>
  <div class="card"><h2>Circuit breakers</h2><table>{breakers}</table></div>
  <div class="card"><h2>Subsystems</h2><table>{subsystems}</table></div>
  <div class="card"><h2>Quality controls</h2>
    <div class="metric">{data['quality']['controls']}</div></div>
  <div class="card"><h2>Bus transport</h2>
    <div class="metric">{html.escape(str(data['transport']['backend']))}</div></div>
</div>
<footer>Refreshes every 15s. Region: {html.escape(str(data['region'] or 'unset'))}</footer>"""
    page = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta http-equiv="refresh" content="15">'
        "<title>AIFENCE console</title>"
        f"<style>{_STYLE}</style></head><body>{body}</body></html>"
    )
    # The style element is inline, so the response carries its own CSP allowing
    # exactly that and nothing else — no script, no external origins.
    return HTMLResponse(
        page,
        headers={
            "Content-Security-Policy": (
                "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; "
                "frame-ancestors 'none'; form-action 'none'"
            )
        },
    )
