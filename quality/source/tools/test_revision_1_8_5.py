#!/usr/bin/env python3
"""Executable Core 1.8.5 fixed-document depth, composite continuity/containment, and workspace routing regressions."""
from pathlib import Path
import json, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
VAL=ROOT/'tools'/'validate_family_emission_evidence.py'
DEPTH=ROOT/'tools'/'validate_family_depth_evidence.py'

def run(cmd,cwd=ROOT): return subprocess.run(cmd,cwd=cwd,text=True,capture_output=True)
def evidence(path,family,terms,bounds,markers,semantics,children=None):
 d={'artifact_id':'r185','family':family,'provenance':'direct','domain_terms':terms,'evidence_boundaries':bounds,'surface_markers':markers,'semantics':semantics,'status':'PASS'}
 if children is not None:d['child_artifacts']=children
 path.write_text(json.dumps(d));return path

def expect(cmd,ok=True,label='case'):
 p=run(cmd)
 if (p.returncode==0)!=ok:
  print(p.stdout+p.stderr); raise SystemExit(f'FAIL: {label}')

with tempfile.TemporaryDirectory(prefix='aifence-185-') as td:
 td=Path(td)
 shallow=td/'shallow.txt'; shallow.write_text('Cold-storage safety review. Questions: dock exposure and freezer access. Evidence: inspection log, maintenance note, incident summary, training roster. Finding: access controls require review. Action: review controls. Source boundary: supplied sample records only. Reader takeaway: follow up.')
 sev=evidence(td/'shallow.json','fixed-document',['cold-storage','freezer access','dock exposure'],['supplied sample records only','no field verification'],['dock exposure','freezer access','inspection log','maintenance note','incident summary','training roster','access controls require review','review controls','Reader takeaway','supplied sample records only','no field verification'],{
  'questions_or_issues':['dock exposure','freezer access'],'evidence_points':['inspection log','maintenance note','incident summary','training roster'],'findings_or_conclusions':['access controls require review','access controls require review','access controls require review'],'implications_or_actions':['review controls','review controls','review controls'],'reader_takeaways':['Reader takeaway','Reader takeaway'],'provenance_markers':['supplied sample records only','no field verification']})
 expect([sys.executable,str(VAL),str(shallow),'--evidence',str(sev)],False,'shallow fixed document should fail')

 deep=td/'deep.txt'; deep.write_text('Cold-storage safety review. Questions: dock exposure and freezer access. Evidence point: inspection log. Evidence point: maintenance note. Evidence point: incident summary. Evidence point: training roster. Finding one: dock-door traffic controls are inconsistently documented. Finding two: freezer-access escalation ownership is unclear. Finding three: training records do not establish current shift coverage. Action one: assign dock-control ownership and verify the posted route. Action two: define freezer-access escalation and responsible role. Action three: reconcile training coverage before the next shift change. Reader takeaway one: ownership gaps block a reliable operating conclusion. Reader takeaway two: evidence should be refreshed before any compliance claim. Source boundary one: supplied sample records only. Source boundary two: no field verification was performed. cold-storage freezer access dock exposure')
 dev=evidence(td/'deep.json','fixed-document',['cold-storage','freezer access','dock exposure'],['supplied sample records only','no field verification was performed'],['inspection log','maintenance note','incident summary','training roster','dock-door traffic controls are inconsistently documented','freezer-access escalation ownership is unclear','training records do not establish current shift coverage','assign dock-control ownership and verify the posted route','define freezer-access escalation and responsible role','reconcile training coverage before the next shift change','ownership gaps block a reliable operating conclusion','evidence should be refreshed before any compliance claim','supplied sample records only','no field verification was performed'],{
  'questions_or_issues':['dock exposure','freezer access'],'evidence_points':['inspection log','maintenance note','incident summary','training roster'],'findings_or_conclusions':['dock-door traffic controls are inconsistently documented','freezer-access escalation ownership is unclear','training records do not establish current shift coverage'],'implications_or_actions':['assign dock-control ownership and verify the posted route','define freezer-access escalation and responsible role','reconcile training coverage before the next shift change'],'reader_takeaways':['ownership gaps block a reliable operating conclusion','evidence should be refreshed before any compliance claim'],'provenance_markers':['supplied sample records only','no field verification was performed']})
 expect([sys.executable,str(VAL),str(deep),'--evidence',str(dev)],True,'deep fixed document should pass')

 comp=td/'comp'; comp.mkdir()
 (comp/'deck.txt').write_text('Transit electrification deck. Base Case and Depot A are shared identifiers. Assumption Register is the shared source. Model handoff uses Base Case. Approval status comes from supplied planning inputs only. Deck acceptance references scenario sensitivity.')
 (comp/'model.txt').write_text('Transit electrification model. Base Case and Depot A are shared identifiers. Assumption Register is the shared source. Model handoff uses Base Case. Approval status comes from supplied planning inputs only. Model acceptance references scenario sensitivity.')
 (comp/'boundary.txt').write_text('approval status is not independently verified')
 cev=evidence(td/'comp.json','composite',['transit electrification','Depot A','Base Case'],['supplied planning inputs only','approval status is not independently verified'],['Transit electrification deck','Transit electrification model','Base Case','Depot A','Assumption Register','Model handoff','scenario sensitivity','supplied planning inputs only'],{
  'shared_context_rules':['Assumption Register','Base Case','Depot A'],'shared_identifiers_or_assumptions':['Base Case','Depot A'],'cross_artifact_continuity':['Assumption Register','Base Case','Model handoff'],'child_acceptance_refs':['Deck acceptance references scenario sensitivity','Model acceptance references scenario sensitivity'],'project_provenance_boundaries':['supplied planning inputs only','approval status is not independently verified']},[
   {'artifact_id':'deck','family':'presentation','surface_markers':['Transit electrification deck','Base Case','Assumption Register']},
   {'artifact_id':'model','family':'spreadsheet','surface_markers':['Transit electrification model','Base Case','Assumption Register']}
 ])
 expect([sys.executable,str(VAL),str(comp),'--evidence',str(cev)],True,'composite continuity should pass')
 bad=td/'badcomp';bad.mkdir();(bad/'deck.txt').write_text((comp/'deck.txt').read_text());(bad/'model.txt').write_text('Transit electrification model. Independent scenario naming with no shared handoff. supplied planning inputs only approval status is not independently verified');(bad/'boundary.txt').write_text('approval status is not independently verified')
 expect([sys.executable,str(VAL),str(bad),'--evidence',str(cev)],False,'disconnected composite should fail')

 depth={'artifact_id':'project-composite','family':'composite','provenance':'direct','checks':[
  {'id':'child-contracts','status':'PASS','evidence':'direct'}, {'id':'shared-context','status':'PASS','evidence':'direct'}, {'id':'independent-child-qa','status':'PASS','evidence':'direct'}, {'id':'cross-artifact-consistency','status':'PASS','evidence':'direct'}],
  'critical_dimensions':{'implementation correctness':9.3,'completeness':9.2,'responsiveness':9.4},
  'records':[{'id':'a','priority':'P0','fields':{'artifact_type':'website','contract':'marketing website','shared_context':'brand rules','independent_qa':'direct','consistency_rule':'shared tokens'}},{'id':'b','priority':'P1','fields':{'artifact_type':'brand','contract':'brand identity','shared_context':'brand rules','independent_qa':'direct','consistency_rule':'shared tokens'}}],
  'requires_narrow_screen':True,'viewport_checks':[{'viewport':320,'overflow':False,'clipping':False,'critical_path_preserved':True,'evidence':'direct screenshot'},{'viewport':390,'overflow':False,'clipping':False,'critical_path_preserved':True,'evidence':'direct screenshot'}],'catastrophic_failures':[],'status':'PASS'}
 dp=td/'depth.json';dp.write_text(json.dumps(depth)); expect([sys.executable,str(DEPTH),str(dp)],True,'compact containment pass')
 depth['viewport_checks'][0]['overflow']=True;dp.write_text(json.dumps(depth));expect([sys.executable,str(DEPTH),str(dp)],False,'320 overflow should fail')

js="""import {classifyRequest} from './tooling/runtime-template/src/classifier.js';
const a=classifyRequest('Create a production contract renewal workspace for account leaders to monitor renewal health, deadlines, risk, evidence, and decisions.');
const b=classifyRequest('Create a production contract editing workspace where legal operations users create records, edit terms, and manage approval workflows.');
if(a.creationType!=='Dashboard') {console.error(a.creationType);process.exit(1)}
if(b.creationType!=='Web App / SaaS / Portal') {console.error(b.creationType);process.exit(2)}"""
p=run(['node','--input-type=module','-e',js],cwd=ROOT.parent)
if p.returncode: print(p.stdout+p.stderr); raise SystemExit('FAIL: workspace routing boundary')
print('PASS: Revision 1.8.5 fixed-document depth, composite continuity/containment, and dashboard/workspace routing')
