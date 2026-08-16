#!/usr/bin/env python3
"""Core 1.8.6 render-aware fixed-document preflight."""
from pathlib import Path
import argparse,json,subprocess,shutil,xml.etree.ElementTree as ET
try: import jsonschema
except Exception as e: print(f"FAIL: jsonschema unavailable: {e}"); raise SystemExit(2)
ROOT=Path(__file__).resolve().parents[1]
SCHEMA=json.loads((ROOT/'schemas'/'fixed_document_render_evidence.schema.json').read_text())
def bbox_words(pdf):
 exe=shutil.which('pdftotext')
 if not exe:return []
 r=subprocess.run([exe,'-bbox',str(pdf),'-'],capture_output=True,text=True)
 if r.returncode:return []
 try: root=ET.fromstring(r.stdout)
 except Exception:return []
 out=[]
 for pi,page in enumerate([x for x in root.iter() if x.tag.rsplit('}',1)[-1]=='page'],1):
  pw=float(page.attrib.get('width',0)); ph=float(page.attrib.get('height',0))
  for w in page.iter():
   if w.tag.rsplit('}',1)[-1]!='word':continue
   try: out.append((pi,pw,ph,float(w.attrib['xMin']),float(w.attrib['yMin']),float(w.attrib['xMax']),float(w.attrib['yMax']),''.join(w.itertext())))
   except: pass
 return out
def overlap(a,b):
 if a[0]!=b[0]:return False
 ix=max(0,min(a[5],b[5])-max(a[3],b[3])); iy=max(0,min(a[6],b[6])-max(a[4],b[4]))
 area=ix*iy
 aa=max(1,(a[5]-a[3])*(a[6]-a[4])); bb=max(1,(b[5]-b[3])*(b[6]-b[4]))
 return area/min(aa,bb)>0.18
ap=argparse.ArgumentParser();ap.add_argument('pdf');ap.add_argument('--evidence',required=True);ap.add_argument('--out');a=ap.parse_args()
pdf=Path(a.pdf); ev=json.loads(Path(a.evidence).read_text()); err=[]
try: jsonschema.Draft202012Validator(SCHEMA).validate(ev)
except Exception as e: print(f'FAIL: evidence schema: {e}'); raise SystemExit(1)
words=bbox_words(pdf)
if not words: err.append('no direct PDF text geometry extracted')
over=0
# Spatial bucketing to avoid O(n^2) blowup.
by={}
for w in words: by.setdefault((w[0],int(w[4]//18)),[]).append(w)
for group in by.values():
 for i,x in enumerate(group):
  for y in group[i+1:]:
   if overlap(x,y): over+=1
edge=sum(1 for w in words if w[3]<-0.5 or w[4]<-0.5 or w[5]>w[1]+0.5 or w[6]>w[2]+0.5)
if over>0: err.append(f'PDF text geometry contains {over} overlapping word pairs')
if edge>0: err.append(f'PDF contains {edge} words outside page bounds')
for pg in ev['rendered_pages']:
 if pg['clipping'] or pg['overlap'] or not pg['readable']: err.append(f'page {pg["page"]} direct render check failed')
ro=ev['reading_order']; ac=ev['accessibility']
if not ro['logical'] or not ro['table_order_preserved']: err.append('direct reading-order/table-order evidence failed')
for k,v in ac.items():
 if not v: err.append(f'accessibility evidence failed: {k}')
rec={'artifact_id':ev['artifact_id'],'word_count':len(words),'computed_overlap_pairs':over,'computed_edge_clipped_words':edge,'status':'FAIL' if err else 'PASS'}
if a.out: Path(a.out).write_text(json.dumps(rec,indent=2)+'\n')
if err: print('FAIL: '+'; '.join(err)); raise SystemExit(1)
print(f'PASS: fixed-document render preflight words={len(words)} overlaps=0 edge_clips=0')
