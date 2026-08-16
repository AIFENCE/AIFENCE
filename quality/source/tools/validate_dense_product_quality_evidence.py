#!/usr/bin/env python3
from pathlib import Path
import argparse,json,sys
try:
 import jsonschema
except Exception as exc:
 print(f"FAIL: jsonschema unavailable: {exc}"); raise SystemExit(2)
ROOT=Path(__file__).resolve().parents[1]
SCHEMA=json.loads((ROOT/'schemas'/'dense_product_quality_evidence.schema.json').read_text())
REQ_COVER={'entry-orientation','information-evidence','primary-action','normal','error-recovery','success-feedback','detail-drilldown','responsive-320-390','accessibility','truth-data-semantics','acceptance-evidence'}
PAY={'find/filter/segment','inspect transaction','status/risk/context','action/recovery','result/feedback','continue'}
ANA={'decision/question','evidence/source','comparison/segmentation','interpretation/guardrail','inspect/drill-down','next action/handoff','continued state'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('evidence');a=ap.parse_args();p=Path(a.evidence)
 try:d=json.loads(p.read_text());jsonschema.Draft202012Validator(SCHEMA).validate(d)
 except Exception as e:print(f'FAIL: schema: {e}');return 1
 fails=[]
 if d.get('provenance')!='direct':fails.append('provenance must be direct')
 v=d['visual_finish']
 if not {320,390,1440}.issubset(set(v['viewports'])):fails.append('visual viewports must include 320/390/1440')
 if len(set(v['surface_roles']))<3: fails.append('at least 3 semantic surface roles required')
 if len(set(v['typography_roles']))<5: fails.append('at least 5 typography roles required')
 if not v['control_alignment']:fails.append('control geometry/alignment failed')
 if v['material_defects']:fails.append('material visual defects remain')
 if v.get('status')!='PASS':fails.append('visual finish not PASS')
 c=d['completeness']
 for f in c['features']:
  miss=REQ_COVER-set(f['coverage'])
  if miss:fails.append(f"{f['feature_id']} missing completion coverage: {', '.join(sorted(miss))}")
  if f['status']!='PASS':fails.append(f"{f['feature_id']} completeness not PASS")
 if c['missing_applicable_rows']:fails.append('missing applicable completion rows')
 if c['status']!='PASS':fails.append('completeness not PASS')
 ac=d['accessibility']
 for t in ac['critical_paths']:
  for k in ['named_controls','keyboard_complete','visible_focus','focus_order_return','programmatic_feedback','non_color_meaning','target_readability','reflow_320_390','errors_associated']:
   if not t[k]:fails.append(f"{t['task_id']} accessibility failed: {k}")
  if t['status']!='PASS':fails.append(f"{t['task_id']} accessibility not PASS")
 if ac['unlabelled_enabled_controls']:fails.append('unlabelled enabled controls remain')
 if ac['status']!='PASS':fails.append('accessibility not PASS')
 fd=d['feature_depth']; roles=set()
 for f in fd['level5_features']:
  if f['level']!=5 or f['status']!='PASS':fails.append(f"{f['feature_id']} not Level-5 PASS")
  roles.update(f['roles'])
 needroles={'investigation-inspection','decision-action-recovery','continuity-comparison'}
 if not needroles.issubset(roles):fails.append('Level-5 features do not cover investigation, action/recovery, and continuity/comparison roles')
 loop=set(fd['workflow_loop']);fl=d.get('product_flavor','general')
 if fl=='payments' and not PAY.issubset(loop):fails.append('payments workflow-specific Level-5 loop incomplete')
 if fl=='analytics' and not ANA.issubset(loop):fails.append('analytics workflow-specific Level-5 loop incomplete')
 if fd['status']!='PASS':fails.append('feature depth not PASS')
 if d['status']!='PASS':fails.append('artifact dense-product quality status not PASS')
 if fails:
  print('FAIL: '+'; '.join(fails));return 1
 print(f"PASS: dense-product first-pass quality family={d['artifact_family']} flavor={d.get('product_flavor','general')} features={len(c['features'])}")
 return 0
if __name__=='__main__':raise SystemExit(main())
