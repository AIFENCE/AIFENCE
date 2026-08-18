#!/usr/bin/env python3
"""Generate AIFENCE capability/control activation, regression, benchmark, and dead-rule review inventory."""
from __future__ import annotations
import csv,json,re,argparse
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--out',default='coverage_report.json');a=ap.parse_args()
rows=[]
for fp in [ROOT/'control_registry.csv',*sorted((ROOT/'control_registry').glob('*.csv'))]:
    with fp.open(encoding='utf-8',newline='') as f: rows+=list(csv.DictReader(f))
reg=[]
for fp in [ROOT/'evals'/'control_regression_matrix.json',*sorted((ROOT/'evals').glob('control_regression_matrix_*.json'))]:
    if fp.exists(): reg+=json.loads(fp.read_text(encoding='utf-8'))
e2e=[]
for fp in sorted((ROOT/'evals').glob('*end_to_end*.json')):
    try:
        x=json.loads(fp.read_text(encoding='utf-8'))
        if isinstance(x,list):e2e += [(fp.name,item) for item in x]
    except Exception:pass
bench=[]
for fp in sorted((ROOT/'benchmarks').glob('*.json')):
    try:
        x=json.loads(fp.read_text(encoding='utf-8'))
        if isinstance(x,list): bench += [(fp.name,item) for item in x]
    except Exception: pass
by=defaultdict(list)
for r in rows: by[r['capability_id']].append(r)

def hits(items,cid,name):
    toks=[t for t in re.findall(r'[a-z0-9]+',name.lower()) if len(t)>4]
    out=[]
    for fn,item in items:
        txt=json.dumps(item).lower()
        if cid.lower() in txt or name.lower() in txt or (toks and sum(t in txt for t in toks)>=min(2,len(toks))):out.append(item.get('id') or fn)
    return sorted(set(filter(None,out)))

out=[]
for cid,rs in sorted(by.items()):
    name=rs[0]['capability'];controls=[x['id'] for x in rs]
    reg_hits=[x.get('id') for x in reg if cid.lower() in json.dumps(x).lower() or name.lower() in json.dumps(x).lower()]
    bench_hits=hits(bench,cid,name);e2e_hits=hits(e2e,cid,name)
    last_exercised='benchmark' if bench_hits else 'end-to-end' if e2e_hits else 'regression' if reg_hits else None
    activation_hint=f"Retrieve stable section {cid} from {rs[0]['shard']} when its capability is selected by the phase/domain router."
    reachable=bool(reg_hits) # every supported capability is expected to have executable regression reachability evidence
    observed=bool(bench_hits or e2e_hits)
    out.append({'capability_id':cid,'capability':name,'domain':rs[0]['domain'],'shard':rs[0]['shard'],'controls':controls,
                'activation_condition':activation_hint,'regression_hits':sorted(set(filter(None,reg_hits))),'end_to_end_hits':e2e_hits,'benchmark_hits':bench_hits,
                'regression_covered':reachable,'behavior_observed':observed,'last_exercised_class':last_exercised,
                'reachability':'regression-addressable' if reachable else 'unproven','dead_rule_candidate':not reachable,
                'observation_gap':reachable and not observed})
summary={'capabilities':len(out),'regression_covered':sum(x['regression_covered'] for x in out),'behavior_observed':sum(x['behavior_observed'] for x in out),
         'dead_rule_candidates':[x['capability_id'] for x in out if x['dead_rule_candidate']],
         'observation_gaps':[x['capability_id'] for x in out if x['observation_gap']]}
p=Path(a.out);p.write_text(json.dumps({'summary':summary,'capabilities':out},indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
