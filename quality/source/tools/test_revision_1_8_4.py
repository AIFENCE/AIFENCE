#!/usr/bin/env python3
"""Executable Core 1.8.4 family-aware emission adapters, XLSX extraction, and composite routing tests."""
from pathlib import Path
import json, subprocess, sys, tempfile, zipfile
ROOT=Path(__file__).resolve().parents[1]
VAL=ROOT/'tools'/'validate_family_emission_evidence.py'

def run(cmd): return subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
def write_ev(path,family,terms,boundaries,markers,semantics,children=None):
 d={'artifact_id':'a','family':family,'provenance':'direct','domain_terms':terms,'evidence_boundaries':boundaries,'surface_markers':markers,'semantics':semantics,'status':'PASS'}
 if children is not None:d['child_artifacts']=children
 path.write_text(json.dumps(d));return path

def expect_pass(artifact,ev):
 p=run([sys.executable,str(VAL),str(artifact),'--evidence',str(ev)])
 if p.returncode: print(p.stdout+p.stderr); raise SystemExit(f'FAIL: expected PASS for {artifact}')
def expect_fail(artifact,ev):
 if run([sys.executable,str(VAL),str(artifact),'--evidence',str(ev)]).returncode==0: raise SystemExit(f'FAIL: expected FAIL for {artifact}')

with tempfile.TemporaryDirectory(prefix='biziq-184-') as td:
 td=Path(td)
 # Brand uses brand-native rules, not workflow states.
 b=td/'brand.md'; b.write_text('''# Northline Metrology identity\nThe split-axis mark signals calibration alignment. The narrow wordmark is reserved for horizontal lockups.\nUse Instrument Sans for interface labels and Source Serif for technical editorial copy. Cobalt is the verification accent; warm gray is neutral.\nComposition uses a left measurement rail and large numeric anchors. Photography shows real inspection setups; icons use square measurement geometry.\nApplications: calibration certificate, instrument case label, service portal header. Never stretch the mark. Never use cobalt for warning states.\nCalibration claims require documented scope confirmation. dimensional calibration optical inspection traceability''')
 bev=write_ev(td/'b.json','brand',['dimensional calibration','optical inspection','traceability'],['Calibration claims require documented scope confirmation'],['split-axis mark','narrow wordmark','Instrument Sans','Source Serif','Cobalt','left measurement rail','inspection setups','square measurement geometry','calibration certificate','instrument case label','service portal header','Never stretch the mark','Never use cobalt for warning states'],{
  'identity_rules':['split-axis mark','narrow wordmark'],'typography_rules':['Instrument Sans','Source Serif'],'color_rules':['Cobalt'],'composition_rules':['left measurement rail'],'imagery_or_iconography_rules':['inspection setups','square measurement geometry'],'applications':['calibration certificate','instrument case label','service portal header'],'misuse_constraints':['Never stretch the mark','Never use cobalt for warning states']})
 expect_pass(b,bev)
 # Email is allowed ordinary transition language when concrete sequence semantics are present.
 e=td/'email.md';e.write_text('''New trial administrator: verify the first workspace import. Message job: establish activation confidence. CTA: Review imported records. Measurement event: import_reviewed.\nActive evaluator: compare permission coverage. Message job: resolve access uncertainty. CTA: Check role coverage. Measurement event: role_reviewed.\nSequence transition: after import review, move to access review; the next state is evaluation readiness. If access is unresolved, send the recovery note. Compliance boundary: do not claim customer savings without supplied evidence. treasury workspace permission review activation''')
 eev=write_ev(td/'e.json','email',['treasury workspace','permission review','activation'],['do not claim customer savings without supplied evidence'],['New trial administrator','Active evaluator','establish activation confidence','resolve access uncertainty','Review imported records','Check role coverage','import_reviewed','role_reviewed','after import review, move to access review','evaluation readiness','recovery note'],{
  'audience_states':['New trial administrator','Active evaluator'],'message_jobs':['establish activation confidence','resolve access uncertainty'],'ctas':['Review imported records','Check role coverage'],'sequence_transitions':['after import review, move to access review','evaluation readiness'],'measurement_events':['import_reviewed','role_reviewed'],'compliance_or_truth_boundaries':['do not claim customer savings without supplied evidence']})
 expect_pass(e,eev)
 # Presentation uses storyline semantics.
 d=td/'deck.txt';d.write_text('''Grid interconnection program. Storyline: queue pressure, study dependency, decision options. Evidence: submitted study dates and utility responses. Implication: schedule confidence remains limited. Decision request: approve the next evidence-gathering gate. Audience takeaway: dependencies are visible; no approval is implied. utility study interconnection queue development gate''')
 dev=write_ev(td/'d.json','presentation',['utility study','interconnection queue','development gate'],['no approval is implied'],['queue pressure','study dependency','decision options','submitted study dates','utility responses','schedule confidence remains limited','approve the next evidence-gathering gate','dependencies are visible','no approval is implied'],{
  'storyline_beats':['queue pressure','study dependency','decision options'],'evidence_points':['submitted study dates','utility responses'],'implications':['schedule confidence remains limited','dependencies are visible'],'decisions_or_requests':['approve the next evidence-gathering gate'],'audience_takeaways':['dependencies are visible','no approval is implied']})
 expect_pass(d,dev)
 # Namespace-safe XLSX with shared string + inline string + formulas.
 x=td/'model.xlsx'
 with zipfile.ZipFile(x,'w') as z:
  z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
  z.writestr('xl/sharedStrings.xml','''<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="5" uniqueCount="5"><si><t>call volume</t></si><si><t>handle time</t></si><si><t>staffing scenario</t></si><si><t>Base case</t></si><si><t>Downside case</t></si></sst>''')
  z.writestr('xl/worksheets/sheet1.xml','''<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row><c t="s"><v>0</v></c><c t="s"><v>1</v></c><c t="s"><v>2</v></c><c t="inlineStr"><is><t>Editable assumptions</t></is></c></row><row><c t="s"><v>3</v></c><c t="s"><v>4</v></c><c t="inlineStr"><is><t>Required staffing</t></is></c><c><f>B2*C2</f><v>42</v></c></row><row><c t="inlineStr"><is><t>Scenario comparison</t></is></c><c t="inlineStr"><is><t>Decision surface</t></is></c><c t="inlineStr"><is><t>Illustrative assumptions only</t></is></c><c t="inlineStr"><is><t>Derived cells are locked</t></is></c></row></sheetData></worksheet>''')
 xev=write_ev(td/'x.json','spreadsheet',['call volume','handle time','staffing scenario'],['Illustrative assumptions only'],['call volume','handle time','staffing scenario','Editable assumptions','Base case','Downside case','Required staffing','Scenario comparison','Decision surface','Illustrative assumptions only','Derived cells are locked'],{
  'inputs':['call volume','handle time','Editable assumptions'],'calculations_or_outputs':['Required staffing','B2*C2'],'scenarios':['Base case','Downside case'],'decision_surfaces':['Scenario comparison','Decision surface'],'provenance_markers':['Illustrative assumptions only'],'editable_boundaries':['Derived cells are locked']})
 expect_pass(x,xev)
 # Generic website evidence cannot self-certify.
 g=td/'g.html';g.write_text('<main><h1>Feature A</h1><p>Proof block</p><button>Service one</button><p>Workflow step</p></main>')
 gev=write_ev(td/'g.json','website',['roofing','membrane','drainage'],['manufacturer confirmation'],['Feature A','Proof block','Service one','Workflow step','decision path','generic proof'],{
  'decisions':['decision path','feature A'],'proof_points':['Proof block','generic proof'],'actions':['Service one','workflow step'],'uncertainties_or_objections':['relevant evidence'],'continuations':['next state']})
 expect_fail(g,gev)
 # Internal vocabulary always fails regardless of family.
 leak=td/'leak.txt';leak.write_text(b.read_text()+' P0 QA gate')
 expect_fail(leak,bev)
 # Composite verifies children and project continuity.
 comp=td/'comp';comp.mkdir();(comp/'deck.txt').write_text('Board deck uses verified demand signal and references scenario workbook. shared assumption register executive gate scenario handoff verification status travels with both deliverables')
 (comp/'model.txt').write_text('Scenario workbook uses shared assumption register and links to executive gate. scenario handoff demand sensitivity editable input verification status travels with both deliverables')
 cev=write_ev(td/'c.json','composite',['demand signal','scenario workbook','assumption register'],['shared assumptions are illustrative'],['shared assumption register','executive gate','Board deck','scenario workbook','demand sensitivity','editable input','verified demand signal'],{
  'shared_context_rules':['shared assumption register','executive gate','scenario handoff'],'shared_identifiers_or_assumptions':['shared assumption register','executive gate'],'cross_artifact_continuity':['shared assumption register','executive gate','scenario handoff'],'child_acceptance_refs':['verified demand signal','demand sensitivity'],'project_provenance_boundaries':['shared assumptions are illustrative','verification status travels with both deliverables']},[
  {'artifact_id':'deck','family':'presentation','surface_markers':['Board deck','verified demand signal','executive gate']},
  {'artifact_id':'model','family':'spreadsheet','surface_markers':['scenario workbook','demand sensitivity','editable input']}
 ])
 # Add boundary to project corpus.
 (comp/'README.txt').write_text('shared assumptions are illustrative; verification status travels with both deliverables')
 expect_pass(comp,cev)

# Composite classifier regression is executed against the canonical runtime-template classifier.
js="""import {classifyRequest} from './tooling/runtime-template/src/classifier.js'; const q='Create an executive decision deck plus spreadsheet scenario model for a fictional community-solar project.'; const c=classifyRequest(q); console.log(JSON.stringify(c.creationTypes)); if(c.artifactGraph.kind!=='composite'||!c.creationTypes.includes('Presentation / Deck')||!c.creationTypes.includes('Spreadsheet / Financial Model')) process.exit(1);"""
p=subprocess.run(['node','--input-type=module','-e',js],cwd=ROOT.parent,text=True,capture_output=True)
if p.returncode: print(p.stdout+p.stderr); raise SystemExit('FAIL: deck + spreadsheet composite routing')
print('PASS: Revision 1.8.4 family-aware emission adapters, XLSX extraction, context scaffold, and deck+model composite routing')
