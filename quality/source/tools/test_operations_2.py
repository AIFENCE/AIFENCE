#!/usr/bin/env python3
"""Execute all 30 Domain 31 regression fixtures and their capability assertions."""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from validate_operational_procedure import validate_data
STRONG={'VERIFIED_ORGANIZATION_PROCEDURE','EXTERNAL_AUTHORITATIVE_REQUIREMENT'}

def assertion(name,a):
    if name=='validator_rejects': return True
    if name=='unknowns_preserved': return bool(a.get('unknowns'))
    if name=='context_resolved': return all(str(a.get(k,'')).strip() for k in ['scope','trigger','responsible_role']) and bool(a.get('role_accountability'))
    if name=='context_ambiguity_preserved': return 'UNKNOWN' in a.get('scope','').upper() and bool(a.get('unknowns'))
    if name=='role_accountability_closed':
        r=a.get('role_accountability',{}); return bool(r.get('accountabilities')) and bool(r.get('scope_boundary')) and bool(r.get('exclusions')) and 'role_id' in r
    if name=='role_authority_unknown_preserved': return bool(a.get('role_accountability',{}).get('authority_unknowns'))
    if name=='strong_authority_verified':
        s=a.get('authority_sources',[]); return a.get('authority_class') in STRONG and bool(s) and all(x.get('verification_state')=='VERIFIED' and (x.get('version') or x.get('effective_date') or x.get('currentness_evidence')) for x in s)
    if name=='draft_authority_truthful': return a.get('authority_class')=='ORGANIZATION_DRAFT' and not a.get('authority_sources') and bool(a.get('unknowns'))
    if name=='material_steps_executable': return all(s.get('check') and s.get('failure_path') and (s.get('evidence_ids') or s.get('evidence_not_required_reason')) for s in a.get('steps',[]) if s.get('materiality')=='MATERIAL')
    if name=='approval_boundary_closed': return any(r.get('right')=='APPROVAL_REQUIRED' and r.get('approval_owner') and r.get('approval_limit_state') for r in a.get('decision_rights',[]))
    if name=='approval_limit_unknown_preserved': return any(r.get('right')=='APPROVAL_REQUIRED' and r.get('approval_limit_state')=='ORGANIZATION_SPECIFIC_NOT_SUPPLIED' and not r.get('approval_limit') for r in a.get('decision_rights',[]))
    if name=='stop_restart_closed': return any(r.get('right')=='STOP_AND_ESCALATE' and r.get('containment') and r.get('notification_targets') and r.get('escalation_path') and r.get('restart_condition') and r.get('restart_authority_state') for r in a.get('decision_rights',[]))
    if name=='restart_authority_unknown_preserved': return any(r.get('right')=='STOP_AND_ESCALATE' and r.get('restart_authority_state')=='ORGANIZATION_SPECIFIC_NOT_SUPPLIED' and not r.get('restart_authorizer') for r in a.get('decision_rights',[]))
    if name=='exception_recovery_closed': return all(x.get('detection_signal') and x.get('containment') and x.get('owner') and x.get('escalation_path') and x.get('recovery_action') and x.get('closure_evidence_ids') for x in a.get('exceptions',[]))
    if name=='evidence_references_resolve':
        ids={e.get('evidence_id') for e in a.get('evidence_requirements',[])}
        refs=[]
        for s in a.get('steps',[]): refs+=s.get('evidence_ids',[])
        for x in a.get('exceptions',[]): refs+=x.get('closure_evidence_ids',[])
        for d in a.get('definition_of_done',[]): refs+=d.get('evidence_ids',[])
        for h in a.get('handoffs',[]): refs+=h.get('evidence_ids',[])
        return bool(ids) and all(r in ids for r in refs)
    if name=='kpi_defined_reproducible':
        ks=a.get('kpis',[]); return bool(ks) and all(k.get('calculation_state')=='DEFINED' and k.get('formula') and k.get('population_scope') and k.get('source_systems') and k.get('calculation_frequency') and k.get('review_cadence') and k.get('audit_evidence') for k in ks)
    if name=='kpi_unresolved_truthful': return any(k.get('calculation_state')=='UNRESOLVED' and k.get('open_unknowns') and k.get('target_provenance') in {'ORGANIZATION_SPECIFIC_NOT_SUPPLIED','NOT_APPLICABLE'} for k in a.get('kpis',[]))
    if name=='effective_approval_closed': return a.get('approval_state')=='EFFECTIVE' and bool(a.get('approver')) and bool(a.get('approval_evidence')) and bool(a.get('effective_date'))
    if name=='draft_lifecycle_truthful': return a.get('approval_state')=='DRAFT' and not a.get('effective_date')
    raise KeyError(name)

def main():
    cases=json.loads((ROOT/'evals'/'control_regression_matrix_31.json').read_text(encoding='utf-8'))
    errors=[]; assertion_count=0
    if len(cases)!=30: errors.append(f'expected 30 cases, found {len(cases)}')
    for c in cases:
        a=c.get('input',{}); verr,_=validate_data(a); actual='FAIL' if verr else 'PASS'
        if actual!=c.get('expected_status'): errors.append(f"{c.get('id')}: expected {c.get('expected_status')} got {actual}: {'; '.join(verr[:3])}")
        if c.get('case')=='failure':
            frag=c.get('expected_error_contains','')
            if frag and frag.lower() not in ' | '.join(verr).lower(): errors.append(f"{c.get('id')}: failed, but not for intended reason containing {frag!r}")
        for name in c.get('expected_assertions',[]):
            assertion_count+=1
            try: ok=assertion(name,a)
            except Exception as e: errors.append(f"{c.get('id')}: assertion {name} raised {e}"); continue
            if not ok: errors.append(f"{c.get('id')}: assertion failed: {name}")
        blob=json.dumps(a,sort_keys=True).lower()
        for phrase in c.get('must_not_contain',[]):
            if phrase.lower() in blob: errors.append(f"{c.get('id')}: forbidden phrase {phrase!r}")
    kinds={k:sum(1 for c in cases if c.get('case')==k) for k in ['normal','ambiguous','failure']}
    if kinds!={'normal':10,'ambiguous':10,'failure':10}: errors.append(f'unbalanced cases: {kinds}')
    print(f'Operations 2.0 executable regressions: {len(cases)} cases')
    print(f'Capability assertions executed: {assertion_count}')
    print('Expected-positive executions: 20')
    print('Expected-negative executions: 10')
    if errors:
        print(f'FAIL: {len(errors)} error(s)')
        for e in errors: print(' -',e)
        return 1
    print('PASS: validator outcomes, intended failure reasons, and capability assertions all matched.')
    return 0
if __name__=='__main__': raise SystemExit(main())
