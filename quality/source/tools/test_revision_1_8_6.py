#!/usr/bin/env python3
"""Core 1.8.6 render-aware documents, semantic acceptance, and routing regressions."""
from pathlib import Path
import json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
VAL=ROOT/'tools'/'validate_family_emission_evidence.py'; RENDER=ROOT/'tools'/'validate_fixed_document_render_evidence.py'
def run(c,cwd=ROOT): return subprocess.run(c,cwd=cwd,text=True,capture_output=True)
def expect(c,ok,label,cwd=ROOT):
 p=run(c,cwd);
 if (p.returncode==0)!=ok: print(p.stdout+p.stderr); raise SystemExit('FAIL: '+label)
expect([sys.executable,'-m','py_compile',str(RENDER)],True,'fixed-document render validator syntax')
with tempfile.TemporaryDirectory(prefix='aifence-186-') as td:
 td=Path(td); art=td/'mobile.txt'; art.write_text('Offline route log. Failed sync preserves the draft. Retry sync when connectivity returns. crew route draft evidence comes from supplied sample only. reconnect and resume field work.')
 ev={'artifact_id':'m','family':'mobile','provenance':'direct','domain_terms':['route log','sync recovery','field work'],'evidence_boundaries':['supplied sample only'],'surface_markers':['Offline route log','Failed sync preserves the draft','Retry sync','crew route','draft','reconnect','resume field work'], 'semantics':{'user_jobs':['crew route','field work'],'actions':['Retry sync','resume field work'],'states':['draft','Failed sync preserves the draft'],'recovery_paths':['sync recovery'],'outcomes':['reconnect','resume field work']},'status':'PASS'}
 ep=td/'e.json';ep.write_text(json.dumps(ev));expect([sys.executable,str(VAL),str(art),'--evidence',str(ep)],True,'semantic-equivalence recovery')
js="""import {classifyRequest} from './tooling/runtime-template/src/classifier.js';
const a=classifyRequest('Create a production service renewal monitoring workspace for account leaders to track health, deadlines, risk, evidence, and decisions.');
if(a.creationType!=='Dashboard'){console.error(a.creationType);process.exit(1)}
const b=classifyRequest('Create a fixed analytical report plus executive decision deck for leadership.');
const t=b.artifactGraph.nodes.map(x=>x.type).sort();
if(JSON.stringify(t)!==JSON.stringify(['Fixed-Format Document / PDF','Presentation / Deck'].sort())){console.error(t);process.exit(2)}
"""
p=run(['node','--input-type=module','-e',js],cwd=ROOT.parent)
if p.returncode: print(p.stdout+p.stderr); raise SystemExit('FAIL: 1.8.6 routing')
print('PASS: Revision 1.8.6 semantic acceptance and routing regressions')
