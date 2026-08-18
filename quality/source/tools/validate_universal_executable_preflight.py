#!/usr/bin/env python3
from pathlib import Path
import argparse, ast, json, re, shutil, subprocess, tempfile
try:
 import jsonschema
except Exception as exc:
 print(f"FAIL: jsonschema unavailable: {exc}"); raise SystemExit(2)
ROOT=Path(__file__).resolve().parents[1]
RUNTIME_SCHEMA=json.loads((ROOT/'schemas'/'universal_executable_runtime_evidence.schema.json').read_text())
SCRIPT_RE=re.compile(r'<script(?P<attrs>[^>]*)>(?P<body>.*?)</script\s*>',re.I|re.S)
SRC_RE=re.compile(r'\bsrc\s*=\s*["\']([^"\']+)["\']',re.I)
TYPE_RE=re.compile(r'\btype\s*=\s*["\']([^"\']+)["\']',re.I)
EXTS={'.js','.mjs','.cjs','.py','.sh','.bash','.html','.htm'}
def files(p):return [p] if p.is_file() else [x for x in sorted(p.rglob('*')) if x.is_file() and x.suffix.lower() in EXTS]
def nearest_pkg_type(p):
 q=p.parent
 for _ in range(8):
  f=q/'package.json'
  if f.exists():
   try:return json.loads(f.read_text()).get('type','commonjs')
   except Exception:return 'commonjs'
  if q.parent==q:break
  q=q.parent
 return 'commonjs'
def check_js_code(code,label,module=False):
 node=shutil.which('node')
 if not node:return False,'Node.js unavailable'
 with tempfile.TemporaryDirectory(prefix='aifence-universal-js-') as td:
  if module:
   p=Path(td)/'check.mjs';p.write_text(code);r=subprocess.run([node,'--check',str(p)],capture_output=True,text=True)
  else:
   p=Path(td)/'check.cjs';p.write_text('const src='+json.dumps(code)+';try{new Function(src)}catch(e){console.error(e.name+": "+e.message);process.exit(1)}');r=subprocess.run([node,str(p)],capture_output=True,text=True)
  return r.returncode==0,(r.stderr or r.stdout).strip().replace(str(p),label)
def html_scripts(p):
 text=p.read_text(encoding='utf-8',errors='replace');out=[]
 for i,m in enumerate(SCRIPT_RE.finditer(text),1):
  attrs=m.group('attrs') or '';body=m.group('body') or '';tm=TYPE_RE.search(attrs);typ=tm.group(1).lower() if tm else ''
  if typ and typ not in ('text/javascript','application/javascript','module'):continue
  sm=SRC_RE.search(attrs)
  if sm:
   src=sm.group(1)
   if re.match(r'^(https?:)?//',src) or src.startswith('data:'):continue
   q=(p.parent/src.split('?',1)[0].split('#',1)[0]).resolve();out.append((f'{p.name}:{src}',q.read_text(encoding='utf-8',errors='replace') if q.exists() else None,typ=='module'))
  elif body.strip():out.append((f'{p.name}:inline:{i}',body,typ=='module'))
 return out
def main():
 ap=argparse.ArgumentParser(description='Fail-closed syntax/runtime preflight for every supported emitted executable artifact.')
 ap.add_argument('artifact');ap.add_argument('--runtime-evidence');ap.add_argument('--require-runtime',action='store_true');ap.add_argument('--out');a=ap.parse_args()
 art=Path(a.artifact).resolve()
 if not art.exists():print('FAIL: artifact missing');return 2
 errs=[];checked=[]
 for p in files(art):
  ext=p.suffix.lower()
  try:
   if ext in {'.js','.mjs','.cjs'}:
    code=p.read_text(encoding='utf-8',errors='replace');module=(ext=='.mjs' or (ext=='.js' and nearest_pkg_type(p)=='module'));ok,diag=check_js_code(code,str(p),module);checked.append({'path':str(p),'language':'javascript','result':'PASS' if ok else 'FAIL'});
    if not ok:errs.append(f'{p}: {diag}')
   elif ext=='.py':
    try:ast.parse(p.read_text(encoding='utf-8',errors='replace'),filename=str(p));ok=True;diag=''
    except SyntaxError as e:ok=False;diag=f'{e.msg} line {e.lineno}'
    checked.append({'path':str(p),'language':'python','result':'PASS' if ok else 'FAIL'});
    if not ok:errs.append(f'{p}: {diag}')
   elif ext in {'.sh','.bash'}:
    bash=shutil.which('bash');r=subprocess.run([bash,'-n',str(p)],capture_output=True,text=True) if bash else None;ok=bool(r and r.returncode==0);checked.append({'path':str(p),'language':'shell','result':'PASS' if ok else 'FAIL'});
    if not ok:errs.append(f'{p}: '+(('bash unavailable') if not r else (r.stderr or r.stdout).strip()))
   elif ext in {'.html','.htm'}:
    for label,code,module in html_scripts(p):
     if code is None:ok=False;diag='required local script missing'
     else:ok,diag=check_js_code(code,label,module)
     checked.append({'path':label,'language':'browser-javascript','result':'PASS' if ok else 'FAIL'});
     if not ok:errs.append(f'{label}: {diag}')
  except Exception as e:errs.append(f'{p}: preflight exception: {e}')
 runtime=None
 if a.runtime_evidence:
  try:
   runtime=json.loads(Path(a.runtime_evidence).read_text());jsonschema.Draft202012Validator(RUNTIME_SCHEMA).validate(runtime)
  except Exception as e:errs.append(f'runtime evidence invalid: {e}');runtime=None
 if a.require_runtime:
  if runtime is None:errs.append('direct runtime evidence required but missing')
  elif runtime.get('result')!='PASS':errs.append('runtime evidence result is not PASS')
  elif runtime.get('runtime_errors'):errs.append('runtime evidence contains runtime errors')
  else:
   for x in runtime.get('executions',[]):
    if x['exit_code'] not in x['expected_exit_codes']:errs.append(f'execution {x["label"]} exit {x["exit_code"]} not in {x["expected_exit_codes"]}')
 if not checked and a.require_runtime:errs.append('runtime-required artifact contains no supported executable files for syntax preflight')
 rec={'artifact_id':art.name,'artifact_path':str(art),'provenance':'direct','files_checked':checked,'runtime_required':a.require_runtime,'runtime_result':None if runtime is None else runtime.get('result'),'errors':errs,'status':'FAIL' if errs else 'PASS'}
 if a.out:Path(a.out).write_text(json.dumps(rec,indent=2)+'\n')
 if errs:print('FAIL: '+'; '.join(errs));return 1
 print(f'PASS: universal executable preflight files={len(checked)} runtime={"PASS" if a.require_runtime else "NOT_REQUIRED"}')
 return 0
if __name__=='__main__':raise SystemExit(main())
