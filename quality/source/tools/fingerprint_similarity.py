#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
W={"artifact_family":.05,"shell":.10,"opening":.12,"sequence":.20,"motifs":.18,"container_ratio":.08,"alignment_bias":.07,"cta_positions":.05,"mobile_transforms":.15}
SETS={"sequence","motifs","cta_positions","mobile_transforms"}
def jac(a,b):
    a=set(a or []);b=set(b or [])
    if not a and not b:return 1
    if not a or not b:return 0
    return len(a&b)/len(a|b)
def sim(a,b):
    return sum(w*(jac(a.get(k),b.get(k)) if k in SETS else (1 if a.get(k)==b.get(k) and a.get(k) is not None else 0)) for k,w in W.items())
ap=argparse.ArgumentParser();ap.add_argument("candidate");ap.add_argument("--library",default="evals/generic_template_fingerprints.json");a=ap.parse_args()
c=json.loads(Path(a.candidate).read_text(encoding="utf-8"));lib=json.loads(Path(a.library).read_text(encoding="utf-8"))
rank=sorted(((sim(c,x),x["id"]) for x in lib),reverse=True)
for s,i in rank[:5]:print(f"{s:.3f}\t{i}")
best=rank[0][0] if rank else 0
print("RESULT:", "REJECT/HIGH genericity similarity" if best>.72 else "HIGH risk; refinement/justification required" if best>=.61 else "MODERATE risk; inspect" if best>=.46 else "LOW template similarity")
