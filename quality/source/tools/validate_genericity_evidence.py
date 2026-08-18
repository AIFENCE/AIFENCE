#!/usr/bin/env python3
"""Validate AIFENCE dense-product structural genericity evidence."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('evidence');ap.add_argument('--out');a=ap.parse_args()
schema=json.loads((ROOT/'schemas'/'genericity_evidence.schema.json').read_text(encoding='utf-8'))
raw=json.loads(Path(a.evidence).read_text(encoding='utf-8'))
errors=[]
for err in Draft202012Validator(schema).iter_errors(raw):
    errors.append({'path':'/'.join(map(str,err.path)),'error':err.message})
if isinstance(raw,dict):
    decisions=raw.get('structural_decisions',[])
    substantive={'user-job','workflow','domain-data','proof-model'}
    if len([d for d in decisions if d.get('source') in substantive])<2:
        errors.append({'path':'structural_decisions','error':'at least two structural decisions must derive from user-job/workflow/domain-data/proof-model'})
    family=raw.get('artifact_family')
    min_grammars=4 if family in {'saas-web-app','dashboard','portal'} else 3
    if len(set(raw.get('component_grammars',[])))<min_grammars:
        errors.append({'path':'component_grammars','error':f'{family} requires at least {min_grammars} distinct meaningful grammar families'})
    min_links=3 if family in {'saas-web-app','dashboard','portal'} else 2
    if len(raw.get('task_structure_links',[]))<min_links:
        errors.append({'path':'task_structure_links','error':f'{family} requires at least {min_links} task-to-structure links'})
    sim=raw.get('template_similarity',{})
    score=sim.get('score'); threshold=sim.get('threshold')
    if threshold is not None and threshold>0.60:
        errors.append({'path':'template_similarity/threshold','error':'premium dense-product threshold may not exceed 0.60'})
    if score is not None and score>=0.61:
        errors.append({'path':'template_similarity/score','error':'best generic-template similarity >= 0.61 is non-pass'})
    if raw.get('status')=='PASS' and errors:
        errors.append({'path':'status','error':'PASS is invalid while structural genericity closure errors remain'})
summary={'ok':not errors,'artifact_id':raw.get('artifact_id') if isinstance(raw,dict) else None,'errors':errors}
if a.out:Path(a.out).write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2));sys.exit(0 if summary['ok'] else 1)
