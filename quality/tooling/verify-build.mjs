#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const BUILD=path.join(ROOT,'build');
function sha(p){return crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');}
function fail(message){throw new Error(message);}

export function verifyBuild({runRuntimeTests=true}={}){
  const lockPath=path.join(BUILD,'BUILD_LOCK.json');if(!fs.existsSync(lockPath))fail('build/BUILD_LOCK.json missing; run npm run build');
  const lock=JSON.parse(fs.readFileSync(lockPath,'utf8'));let checked=0;
  for(const [rel,expected] of Object.entries(lock.files)){
    const p=path.join(BUILD,rel);if(!fs.existsSync(p))fail(`missing generated file ${rel}`);if(sha(p)!==expected)fail(`generated file drift ${rel}`);checked++;
  }
  const manifest=JSON.parse(fs.readFileSync(path.join(BUILD,'BUILD_MANIFEST.json'),'utf8'));
  const runtime=JSON.parse(fs.readFileSync(path.join(BUILD,'runtime','runtime.config.json'),'utf8'));
  if(runtime.coreRevision!==manifest.coreRevision)fail('runtime/core revision drift');
  if(runtime.architecture.controls!==manifest.architecture.controls)fail('runtime/control count drift');
  if(runRuntimeTests){
    const testRunner=path.join(BUILD,'runtime','scripts','run-tests.js');if(!fs.existsSync(testRunner))fail('runtime test runner missing');
    const test=spawnSync(process.execPath,[testRunner],{cwd:path.join(BUILD,'runtime'),shell:false,encoding:'utf8'});
    process.stdout.write(test.stdout||'');process.stderr.write(test.stderr||'');
    if(test.error)fail(`runtime test launcher failed: ${test.error.message}`);if(test.status!==0)fail('runtime tests failed');
  }
  console.log(`PASS: generated build lock verified (${checked} files)`);
  if(runRuntimeTests)console.log(`PASS: Runtime tests for Core ${manifest.coreRevision}`);
  return {checked,coreRevision:manifest.coreRevision,runtimeVersion:manifest.runtimeVersion};
}

const isMain=process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(isMain){
  try{verifyBuild();}catch(error){console.error('VERIFY FAIL:',error.message);process.exit(1);}
}
