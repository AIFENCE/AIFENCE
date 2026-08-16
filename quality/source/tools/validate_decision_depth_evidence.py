#!/usr/bin/env python3
"""Validate BizIQ complex-B2B buyer decision-depth evidence."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('evidence');ap.add_argument('--out');a=ap.parse_args()
schema=json.loads((ROOT/'schemas'/'decision_depth_evidence.schema.json').read_text(encoding='utf-8'))
raw=json.loads(Path(a.evidence).read_text(encoding='utf-8'))
errors=[]
for err in Draft202012Validator(schema).iter_errors(raw):errors.append({'path':'/'.join(map(str,err.path)),'error':err.message})
if isinstance(raw,dict):
    paths=raw.get('decision_paths',[])
    if len({p.get('id') for p in paths if p.get('id')}) != len([p for p in paths if p.get('id')]):
        errors.append({'path':'decision_paths','error':'decision path ids must be unique'})
    # Require at least two materially different decisions/surfaces, not duplicated CTA wrappers.
    if len({p.get('buyer_decision','').strip().lower() for p in paths})<2:
        errors.append({'path':'decision_paths','error':'at least two distinct buyer decisions are required'})
    if len({p.get('artifact_surface','').strip().lower() for p in paths})<2:
        errors.append({'path':'decision_paths','error':'decision depth must appear in at least two distinct observable artifact surfaces'})
    if raw.get('status')=='PASS' and errors:errors.append({'path':'status','error':'PASS is invalid while decision-depth closure errors remain'})
summary={'ok':not errors,'artifact_id':raw.get('artifact_id') if isinstance(raw,dict) else None,'errors':errors}
if a.out:Path(a.out).write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2));sys.exit(0 if summary['ok'] else 1)
