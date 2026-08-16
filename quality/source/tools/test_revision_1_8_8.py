#!/usr/bin/env python3
"""Core 1.8.8 deliverable phrase normalization and modifier-tolerant composite regressions."""
from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
cases=json.loads((ROOT/'benchmarks'/'v12_deliverable_phrase_composite_cases.json').read_text())
script="""import fs from 'node:fs'; import {classifyRequest} from './tooling/runtime-template/src/classifier.js';
const cases=JSON.parse(fs.readFileSync('./source/benchmarks/v12_deliverable_phrase_composite_cases.json','utf8'));
let bad=[]; for(const c of cases){const got=classifyRequest(c.prompt).creationTypes.slice().sort(); const exp=c.expected_types.slice().sort(); if(JSON.stringify(got)!==JSON.stringify(exp)) bad.push({id:c.id,got,exp,prompt:c.prompt});}
if(bad.length){console.error(JSON.stringify(bad,null,2));process.exit(1)} console.log(`PASS: ${cases.length}/${cases.length} Revision 1.8.8 routing cases`);"""
p=subprocess.run(['node','--input-type=module','-e',script],cwd=ROOT.parent,text=True,capture_output=True)
if p.returncode:
 print(p.stdout+p.stderr); raise SystemExit('FAIL: Revision 1.8.8 routing corpus')
if len(cases)!=40 or len({c['id'] for c in cases})!=40: raise SystemExit('FAIL: Revision 1.8.8 corpus cardinality/IDs')
print(p.stdout.strip())
print('PASS: Revision 1.8.8 deliverable phrase normalization and modifier-tolerant composite parsing')
