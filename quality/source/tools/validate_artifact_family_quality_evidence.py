#!/usr/bin/env python3
from pathlib import Path
import argparse,json
try:
 import jsonschema
except Exception as exc:
 print(f"FAIL: jsonschema unavailable: {exc}"); raise SystemExit(2)
ROOT=Path(__file__).resolve().parents[1]
SCHEMA=json.loads((ROOT/'schemas'/'artifact_family_quality_evidence.schema.json').read_text())
REQ={
 'mobile':{'compact-large-states','critical-path-depth','safe-area-target-readability','keyboard-focus','interruption-recovery','state-continuity'},
 'presentation':{'narrative-decision-structure','legibility','contrast','reading-order','provenance-boundaries','decision-next-state','export-render','non-generic-story-grammar'},
 'spreadsheet':{'formula-integrity','recalculation','scenario-mutation','editable-vs-derived','decision-surface','validation','labels-number-formats','screen-print-legibility','assumption-provenance'},
 'fixed-document':{'page-rendering-clipping','heading-hierarchy','text-extraction-reading-order','links','tables-page-breaks','provenance-limitations','document-accessibility','decision-action-depth'},
 'brand':{'symbol-wordmark-type-color','usage-grammar','anti-cliche-differentiation','accessible-contrast','application-contexts','asset-claim-provenance'},
 'email':{'sequence-state-progression','responsive-mobile','link-cta-semantics','image-alternatives','truth-proof-boundaries','cta-recovery'},
 'marketing-creative':{'campaign-grammar','differentiated-hook','legibility-contrast','truth-proof-boundaries','placement-adaptation','accessible-alternatives'},
 'cli':{'help','happy-path','invalid-input','exit-codes','stdout-stderr','determinism','failure-recovery','fixtures-tests','truth-boundary'},
 'composite':{'child-contracts','shared-context','independent-qa','cross-artifact-consistency'}
}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('evidence');a=ap.parse_args();p=Path(a.evidence)
 try:d=json.loads(p.read_text());jsonschema.Draft202012Validator(SCHEMA).validate(d)
 except Exception as e:print(f'FAIL: schema: {e}');return 1
 fails=[]; fam=d['artifact_family']; checks={x['id']:x for x in d['checks']}
 missing=REQ[fam]-set(checks)
 if missing:fails.append('missing family checks: '+', '.join(sorted(missing)))
 for cid in REQ[fam]&set(checks):
  x=checks[cid]
  if x['status']=='N/A' and not x.get('na_reason','').strip():fails.append(f'{cid} N/A missing explicit reason')
  elif x['status']!='PASS' and x['status']!='N/A':fails.append(f'{cid} is {x["status"]}')
 dims=d['critical_dimensions']
 for k,v in dims.items():
  if v<9.0:fails.append(f'critical dimension {k} below 9.0 ({v})')
 if d['overall_score']<90:fails.append(f'overall score below 90 ({d["overall_score"]})')
 if d.get('catastrophic_failures'):fails.append('catastrophic failures present')
 if d['status']!='PASS':fails.append('artifact status not PASS')
 if fails:
  print('FAIL: '+'; '.join(fails));return 1
 print(f"PASS: artifact-family quality family={fam} checks={len(checks)} overall={d['overall_score']}")
 return 0
if __name__=='__main__':raise SystemExit(main())
