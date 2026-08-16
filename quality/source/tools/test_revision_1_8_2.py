#!/usr/bin/env python3
"""Executable Core 1.8.2 domain materialization / naturalization smoke tests."""
from pathlib import Path
import json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
VALIDATOR=ROOT/'tools'/'validate_materialization_evidence.py'
MIN={'website':5,'mobile':5,'brand':6,'email':4,'cli':4,'presentation':4,'spreadsheet':4,'fixed-document':4,'marketing-creative':4,'composite':4}
CHECKS={
'website':['domain-specific-offerings','qualification-evaluation','proof-objection-material','natural-language-scan'],
'mobile':['domain-objects-states','interruption-recovery-material','secondary-workflow-material','natural-language-scan'],
'brand':['rule-not-inventory','application-specificity','claim-provenance','natural-language-scan'],
'email':['lifecycle-material','domain-specific-copy','cta-next-state','natural-language-scan'],
'cli':['help-output-ergonomics','error-recovery-copy','domain-command-language','natural-language-scan'],
'presentation':['decision-material','evidence-implication','reading-order-material','natural-language-scan'],
'spreadsheet':['assumptions-inputs','derived-decision-surface','scenario-material','natural-language-scan'],
'fixed-document':['findings-actions','reading-order-material','provenance-material','natural-language-scan'],
'marketing-creative':['domain-hook','placement-material','truth-boundary-material','natural-language-scan'],
'composite':['child-materialization','shared-language-consistency','independent-child-depth','natural-language-scan']}
DIMS={
'website':{'completeness':9.2,'feature depth':9.2},'mobile':{'completeness':9.2,'feature depth':9.2,'accessibility':9.1},'brand':{'completeness':9.2,'feature depth':9.2},'email':{'completeness':9.2,'feature depth':9.2},'cli':{'completeness':9.2,'feature depth':9.2},'presentation':{'completeness':9.2,'feature depth':9.2},'spreadsheet':{'completeness':9.2,'feature depth':9.2},'fixed-document':{'completeness':9.2,'accessibility':9.1},'marketing-creative':{'completeness':9.2,'feature depth':9.2},'composite':{'completeness':9.2,'feature depth':9.2}}
SPEC={
'website':['roof membrane compatibility','occupied-building staging','weather-window planning','warranty documentation','roof-access constraints','drainage inspection'],
'mobile':['inspection asset ID','offline photo queue','failed sync retry','defect severity','site handoff','inspection sign-off'],
'brand':['identity lockup rule','typography hierarchy rule','color contrast pair','composition grid rule','icon stroke rule','imagery crop rule'],
'email':['payroll setup checklist','bank verification state','employee import readiness','first payroll review','tax setup state'],
'cli':['manifest schema help','invalid shipment row error','exit code 2','dry-run summary','config file precedence'],
'presentation':['battery duration tradeoff','interconnection risk','site readiness evidence','capital approval decision','deployment sequencing'],
'spreadsheet':['store build cost assumption','unit volume scenario','labor sensitivity','cash runway output','site comparison'],
'fixed-document':['clinical rollout dependency','readiness finding','owner action','evidence citation','implementation risk'],
'marketing-creative':['CNC setup skill','shift schedule detail','apprenticeship proof','shop-floor placement','application CTA'],
'composite':['managed endpoint scope','response-time wording','identity application rule','website qualification path','onboarding next state']}
def doc(fam):
 rec=[]; specs=SPEC[fam]
 for i in range(MIN[fam]):
  s=specs[i%len(specs)]
  need=s
  if fam=='brand':
   elems=['identity','typography','color','composition','iconography','imagery']; need=f'{elems[i]} {s}'
  mat=(f'{s} guidance with concrete user-facing detail')
  if fam=='cli':
   suffix=['help command output','error recovery output','exit code semantics','config precedence output'][i%4];mat=f'{s} {suffix}'
  rec.append({'id':f'{fam}-{i+1}','priority':'P0' if i<2 else 'P1','user_job_or_decision':f'complete {s}','domain_need':need,'artifact_surface':f'{fam} surface {i+1}','user_facing_material':mat,'action_or_state':('show help and error exit guidance' if fam=='cli' else f'act on {s}'),'truth_or_evidence_boundary':'supplied facts only; unknown proof remains labeled','continuation_or_outcome':f'continue after {s}','specificity_marker':s})
 return {'artifact_id':'smoke','family':fam,'provenance':'direct','records':rec,'user_facing_copy':['Choose the right option for your situation','See requirements, evidence, and what happens next'], 'checks':[{'id':x,'status':'PASS','evidence':'direct fixture'} for x in CHECKS[fam]],'critical_dimensions':DIMS[fam],'catastrophic_failures':[],'status':'PASS'}
def run(d):
 with tempfile.NamedTemporaryFile('w',suffix='.json',delete=False) as f:json.dump(d,f);name=f.name
 p=subprocess.run([sys.executable,str(VALIDATOR),name],cwd=ROOT,text=True,capture_output=True)
 Path(name).unlink(missing_ok=True);return p
for fam in CHECKS:
 p=run(doc(fam))
 if p.returncode:print(p.stdout+p.stderr);raise SystemExit(1)
bad=doc('website');bad['user_facing_copy'].append('P0 Decision Depth Closure')
if run(bad).returncode==0:raise SystemExit('FAIL: leaked internal vocabulary incorrectly passed')
bad=doc('email');bad['records'][0]['user_facing_material']='Feature A'
if run(bad).returncode==0:raise SystemExit('FAIL: generic campaign material incorrectly passed')
bad=doc('brand');bad['records'][5]['domain_need']='logo rule';bad['records'][5]['user_facing_material']='logo application rule';bad['records'][5]['specificity_marker']='logo application rule'
if run(bad).returncode==0:raise SystemExit('FAIL: incomplete brand system incorrectly passed')
print('PASS: Revision 1.8.2 materialization/naturalization semantics')
