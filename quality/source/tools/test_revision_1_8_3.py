#!/usr/bin/env python3
"""Executable Core 1.8.3 finished-surface naturalization/substance and universal executable-preflight tests."""
from pathlib import Path
import json, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
EMIT=ROOT/'tools'/'validate_emission_preflight.py'
EXEC=ROOT/'tools'/'validate_universal_executable_preflight.py'

def evidence():
 return {
  'artifact_id':'roofing-site','family':'website','provenance':'direct',
  'domain_terms':['roof membrane','occupied building','drainage inspection'],
  'decisions':['choose repair or replacement','confirm occupied-building staging'],
  'actions':['request roof assessment','review drainage findings'],
  'states':['inspection scheduled','weather delay'],
  'outcomes':['repair scope confirmed','replacement plan prepared'],
  'evidence_boundaries':['warranty eligibility requires manufacturer confirmation'],
  'surface_markers':['roof membrane','occupied building','drainage inspection','repair or replacement','occupied-building staging','request roof assessment','review drainage findings','inspection scheduled','weather delay','repair scope confirmed','replacement plan prepared','manufacturer confirmation'],
  'status':'PASS'
 }

def run(cmd):return subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
with tempfile.TemporaryDirectory(prefix='biziq-183-') as td:
 td=Path(td);ev=td/'evidence.json';ev.write_text(json.dumps(evidence()))
 good=td/'good.html';good.write_text('''<!doctype html><main><h1>Commercial roof planning</h1><p>Compare roof membrane conditions and choose repair or replacement for an occupied building.</p><p>Confirm occupied-building staging before work. A drainage inspection supports the review.</p><button>Request roof assessment</button><p>Review drainage findings when the inspection scheduled notice arrives. A weather delay keeps the request open.</p><p>Outcome: repair scope confirmed or replacement plan prepared. Warranty eligibility requires manufacturer confirmation.</p></main>''')
 p=run([sys.executable,str(EMIT),str(good),'--evidence',str(ev)])
 if p.returncode:print(p.stdout+p.stderr);raise SystemExit('FAIL: concrete naturalized emission should pass')
 leak=td/'leak.html';leak.write_text(good.read_text().replace('Commercial roof planning','P0 Decision Depth Closure').replace('Warranty eligibility','Truth Boundary: warranty eligibility'))
 if run([sys.executable,str(EMIT),str(leak),'--evidence',str(ev)]).returncode==0:raise SystemExit('FAIL: internal vocabulary leak incorrectly passed')
 scaffold=td/'scaffold.html';scaffold.write_text('<main><h1>Decision path</h1><p>Relevant evidence</p><p>Workflow step</p><p>Next state</p></main>')
 if run([sys.executable,str(EMIT),str(scaffold),'--evidence',str(ev)]).returncode==0:raise SystemExit('FAIL: scaffold-only artifact incorrectly passed')
 cli=td/'tool.mjs';cli.write_text("const args=process.argv.slice(2); if(args.includes('--help')){console.log('manifest validate --input FILE');process.exit(0)} console.log('validated manifest rows');\n")
 runtime={'artifact_id':'tool','provenance':'direct','result':'PASS','executions':[{'label':'help','command':'node tool.mjs --help','exit_code':0,'expected_exit_codes':[0],'stdout':'manifest validate --input FILE','stderr':''},{'label':'happy','command':'node tool.mjs input.csv','exit_code':0,'expected_exit_codes':[0],'stdout':'validated manifest rows','stderr':''}],'runtime_errors':[]}
 rt=td/'runtime.json';rt.write_text(json.dumps(runtime))
 p=run([sys.executable,str(EXEC),str(cli),'--require-runtime','--runtime-evidence',str(rt)])
 if p.returncode:print(p.stdout+p.stderr);raise SystemExit('FAIL: clean directly exercised CLI should pass')
 if run([sys.executable,str(EXEC),str(cli),'--require-runtime']).returncode==0:raise SystemExit('FAIL: runtime-required CLI without direct evidence incorrectly passed')
 bad=td/'bad.mjs';bad.write_text("export.onclick = () => console.log('bad')\n")
 if run([sys.executable,str(EXEC),str(bad)]).returncode==0:raise SystemExit('FAIL: parser-invalid CLI incorrectly passed')
 badrt=dict(runtime);badrt['result']='PASS';badrt['executions']=[dict(runtime['executions'][0],exit_code=2,expected_exit_codes=[0])]
 br=td/'bad-runtime.json';br.write_text(json.dumps(badrt))
 if run([sys.executable,str(EXEC),str(cli),'--require-runtime','--runtime-evidence',str(br)]).returncode==0:raise SystemExit('FAIL: unexpected runtime exit incorrectly passed')
 py=td/'bad.py';py.write_text('def broken(:\n  pass\n')
 if run([sys.executable,str(EXEC),str(py)]).returncode==0:raise SystemExit('FAIL: invalid Python syntax incorrectly passed')
print('PASS: Revision 1.8.3 emission naturalization/substance + universal executable preflight semantics')
