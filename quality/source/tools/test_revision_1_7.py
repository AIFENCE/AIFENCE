#!/usr/bin/env python3
"""Executable Revision 1.7/1.7.1/1.7.3/1.7.4 governance, evidence, benchmark, interaction, genericity, and decision-depth smoke tests."""
from __future__ import annotations
import csv,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PY=sys.executable

def run(*args,ok=True):
    p=subprocess.run([PY,*map(str,args)],cwd=ROOT,text=True,capture_output=True)
    if ok and p.returncode!=0: raise AssertionError((p.stdout+p.stderr)[-4000:])
    if not ok and p.returncode==0: raise AssertionError('expected failure: '+' '.join(map(str,args)))
    return p

with tempfile.TemporaryDirectory(prefix='biziq-1-7-test-') as td:
    td=Path(td)
    cases=[
      {'id':'T1','category':'website','split':'development','prompt':'Create a premium landscaping website.','artifact_contracts':['marketing-website']},
      {'id':'T2','category':'dashboard','split':'holdout','prompt':'Create a payments dashboard concept.','artifact_contracts':['dashboard']},
    ]
    cases_path=td/'cases.json';cases_path.write_text(json.dumps(cases))
    bench=td/'bench'
    run(ROOT/'tools'/'benchmark_pipeline.py','prepare',cases_path,'--run-id','smoke','--out',bench)
    jobs=json.loads((bench/'generation_jobs.json').read_text())['jobs'];assert len(jobs)==4
    manifest=[]
    for j in jobs:
        artifact=td/(j['job_id'].replace(':','_')+'.txt');artifact.write_text(j['job_id'])
        manifest.append({'job_id':j['job_id'],'artifact_path':str(artifact),'render_profile':'text-smoke'})
    manifest_path=td/'artifacts.json';manifest_path.write_text(json.dumps({'items':manifest}))
    run(ROOT/'tools'/'benchmark_pipeline.py','capture',bench,manifest_path)
    run(ROOT/'tools'/'benchmark_pipeline.py','blind',bench)
    blind=json.loads((bench/'judge'/'blind_judging_manifest.json').read_text())['items'];assert len(blind)==4
    key=json.loads((bench/'private'/'blind_key.json').read_text())['items']
    scores=td/'scores.csv'
    dims=['visual_quality','completeness','truthfulness','usability','feature_depth','responsiveness','accessibility','implementation_correctness','genericity_resistance']
    with scores.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['judge_id','blind_id',*dims,'pairwise_preference','notes']);w.writeheader()
        km={x['blind_id']:x for x in key}
        for item in blind:
            cond=km[item['blind_id']]['condition'];v=9.4 if cond=='biziq' else 8.8
            w.writerow({'judge_id':'J1','blind_id':item['blind_id'],**{d:v for d in dims},'pairwise_preference':'','notes':''})
    run(ROOT/'tools'/'benchmark_pipeline.py','lock',bench,scores)
    analysis=td/'analysis';run(ROOT/'tools'/'benchmark_pipeline.py','analyze',scores,bench/'private'/'blind_key.json','--run',bench,'--out',analysis)
    summary=json.loads((analysis/'statistical_summary.json').read_text());assert summary['pairs']==2 and summary['biziq_wins']==2 and summary['mean_delta']>0

    # Evidence schema and plan-aware acceptance.
    plan={'evidencePlan':[{'artifactId':'artifact-1','profile':'browser','required':True,'checks':['viewport captures']} ]}
    plan_path=td/'plan.json';plan_path.write_text(json.dumps(plan))
    good=td/'good.json';good.write_text(json.dumps([{'artifact_id':'artifact-1','profile':'browser','evidence_type':'viewport captures','result':'PASS','observations':['direct test'],'artifacts':[],'hashes':{},'provenance':'direct'}]))
    run(ROOT/'tools'/'validate_execution_evidence.py',good,'--plan',plan_path)
    bad=td/'bad.json';bad.write_text(json.dumps({'artifact_id':'artifact-1','profile':'browser','evidence_type':'viewport captures','result':'PASS','observations':[],'artifacts':[],'hashes':{},'provenance':'inferred'}))
    run(ROOT/'tools'/'validate_execution_evidence.py',bad,ok=False)

    # Revision 1.7.1 exhaustive interaction/mobile closure.
    interaction_manifest={
      'artifact_id':'artifact-1','generated_before_final_acceptance':True,
      'controls':[
        {'id':'period','label':'Period','expected_behavior':'changes period','enabled':True,'priority':'P1','required_viewports':[320,390,768,1440]},
        {'id':'more','label':'More actions','expected_behavior':'opens menu','enabled':True,'priority':'P1','required_viewports':[320,390,768,1440]}
      ],
      'tasks':[{'id':'inspect-recover','description':'inspect and recover transaction','priority':'P0','required_viewports':[320,390,768,1440],'completion_definition':'detail and recovery available','recovery_required':True,'desktop_surface':'side panel','mobile_equivalent':'full-screen detail sheet'}]
    }
    im=td/'interaction.json';im.write_text(json.dumps(interaction_manifest))
    run(ROOT/'tools'/'validate_interaction_manifest.py',im)
    plan2={'interactionClosure':[{'artifactId':'artifact-1','required':True}], 'evidencePlan':[{'artifactId':'artifact-1','profile':'browser','required':True,'checks':['interactive control closure','mobile task preservation']}]}
    plan2p=td/'plan2.json';plan2p.write_text(json.dumps(plan2))
    good2=td/'good2.json';good2.write_text(json.dumps([
      {'artifact_id':'artifact-1','profile':'browser','evidence_type':'interactive control closure','result':'PASS','observations':['all controls exercised'],'artifacts':[],'hashes':{},'provenance':'direct','details':{'discoveredEnabledControlIds':['period','more'],'accountedControlIds':['period','more'],'exercisedControlIds':['period','more'],'deadControlIds':[]}},
      {'artifact_id':'artifact-1','profile':'browser','evidence_type':'mobile task preservation','result':'PASS','observations':['task preserved'],'artifacts':[],'hashes':{},'provenance':'direct','details':{'taskResults':[{'taskId':'inspect-recover','viewport':320,'result':'PASS','entryReachable':True,'completionReachable':True,'statePreserved':True,'recoveryStatus':'PASS'},{'taskId':'inspect-recover','viewport':390,'result':'PASS','entryReachable':True,'completionReachable':True,'statePreserved':True,'recoveryStatus':'PASS'}]}}
    ]))
    run(ROOT/'tools'/'validate_execution_evidence.py',good2,'--plan',plan2p,'--interaction-manifest',im)
    run(ROOT/'tools'/'validate_execution_evidence.py',good2,'--plan',plan2p,ok=False)
    dead=json.loads(good2.read_text());dead[0]['details']['deadControlIds']=['more'];dead[0]['details']['exercisedControlIds']=['period'];deadp=td/'dead.json';deadp.write_text(json.dumps(dead));run(ROOT/'tools'/'validate_execution_evidence.py',deadp,'--plan',plan2p,'--interaction-manifest',im,ok=False)
    mobile=json.loads(good2.read_text());mobile[1]['details']['taskResults'][0].update({'result':'FAIL','completionReachable':False,'recoveryStatus':'FAIL'});mobilep=td/'mobile.json';mobilep.write_text(json.dumps(mobile));run(ROOT/'tools'/'validate_execution_evidence.py',mobilep,'--plan',plan2p,'--interaction-manifest',im,ok=False)
    closure_cases=json.loads((ROOT/'benchmarks'/'v3_interaction_closure_cases.json').read_text());assert len(closure_cases)==3

    # Revision 1.7.3 dense-product structural genericity closure.
    generic_good=td/'generic-good.json';generic_good.write_text(json.dumps({
      'artifact_id':'artifact-saas','artifact_family':'saas-web-app',
      'structural_decisions':[
        {'id':'s1','source':'workflow','decision':'exception-first queue with inline recovery history','non_cosmetic':True,'swap_resistant':True},
        {'id':'s2','source':'domain-data','decision':'persistent dependency map beside the selected work item','non_cosmetic':True,'swap_resistant':True},
        {'id':'s3','source':'brand','decision':'compact command rail tied to product terminology','non_cosmetic':True,'swap_resistant':True}],
      'component_grammars':['queue-list','timeline','dependency-graph','structured-form'],
      'task_structure_links':[{'task_id':'triage','region':'exception queue','reason':'prioritizes unresolved operational exceptions'},{'task_id':'inspect','region':'dependency map','reason':'shows upstream and downstream impact before action'},{'task_id':'recover','region':'timeline','reason':'keeps recovery history visible during retry'}],
      'template_similarity':{'best_match_id':'generic.saas-master-detail-queue','score':0.52,'threshold':0.60},
      'competitor_swap_test':{'passes':True,'break_reasons':['dependency topology is domain specific','recovery history controls primary layout']},
      'rendered_observations':['exception queue drives the opening composition','dependency map persists beside the active item','recovery timeline replaces generic activity cards'],
      'status':'PASS'}))
    run(ROOT/'tools'/'validate_genericity_evidence.py',generic_good)
    generic_bad=td/'generic-bad.json';badg=json.loads(generic_good.read_text());badg['component_grammars']=['cards','table'];badg['template_similarity']['score']=0.66;generic_bad.write_text(json.dumps(badg));run(ROOT/'tools'/'validate_genericity_evidence.py',generic_bad,ok=False)

    # Revision 1.7.3 complex-B2B buyer decision-depth closure.
    b2b_good=td/'b2b-good.json';b2b_good.write_text(json.dumps({'artifact_id':'artifact-b2b','journey_type':'b2b-complex','decision_paths':[
      {'id':'fit','priority':'P0','buyer_decision':'Will this fit our current architecture?','evidence_inputs':['integration matrix','deployment constraints'],'fit_or_qualification':'supported integration and deployment conditions','objection_or_risk':'migration and compatibility risk','next_action':'open technical evaluation','downstream_state':'evaluation checklist with owner and expectations','artifact_surface':'integration readiness matrix','status':'PASS'},
      {'id':'adopt','priority':'P1','buyer_decision':'Can our team adopt this safely?','evidence_inputs':['implementation sequence','security review boundaries'],'fit_or_qualification':'required stakeholders and prerequisites','objection_or_risk':'implementation and procurement delay','next_action':'request implementation review','downstream_state':'review handoff with required inputs','artifact_surface':'implementation readiness path','status':'PASS'}],
      'rendered_or_direct_evidence':['integration readiness matrix is rendered and actionable','implementation path exposes risk and next-step state'],'status':'PASS'}))
    run(ROOT/'tools'/'validate_decision_depth_evidence.py',b2b_good)
    b2b_bad=td/'b2b-bad.json';badb=json.loads(b2b_good.read_text());badb['decision_paths']=badb['decision_paths'][:1];b2b_bad.write_text(json.dumps(badb));run(ROOT/'tools'/'validate_decision_depth_evidence.py',b2b_bad,ok=False)
    qfc=json.loads((ROOT/'benchmarks'/'v3_quality_floor_closure_cases.json').read_text());assert len(qfc)==3



# Revision 1.7.4 dense-product first-pass quality closure.
with tempfile.TemporaryDirectory(prefix='biziq-dense-quality-') as td:
    td=Path(td)
    good={
      'artifact_id':'artifact-payments','artifact_family':'dashboard','product_flavor':'payments','provenance':'direct',
      'visual_finish':{'viewports':[1440,768,390,320],'hierarchy':{'dominant_region':'transaction decision workspace','secondary_regions':['evidence rail','recovery/action area']},'surface_roles':['workspace','evidence','selected-detail','recovery'],'typography_roles':['task-title','region-label','data-value','metadata','state-feedback'],'control_alignment':True,'state_surfaces':['selected detail','error recovery','success feedback'],'material_defects':[],'rendered_observations':['workspace dominates the view','detail is optically distinct','mobile preserves hierarchy'],'status':'PASS'},
      'completeness':{'features':[
        {'feature_id':'find','priority':'P0','coverage':['entry-orientation','information-evidence','primary-action','contextual-action','normal','empty-no-results','error-recovery','success-feedback','detail-drilldown','responsive-320-390','accessibility','truth-data-semantics','dependency','acceptance-evidence'],'status':'PASS'},
        {'feature_id':'inspect','priority':'P0','coverage':['entry-orientation','information-evidence','primary-action','normal','error-recovery','success-feedback','detail-drilldown','responsive-320-390','accessibility','truth-data-semantics','acceptance-evidence'],'status':'PASS'},
        {'feature_id':'recover','priority':'P1','coverage':['entry-orientation','information-evidence','primary-action','normal','error-recovery','success-feedback','detail-drilldown','responsive-320-390','accessibility','truth-data-semantics','acceptance-evidence'],'status':'PASS'}], 'missing_applicable_rows':[],'status':'PASS'},
      'accessibility':{'critical_paths':[{'task_id':'investigate-recover','named_controls':True,'keyboard_complete':True,'visible_focus':True,'focus_order_return':True,'programmatic_feedback':True,'non_color_meaning':True,'target_readability':True,'reflow_320_390':True,'errors_associated':True,'status':'PASS'}],'unlabelled_enabled_controls':[],'status':'PASS'},
      'feature_depth':{'level5_features':[
        {'feature_id':'inspect','user_job':'inspect transaction evidence','level':5,'roles':['investigation-inspection'],'status':'PASS'},
        {'feature_id':'recover','user_job':'resolve transaction exception','level':5,'roles':['decision-action-recovery'],'status':'PASS'},
        {'feature_id':'continue','user_job':'preserve filters and continue review','level':5,'roles':['continuity-comparison'],'status':'PASS'}],
        'workflow_loop':['find/filter/segment','inspect transaction','status/risk/context','action/recovery','result/feedback','continue'],'status':'PASS'},
      'status':'PASS'}
    gp=td/'good.json';gp.write_text(json.dumps(good));run(ROOT/'tools'/'validate_dense_product_quality_evidence.py',gp)
    bad=json.loads(gp.read_text());bad['visual_finish']['material_defects']=['unfinished mobile recovery state'];bp=td/'bad.json';bp.write_text(json.dumps(bad));run(ROOT/'tools'/'validate_dense_product_quality_evidence.py',bp,ok=False)
    bad2=json.loads(gp.read_text());bad2['accessibility']['critical_paths'][0]['keyboard_complete']=False;bp2=td/'bad2.json';bp2.write_text(json.dumps(bad2));run(ROOT/'tools'/'validate_dense_product_quality_evidence.py',bp2,ok=False)
    bad3=json.loads(gp.read_text());bad3['feature_depth']['workflow_loop']=['find/filter/segment','inspect transaction','action/recovery'];bp3=td/'bad3.json';bp3.write_text(json.dumps(bad3));run(ROOT/'tools'/'validate_dense_product_quality_evidence.py',bp3,ok=False)
    dense=json.loads((ROOT/'benchmarks'/'v3_dense_product_first_pass_cases.json').read_text());assert len(dense)==3

# Revision 1.7.3 generation preflight: reserved-keyword parse failure is blocked and clean direct runtime evidence passes.
with tempfile.TemporaryDirectory(prefix='biziq-preflight-') as td:
    td=Path(td); bad=td/'bad.html'; good=td/'good.html'; runtime=td/'runtime.json'
    bad.write_text('<!doctype html><button id="export">Export</button><script>export.onclick=()=>1</script>')
    good.write_text('<!doctype html><button id="export">Export</button><script>const exportButton=document.getElementById("export");exportButton.onclick=()=>1</script>')
    runtime.write_text(json.dumps({'provenance':'direct','result':'PASS','document_loaded':True,'page_errors':[],'console_errors':[],'failed_required_resources':[]}))
    r=subprocess.run([sys.executable,str(ROOT/'tools'/'validate_generation_preflight.py'),str(bad),'--runtime-evidence',str(runtime)],capture_output=True,text=True)
    assert r.returncode!=0 and ('syntax/parser' in r.stdout or 'SyntaxError' in r.stdout+r.stderr)
    r=subprocess.run([sys.executable,str(ROOT/'tools'/'validate_generation_preflight.py'),str(good),'--runtime-evidence',str(runtime)],capture_output=True,text=True)
    assert r.returncode==0, r.stdout+r.stderr

print('PASS: Revision 1.7.4 benchmark lifecycle, executable evidence, interaction closure, structural genericity, B2B decision-depth, generation preflight, and dense-product first-pass quality semantics')
