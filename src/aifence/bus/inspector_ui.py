# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import html
import json
from typing import Any


def render_inspector(report: dict[str, Any]) -> str:
    wf = report["waterfall"]
    original = max(1, int(wf["original_bytes"]))
    sent_pct = min(100.0, 100.0 * int(wf["sent_bytes"]) / original)
    avoided_pct = max(0.0, 100.0 - sent_pct)
    patterns = "".join(
        f"<tr><td>{html.escape(str(item.get('pattern_id','')))}</td><td>{html.escape(str(item.get('action','')))}</td><td>{html.escape(str(item.get('estimated_savings_bytes',0)))}</td></tr>"
        for item in report["patterns"]
    ) or "<tr><td colspan='3'>None</td></tr>"
    refs = "".join(
        f"<tr><td>{html.escape(str(item.get('ref','')))}</td><td>{html.escape(str(item.get('byte_size','')))}</td></tr>"
        for item in report["refs"]
    ) or "<tr><td colspan='2'>None</td></tr>"
    decisions = html.escape(json.dumps(report["decisions"], indent=2, sort_keys=True))
    return f"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>SAGE Inspector</title><style>body{{font-family:ui-monospace,monospace;margin:0;background:#101216;color:#edf1f7}}main{{max-width:1100px;margin:auto;padding:28px}}section{{background:#171a20;border:1px solid #2b303a;border-radius:10px;padding:18px;margin:16px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}}.metric{{padding:12px;background:#11141a;border-radius:8px}}.bar{{display:flex;height:26px;border-radius:6px;overflow:hidden;background:#343a46}}.sent{{width:{sent_pct:.4f}%;background:#d9e2f2}}.avoided{{width:{avoided_pct:.4f}%;background:#596579}}table{{width:100%;border-collapse:collapse}}th,td{{padding:8px;border-bottom:1px solid #2b303a;text-align:left;vertical-align:top}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}small{{color:#aeb7c5}}</style></head><body><main><h1>SAGE Inspector</h1><small>{html.escape(report['packet_id'])}</small><section><div class='grid'><div class='metric'>Original<br><strong>{report['original_bytes']} bytes</strong><br>{report['estimated_original_tokens']} tokens est.</div><div class='metric'>Sent<br><strong>{report['sent_bytes']} bytes</strong><br>{report['estimated_sent_tokens']} tokens est.</div><div class='metric'>Known ratio<br><strong>{float(report['receiver_known_ratio'] or 0):.3f}</strong></div><div class='metric'>Semantic loss<br><strong>{float(report['semantic_loss_score'] or 0):.6f}</strong></div></div></section><section><h2>Compression waterfall</h2><div class='bar'><div class='sent' title='sent'></div><div class='avoided' title='avoided'></div></div><table><tr><th>Stage</th><th>Value</th></tr><tr><td>Receiver-known bytes estimate</td><td>{wf['receiver_known_bytes_estimate']}</td></tr><tr><td>Pattern bytes avoided estimate</td><td>{wf['pattern_bytes_avoided_estimate']}</td></tr><tr><td>Reference bytes avoided</td><td>{wf['ref_bytes_avoided']}</td></tr><tr><td>Total bytes avoided</td><td>{wf['total_bytes_avoided']}</td></tr><tr><td>Byte reduction ratio</td><td>{float(wf['byte_reduction_ratio']):.4f}</td></tr></table></section><section><h2>Patterns</h2><table><tr><th>Pattern</th><th>Decision</th><th>Estimated savings</th></tr>{patterns}</table></section><section><h2>References</h2><table><tr><th>Reference</th><th>Bytes</th></tr>{refs}</table></section><section><h2>Decision trace</h2><pre>{decisions}</pre></section></main></body></html>"""
