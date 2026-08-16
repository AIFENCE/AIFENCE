#!/usr/bin/env python3
"""Validate a BizIQ Operational Procedure against Revision 1.6 machine semantics."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from jsonschema.validators import validator_for
from referencing import Registry, Resource

ROOT=Path(__file__).resolve().parents[1]
SCHEMA_DIR=ROOT/'schemas'
STRONG={'VERIFIED_ORGANIZATION_PROCEDURE','EXTERNAL_AUTHORITATIVE_REQUIREMENT'}


def _schema_registry():
    resources=[]
    for p in SCHEMA_DIR.glob('*.schema.json'):
        data=json.loads(p.read_text(encoding='utf-8'))
        if '$id' in data:
            resources.append((data['$id'],Resource.from_contents(data)))
    return Registry().with_resources(resources)


def schema_errors(data):
    schema=json.loads((SCHEMA_DIR/'operational_procedure.schema.json').read_text(encoding='utf-8'))
    cls=validator_for(schema); cls.check_schema(schema)
    v=cls(schema, registry=_schema_registry())
    return sorted(v.iter_errors(data), key=lambda e:list(e.absolute_path))


def validate_data(data):
    errors=[]; warnings=[]
    for e in schema_errors(data):
        path='.'.join(str(x) for x in e.absolute_path) or '<root>'
        errors.append(f'schema {path}: {e.message}')
    if errors:
        return errors,warnings

    def unique(items,key,label):
        seen=set()
        for x in items:
            v=x.get(key)
            if v in seen: errors.append(f'duplicate {label}: {v}')
            seen.add(v)
        return seen

    steps=data['steps']; sources=data['authority_sources']; evid=data['evidence_requirements']; rights=data['decision_rights']; kpis=data['kpis']
    step_ids=unique(steps,'step_id','step_id')
    source_ids=unique(sources,'authority_id','authority_id')
    evidence_ids=unique(evid,'evidence_id','evidence_id')
    unique(rights,'decision_id','decision_id'); unique(kpis,'metric_id','metric_id')

    source_by={x['authority_id']:x for x in sources}
    # Strong authority source truth/currentness.
    for s in sources:
        if s['authority_class'] in STRONG and s['verification_state']!='VERIFIED':
            errors.append(f"authority source {s['authority_id']} strong class is not VERIFIED")
    if data['authority_class'] in STRONG and not sources:
        errors.append(f"{data['authority_class']} requires authority_sources")

    # MIXED must classify every material step explicitly via authority_map.
    mapped=set()
    for m in data['authority_map']:
        for sid in m['section_or_step_ids']:
            mapped.add(sid)
        for aid in m['authority_source_ids']:
            if aid not in source_ids: errors.append(f'authority_map references unknown authority_source_id: {aid}')
        if m['authority_class'] in STRONG:
            if not m['authority_source_ids']:
                errors.append('strong authority_map entry has no authority_source_ids')
            for aid in m['authority_source_ids']:
                src=source_by.get(aid)
                if src and (src['authority_class'] not in STRONG or src['verification_state']!='VERIFIED'):
                    errors.append(f'authority_map strong entry references non-verified source: {aid}')
    if data['authority_class']=='MIXED':
        for s in steps:
            if s['materiality']=='MATERIAL' and s['step_id'] not in mapped:
                errors.append(f"MIXED procedure material step not covered by authority_map: {s['step_id']}")

    # Resolve step authority/evidence refs.
    for s in steps:
        for eid in s.get('evidence_ids',[]):
            if eid not in evidence_ids: errors.append(f"step {s['step_id']} references unknown evidence_id: {eid}")
        for aid in s.get('authority_source_ids',[]):
            if aid not in source_ids: errors.append(f"step {s['step_id']} references unknown authority_source_id: {aid}")
        if s.get('authority_class') in STRONG and not s.get('authority_source_ids'):
            errors.append(f"step {s['step_id']} has strong authority_class without authority_source_ids")

    # Evidence refs from exceptions / DoD / handoffs.
    for ex in data['exceptions']:
        for eid in ex['closure_evidence_ids']:
            if eid not in evidence_ids: errors.append(f"exception {ex['exception_id']} references unknown evidence_id: {eid}")
    for i,d in enumerate(data['definition_of_done'],1):
        for eid in d['evidence_ids']:
            if eid not in evidence_ids: errors.append(f'Definition-of-Done criterion {i} references unknown evidence_id: {eid}')
    for h in data['handoffs']:
        for eid in h['evidence_ids']:
            if eid not in evidence_ids: errors.append(f"handoff {h['handoff_id']} references unknown evidence_id: {eid}")

    # Every declared evidence record must point at a known step/decision or explicit procedure-level token.
    decision_ids={r['decision_id'] for r in rights}
    allowed_links=step_ids|decision_ids|{'PROCEDURE','HANDOFF','OUTCOME','EXCEPTION'}
    for e in evid:
        if e['linked_step_or_decision'] not in allowed_links:
            errors.append(f"evidence {e['evidence_id']} links unknown step/decision: {e['linked_step_or_decision']}")

    # Lifecycle semantics not completely expressible by structure alone.
    state=data['approval_state']
    if state in {'APPROVED','EFFECTIVE'} and (not data.get('approver') or not data.get('approval_evidence')):
        errors.append(f'{state} requires approver and approval_evidence')
    if state=='EFFECTIVE' and not data.get('effective_date'):
        errors.append('EFFECTIVE requires effective_date')
    if state=='SUPERSEDED' and not data.get('superseded_by'):
        errors.append('SUPERSEDED requires superseded_by')

    # KPI semantic target provenance and reproducibility.
    for k in kpis:
        if k['calculation_state']=='DEFINED':
            required=['formula','population_scope','source_systems','calculation_frequency','review_cadence','audit_evidence']
            missing=[x for x in required if not k.get(x)]
            if missing: errors.append(f"kpi {k['metric_id']} DEFINED missing reproducibility fields: {', '.join(missing)}")
        if k['calculation_state']=='UNRESOLVED' and not k.get('open_unknowns'):
            errors.append(f"kpi {k['metric_id']} UNRESOLVED requires open_unknowns")
        if k.get('target'):
            if k['target_provenance'] not in {'ORGANIZATION_VERIFIED','EXTERNAL_VERIFIED'} or not k.get('target_source'):
                errors.append(f"kpi {k['metric_id']} target lacks verified provenance/source")

    # Draft/general procedures should expose organization-specific unknowns when material.
    if data['authority_class'] in {'GENERAL_GUIDANCE','ORGANIZATION_DRAFT'} and not data['unknowns']:
        warnings.append('draft/general procedure has no explicit unknowns; confirm all organization-specific facts are truly known or inapplicable')
    if data['approval_state'] in {'DRAFT','IN_REVIEW'} and data.get('effective_date'):
        warnings.append(f"{data['approval_state']} procedure carries effective_date; confirm this is descriptive rather than an approval claim")
    return errors,warnings


def main():
    ap=argparse.ArgumentParser(description='Validate a compiled BizIQ operational procedure JSON artifact (Revision 1.6).')
    ap.add_argument('file',type=Path)
    args=ap.parse_args()
    try: data=json.loads(args.file.read_text(encoding='utf-8'))
    except Exception as e:
        print(f'FAIL: cannot parse JSON: {e}'); return 2
    errors,warnings=validate_data(data)
    print(f'Operational procedure validator: {args.file}')
    for w in warnings: print('WARN:',w)
    if errors:
        print(f'FAIL: {len(errors)} error(s)')
        for e in errors: print(' -',e)
        return 1
    print('PASS: operational procedure schema + semantic authority/closure checks satisfied.')
    return 0

if __name__=='__main__': raise SystemExit(main())
