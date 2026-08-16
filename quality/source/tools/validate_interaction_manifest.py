#!/usr/bin/env python3
"""Validate a BizIQ interaction-closure manifest."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('manifest');ap.add_argument('--out');a=ap.parse_args()
schema=json.loads((ROOT/'schemas'/'interaction_closure_manifest.schema.json').read_text(encoding='utf-8'))
raw=json.loads(Path(a.manifest).read_text(encoding='utf-8'))
errors=[]
for err in Draft202012Validator(schema).iter_errors(raw): errors.append({'path':'/'.join(map(str,err.path)),'error':err.message})
controls=raw.get('controls',[]) if isinstance(raw,dict) else []
tasks=raw.get('tasks',[]) if isinstance(raw,dict) else []
def duplicate_ids(items):
    ids=[x.get('id') for x in items if isinstance(x,dict) and x.get('id')]
    return sorted({x for x in ids if ids.count(x)>1})
for kind,items in [('control',controls),('task',tasks)]:
    for x in duplicate_ids(items): errors.append({'path':f'{kind}s','error':f'duplicate {kind} id: {x}'})
for c in controls:
    if not c.get('enabled',True) and not (c.get('disabled_reason') or '').strip():
        errors.append({'path':f"controls/{c.get('id','?')}",'error':'disabled control requires disabled_reason'})
for t in tasks:
    if t.get('priority') in {'P0','P1'}:
        v=set(t.get('required_viewports',[]))
        if not {320,390}.issubset(v): errors.append({'path':f"tasks/{t.get('id','?')}/required_viewports",'error':'P0/P1 web task must include 320 and 390'})
        if not (t.get('mobile_equivalent') or '').strip(): errors.append({'path':f"tasks/{t.get('id','?')}/mobile_equivalent",'error':'P0/P1 task requires an explicit mobile equivalent'})
summary={'ok':not errors,'artifact_id':raw.get('artifact_id') if isinstance(raw,dict) else None,'controls':len(controls),'tasks':len(tasks),'errors':errors}
if a.out: Path(a.out).write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2));sys.exit(0 if summary['ok'] else 1)
