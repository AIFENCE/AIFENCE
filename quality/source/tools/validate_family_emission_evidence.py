#!/usr/bin/env python3
"""AIFENCE Core 1.8.6 family-aware finished-surface emission validator."""
from pathlib import Path
import argparse, html, json, re, shutil, subprocess, sys, zipfile
import xml.etree.ElementTree as ET
try:
 import jsonschema
except Exception as exc:
 print(f"FAIL: jsonschema unavailable: {exc}"); raise SystemExit(2)
ROOT=Path(__file__).resolve().parents[1]
SCHEMA=json.loads((ROOT/'schemas'/'family_emission_evidence.schema.json').read_text())
FORBIDDEN=[
 r'\bP0\b',r'\bP1\b',r'decision depth closure',r'truth boundary',r'feature depth',r'quality gate',r'genericity',
 r'artifact contract',r'evidence plan',r'acceptance ledger',r'qa gate',r'family depth closure',r'materialization closure',r'compiler gate',
 r'dense[- ]product quality',r'emission preflight',r'substance gate'
]
# These phrases are only suspicious in families where they are framework vocabulary. They are
# not globally banned because ordinary phrases such as "next state" can be valid email/document copy.
SCAFFOLD_BY_FAMILY={
 'website':[r'\bfeature [ab]\b',r'\bservice (one|two)\b',r'\bproof block\b',r'\bgeneric proof\b',r'\bworkflow step\b'],
 'web-app':[r'\bfeature [ab]\b',r'\bworkflow step\b',r'\bgeneric proof\b'],
 'dashboard':[r'\bfeature [ab]\b',r'\bworkflow step\b',r'\bgeneric proof\b'],
 'mobile':[r'\bfeature [ab]\b',r'\bworkflow step\b',r'\bgeneric proof\b'],
 'brand':[r'\bbrand rule [ab]\b',r'\bapplication example\b',r'\bgeneric proof\b'],
 'email':[r'\bemail [ab]\b',r'\bgeneric proof\b'],
 'cli':[r'\bcommand [ab]\b',r'\bworkflow step\b'],
 'presentation':[r'\bslide [ab]\b',r'\bproof block\b',r'\brelevant evidence\b'],
 'spreadsheet':[r'\binput [ab]\b',r'\bscenario [ab]\b',r'\brelevant evidence\b'],
 'fixed-document':[r'\bsection [ab]\b',r'\bproof block\b'],
 'documentation':[r'\bsection [ab]\b',r'\bproof block\b'],
 'marketing-creative':[r'\bmessage [ab]\b',r'\bproof block\b'],
 'composite':[r'\bchild artifact [ab]\b',r'\bgeneric proof\b']
}
FAMILY_RULES={
 'website':{'decisions':2,'proof_points':2,'actions':2,'uncertainties_or_objections':1,'continuations':1},
 'web-app':{'user_jobs':2,'actions':2,'states':2,'recovery_paths':1,'outcomes':2},
 'dashboard':{'decision_questions':2,'evidence_views':2,'actions':2,'states':2,'recovery_or_handoff':1},
 'mobile':{'user_jobs':2,'actions':2,'states':2,'recovery_paths':1,'outcomes':2},
 'brand':{'identity_rules':2,'typography_rules':1,'color_rules':1,'composition_rules':1,'imagery_or_iconography_rules':1,'applications':3,'misuse_constraints':2},
 'email':{'audience_states':2,'message_jobs':2,'ctas':2,'sequence_transitions':2,'measurement_events':2,'compliance_or_truth_boundaries':1},
 'cli':{'commands':2,'help_surfaces':1,'configuration_rules':1,'io_contracts':2,'exit_semantics':2,'recovery_guidance':1},
 'presentation':{'storyline_beats':3,'evidence_points':2,'implications':2,'decisions_or_requests':1,'audience_takeaways':2},
 'spreadsheet':{'inputs':3,'calculations_or_outputs':2,'scenarios':2,'decision_surfaces':2,'provenance_markers':1,'editable_boundaries':1},
 'fixed-document':{'questions_or_issues':2,'evidence_points':4,'findings_or_conclusions':3,'implications_or_actions':3,'reader_takeaways':2,'provenance_markers':2},
 'documentation':{'questions_or_tasks':2,'evidence_or_examples':2,'instructions_or_findings':2,'next_actions':1,'provenance_markers':1},
 'marketing-creative':{'message_layers':2,'proof_elements':1,'ctas':1,'visual_rules':2,'channel_context':1},
 'composite':{'shared_context_rules':3,'shared_identifiers_or_assumptions':2,'cross_artifact_continuity':3,'child_acceptance_refs':2,'project_provenance_boundaries':2}
}
TEXT_EXT={'.html','.htm','.md','.txt','.csv','.json','.yaml','.yml','.xml','.svg'}
OOXML={'.pptx','.xlsx','.docx'}

def norm(s): return re.sub(r'\s+',' ',str(s).strip().lower())
def local(tag): return tag.rsplit('}',1)[-1]
def html_text(s):
 s=re.sub(r'<(script|style)\b[^>]*>.*?</\1\s*>',' ',s,flags=re.I|re.S)
 s=re.sub(r'<!--.*?-->',' ',s,flags=re.S); s=re.sub(r'<[^>]+>',' ',s)
 return html.unescape(re.sub(r'\s+',' ',s))
def xml_text_nodes(raw):
 try: root=ET.fromstring(raw)
 except Exception:return []
 vals=[]
 for el in root.iter():
  if local(el.tag) in {'t','v','f'} and el.text: vals.append(html.unescape(el.text))
 return vals

def xlsx_text(p):
 chunks=[]
 with zipfile.ZipFile(p) as z:
  names=set(z.namelist()); shared=[]
  if 'xl/sharedStrings.xml' in names:
   try:
    root=ET.fromstring(z.read('xl/sharedStrings.xml'))
    for si in root.iter():
     if local(si.tag)=='si':
      parts=[el.text or '' for el in si.iter() if local(el.tag)=='t']
      shared.append(''.join(parts))
   except Exception: pass
  # workbook labels, table labels, comments and style-adjacent text are useful production surfaces.
  for n in sorted(names):
   if n.startswith('xl/') and n.endswith('.xml') and not n.startswith('xl/worksheets/') and n!='xl/sharedStrings.xml':
    try: chunks.extend(xml_text_nodes(z.read(n)))
    except Exception: pass
  for n in sorted(x for x in names if x.startswith('xl/worksheets/') and x.endswith('.xml')):
   try: root=ET.fromstring(z.read(n))
   except Exception: continue
   for c in (el for el in root.iter() if local(el.tag)=='c'):
    ctype=c.attrib.get('t',''); vals=[]
    if ctype=='inlineStr': vals=[el.text or '' for el in c.iter() if local(el.tag)=='t']
    else:
     v=next((el.text for el in c if local(el.tag)=='v' and el.text is not None),None)
     f=next((el.text for el in c if local(el.tag)=='f' and el.text is not None),None)
     if f: vals.append(f)
     if v is not None:
      if ctype=='s':
       try: vals.append(shared[int(v)])
       except Exception: vals.append(v)
      elif ctype in {'str','e','b'}: vals.append(v)
      else: vals.append(v)
    # rich inline strings can exist without t=inlineStr in imperfect generators.
    vals.extend(el.text or '' for el in c.iter() if local(el.tag)=='t')
    chunks.extend(vals)
 return ' '.join(x for x in chunks if str(x).strip())

def ooxml_text(p):
 if p.suffix.lower()=='.xlsx': return xlsx_text(p)
 chunks=[]
 with zipfile.ZipFile(p) as z:
  for n in z.namelist():
   if n.endswith('.xml') and (n.startswith('ppt/') or n.startswith('word/')):
    try: chunks.extend(xml_text_nodes(z.read(n)))
    except Exception: pass
 return ' '.join(chunks)
def pdf_text(p):
 exe=shutil.which('pdftotext')
 if not exe:return ''
 r=subprocess.run([exe,'-layout',str(p),'-'],capture_output=True,text=True)
 return r.stdout if r.returncode==0 else ''
def extract_path(p):
 if p.is_dir(): return '\n'.join(extract_path(x) for x in sorted(p.rglob('*')) if x.is_file())
 ext=p.suffix.lower()
 try:
  if ext in TEXT_EXT:
   t=p.read_text(encoding='utf-8',errors='replace'); return html_text(t) if ext in {'.html','.htm','.svg'} else t
  if ext in OOXML:return ooxml_text(p)
  if ext=='.pdf':return pdf_text(p)
 except Exception:return ''
 return ''
SYNONYMS={
 'recovery':{'retry','restore','resume','preserve','reconnect','recover'},
 'sync':{'synchronization','synchronise','synchronize'},
 'failure':{'error','failed','failure','exception'},
 'approval':{'approve','approved','review','signoff'},
 'monitoring':{'monitor','track','tracking','watch','health'},
 'renewal':{'renew','renewing','expiration','expiry'},
 'report':{'assessment','analysis','brief','memo'},
 'decision':{'decide','choice','recommendation','approval'},
 'evidence':{'proof','source','record','records','support'},
 'action':{'next','step','remediation','response'},
}
STOP={'the','a','an','of','to','for','and','or','with','on','in','by','from','is','are','be','this','that'}
def stem(t):
 t=re.sub(r'[^a-z0-9]+','',t.lower())
 for suf in ('ing','ed','es','s'):
  if len(t)>5 and t.endswith(suf): return t[:-len(suf)]
 return t
def token_set(s): return {stem(x) for x in re.findall(r'[a-z0-9]+',norm(s)) if x not in STOP and len(x)>1}
def token_equiv(a,b):
 if a==b:return True
 for k,vals in SYNONYMS.items():
  group={stem(k)}|{stem(x) for x in vals}
  if a in group and b in group:return True
 return False
def sem_present(item,c):
 ni=norm(item)
 if ni in c:return True
 it=token_set(ni); ct=token_set(c)
 if not it:return False
 matched=0
 for t in it:
  if any(token_equiv(t,u) for u in ct): matched+=1
 ratio=matched/len(it)
 # Conservative: all tokens for short phrases; >=75% for 4+ token phrases.
 return matched>=2 and (ratio>=1.0 if len(it)<=3 else ratio>=0.75)
def present_count(items,c): return sum(1 for x in items if sem_present(x,c))
def evidence_generic(items,family):
 pats=SCAFFOLD_BY_FAMILY.get(family,[])
 return [x for x in items if any(re.search(p,norm(x),re.I) for p in pats)]

def main():
 ap=argparse.ArgumentParser(description='Validate family-native substance on finished AIFENCE artifact surfaces.')
 ap.add_argument('artifact'); ap.add_argument('--evidence',required=True); ap.add_argument('--runtime-evidence'); ap.add_argument('--out'); a=ap.parse_args()
 art=Path(a.artifact).resolve()
 try:
  d=json.loads(Path(a.evidence).read_text()); jsonschema.Draft202012Validator(SCHEMA).validate(d)
 except Exception as e: print(f'FAIL: evidence schema: {e}'); return 1
 if not art.exists(): print('FAIL: artifact missing'); return 2
 family=d['family']; rules=FAMILY_RULES[family]; corpus=extract_path(art)
 if a.runtime_evidence:
  try:
   rr=json.loads(Path(a.runtime_evidence).read_text())
   if rr.get('provenance')!='direct': print('FAIL: runtime surface evidence provenance must be direct'); return 1
   corpus+='\n'+'\n'.join(str(x.get('stdout',''))+'\n'+str(x.get('stderr','')) for x in rr.get('executions',[]))
  except Exception as e: print(f'FAIL: runtime surface evidence: {e}'); return 1
 c=norm(corpus); err=[]; hits=[]
 if not c.strip(): err.append('no extractable production-facing surface text')
 for pat in FORBIDDEN:
  if re.search(pat,c,re.I): hits.append(pat)
 if hits: err.append('production-facing output leaks internal vocabulary: '+', '.join(hits))
 # Family-native semantic categories must exist in evidence and materialize directly.
 coverage={}
 for category,minimum in rules.items():
  items=d['semantics'].get(category,[])
  if len(items)<minimum: err.append(f'{family} semantics {category} declares {len(items)} items; requires at least {minimum}'); continue
  generic=evidence_generic(items,family)
  if generic: err.append(f'{family} semantics {category} relies on generic scaffold markers: '+', '.join(generic))
  n=present_count(items,c); coverage[category]=n
  if n<minimum: err.append(f'emitted surface contains only {n}/{len(items)} family-native {category}; requires at least {minimum}')
 # Common truth/domain material must be present regardless of family.
 domain_n=present_count(d['domain_terms'],c); bound_n=present_count(d['evidence_boundaries'],c)
 coverage['domain_terms']=domain_n; coverage['evidence_boundaries']=bound_n
 if domain_n<3: err.append(f'emitted surface contains only {domain_n}/{len(d["domain_terms"])} domain terms; requires 3')
 if bound_n<1: err.append('emitted surface contains no declared evidence/provenance boundary')
 marker_n=present_count(d['surface_markers'],c); marker_need=max(5,round(len(d['surface_markers'])*0.65))
 if marker_n<marker_need: err.append(f'emitted surface contains only {marker_n}/{len(d["surface_markers"])} direct substance markers; requires {marker_need}')
 # Context-sensitive scaffold detection: fail only when multiple family-scaffold phrases dominate
 # and direct specific marker coverage is weak. Natural isolated uses are allowed.
 scaffold=[]
 for pat in SCAFFOLD_BY_FAMILY.get(family,[]):
  n=len(re.findall(pat,c,re.I))
  if n: scaffold.append({'pattern':pat,'count':n})
 if sum(x['count'] for x in scaffold)>=3 and marker_n/max(1,len(d['surface_markers']))<0.80:
  err.append('generic scaffold language dominates family-native surface: '+', '.join(f"{x['pattern']} x{x['count']}" for x in scaffold))
 # Core 1.8.5 fixed-document depth rejects repeated paraphrases as fake finding/action depth.
 if family=='fixed-document':
  for category,minimum in [('findings_or_conclusions',3),('implications_or_actions',3),('reader_takeaways',2)]:
   vals=[norm(x) for x in d['semantics'].get(category,[]) if norm(x)]
   if len(set(vals))<minimum: err.append(f'fixed-document {category} requires at least {minimum} distinct items')
 # Core 1.8.5 composite continuity anchors intended to connect children must recur on emitted project surfaces.
 if family=='composite':
  for category in ('shared_identifiers_or_assumptions','cross_artifact_continuity'):
   for item in d['semantics'].get(category,[]):
    if c.count(norm(item))<2: err.append(f'composite continuity anchor appears fewer than twice across project surfaces: {item}')
 # Composite evidence additionally proves each child has visible family-specific markers.
 if family=='composite':
  children=d.get('child_artifacts',[])
  if len(children)<2: err.append('composite emission requires at least two child_artifacts records')
  for child in children:
   n=present_count(child['surface_markers'],c)
   if n<max(2,round(len(child['surface_markers'])*0.60)): err.append(f'composite child {child["artifact_id"]} lacks direct child-specific surface evidence')
 record={'artifact_id':d['artifact_id'],'artifact_path':str(art),'family':family,'provenance':'direct','forbidden_hits':hits,'family_coverage':coverage,'surface_markers_present':marker_n,'surface_markers_required':marker_need,'scaffold_hits':scaffold,'surface_text_chars':len(c),'status':'FAIL' if err else 'PASS'}
 if a.out: Path(a.out).write_text(json.dumps(record,indent=2)+'\n')
 if err: print('FAIL: '+'; '.join(err)); return 1
 print(f'PASS: family-aware emission family={family} markers={marker_n}/{len(d["surface_markers"])} chars={len(c)}')
 return 0
if __name__=='__main__': raise SystemExit(main())
