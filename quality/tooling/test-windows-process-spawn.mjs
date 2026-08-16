#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const verify=fs.readFileSync(path.join(ROOT,'tooling','verify-build.mjs'),'utf8');
const build=fs.readFileSync(path.join(ROOT,'tooling','build.mjs'),'utf8');
const runner=fs.readFileSync(path.join(ROOT,'tooling','runtime-template','scripts','run-tests.js'),'utf8');

const failures=[];
if(/shell\s*:\s*true/.test(verify)) failures.push('verify-build.mjs must not use shell:true for Node test launching');
if(/node --test tests\/\*\.test\.js/.test(build)) failures.push('generated Runtime package scripts must not depend on shell wildcard expansion');
if(/shell\s*:\s*true/.test(runner)) failures.push('Runtime test runner must use shell:false');
if(!/spawnSync\(process\.execPath,\s*\['--test',\s*\.\.\.testFiles\]/.test(runner)) failures.push('Runtime test runner must spawn process.execPath with an argument array');
if(!/readdirSync\(testsDir/.test(runner)) failures.push('Runtime test runner must enumerate test files itself');

if(failures.length){
  console.error(`FAIL: ${failures.length} Windows process-launch regression(s)`);
  for(const f of failures) console.error(`- ${f}`);
  process.exit(1);
}
console.log('PASS: Windows-safe Runtime test process launching');
