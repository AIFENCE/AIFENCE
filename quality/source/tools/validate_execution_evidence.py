#!/usr/bin/env python3
"""Validate executable AIFENCE QA evidence, Runtime coverage, and interaction/mobile closure."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker
ROOT=Path(__file__).resolve().parents[1]

ap=argparse.ArgumentParser()
ap.add_argument('evidence',help='JSON evidence record or array of records')
ap.add_argument('--plan',help='Optional Runtime plan JSON; required evidence checks must be directly PASSed')
ap.add_argument('--interaction-manifest',help='Interaction-closure manifest for exhaustive control/task cross-checking')
ap.add_argument('--out',help='Optional JSON validation summary path')
a=ap.parse_args()

schema=json.loads((ROOT/'schemas'/'execution_evidence.schema.json').read_text(encoding='utf-8'))
raw=json.loads(Path(a.evidence).read_text(encoding='utf-8'))
records=raw.get('records',[]) if isinstance(raw,dict) and 'records' in raw else raw if isinstance(raw,list) else [raw]
errors=[]
validator=Draft202012Validator(schema,format_checker=FormatChecker())
for i,record in enumerate(records):
    for err in validator.iter_errors(record): errors.append({'record':i,'path':'/'.join(map(str,err.path)),'error':err.message})
    if record.get('result')=='PASS' and record.get('provenance')!='direct':
        errors.append({'record':i,'path':'provenance','error':'PASS requires direct provenance'})

plan=None;coverage=[]
if a.plan:
    plan=json.loads(Path(a.plan).read_text(encoding='utf-8'))
    for ep in plan.get('evidencePlan',[]):
        artifact_id=ep.get('artifactId');profile=ep.get('profile')
        for check in ep.get('checks',[]):
            matches=[r for r in records if r.get('artifact_id')==artifact_id and r.get('profile')==profile and r.get('evidence_type')==check]
            direct_pass=any(r.get('result')=='PASS' and r.get('provenance')=='direct' for r in matches)
            status='PASS' if direct_pass else ('FAIL' if any(r.get('result')=='FAIL' for r in matches) else 'UNVERIFIED')
            item={'artifact_id':artifact_id,'profile':profile,'evidence_type':check,'required':bool(ep.get('required')),'status':status,'records':len(matches)}
            coverage.append(item)
            if ep.get('required') and not direct_pass:
                errors.append({'artifact_id':artifact_id,'profile':profile,'evidence_type':check,'error':'release-critical evidence does not have direct PASS evidence'})

interaction_summary=None
manifest=None
if a.interaction_manifest:
    manifest=json.loads(Path(a.interaction_manifest).read_text(encoding='utf-8'))
    ms=json.loads((ROOT/'schemas'/'interaction_closure_manifest.schema.json').read_text(encoding='utf-8'))
    for err in Draft202012Validator(ms).iter_errors(manifest): errors.append({'path':'interaction_manifest/'+('/'.join(map(str,err.path))),'error':err.message})
    artifact_id=manifest.get('artifact_id')
    controls=manifest.get('controls',[]);tasks=manifest.get('tasks',[])
    control_ids=[c.get('id') for c in controls if c.get('id')]
    task_ids=[t.get('id') for t in tasks if t.get('id')]
    if len(control_ids)!=len(set(control_ids)): errors.append({'path':'interaction_manifest/controls','error':'duplicate control ids'})
    if len(task_ids)!=len(set(task_ids)): errors.append({'path':'interaction_manifest/tasks','error':'duplicate task ids'})
    for c in controls:
        if not c.get('enabled',True) and not (c.get('disabled_reason') or '').strip(): errors.append({'path':f"interaction_manifest/controls/{c.get('id','?')}",'error':'disabled control requires disabled_reason'})
    p01=[t for t in tasks if t.get('priority') in {'P0','P1'}]
    for t in p01:
        if not {320,390}.issubset(set(t.get('required_viewports',[]))): errors.append({'path':f"interaction_manifest/tasks/{t.get('id','?')}",'error':'P0/P1 task requires 320 and 390 evidence'})
        if not (t.get('mobile_equivalent') or '').strip(): errors.append({'path':f"interaction_manifest/tasks/{t.get('id','?')}",'error':'P0/P1 task requires mobile_equivalent'})

    ctrl_records=[r for r in records if r.get('artifact_id')==artifact_id and r.get('profile')=='browser' and r.get('evidence_type')=='interactive control closure']
    task_records=[r for r in records if r.get('artifact_id')==artifact_id and r.get('profile')=='browser' and r.get('evidence_type')=='mobile task preservation']
    ctrl=next((r for r in ctrl_records if r.get('result')=='PASS' and r.get('provenance')=='direct'),None)
    task=next((r for r in task_records if r.get('result')=='PASS' and r.get('provenance')=='direct'),None)
    enabled={c['id'] for c in controls if c.get('enabled',True)}
    dead=[];missing_accounted=[];missing_exercised=[]
    if ctrl:
        d=ctrl.get('details') or {}; discovered=set(d.get('discoveredEnabledControlIds',[])); accounted=set(d.get('accountedControlIds',[])); exercised=set(d.get('exercisedControlIds',[])); dead=list(d.get('deadControlIds',[]))
        missing_discovered=sorted(enabled-discovered);extra_discovered=sorted(discovered-enabled)
        missing_accounted=sorted(enabled-accounted);missing_exercised=sorted(enabled-exercised)
        unknown=sorted((discovered|accounted|exercised|set(dead))-set(control_ids))
        if missing_discovered: errors.append({'artifact_id':artifact_id,'evidence_type':'interactive control closure','error':'manifest controls absent from runtime-discovered enabled inventory','ids':missing_discovered})
        if extra_discovered: errors.append({'artifact_id':artifact_id,'evidence_type':'interactive control closure','error':'runtime discovered enabled controls omitted from manifest','ids':extra_discovered})
        if missing_accounted: errors.append({'artifact_id':artifact_id,'evidence_type':'interactive control closure','error':'enabled controls omitted from accounting','ids':missing_accounted})
        if missing_exercised: errors.append({'artifact_id':artifact_id,'evidence_type':'interactive control closure','error':'enabled controls not directly exercised','ids':missing_exercised})
        if dead: errors.append({'artifact_id':artifact_id,'evidence_type':'interactive control closure','error':'dead enabled controls block PASS','ids':dead})
        if unknown: errors.append({'artifact_id':artifact_id,'evidence_type':'interactive control closure','error':'evidence references controls absent from manifest','ids':unknown})
    else:
        errors.append({'artifact_id':artifact_id,'evidence_type':'interactive control closure','error':'direct PASS record required for interaction manifest'})

    expected={(t['id'],vp):t for t in p01 for vp in t.get('required_viewports',[]) if vp in {320,390}}
    missing_tasks=[];failed_tasks=[]
    if task:
        rows=(task.get('details') or {}).get('taskResults',[]); by={(x.get('taskId'),x.get('viewport')):x for x in rows}
        for key,t in expected.items():
            x=by.get(key)
            if not x: missing_tasks.append({'taskId':key[0],'viewport':key[1]});continue
            ok=x.get('result')=='PASS' and x.get('entryReachable') is True and x.get('completionReachable') is True and x.get('statePreserved') is True
            recovery=x.get('recoveryStatus')
            if t.get('recovery_required',False): ok=ok and recovery=='PASS'
            else: ok=ok and recovery in {'PASS','N/A'}
            if not ok: failed_tasks.append({'taskId':key[0],'viewport':key[1]})
        if missing_tasks: errors.append({'artifact_id':artifact_id,'evidence_type':'mobile task preservation','error':'declared P0/P1 task/viewport evidence missing','items':missing_tasks})
        if failed_tasks: errors.append({'artifact_id':artifact_id,'evidence_type':'mobile task preservation','error':'declared P0/P1 mobile task did not preserve completion/state/recovery','items':failed_tasks})
    else:
        errors.append({'artifact_id':artifact_id,'evidence_type':'mobile task preservation','error':'direct PASS record required for interaction manifest'})
    interaction_summary={'artifact_id':artifact_id,'enabled_controls':len(enabled),'p0_p1_tasks':len(p01),'required_mobile_task_checks':len(expected),'dead_controls':dead,'missing_control_discovery':missing_discovered,'extra_runtime_controls':extra_discovered,'missing_control_accounting':missing_accounted,'missing_control_execution':missing_exercised,'missing_task_checks':missing_tasks,'failed_task_checks':failed_tasks}

# A Runtime plan may require interaction closure; absence of a manifest is then itself release-blocking.
if plan and any(x.get('required') for x in plan.get('interactionClosure',[])) and not a.interaction_manifest:
    errors.append({'path':'interaction_manifest','error':'Runtime plan requires interaction-closure manifest for production/high-fidelity interactive acceptance'})
if plan and manifest:
    required_ids={x.get('artifactId') for x in plan.get('interactionClosure',[]) if x.get('required')}
    if required_ids and manifest.get('artifact_id') not in required_ids:
        errors.append({'path':'interaction_manifest/artifact_id','error':f'manifest artifact is not a required interaction-closure artifact: {manifest.get("artifact_id")}'})

summary={'ok':not errors,'records':len(records),'coverage':coverage,'interactionClosure':interaction_summary,'errors':errors,'rule':'PASS is accepted only from schema-valid direct evidence; required plan checks remain unverified until directly exercised; enabled controls and declared P0/P1 320/390 tasks are fail-closed when an interaction manifest is required.'}
if a.out: Path(a.out).write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2));sys.exit(0 if summary['ok'] else 1)
