#!/usr/bin/env python3
"""Heuristic duplicate/conflict lint for AIFENCE control requirements."""
from __future__ import annotations
import csv,re,json,argparse
from pathlib import Path
from difflib import SequenceMatcher
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--threshold',type=float,default=.92);ap.add_argument('--out',default='semantic_lint.json');a=ap.parse_args()
rows=[]
for fp in [ROOT/'control_registry.csv',*sorted((ROOT/'control_registry').glob('*.csv'))]:
  with fp.open(encoding='utf-8',newline='') as f: rows+=list(csv.DictReader(f))
# One requirement per capability is enough to detect cross-capability duplication; stage rows intentionally repeat it.
uniq={}
for r in rows: uniq.setdefault(r['capability_id'],r)
items=list(uniq.values())
def norm(s):
  s=s.lower();s=re.sub(r'\b(must|should|may|the|a|an|and|or|to|of|for|in|with|when|where|before|after)\b',' ',s);return ' '.join(re.findall(r'[a-z0-9]+',s))
findings=[]
for i,a1 in enumerate(items):
  n1=norm(a1['requirement'])
  for b in items[i+1:]:
    if a1['capability_id']==b['capability_id']:continue
    n2=norm(b['requirement']); ratio=SequenceMatcher(None,n1,n2).ratio()
    if ratio>=a.threshold:
      findings.append({'kind':'probable-duplicate','similarity':round(ratio,3),'a':a1['capability_id'],'b':b['capability_id'],'a_requirement':a1['requirement'],'b_requirement':b['requirement']})
# Direct textual MUST/MUST NOT conflicts in stable sections targeting similar normalized clauses.
for fp in sorted((ROOT/'controls').glob('*.md')):
  text=fp.read_text(encoding='utf-8')
  lines=[x.strip() for x in text.splitlines() if '**MUST' in x.upper()]
  pos=[x for x in lines if '**MUST:**' in x.upper()]
  neg=[x for x in lines if '**MUST NOT:**' in x.upper()]
  for p in pos:
    np=norm(p)
    for n in neg:
      rr=SequenceMatcher(None,np,norm(n)).ratio()
      if rr>=.84:findings.append({'kind':'possible-must-conflict','similarity':round(rr,3),'file':str(fp.relative_to(ROOT)),'positive':p,'negative':n})
Path(a.out).write_text(json.dumps({'threshold':a.threshold,'finding_count':len(findings),'findings':findings},indent=2)+'\n',encoding='utf-8')
print(f"Semantic lint: {len(findings)} review finding(s); no automatic canonical rewrites performed.")
