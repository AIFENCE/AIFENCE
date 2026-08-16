#!/usr/bin/env python3
from pathlib import Path
import argparse,json,re
try:
 import jsonschema
except Exception as exc:
 print(f"FAIL: jsonschema unavailable: {exc}"); raise SystemExit(2)
ROOT=Path(__file__).resolve().parents[1]
SCHEMA=json.loads((ROOT/'schemas'/'materialization_evidence.schema.json').read_text())
FORBIDDEN=[
 r'\bP0\b',r'\bP1\b',r'decision depth closure',r'truth boundary',r'feature depth',r'quality gate',r'genericity',
 r'artifact contract',r'evidence plan',r'acceptance ledger',r'qa gate',r'family depth closure',r'materialization closure',r'compiler gate'
]
GENERIC={
 'service one','service two','feature a','feature b','proof block','relevant evidence','learn more','workflow step','next step','task status','generic proof','sample feature'
}
MIN={'website':5,'mobile':5,'brand':6,'email':4,'cli':4,'presentation':4,'spreadsheet':4,'fixed-document':4,'marketing-creative':4,'composite':4}
REQ_CHECKS={
 'website':{'domain-specific-offerings','qualification-evaluation','proof-objection-material','natural-language-scan'},
 'mobile':{'domain-objects-states','interruption-recovery-material','secondary-workflow-material','natural-language-scan'},
 'brand':{'rule-not-inventory','application-specificity','claim-provenance','natural-language-scan'},
 'email':{'lifecycle-material','domain-specific-copy','cta-next-state','natural-language-scan'},
 'cli':{'help-output-ergonomics','error-recovery-copy','domain-command-language','natural-language-scan'},
 'presentation':{'decision-material','evidence-implication','reading-order-material','natural-language-scan'},
 'spreadsheet':{'assumptions-inputs','derived-decision-surface','scenario-material','natural-language-scan'},
 'fixed-document':{'findings-actions','reading-order-material','provenance-material','natural-language-scan'},
 'marketing-creative':{'domain-hook','placement-material','truth-boundary-material','natural-language-scan'},
 'composite':{'child-materialization','shared-language-consistency','independent-child-depth','natural-language-scan'}
}
REQ_DIMS={
 'website':{'completeness','feature depth'},'mobile':{'completeness','feature depth','accessibility'},'brand':{'completeness','feature depth'},
 'email':{'completeness','feature depth'},'cli':{'completeness','feature depth'},'presentation':{'completeness','feature depth'},
 'spreadsheet':{'completeness','feature depth'},'fixed-document':{'completeness','accessibility'},'marketing-creative':{'completeness','feature depth'},
 'composite':{'completeness','feature depth'}
}
def norm(s): return re.sub(r'\s+',' ',str(s).strip().lower())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('evidence');a=ap.parse_args();p=Path(a.evidence)
 try:d=json.loads(p.read_text());jsonschema.Draft202012Validator(SCHEMA).validate(d)
 except Exception as e:print(f'FAIL: schema: {e}');return 1
 fam=d['family'];err=[];recs=d['records'];checks={x['id']:x for x in d['checks']}
 if len(recs)<MIN[fam]:err.append(f'{fam} requires at least {MIN[fam]} materialization records')
 missing=REQ_CHECKS[fam]-set(checks)
 if missing:err.append('missing checks: '+', '.join(sorted(missing)))
 for cid in REQ_CHECKS[fam]&set(checks):
  x=checks[cid]
  if x['status']=='N/A' and not x.get('na_reason','').strip():err.append(f'{cid} N/A missing reason')
  elif x['status']!='PASS':err.append(f'{cid} is {x["status"]}')
 for k in REQ_DIMS[fam]:
  v=d['critical_dimensions'].get(k)
  if v is None:err.append(f'missing critical dimension {k}')
  elif v<9.0:err.append(f'critical dimension {k} below 9.0 ({v})')
 jobs=set();surfaces=set();specific=0
 for r in recs:
  jobs.add(norm(r['user_job_or_decision']));surfaces.add(norm(r['artifact_surface']))
  material=norm(r['user_facing_material']);marker=norm(r.get('specificity_marker',''))
  if material in GENERIC or any(g in material for g in GENERIC):err.append(f'{r["id"]} uses generic material: {r["user_facing_material"]}')
  if marker and marker not in GENERIC and len(marker.split())>=2:specific+=1
  else:err.append(f'{r["id"]} lacks a concrete specificity marker')
 if len(jobs)<min(3,MIN[fam]):err.append('materialization records do not cover enough distinct jobs/decisions')
 if len(surfaces)<min(3,MIN[fam]):err.append('materialization records do not cover enough distinct artifact surfaces')
 corpus='\n'.join(d['user_facing_copy'])
 for pat in FORBIDDEN:
  if re.search(pat,corpus,re.I):err.append(f'production-facing copy leaks internal vocabulary: {pat}')
 if fam=='brand':
  for term in ['typography','color','composition','icon','imag','identity']:
   if not any(term in norm(r['domain_need']+' '+r['user_facing_material']) for r in recs):err.append(f'brand materialization missing concrete {term} rule')
 if fam=='email' and len({norm(r['continuation_or_outcome']) for r in recs})<3:err.append('campaign does not materialize enough distinct lifecycle outcomes')
 if fam=='cli':
  corpus2=' '.join(norm(r['user_facing_material']+' '+r['action_or_state']) for r in recs)
  for t in ['help','error','exit']:
   if t not in corpus2:err.append(f'CLI materialization missing {t} ergonomics')
 if d.get('catastrophic_failures'):err.append('catastrophic failures present')
 if d['status']!='PASS':err.append('artifact status not PASS')
 if err:print('FAIL: '+'; '.join(err));return 1
 print(f'PASS: materialization family={fam} records={len(recs)} specific={specific}')
 return 0
if __name__=='__main__':raise SystemExit(main())
