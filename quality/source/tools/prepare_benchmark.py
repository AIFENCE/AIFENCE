#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,random
from pathlib import Path
def load(path):
    x=json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(x,list):raise SystemExit("Expected JSON array")
    return x
ap=argparse.ArgumentParser()
ap.add_argument("--development",default="benchmarks/v2_development_cases.json")
ap.add_argument("--private-holdout")
ap.add_argument("--out",default="benchmark_run")
ap.add_argument("--seed",type=int,default=20260809)
a=ap.parse_args()
cases=load(a.development)
for x in cases:x["split"]="development"
if a.private_holdout:
    h=load(a.private_holdout)
    for x in h:x["split"]="holdout"
    cases+=h
rng=random.Random(a.seed);blind=[];key=[];n=1
for c in cases:
    cond=["control","biziq"];rng.shuffle(cond)
    for condition in cond:
        bid=f"A{n:04d}";n+=1
        blind.append({"blind_id":bid,"case_id":c["id"],"split":c["split"],"category":c.get("category"),"title":c.get("title"),"prompt":c["prompt"],"artifact_contracts":c.get("artifact_contracts",[])})
        key.append({"blind_id":bid,"case_id":c["id"],"condition":condition})
rng.shuffle(blind)
out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
(out/"blind_run_manifest.json").write_text(json.dumps({"seed":a.seed,"artifact_count":len(blind),"items":blind},indent=2)+"\n",encoding="utf-8")
(out/"unblinding_key.json").write_text(json.dumps({"seed":a.seed,"items":key},indent=2)+"\n",encoding="utf-8")
print(f"Prepared {len(blind)} blinded artifacts from {len(cases)} cases.")
