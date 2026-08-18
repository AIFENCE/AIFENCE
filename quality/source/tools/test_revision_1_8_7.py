#!/usr/bin/env python3
"""Core 1.8.7 artifact-graph phrase coverage and slide-fit regressions."""
from pathlib import Path
import json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
def run(c,cwd=ROOT): return subprocess.run(c,cwd=cwd,text=True,capture_output=True)
def expect(c,ok,label,cwd=ROOT):
 p=run(c,cwd);
 if (p.returncode==0)!=ok: print(p.stdout+p.stderr);raise SystemExit('FAIL: '+label)
js="""import {classifyRequest} from './tooling/runtime-template/src/classifier.js';
const a=classifyRequest('Create an Excel staffing scenario model for a fictional field-services operator.');if(a.creationType!=='Spreadsheet / Financial Model'){console.error(a);process.exit(1)}
const b=classifyRequest('Create an Excel maintenance replacement model for a fictional transit fleet.');if(b.creationType!=='Spreadsheet / Financial Model'){console.error(b);process.exit(2)}
const c=classifyRequest('Create a brand identity, onboarding email campaign, and landing page for a fictional tutoring service.');const t=c.artifactGraph.nodes.map(x=>x.type);for(const q of ['Brand Identity / Logo','Email / Campaign','Website / Landing Page'])if(!t.includes(q)){console.error(t);process.exit(3)}
"""
p=run(['node','--input-type=module','-e',js],cwd=ROOT.parent)
if p.returncode: print(p.stdout+p.stderr);raise SystemExit('FAIL: 1.8.7 routing')
val=ROOT/'tools'/'validate_presentation_slide_fit_evidence.py'
with tempfile.TemporaryDirectory(prefix='aifence-187-') as td:
 td=Path(td);good={'artifact_id':'deck','provenance':'direct','slides':[{'slide':1,'title_fits':True,'title_subtitle_overlap':False,'body_visual_overlap':False,'edge_clipping':False,'readable':True}],'status':'PASS'};bad=json.loads(json.dumps(good));bad['slides'][0]['title_fits']=False
 gp=td/'good.json';bp=td/'bad.json';gp.write_text(json.dumps(good));bp.write_text(json.dumps(bad));expect([sys.executable,str(val),str(gp)],True,'good slide fit');expect([sys.executable,str(val),str(bp)],False,'bad slide fit')
print('PASS: Revision 1.8.7 artifact graph and slide-fit regressions')
