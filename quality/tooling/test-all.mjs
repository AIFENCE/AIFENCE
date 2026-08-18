#!/usr/bin/env node
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {checkPythonDependencies} from './python-env.mjs';
import {verifyBuild} from './verify-build.mjs';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
function run(command,args,label,env=process.env){
  const r=spawnSync(command,args,{cwd:ROOT,stdio:'inherit',env,shell:false});
  if(r.error){console.error(`TEST FAIL: ${label}: ${r.error.message}`);process.exit(1);}
  if(r.status!==0)process.exit(r.status??1);
}

for(const rel of ['tooling/test-portability.mjs','tooling/test-windows-process-spawn.mjs'])
  run(process.execPath,[path.join(ROOT,rel)],rel);

try{verifyBuild();}catch(error){console.error(`VERIFY FAIL: ${error.message}`);process.exit(1);}

let python;
try{python=checkPythonDependencies().py;}catch(error){console.error(`TEST FAIL: ${error.message}`);process.exit(1);}
const pyEnv={...process.env,PYTHONDONTWRITEBYTECODE:'1'};
for(const rel of ['source/tools/validate_pack.py'])
  run(python.command,[...python.prefix,'-B',path.join(ROOT,rel)],rel,pyEnv);

run(process.execPath,[path.join(ROOT,'tooling/test-wiki.mjs')],'tooling/test-wiki.mjs');

console.log('PASS: complete AIFENCE repository test suite');
