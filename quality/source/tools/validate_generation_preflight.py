#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess, sys, tempfile
try:
    import jsonschema
except Exception as exc:
    print(f"FAIL: jsonschema unavailable: {exc}")
    raise SystemExit(2)

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=json.loads((ROOT/'schemas'/'generation_preflight_evidence.schema.json').read_text())
SCRIPT_RE=re.compile(r'<script(?P<attrs>[^>]*)>(?P<body>.*?)</script\s*>',re.I|re.S)
SRC_RE=re.compile(r'\bsrc\s*=\s*["\']([^"\']+)["\']',re.I)
TYPE_RE=re.compile(r'\btype\s*=\s*["\']([^"\']+)["\']',re.I)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def scripts(html_path):
    text=html_path.read_text(encoding='utf-8',errors='replace');out=[]
    for i,m in enumerate(SCRIPT_RE.finditer(text),1):
        attrs=m.group('attrs') or ''; body=m.group('body') or ''
        typ=(TYPE_RE.search(attrs).group(1).lower() if TYPE_RE.search(attrs) else '')
        if typ and typ not in ('text/javascript','application/javascript','module'): continue
        sm=SRC_RE.search(attrs)
        if sm:
            src=sm.group(1)
            if re.match(r'^(https?:)?//',src) or src.startswith('data:'): continue
            q=(html_path.parent/src.split('?',1)[0].split('#',1)[0]).resolve()
            if q.exists():out.append((f'external:{src}',q.read_text(encoding='utf-8',errors='replace'),typ=='module'))
            else:out.append((f'external:{src}',None,typ=='module'))
        elif body.strip():out.append((f'inline:{i}',body,typ=='module'))
    return out

def check_js(items):
    node=shutil.which('node'); errors=[];checked=0
    if not node:return 'FAIL','node-unavailable',0,['Node.js is required for JavaScript syntax preflight']
    with tempfile.TemporaryDirectory(prefix='aifence-js-preflight-') as td:
        for label,code,is_module in items:
            checked+=1
            if code is None:
                errors.append(f'{label}: required local script missing');continue
            if is_module:
                p=Path(td)/(f'script-{checked}.mjs');p.write_text(code)
                r=subprocess.run([node,'--check',str(p)],capture_output=True,text=True)
                diag=(r.stderr or r.stdout).strip().replace(str(p),label) if r.returncode!=0 else ''
            else:
                # Browser classic scripts follow Script grammar, not CommonJS parsing. new Function gives a real Script-grammar parse and catches reserved-word hazards such as export.onclick.
                wrapper=Path(td)/(f'script-{checked}-check.cjs');wrapper.write_text('const src='+json.dumps(code)+'; try { new Function(src); } catch (e) { console.error(e.name+\": \"+e.message); process.exit(1); }')
                r=subprocess.run([node,str(wrapper)],capture_output=True,text=True)
                diag=f'{label}: '+(r.stderr or r.stdout).strip() if r.returncode!=0 else ''
            if r.returncode!=0: errors.append(diag)
    return ('PASS' if not errors else 'FAIL'),f'node {subprocess.run([node,"--version"],capture_output=True,text=True).stdout.strip()}',checked,errors

def main():
    ap=argparse.ArgumentParser(description='Fail-closed generated browser JavaScript syntax/runtime preflight.')
    ap.add_argument('artifact');ap.add_argument('--runtime-evidence');ap.add_argument('--out');a=ap.parse_args()
    art=Path(a.artifact).resolve()
    if not art.exists():print('FAIL: artifact missing');return 2
    items=scripts(art);js_present=bool(items);syn,engine,count,errors=check_js(items)
    runtime={'required':js_present,'result':'NOT_REQUIRED' if not js_present else 'FAIL','document_loaded':not js_present,'page_errors':[],'console_errors':[],'failed_required_resources':[]}
    provenance='direct'
    if a.runtime_evidence:
        raw=json.loads(Path(a.runtime_evidence).read_text())
        provenance=raw.get('provenance','')
        runtime={
          'required':js_present,
          'result':raw.get('result','FAIL'),
          'document_loaded':bool(raw.get('document_loaded',False)),
          'page_errors':raw.get('page_errors',[]) or [],
          'console_errors':raw.get('console_errors',[]) or [],
          'failed_required_resources':raw.get('failed_required_resources',[]) or [],
          'observations':raw.get('observations',[]) or []
        }
    if js_present:
        clean=(provenance=='direct' and runtime['result']=='PASS' and runtime['document_loaded'] and not runtime['page_errors'] and not runtime['console_errors'] and not runtime['failed_required_resources'])
        runtime['result']='PASS' if clean else 'FAIL'
    record={'artifact_id':art.stem,'artifact_path':str(art),'artifact_sha256':sha(art),'provenance':'direct' if provenance=='direct' else provenance,'javascript_present':js_present,'syntax':{'result':syn,'engine':engine,'scripts_checked':count,'errors':errors},'runtime':runtime}
    try:jsonschema.Draft202012Validator(SCHEMA).validate(record)
    except Exception as exc:print(f'FAIL: evidence schema: {exc}');return 1
    failures=[]
    if syn!='PASS':failures.append('JavaScript syntax/parser preflight failed')
    if js_present and not a.runtime_evidence:failures.append('interactive/generated JavaScript requires direct runtime-preflight evidence')
    if js_present and runtime['result']!='PASS':failures.append('runtime initialization/load preflight failed')
    if provenance!='direct' and js_present:failures.append('runtime-preflight provenance must be direct')
    if a.out:Path(a.out).write_text(json.dumps(record,indent=2)+'\n')
    if failures:
        print('FAIL: '+'; '.join(failures))
        for e in errors:print(e)
        for k in ('page_errors','console_errors','failed_required_resources'):
            for e in runtime.get(k,[]):print(f'{k}: {e}')
        return 1
    print(f'PASS: generation preflight scripts={count} runtime={runtime["result"]}')
    return 0
if __name__=='__main__':raise SystemExit(main())
