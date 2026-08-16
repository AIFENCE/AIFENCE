import { spawnSync } from 'node:child_process';
import path from 'node:path';
import fs from 'node:fs';
import { CoreProvider } from './core-provider.js';
import { BizIQRouter } from './router.js';
import { CORE_ROOT } from './paths.js';
import { RUNTIME_VERSION } from './config.js';

export const core=new CoreProvider();
export const router=new BizIQRouter(core);
export function status(){ const v=core.verifyCoreLock(); const rows=core.registry(); const domains=new Set(rows.map(r=>r.domain).filter(Boolean)); const capabilities=new Set(rows.map(r=>r.capability_id||`${r.domain}:${r.capability}`).filter(Boolean)); return {runtimeVersion:RUNTIME_VERSION,coreRevision:core.revision(),coreIntegrity:v.ok?'PASS':'FAIL',coreFilesChecked:v.checked,domains:domains.size,capabilities:capabilities.size,controls:rows.length}; }
export function plan(request,hints={}){return router.plan(request,hints);}
export function getSections(items){ return items.map(i=>{
  if(i.id) return {path:i.path,id:i.id,text:core.stableSection(i.path,i.id)};
  return {path:i.path,text:core.read(i.path)};
 }); }
export function getCapability(query){ const cap=core.capability(query); return cap?{...cap,text:cap.text||null}:null; }
export function getControl(query){ const groups=core.getControl(query); return groups.map(g=>({...g,section:(()=>{try{return core.stableSection(g.shard,g.key)}catch{return null}})()})); }
export function getContract(slug){return {slug:slug.replace(/\.md$/,''),text:core.contract(slug)};}
export function getProfile(industry){ const q=industry.toLowerCase(); const rows=core.profileRows(); const exact=rows.find(r=>(r.Industry||'').toLowerCase()===q || (r['Industry ID']||'').toLowerCase()===q); const fuzzy=exact||rows.find(r=>(r.Industry||'').toLowerCase().includes(q)); return fuzzy||null; }
export function evidenceContract(){return {module:'EVIDENCE_ADAPTER.md',schema:'schemas/execution_evidence.schema.json',interactionManifestSchema:'schemas/interaction_closure_manifest.schema.json',generationPreflightSchema:'schemas/generation_preflight_evidence.schema.json',text:core.read('EVIDENCE_ADAPTER.md')};}
export function compiler(kind){ const map={feature:'FEATURE_COMPILER.md',component:'COMPONENT_COMPILER.md',operation:'OPERATIONAL_PROCEDURE_COMPILER.md'}; const file=map[kind]; if(!file) throw new Error('compiler kind must be feature, component, or operation'); return {kind,file,text:core.read(file)}; }
function python(){for(const cmd of ['python','python3']){const x=spawnSync(cmd,['--version'],{encoding:'utf8'});if(x.status===0)return cmd;}return null;}
export function validate({target='core',file=null,plan=null,interactionManifest=null}={}){
 const py=python(); if(!py) return {ok:false,target,error:'Python not found; core validators require Python.'};
 let args;
 if(target==='core') args=[path.join(CORE_ROOT,'tools','validate_pack.py')];
 else if(target==='operation'){ if(!file) return {ok:false,target,error:'operation validation requires file'}; args=[path.join(CORE_ROOT,'tools','validate_operational_procedure.py'),path.resolve(file)]; }
 else if(target==='operations-regressions') args=[path.join(CORE_ROOT,'tools','test_operations_2.py')];
 else if(target==='generation-preflight'){ if(!file) return {ok:false,target,error:'generation-preflight validation requires artifact file'}; const extra=plan?['--runtime-evidence',path.resolve(plan)]:[]; args=[path.join(CORE_ROOT,'tools','validate_generation_preflight.py'),path.resolve(file),...extra]; }
 else if(target==='interaction-manifest'){ if(!file) return {ok:false,target,error:'interaction-manifest validation requires file'}; args=[path.join(CORE_ROOT,'tools','validate_interaction_manifest.py'),path.resolve(file)]; }
 else if(target==='evidence'){ if(!file) return {ok:false,target,error:'evidence validation requires file'}; args=[path.join(CORE_ROOT,'tools','validate_execution_evidence.py'),path.resolve(file),...(plan?['--plan',path.resolve(plan)]:[]),...(interactionManifest?['--interaction-manifest',path.resolve(interactionManifest)]:[])]; }
 else return {ok:false,target,error:'target must be core, operation, operations-regressions, generation-preflight, interaction-manifest, or evidence'};
 const r=spawnSync(py,args,{cwd:CORE_ROOT,encoding:'utf8'}); return {ok:r.status===0,target,exitCode:r.status,stdout:r.stdout,stderr:r.stderr};
}
