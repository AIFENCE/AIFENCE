#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const WIKI=path.join(ROOT,'build','wiki');
const die=m=>{console.error('WIKI TEST FAIL:',m);process.exit(1)};
for(const rel of ['index.html','assets/styles.css','assets/app.js','wiki-index.json','.nojekyll']) if(!fs.existsSync(path.join(WIKI,rel))) die(`missing build/wiki/${rel}`);
let data; try{data=JSON.parse(fs.readFileSync(path.join(WIKI,'wiki-index.json'),'utf8'));}catch(e){die(`wiki-index.json invalid: ${e.message}`)}
const manifest=JSON.parse(fs.readFileSync(path.join(ROOT,'build','BUILD_MANIFEST.json'),'utf8'));
if(data.meta.coreRevision!==manifest.coreRevision) die('Core revision drift');
if(data.meta.runtimeVersion!==manifest.runtimeVersion) die('Runtime version drift');
if(data.meta.controls!==manifest.architecture.controls) die('control-count drift');
if(data.meta.documents!==manifest.source.documents) die('source-document count drift');
const slugs=new Set();
for(const doc of data.documents){
  if(!doc.slug||slugs.has(doc.slug)) die(`duplicate/missing slug ${doc.slug}`); slugs.add(doc.slug);
  if(!doc.contentPath?.startsWith('./content/')) die(`invalid content path ${doc.slug}`);
  const p=path.join(WIKI,doc.contentPath.replace(/^\.\//,'')); if(!fs.existsSync(p)) die(`missing content for ${doc.slug}: ${doc.contentPath}`);
}
for(const group of data.navigation) for(const item of group.items) if(!slugs.has(item.slug)) die(`navigation target missing: ${item.slug}`);
for(const required of ['getting-started','repository-layout','source-readme','artifact-contracts','feature-compiler','operations-compiler','quality-floors']) if(!slugs.has(required)) die(`required wiki route missing: ${required}`);
const html=fs.readFileSync(path.join(WIKI,'index.html'),'utf8');
if(!html.includes('Search documentation')||!html.includes('sidebar')||!html.includes('themeButton')) die('wiki shell missing core UX controls');
const css=fs.readFileSync(path.join(WIKI,'assets','styles.css'),'utf8');
if(!css.includes('@media (max-width: 620px)')||!css.includes(':focus-visible')) die('responsive/accessibility styles missing');
const js=path.join(WIKI,'assets','app.js'); const check=spawnSync(process.execPath,['--check',js],{encoding:'utf8',shell:false});
if(check.status!==0){process.stdout.write(check.stdout||'');process.stderr.write(check.stderr||'');die('wiki app JavaScript syntax invalid');}
console.log(`PASS: source-driven BizIQ wiki (${data.documents.length} indexed pages, ${data.navigation.reduce((n,g)=>n+g.items.length,0)} curated navigation entries)`);
