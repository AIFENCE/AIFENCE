#!/usr/bin/env python3
from pathlib import Path
import argparse,json
try:
 import jsonschema
except Exception as exc:
 print(f"FAIL: jsonschema unavailable: {exc}"); raise SystemExit(2)
ROOT=Path(__file__).resolve().parents[1]
SCHEMA=json.loads((ROOT/'schemas'/'family_depth_evidence.schema.json').read_text())
REQ_CHECKS={
 'website':{'visitor-decision-paths','proof-before-commitment','secondary-path','truth-boundary','narrow-screen-equivalence'},
 'mobile':{'p0-workflow','p1-workflow','error-interruption-recovery','state-continuity','adaptive-device-surfaces','mobile-navigation'},
 'brand':{'identity-system','typography-system','color-system','composition-system','iconography-system','imagery-system','application-system','truth-provenance'},
 'email':{'sequence-progression','audience-state-segmentation','cta-continuity','measurement-events','fallback-recovery','truth-proof-boundary'},
 'cli':{'discoverability-help','primary-job','config-precedence','stdout-stderr-exit','failure-recovery','fixtures-tests','safety-boundary'},
 'composite':{'child-contracts','shared-context','independent-child-qa','cross-artifact-consistency'}
}
REQ_DIMS={
 'website':{'truthfulness','completeness','accessibility','feature depth'},
 'mobile':{'completeness','usability','responsiveness','accessibility','feature depth'},
 'brand':{'visual quality','truthfulness','completeness','accessibility','genericity resistance'},
 'email':{'truthfulness','completeness','accessibility','feature depth'},
 'cli':{'truthfulness','implementation correctness','completeness','feature depth'},
 'composite':{'implementation correctness','completeness','responsiveness'}
}
FIELD_SETS={
 'website':{'decision','evidence','objection_or_uncertainty','next_action','continuation','surface','truth_boundary','narrow_screen_equivalent'},
 'mobile':{'entry','action','state_feedback','error_or_interruption','recovery','continuation','compact_surface','adaptive_surface'},
 'brand':{'system_element','role','rules','do','dont','application'},
 'email':{'stage','audience_state','message_job','proof_boundary','cta','measurement_event','fallback_or_recovery','next_state'},
 'cli':{'command_or_mode','job','inputs','config_precedence','success_output','error_output','exit_semantics','recovery'},
 'composite':{'artifact_type','contract','shared_context','independent_qa','consistency_rule'}
}
def fail(msgs):
 print('FAIL: '+'; '.join(msgs));return 1
def main():
 ap=argparse.ArgumentParser();ap.add_argument('evidence');a=ap.parse_args();p=Path(a.evidence)
 try:d=json.loads(p.read_text());jsonschema.Draft202012Validator(SCHEMA).validate(d)
 except Exception as e:print(f'FAIL: schema: {e}');return 1
 fam=d['family'];errors=[]; checks={x['id']:x for x in d['checks']}
 missing=REQ_CHECKS[fam]-set(checks)
 if missing:errors.append('missing checks: '+', '.join(sorted(missing)))
 for cid in REQ_CHECKS[fam]&set(checks):
  x=checks[cid]
  if x['status']=='N/A' and not x.get('na_reason','').strip():errors.append(f'{cid} N/A missing reason')
  elif x['status']!='PASS':errors.append(f'{cid} is {x["status"]}')
 dims=d['critical_dimensions']
 for k in REQ_DIMS[fam]:
  if k not in dims:errors.append(f'missing critical dimension {k}')
  elif dims[k]<9.0:errors.append(f'critical dimension {k} below 9.0 ({dims[k]})')
 recs=d['records']; required_fields=FIELD_SETS[fam]
 minimum={'website':2,'mobile':2,'brand':6,'email':3,'cli':2,'composite':2}[fam]
 if len(recs)<minimum:errors.append(f'{fam} requires at least {minimum} depth records')
 for r in recs:
  missing_fields=[x for x in required_fields if not r.get('fields',{}).get(x)]
  if missing_fields:errors.append(f'{r.get("id")} missing fields: '+', '.join(sorted(missing_fields)))
 if fam=='website' and not ({r['priority'] for r in recs}&{'P0'} and {r['priority'] for r in recs}&{'P1'}):errors.append('website requires both P0 and P1 decision paths')
 if fam=='mobile' and not ({r['priority'] for r in recs}&{'P0'} and {r['priority'] for r in recs}&{'P1'}):errors.append('mobile requires both P0 and P1 workflows')
 if fam=='brand':
  elems={str(r['fields'].get('system_element','')).lower() for r in recs}
  for x in {'identity','typography','color','composition','iconography','imagery'}:
   if not any(x in e for e in elems):errors.append(f'brand system missing {x} element')
  apps={str(r['fields'].get('application','')).strip().lower() for r in recs if r['fields'].get('application')}
  if len(apps)<3:errors.append('brand requires at least three materially distinct application contexts')
 if fam=='email':
  stages={str(r['fields'].get('stage','')).strip().lower() for r in recs}
  if len(stages)<3:errors.append('email sequence requires at least three meaningful stages')
 if fam=='cli':
  jobs={str(r['fields'].get('job','')).strip().lower() for r in recs}
  if len(jobs)<2:errors.append('cli requires discoverability/help plus at least one primary job surface')
 if d.get('requires_narrow_screen'):
  v={x['viewport']:x for x in d.get('viewport_checks',[])}
  for width in (320,390):
   x=v.get(width)
   if not x:errors.append(f'missing {width}px containment evidence')
   elif x['overflow'] or x['clipping'] or not x['critical_path_preserved']:errors.append(f'{width}px containment failed')
 if d.get('catastrophic_failures'):errors.append('catastrophic failures present')
 if d['status']!='PASS':errors.append('artifact status not PASS')
 if errors:return fail(errors)
 print(f'PASS: family-depth closure family={fam} records={len(recs)}')
 return 0
if __name__=='__main__':raise SystemExit(main())
