#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,statistics
from collections import defaultdict
from pathlib import Path
D=["visual_quality","completeness","truthfulness","usability","feature_depth","responsiveness","accessibility","implementation_correctness","genericity_resistance"]
ap=argparse.ArgumentParser();ap.add_argument("scores_csv");ap.add_argument("unblinding_key");ap.add_argument("--out",default="benchmark_results");a=ap.parse_args()
rows=list(csv.DictReader(Path(a.scores_csv).open(encoding="utf-8",newline="")));by=defaultdict(list)
for r in rows:
    vals={}
    for d in D:
        v=float(r[d])
        if not 0<=v<=10:raise SystemExit(f"{r['blind_id']} {d} out of range")
        vals[d]=v
    by[r["blind_id"]].append(vals)
agg={}
for bid,rs in by.items():
    agg[bid]={d:statistics.median([x[d] for x in rs]) for d in D}
    agg[bid]["overall_100"]=sum(agg[bid][d] for d in D)/90*100
key=json.loads(Path(a.unblinding_key).read_text(encoding="utf-8"))["items"];km={x["blind_id"]:x for x in key}
revealed=[{"blind_id":bid,**km[bid],**{d:round(s[d],3) for d in D},"overall_100":round(s["overall_100"],3)} for bid,s in agg.items()]
out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
if revealed:
    with (out/"artifact_scores_unblinded.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(revealed[0]));w.writeheader();w.writerows(revealed)
pairs=defaultdict(dict)
for r in revealed:pairs[r["case_id"]][r["condition"]]=r
pr=[]
for cid,p in sorted(pairs.items()):
    if "control" not in p or "aifence" not in p:continue
    c,b=p["control"],p["aifence"];row={"case_id":cid,"control_overall":c["overall_100"],"aifence_quality_overall":b["overall_100"],"delta":round(b["overall_100"]-c["overall_100"],3)}
    for d in D:row[d+"_delta"]=round(b[d]-c[d],3)
    pr.append(row)
if pr:
    with (out/"paired_deltas.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(pr[0]));w.writeheader();w.writerows(pr)
    ds=[x["delta"] for x in pr]
    summary={"pairs":len(pr),"median_delta":round(statistics.median(ds),3),"mean_delta":round(statistics.mean(ds),3),"aifence_quality_wins":sum(x>0 for x in ds),"control_wins":sum(x<0 for x in ds),"ties":sum(x==0 for x in ds)}
    (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))
