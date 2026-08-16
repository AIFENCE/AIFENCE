#!/usr/bin/env python3
"""Executable Core 1.8.1 family-depth closure smoke tests."""
from pathlib import Path
import json, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
VALIDATOR=ROOT/'tools'/'validate_family_depth_evidence.py'
CHECKS={
 'website':['visitor-decision-paths','proof-before-commitment','secondary-path','truth-boundary','narrow-screen-equivalence'],
 'mobile':['p0-workflow','p1-workflow','error-interruption-recovery','state-continuity','adaptive-device-surfaces','mobile-navigation'],
 'brand':['identity-system','typography-system','color-system','composition-system','iconography-system','imagery-system','application-system','truth-provenance'],
 'email':['sequence-progression','audience-state-segmentation','cta-continuity','measurement-events','fallback-recovery','truth-proof-boundary'],
 'cli':['discoverability-help','primary-job','config-precedence','stdout-stderr-exit','failure-recovery','fixtures-tests','safety-boundary'],
 'composite':['child-contracts','shared-context','independent-child-qa','cross-artifact-consistency']
}
FIELDS={
 'website':dict(decision='choose service path',evidence='proof block',objection_or_uncertainty='scope uncertainty',next_action='request estimate',continuation='confirmation state',surface='decision section',truth_boundary='no invented reviews',narrow_screen_equivalent='stacked proof before action'),
 'mobile':dict(entry='task home',action='complete task',state_feedback='saved state',error_or_interruption='network loss',recovery='retry/resume',continuation='return to task',compact_surface='320 layout',adaptive_surface='large-device layout'),
 'brand':dict(system_element='identity mark',role='recognition',rules='clear-space rules',do='use approved lockup',dont='distort',application='website header'),
 'email':dict(stage='activation',audience_state='new user',message_job='complete setup',proof_boundary='sample benefit only',cta='continue setup',measurement_event='setup click',fallback_or_recovery='help link',next_state='configured'),
 'cli':dict(command_or_mode='audit',job='audit a CSV',inputs='input path',config_precedence='flag > env > config',success_output='summary',error_output='stderr diagnostic',exit_semantics='0 success / 2 input error',recovery='correct input and rerun'),
 'composite':dict(artifact_type='website',contract='marketing-website',shared_context='brand tokens',independent_qa='browser QA',consistency_rule='shared naming and identity')
}
DIMS={
 'website':{'truthfulness':9.2,'completeness':9.2,'accessibility':9.1,'feature depth':9.2},
 'mobile':{'completeness':9.2,'usability':9.2,'responsiveness':9.2,'accessibility':9.1,'feature depth':9.2},
 'brand':{'visual quality':9.2,'truthfulness':9.2,'completeness':9.2,'accessibility':9.1,'genericity resistance':9.2},
 'email':{'truthfulness':9.2,'completeness':9.2,'accessibility':9.1,'feature depth':9.2},
 'cli':{'truthfulness':9.2,'implementation correctness':9.3,'completeness':9.2,'feature depth':9.2},
 'composite':{'implementation correctness':9.3,'completeness':9.2,'responsiveness':9.2}
}
MIN={'website':2,'mobile':2,'brand':6,'email':3,'cli':2,'composite':2}
def doc(fam):
 rec=[]
 for i in range(MIN[fam]):
  fields=dict(FIELDS[fam])
  if fam=='brand':
   elems=['identity','typography','color','composition','iconography','imagery'];fields['system_element']=elems[i];fields['application']=['website','packaging','social','email','signage','app'][i]
  if fam=='email':fields['stage']=['welcome','activation','adoption'][i]
  if fam=='cli':fields['job']=['discover commands','audit a CSV'][i];fields['command_or_mode']=['help','audit'][i]
  rec.append({'id':f'{fam}-{i+1}','priority':'P0' if i==0 else 'P1','fields':fields})
 d={'artifact_id':'smoke','family':fam,'provenance':'direct','checks':[{'id':x,'status':'PASS','evidence':'direct fixture'} for x in CHECKS[fam]],'critical_dimensions':DIMS[fam],'records':rec,'catastrophic_failures':[],'status':'PASS'}
 if fam=='composite':d.update({'requires_narrow_screen':True,'viewport_checks':[{'viewport':320,'overflow':False,'clipping':False,'critical_path_preserved':True,'evidence':'direct 320 screenshot/task check'},{'viewport':390,'overflow':False,'clipping':False,'critical_path_preserved':True,'evidence':'direct 390 screenshot/task check'}]})
 return d
def run(d):
 with tempfile.NamedTemporaryFile('w',suffix='.json',delete=False) as f:json.dump(d,f);name=f.name
 p=subprocess.run([sys.executable,str(VALIDATOR),name],cwd=ROOT,text=True,capture_output=True)
 Path(name).unlink(missing_ok=True);return p
for fam in CHECKS:
 p=run(doc(fam))
 if p.returncode:print(p.stdout+p.stderr);raise SystemExit(1)
bad=doc('website');bad['records']=bad['records'][:1]
if run(bad).returncode==0:raise SystemExit('FAIL: website single-path evidence incorrectly passed')
bad=doc('brand');bad['records'][5]['fields']['system_element']='logo'
if run(bad).returncode==0:raise SystemExit('FAIL: incomplete brand system incorrectly passed')
bad=doc('composite');bad['viewport_checks'][0]['overflow']=True
if run(bad).returncode==0:raise SystemExit('FAIL: 320px composite overflow incorrectly passed')
print('PASS: Revision 1.8.1 family-depth closure semantics')
