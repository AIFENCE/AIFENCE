#!/usr/bin/env node
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import fs from 'node:fs';
const args=process.argv.slice(2);const candidates=[];
if(process.env.AIFENCE_RUNTIME_HOME)candidates.push(path.join(process.env.AIFENCE_RUNTIME_HOME,'src','cli.js'));
let d=process.cwd();
for(let i=0;i<8;i++){
  candidates.push(path.join(d,'build','runtime','src','cli.js'),path.join(d,'.aifence-runtime','src','cli.js'),path.join(d,'aifence-runtime','src','cli.js'));
  const up=path.dirname(d);if(up===d)break;d=up;
}
const found=candidates.find(fs.existsSync);
if(found){const r=spawnSync(process.execPath,[found,...args],{stdio:'inherit'});process.exit(r.status??1)}
const r=spawnSync(process.platform==='win32'?'aifence.cmd':'aifence',args,{stdio:'inherit',shell:false});
if(r.error){console.error('AIFENCE Runtime not found. Set AIFENCE_RUNTIME_HOME, run from a AIFENCE repository, or install the aifence CLI.');process.exit(2)}
process.exit(r.status??1);
