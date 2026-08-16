#!/usr/bin/env python3
from pathlib import Path
import argparse, html, json, re, shutil, subprocess, zipfile
import xml.etree.ElementTree as ET
try:
 import jsonschema
except Exception as exc:
 print(f"FAIL: jsonschema unavailable: {exc}"); raise SystemExit(2)
ROOT=Path(__file__).resolve().parents[1]
SCHEMA=json.loads((ROOT/'schemas'/'emission_substance_evidence.schema.json').read_text())
FORBIDDEN=[
 r'\bP0\b',r'\bP1\b',r'decision depth closure',r'truth boundary',r'feature depth',r'quality gate',r'genericity',
 r'artifact contract',r'evidence plan',r'acceptance ledger',r'qa gate',r'family depth closure',r'materialization closure',r'compiler gate',
 r'dense[- ]product quality',r'emission preflight',r'substance gate'
]
GENERIC=[r'\bfeature [ab]\b',r'\bservice (one|two)\b',r'\bproof block\b',r'\brelevant evidence\b',r'\bworkflow step\b',r'\bdecision path\b',r'\bnext state\b',r'\bgeneric proof\b']
TEXT_EXT={'.html','.htm','.md','.txt','.csv','.json','.yaml','.yml','.xml','.svg'}
OOXML={'.pptx','.xlsx','.docx'}

def norm(s):return re.sub(r'\s+',' ',str(s).strip().lower())
def html_text(s):
 s=re.sub(r'<(script|style)\b[^>]*>.*?</\1\s*>',' ',s,flags=re.I|re.S)
 s=re.sub(r'<!--.*?-->',' ',s,flags=re.S);s=re.sub(r'<[^>]+>',' ',s)
 return html.unescape(re.sub(r'\s+',' ',s))
def _local(tag): return tag.rsplit('}',1)[-1]
def _xml_text(raw):
 try: root=ET.fromstring(raw)
 except Exception:return []
 return [html.unescape(el.text) for el in root.iter() if _local(el.tag) in {'t','v','f'} and el.text]
def _xlsx_text(p):
 chunks=[]
 with zipfile.ZipFile(p) as z:
  names=set(z.namelist());shared=[]
  if 'xl/sharedStrings.xml' in names:
   try:
    root=ET.fromstring(z.read('xl/sharedStrings.xml'))
    for si in root.iter():
     if _local(si.tag)=='si': shared.append(''.join((el.text or '') for el in si.iter() if _local(el.tag)=='t'))
   except Exception:pass
  for n in sorted(x for x in names if x.startswith('xl/worksheets/') and x.endswith('.xml')):
   try:root=ET.fromstring(z.read(n))
   except Exception:continue
   for c in (el for el in root.iter() if _local(el.tag)=='c'):
    typ=c.attrib.get('t',''); vals=[]
    vals.extend(el.text or '' for el in c.iter() if _local(el.tag)=='t')
    f=next((el.text for el in c if _local(el.tag)=='f' and el.text),None)
    v=next((el.text for el in c if _local(el.tag)=='v' and el.text is not None),None)
    if f: vals.append(f)
    if v is not None:
     if typ=='s':
      try:vals.append(shared[int(v)])
      except Exception:vals.append(v)
     else:vals.append(v)
    chunks.extend(vals)
  for n in sorted(names):
   if n.startswith('xl/') and n.endswith('.xml') and not n.startswith('xl/worksheets/') and n!='xl/sharedStrings.xml':
    try:chunks.extend(_xml_text(z.read(n)))
    except Exception:pass
 return ' '.join(x for x in chunks if str(x).strip())
def ooxml_text(p):
 if p.suffix.lower()=='.xlsx':return _xlsx_text(p)
 chunks=[]
 with zipfile.ZipFile(p) as z:
  for n in z.namelist():
   if n.endswith('.xml') and (n.startswith('ppt/') or n.startswith('word/')):
    try:chunks.extend(_xml_text(z.read(n)))
    except Exception:pass
 return ' '.join(chunks)
def pdf_text(p):
 exe=shutil.which('pdftotext')
 if not exe:return ''
 r=subprocess.run([exe,'-layout',str(p),'-'],capture_output=True,text=True)
 return r.stdout if r.returncode==0 else ''
def extract_path(p):
 if p.is_dir():return '\n'.join(extract_path(x) for x in sorted(p.rglob('*')) if x.is_file())
 ext=p.suffix.lower()
 try:
  if ext in TEXT_EXT:
   t=p.read_text(encoding='utf-8',errors='replace');return html_text(t) if ext in {'.html','.htm','.svg'} else t
  if ext in OOXML:return ooxml_text(p)
  if ext=='.pdf':return pdf_text(p)
 except Exception:return ''
 return ''
def main():
 ap=argparse.ArgumentParser(description='Scan emitted artifact surfaces for naturalization and concrete domain substance.')
 ap.add_argument('artifact');ap.add_argument('--evidence',required=True);ap.add_argument('--runtime-evidence');ap.add_argument('--out');a=ap.parse_args()
 art=Path(a.artifact).resolve();evp=Path(a.evidence)
 try:d=json.loads(evp.read_text());jsonschema.Draft202012Validator(SCHEMA).validate(d)
 except Exception as e:print(f'FAIL: evidence schema: {e}');return 1
 if not art.exists():print('FAIL: artifact missing');return 2
 corpus=extract_path(art)
 if a.runtime_evidence:
  try:
   rr=json.loads(Path(a.runtime_evidence).read_text())
   if rr.get('provenance')!='direct':print('FAIL: runtime surface evidence provenance must be direct');return 1
   corpus+='\n'+'\n'.join(str(x.get('stdout',''))+'\n'+str(x.get('stderr','')) for x in rr.get('executions',[]))
  except Exception as e:print(f'FAIL: runtime surface evidence: {e}');return 1
 c=norm(corpus);err=[]
 if not c.strip():err.append('no extractable production-facing surface text')
 hits=[]
 for pat in FORBIDDEN:
  if re.search(pat,c,re.I):hits.append(pat)
 if hits:err.append('production-facing output leaks internal vocabulary: '+', '.join(hits))
 gh=[pat for pat in GENERIC if re.search(pat,c,re.I)]
 if gh:err.append('generic scaffold language remains on emitted surface: '+', '.join(gh))
 def count_present(items):return sum(1 for x in items if norm(x) in c)
 groups=[('domain_terms',d['domain_terms'],3),('decisions',d['decisions'],2),('actions',d['actions'],2),('states',d['states'],2),('outcomes',d['outcomes'],2),('evidence_boundaries',d['evidence_boundaries'],1)]
 coverage={}
 for name,items,minimum in groups:
  n=count_present(items);coverage[name]=n
  if n<minimum:err.append(f'emitted surface contains only {n}/{len(items)} declared {name}; requires at least {minimum}')
 marker_count=count_present(d['surface_markers']);marker_need=max(6,round(len(d['surface_markers'])*0.70))
 if marker_count<marker_need:err.append(f'emitted surface contains only {marker_count}/{len(d["surface_markers"])} direct substance markers; requires {marker_need}')
 # Reject evidence that is itself mostly generic category language.
 distinct_specific={norm(x) for x in d['surface_markers']+d['domain_terms'] if len(norm(x).split())>=1 and not any(re.search(g,norm(x),re.I) for g in GENERIC)}
 if len(distinct_specific)<8:err.append('substance evidence lacks enough distinct concrete markers')
 record={'artifact_id':d['artifact_id'],'artifact_path':str(art),'family':d['family'],'provenance':'direct','forbidden_hits':hits,'generic_hits':gh,'coverage':coverage,'surface_markers_present':marker_count,'surface_markers_required':marker_need,'surface_text_chars':len(c),'status':'FAIL' if err else 'PASS'}
 if a.out:Path(a.out).write_text(json.dumps(record,indent=2)+'\n')
 if err:print('FAIL: '+'; '.join(err));return 1
 print(f'PASS: emission naturalization/substance family={d["family"]} markers={marker_count}/{len(d["surface_markers"])} chars={len(c)}')
 return 0
if __name__=='__main__':raise SystemExit(main())
