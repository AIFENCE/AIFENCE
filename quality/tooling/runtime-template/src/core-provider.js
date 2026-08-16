import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { CORE_ROOT, RUNTIME_ROOT } from './paths.js';
import { readText, parseMetadata, parseCsv, extractSectionById, normalizeName, tableAfterHeading, parseMarkdownTable } from './parser.js';

const TEXT_EXTENSIONS = new Set(['.md','.json','.js','.mjs','.cjs','.txt','.yml','.yaml','.html','.css','.csv','.py','.toml','.xml','.sh','.bat','.ps1']);
function canonicalBytes(p){
  const raw=fs.readFileSync(p);
  const base=path.basename(p);
  if(!(TEXT_EXTENSIONS.has(path.extname(p).toLowerCase()) || base.startsWith('.') || ['LICENSE','NOTICE'].includes(base))) return raw;
  return Buffer.from(raw.toString('utf8').replace(/\r\n?/g,'\n'),'utf8');
}

const SAFE_TOP = /^(?:[A-Z0-9_-]+\.md|control_registry(?:_extension)?\.csv)$/;
const SAFE_SUB = /^(contracts|controls|operations|schemas|evals|benchmarks)\/[A-Za-z0-9._/-]+$/;
function safeRel(rel){ const r=rel.replaceAll('\\','/').replace(/^\.\//,''); if(r.includes('..')) throw new Error('Path traversal rejected'); if(!(SAFE_TOP.test(r)||SAFE_SUB.test(r))) throw new Error(`Unsupported BizIQ path: ${r}`); return r; }

export class CoreProvider {
  constructor(coreRoot=CORE_ROOT){ this.root=coreRoot; this._registry=null; this._profiles=null; this._ops=null; }
  path(rel){ return path.join(this.root, safeRel(rel)); }
  exists(rel){ try{return fs.existsSync(this.path(rel));}catch{return false;} }
  read(rel){ return readText(this.path(rel)); }
  metadata(rel='README.md'){ return parseMetadata(this.read(rel)); }
  revision(){ return this.metadata('README.md')['Control-Plane-Revision'] || 'unknown'; }
  stableSection(rel,id){ const s=extractSectionById(this.read(rel),id); if(!s) throw new Error(`Stable section not found: ${rel}#${id}`); return s; }
  contracts(){ return fs.readdirSync(path.join(this.root,'contracts')).filter(x=>x.endsWith('.md')).sort(); }
  contract(slug){ return this.read(`contracts/${slug.replace(/\.md$/,'')}.md`); }
  module(name){ const n=name.toUpperCase().replace(/\.MD$/,''); return this.read(`${n}.md`); }
  registry(){
    if(this._registry) return this._registry;
    let rows=parseCsv(this.read('control_registry.csv'));
    const dir=path.join(this.root,'control_registry');
    for(const file of fs.readdirSync(dir).filter(x=>x.endsWith('.csv')).sort()) rows=rows.concat(parseCsv(readText(path.join(dir,file))));
    this._registry=rows; return rows;
  }
  getControl(query){
    const q=normalizeName(query); const rows=this.registry();
    let hits=rows.filter(r=>normalizeName(r.id)===q || normalizeName(r.control_id)===q);
    if(!hits.length) hits=rows.filter(r=>normalizeName(r.capability)===q || normalizeName(r.capability_id)===q);
    if(!hits.length) hits=rows.filter(r=>normalizeName(r.capability).includes(q) || normalizeName(r.id).includes(q));
    const grouped={};
    for(const r of hits){ const k=r.capability_id||r.capability; (grouped[k]??=[]).push(r); }
    return Object.entries(grouped).map(([key,controls])=>({key, capability:controls[0].capability, domain:controls[0].domain, shard:controls[0].shard, controls}));
  }
  capability(query){
    const q=normalizeName(query); const rows=this.registry();
    const hit=rows.find(r=>normalizeName(r.capability_id)===q || normalizeName(r.capability)===q);
    if(!hit) return null;
    const controls=rows.filter(r=>(r.capability_id||r.capability)===(hit.capability_id||hit.capability));
    const capabilityId=hit.capability_id||hit.capability;
    let text=null; try{text=this.stableSection(hit.shard,capabilityId);}catch{}
    return {capability:hit.capability,capabilityId,domain:hit.domain,shard:hit.shard,priority:controls.some(x=>x.priority==='P0')?'P0':'P1',controlIds:controls.map(x=>x.id),stableControlIds:controls.map(x=>x.control_id),text};
  }
  capabilityByTerms(terms=[]){
    const qs=terms.map(normalizeName).filter(Boolean); const rows=this.registry(); const seen=new Set(); const out=[];
    for(const r of rows){
      const hay=normalizeName(`${r.capability} ${r.requirement} ${r.target}`);
      if(!qs.some(q=>hay.includes(q))) continue;
      const id=r.capability_id||r.capability; if(seen.has(id))continue; seen.add(id);
      const cap=this.capability(id); if(cap)out.push(cap);
    }
    return out;
  }
  profileRows(){
    if(this._profiles) return this._profiles;
    this._profiles=tableAfterHeading(this.read('PROFILE_MATRIX.md'),'# Industry Matrix').map(r=>Object.fromEntries(Object.entries(r).map(([k,v])=>[k,v.replace(/`/g,'')])));
    return this._profiles;
  }
  operationsRows(){
    if(this._ops) return this._ops;
    const text=this.read('MANIFEST.md');
    const lines=text.split(/\r?\n/); let rows=[];
    for(let i=0;i<lines.length;i++) if(lines[i].startsWith('| Operating Profile |') && lines[i].includes('File')) { const table=[]; for(let j=i;j<lines.length&&lines[j].trim().startsWith('|');j++) table.push(lines[j]); rows=parseMarkdownTable(table); break; }
    this._ops=rows; return rows;
  }
  verifyCoreLock(){
    const lock=JSON.parse(readText(path.join(RUNTIME_ROOT,'CORE_LOCK.json'))); const failures=[]; let checked=0;
    for(const [rel,expected] of Object.entries(lock.files)){
      const p=path.join(this.root,rel); if(!fs.existsSync(p)){failures.push({rel,reason:'missing'});continue;}
      const got=crypto.createHash('sha256').update(canonicalBytes(p)).digest('hex'); checked++; if(got!==expected) failures.push({rel,reason:'hash',expected,got});
    }
    return {ok:failures.length===0,checked,revision:this.revision(),expectedRevision:lock.biziq_revision,failures};
  }
}

