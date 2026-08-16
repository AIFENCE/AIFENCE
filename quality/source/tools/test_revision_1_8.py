#!/usr/bin/env python3
"""Executable Core 1.8 artifact-family quality closure smoke tests."""
from pathlib import Path
import json, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
VALIDATOR=ROOT/'tools'/'validate_artifact_family_quality_evidence.py'
REQ={
 'presentation':['narrative-decision-structure','legibility','contrast','reading-order','provenance-boundaries','decision-next-state','export-render','non-generic-story-grammar'],
 'spreadsheet':['formula-integrity','recalculation','scenario-mutation','editable-vs-derived','decision-surface','validation','labels-number-formats','screen-print-legibility','assumption-provenance'],
 'mobile':['compact-large-states','critical-path-depth','safe-area-target-readability','keyboard-focus','interruption-recovery','state-continuity'],
 'cli':['help','happy-path','invalid-input','exit-codes','stdout-stderr','determinism','failure-recovery','fixtures-tests','truth-boundary']
}
def evidence(fam,score=92):
 return {'artifact_id':'smoke','artifact_family':fam,'provenance':'direct','checks':[{'id':x,'status':'PASS','evidence':'direct fixture evidence'} for x in REQ[fam]],'critical_dimensions':{'truthfulness':9.2,'implementation correctness':9.3,'completeness':9.1,'accessibility':9.1,'feature depth':9.1},'overall_score':score,'catastrophic_failures':[],'status':'PASS'}
def run(doc):
 with tempfile.NamedTemporaryFile('w',suffix='.json',delete=False) as f: json.dump(doc,f); name=f.name
 p=subprocess.run([sys.executable,str(VALIDATOR),name],cwd=ROOT,text=True,capture_output=True)
 Path(name).unlink(missing_ok=True); return p
for fam in REQ:
 p=run(evidence(fam));
 if p.returncode: print(p.stdout+p.stderr);raise SystemExit(1)
bad=evidence('presentation',89)
p=run(bad)
if p.returncode==0: raise SystemExit('FAIL: family validator accepted below-threshold overall score')
print('PASS: Revision 1.8 artifact-family quality closure semantics')
