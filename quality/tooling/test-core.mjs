#!/usr/bin/env node
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {checkPythonDependencies} from './python-env.mjs';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
let python;
try { python=checkPythonDependencies().py; }
catch(error){ console.error(`TEST FAIL: ${error.message}`); process.exit(1); }
const env={...process.env,PYTHONDONTWRITEBYTECODE:'1'};
for(const rel of ['source/tools/validate_pack.py','source/tools/test_revision_1_7.py','source/tools/test_revision_1_8.py','source/tools/test_revision_1_8_1.py','source/tools/test_revision_1_8_2.py','source/tools/test_revision_1_8_3.py','source/tools/test_revision_1_8_4.py','source/tools/test_revision_1_8_5.py','source/tools/test_revision_1_8_6.py','source/tools/test_revision_1_8_7.py','source/tools/test_revision_1_8_8.py']){
  const r=spawnSync(python.command,[...python.prefix,'-B',path.join(ROOT,rel)],{cwd:ROOT,encoding:'utf8',env});
  process.stdout.write(r.stdout||'');process.stderr.write(r.stderr||'');
  if(r.status!==0) process.exit(r.status??1);
}
