#!/usr/bin/env python3
"""Auditable AIFENCE benchmark lifecycle: prepare -> capture -> blind -> lock -> analyze."""
from __future__ import annotations
import argparse,csv,hashlib,json,random,statistics,math,shutil
from pathlib import Path
D=['visual_quality','completeness','truthfulness','usability','feature_depth','responsiveness','accessibility','implementation_correctness','genericity_resistance']

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,obj): Path(p).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
def percentile(xs,p):
    if not xs:return None
    ys=sorted(xs);k=(len(ys)-1)*p;lo=math.floor(k);hi=math.ceil(k)
    return ys[lo] if lo==hi else ys[lo]*(hi-k)+ys[hi]*(k-lo)
def bootstrap_ci(values,fn,seed=1701,n=4000):
    if not values:return [None,None]
    rng=random.Random(seed); sims=[fn([rng.choice(values) for __ in values]) for _ in range(n)]
    return [round(percentile(sims,.025),3),round(percentile(sims,.975),3)]
def prompt_of(case): return case.get('prompt') or case.get('request') or case.get('input') or case.get('title') or case['id']

def stage_prepare(args):
    cases=json.loads(Path(args.cases).read_text(encoding='utf-8'))
    if not isinstance(cases,list) or not cases: raise SystemExit('cases must be a non-empty JSON array')
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True);(out/'private').mkdir(exist_ok=True)
    rng=random.Random(args.seed); jobs=[]; blind_key=[]
    for case in cases:
        cid=case['id']
        for condition in ['control','aifence']:
            blind_id=f"B{rng.randrange(10**9,10**10)}"
            jobs.append({'job_id':f'{cid}:{condition}','case_id':cid,'condition':condition,'prompt':prompt_of(case),'artifact_contracts':case.get('artifact_contracts',[]),'evaluation_emphasis':case.get('evaluation_emphasis',[])})
            blind_key.append({'blind_id':blind_id,'case_id':cid,'condition':condition,'job_id':f'{cid}:{condition}','category':case.get('category','unclassified'),'split':case.get('split','unspecified'),'evaluation_emphasis':case.get('evaluation_emphasis',[])})
    rng.shuffle(jobs); rng.shuffle(blind_key)
    dump(out/'generation_jobs.json',{'run_id':args.run_id,'jobs':jobs})
    dump(out/'private'/'blind_key.json',{'run_id':args.run_id,'items':blind_key})
    run={'run_id':args.run_id,'stage':'prepared','case_count':len(cases),'conditions':['control','aifence'],'hashes':{'cases':sha(args.cases),'generation_jobs':sha(out/'generation_jobs.json'),'blind_key':sha(out/'private'/'blind_key.json')},'artifacts':[],'score_lock':None,'notes':['Generation jobs are explicit and condition-labelled; judge-facing material is produced only by the blind stage.','No artifact generation is implied by preparation.']}
    dump(out/'run_state.json',run);print(out/'run_state.json')

def stage_capture(args):
    rp=Path(args.run);p=rp/'run_state.json';run=json.loads(p.read_text());manifest=json.loads(Path(args.manifest).read_text());items=manifest.get('items',manifest if isinstance(manifest,list) else [])
    jobs={x['job_id']:x for x in json.loads((rp/'generation_jobs.json').read_text())['jobs']}
    captured=[]
    for x in items:
        y=dict(x);job=jobs.get(y.get('job_id'))
        if not job: raise SystemExit(f"Unknown generation job: {y.get('job_id')}")
        fp=y.get('artifact_path');
        if not fp or not Path(fp).is_file(): raise SystemExit(f"Artifact missing for {y.get('job_id')}: {fp}")
        y.update({'case_id':job['case_id'],'condition':job['condition'],'sha256':sha(fp),'bytes':Path(fp).stat().st_size})
        captured.append(y)
    expected=set(jobs);got={x['job_id'] for x in captured};missing=sorted(expected-got)
    if missing and not args.allow_partial: raise SystemExit(f'Missing {len(missing)} generation artifacts; first: {missing[:3]}')
    run['artifacts']=captured;run['stage']='generated';run['hashes']['artifact_manifest']=sha(args.manifest);run['missing_jobs']=missing;dump(p,run);print(f"Captured {len(captured)} artifact records; missing {len(missing)}")

def stage_blind(args):
    rp=Path(args.run);run=json.loads((rp/'run_state.json').read_text());key=json.loads((rp/'private'/'blind_key.json').read_text())['items'];km={x['job_id']:x for x in key};out=rp/'judge';out.mkdir(exist_ok=True)
    items=[]
    for art in run.get('artifacts',[]):
        k=km.get(art['job_id']);
        if not k: continue
        item={'blind_id':k['blind_id'],'artifact_path':art['artifact_path'],'sha256':art['sha256'],'bytes':art['bytes']}
        for optional in ['normalized_path','render_profile','notes']:
            if optional in art:item[optional]=art[optional]
        items.append(item)
    rng=random.Random(args.seed);rng.shuffle(items)
    dump(out/'blind_judging_manifest.json',{'run_id':run['run_id'],'items':items,'rubric':args.rubric})
    score_header=['judge_id','blind_id',*D,'pairwise_preference','notes']
    with (out/'score_template.csv').open('w',encoding='utf-8',newline='') as f: csv.writer(f).writerow(score_header)
    run['stage']='blinded';run['hashes']['blind_judging_manifest']=sha(out/'blind_judging_manifest.json');dump(rp/'run_state.json',run)
    print(out/'blind_judging_manifest.json')

def stage_lock(args):
    p=Path(args.run)/'run_state.json';run=json.loads(p.read_text());h=sha(args.scores);run['stage']='score-locked';run['hashes']['scores']=h;run['score_lock']={'sha256':h,'file':str(Path(args.scores).resolve())};dump(p,run);print('Scores locked by hash; unblind only after this stage.')

def judge_agreement(rows):
    by_dim={d:{} for d in D}
    for r in rows:
        j=r.get('judge_id') or 'judge-unknown';bid=r['blind_id']
        for d in D:by_dim[d].setdefault(bid,[]).append((j,float(r[d])))
    out={}
    for d,items in by_dim.items():
        spreads=[max(v for _,v in vals)-min(v for _,v in vals) for vals in items.values() if len(vals)>1]
        out[d]={'median_within_item_spread':round(statistics.median(spreads),3) if spreads else None,'items_with_multiple_judges':len(spreads)}
    return out

def stage_analyze(args):
    score_path=Path(args.scores);run_path=Path(args.run)/'run_state.json' if args.run else None
    if run_path and run_path.exists():
        run=json.loads(run_path.read_text());lock=run.get('score_lock') or {}
        if lock.get('sha256') and lock['sha256']!=sha(score_path): raise SystemExit('Score file hash differs from locked score file; analysis refused.')
    rows=list(csv.DictReader(score_path.open(encoding='utf-8',newline='')));key=json.loads(Path(args.key).read_text())['items'];km={x['blind_id']:x for x in key};by={}
    for r in rows:
        vals={d:float(r[d]) for d in D};by.setdefault(r['blind_id'],[]).append(vals)
    agg={bid:{d:statistics.median([x[d] for x in rs]) for d in D} for bid,rs in by.items()}
    for x in agg.values():x['overall_100']=sum(x[d] for d in D)/90*100
    pairs={}
    for bid,s in agg.items():
        if bid not in km:continue
        meta=km[bid];pairs.setdefault(meta['case_id'],{})[meta['condition']]=s
    deltas=[];dims={d:[] for d in D};wins=losses=ties=0
    for cid,pair in pairs.items():
        if not {'control','aifence'}<=set(pair):continue
        d=pair['aifence']['overall_100']-pair['control']['overall_100'];deltas.append(d);wins+=d>0;losses+=d<0;ties+=d==0
        for k in D:dims[k].append(pair['aifence'][k]-pair['control'][k])
    sd=statistics.stdev(deltas) if len(deltas)>1 else 0;effect=(statistics.mean(deltas)/sd if sd else None)
    pref=[(r.get('pairwise_preference') or '').strip().lower() for r in rows if (r.get('pairwise_preference') or '').strip()]
    family={};split_deltas={};floor_failures={'control':0,'aifence':0};floor_total={'control':0,'aifence':0}
    for cid,pair in pairs.items():
        if not {'control','aifence'}<=set(pair):continue
        meta=next((v for v in km.values() if v['case_id']==cid),{})
        delta=pair['aifence']['overall_100']-pair['control']['overall_100']
        family.setdefault(meta.get('category','unclassified'),[]).append(delta);split_deltas.setdefault(meta.get('split','unspecified'),[]).append(delta)
        for cond in ['control','aifence']:
            floor_total[cond]+=1
            if pair[cond]['overall_100'] < args.floor*10 or any(pair[cond][d] < args.floor for d in D): floor_failures[cond]+=1
    summary={'pairs':len(deltas),'mean_delta':round(statistics.mean(deltas),3) if deltas else None,'median_delta':round(statistics.median(deltas),3) if deltas else None,'mean_delta_ci95':bootstrap_ci(deltas,statistics.mean),'median_delta_ci95':bootstrap_ci(deltas,statistics.median),'aifence_quality_wins':wins,'control_wins':losses,'ties':ties,'paired_effect_size':round(effect,3) if effect is not None else None,'dimensions':{d:{'mean_delta':round(statistics.mean(v),3) if v else None,'wins':sum(x>0 for x in v),'losses':sum(x<0 for x in v),'ties':sum(x==0 for x in v)} for d,v in dims.items()},'artifact_family_deltas':{k:round(statistics.mean(v),3) for k,v in family.items()},'split_deltas':{k:round(statistics.mean(v),3) for k,v in split_deltas.items()},'floor':args.floor,'floor_failures':{k:{'failures':floor_failures[k],'total':floor_total[k],'rate':round(floor_failures[k]/floor_total[k],3) if floor_total[k] else None} for k in floor_failures},'judge_agreement':judge_agreement(rows),'pairwise_preference_counts':{x:pref.count(x) for x in sorted(set(pref))},'score_file_sha256':sha(score_path)}
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True);dump(out/'statistical_summary.json',summary);print(json.dumps(summary,indent=2))

ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True)
p=sub.add_parser('prepare');p.add_argument('cases');p.add_argument('--run-id',default='benchmark-run');p.add_argument('--out',default='benchmark_pipeline_run');p.add_argument('--seed',type=int,default=1701);p.set_defaults(fn=stage_prepare)
p=sub.add_parser('capture');p.add_argument('run');p.add_argument('manifest');p.add_argument('--allow-partial',action='store_true');p.set_defaults(fn=stage_capture)
p=sub.add_parser('blind');p.add_argument('run');p.add_argument('--rubric',default='source/benchmarks/scoring_rubric.md');p.add_argument('--seed',type=int,default=1701);p.set_defaults(fn=stage_blind)
p=sub.add_parser('lock');p.add_argument('run');p.add_argument('scores');p.set_defaults(fn=stage_lock)
p=sub.add_parser('analyze');p.add_argument('scores');p.add_argument('key');p.add_argument('--run');p.add_argument('--floor',type=float,default=9.0);p.add_argument('--out',default='benchmark_analysis');p.set_defaults(fn=stage_analyze)
a=ap.parse_args();a.fn(a)
