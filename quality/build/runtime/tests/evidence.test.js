import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {plan,validate} from '../src/runtime-api.js';

function fixture(dir,request='Create a payments operations dashboard.'){
  const p=plan(request);const ep=p.evidencePlan[0];
  const manifest={artifact_id:ep.artifactId,generated_before_final_acceptance:true,controls:[
    {id:'period-30d',label:'30 day period',expected_behavior:'changes visible period state',enabled:true,priority:'P1',required_viewports:[320,390,768,1440]},
    {id:'more-actions',label:'More actions',expected_behavior:'opens contextual action menu',enabled:true,priority:'P1',required_viewports:[320,390,768,1440]}
  ],tasks:[
    {id:'inspect-transaction-recover',description:'Inspect a transaction and open recovery actions',priority:'P0',required_viewports:[320,390,768,1440],completion_definition:'transaction detail and recovery action are reachable',recovery_required:true,desktop_surface:'side inspector',mobile_equivalent:'full-screen transaction detail sheet'}
  ]};
  const records=ep.checks.map(check=>({artifact_id:ep.artifactId,profile:ep.profile,evidence_type:check,result:'PASS',observations:['executed fixture'],artifacts:[],hashes:{},provenance:'direct'}));
  const ctrl=records.find(x=>x.evidence_type==='interactive control closure');ctrl.details={discoveredEnabledControlIds:['period-30d','more-actions'],accountedControlIds:['period-30d','more-actions'],exercisedControlIds:['period-30d','more-actions'],deadControlIds:[]};
  const mobile=records.find(x=>x.evidence_type==='mobile task preservation');mobile.details={taskResults:[320,390].map(viewport=>({taskId:'inspect-transaction-recover',viewport,result:'PASS',entryReachable:true,completionReachable:true,statePreserved:true,recoveryStatus:'PASS'}))};
  const planFile=path.join(dir,'plan.json'),manifestFile=path.join(dir,'manifest.json'),evidenceFile=path.join(dir,'evidence.json');
  fs.writeFileSync(planFile,JSON.stringify(p));fs.writeFileSync(manifestFile,JSON.stringify(manifest));fs.writeFileSync(evidenceFile,JSON.stringify(records));
  return {p,records,manifest,planFile,manifestFile,evidenceFile};
}

test('direct exhaustive control and mobile-task evidence can satisfy release-critical plan',()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'biziq-evidence-'));try{const x=fixture(dir);const result=validate({target:'evidence',file:x.evidenceFile,plan:x.planFile,interactionManifest:x.manifestFile});assert.equal(result.ok,true,result.stderr||result.stdout);}finally{fs.rmSync(dir,{recursive:true,force:true});}
});

test('required interaction closure fails without manifest',()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'biziq-evidence-'));try{const x=fixture(dir);const result=validate({target:'evidence',file:x.evidenceFile,plan:x.planFile});assert.equal(result.ok,false);assert.match(result.stdout,/requires interaction-closure manifest/);}finally{fs.rmSync(dir,{recursive:true,force:true});}
});

test('dead enabled controls fail exhaustive closure',()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'biziq-evidence-'));try{const x=fixture(dir);const records=JSON.parse(fs.readFileSync(x.evidenceFile));const ctrl=records.find(r=>r.evidence_type==='interactive control closure');ctrl.details.exercisedControlIds=['period-30d'];ctrl.details.deadControlIds=['more-actions'];fs.writeFileSync(x.evidenceFile,JSON.stringify(records));const result=validate({target:'evidence',file:x.evidenceFile,plan:x.planFile,interactionManifest:x.manifestFile});assert.equal(result.ok,false);assert.match(result.stdout,/dead enabled controls block PASS/);}finally{fs.rmSync(dir,{recursive:true,force:true});}
});

test('mobile task loss at 320 fails even when generic responsive evidence passes',()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'biziq-evidence-'));try{const x=fixture(dir);const records=JSON.parse(fs.readFileSync(x.evidenceFile));const mobile=records.find(r=>r.evidence_type==='mobile task preservation');mobile.details.taskResults=mobile.details.taskResults.map(r=>r.viewport===320?{...r,result:'FAIL',completionReachable:false,recoveryStatus:'FAIL'}:r);fs.writeFileSync(x.evidenceFile,JSON.stringify(records));const result=validate({target:'evidence',file:x.evidenceFile,plan:x.planFile,interactionManifest:x.manifestFile});assert.equal(result.ok,false);assert.match(result.stdout,/mobile task did not preserve/);}finally{fs.rmSync(dir,{recursive:true,force:true});}
});

test('inferred PASS evidence is rejected',()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'biziq-evidence-'));try{const evidenceFile=path.join(dir,'evidence.json');fs.writeFileSync(evidenceFile,JSON.stringify({artifact_id:'artifact-1',profile:'browser',evidence_type:'viewport captures',result:'PASS',observations:[],artifacts:[],hashes:{},provenance:'inferred'}));const result=validate({target:'evidence',file:evidenceFile});assert.equal(result.ok,false);}finally{fs.rmSync(dir,{recursive:true,force:true});}
});


test('runtime-discovered control omitted from manifest fails closure',()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'biziq-evidence-'));try{const x=fixture(dir);const records=JSON.parse(fs.readFileSync(x.evidenceFile));const ctrl=records.find(r=>r.evidence_type==='interactive control closure');ctrl.details.discoveredEnabledControlIds.push('undeclared-nav');fs.writeFileSync(x.evidenceFile,JSON.stringify(records));const result=validate({target:'evidence',file:x.evidenceFile,plan:x.planFile,interactionManifest:x.manifestFile});assert.equal(result.ok,false);assert.match(result.stdout,/runtime discovered enabled controls omitted from manifest|evidence references controls absent from manifest/);}finally{fs.rmSync(dir,{recursive:true,force:true});}
});


test('generation preflight rejects reserved-keyword DOM-global JavaScript syntax failure',()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'biziq-preflight-'));try{
    const html=path.join(dir,'index.html');const runtime=path.join(dir,'runtime.json');
    fs.writeFileSync(html,'<!doctype html><button id="export">Export</button><script>export.onclick=()=>1</script>');
    fs.writeFileSync(runtime,JSON.stringify({provenance:'direct',result:'PASS',document_loaded:true,page_errors:[],console_errors:[],failed_required_resources:[]}));
    const result=validate({target:'generation-preflight',file:html,plan:runtime});assert.equal(result.ok,false);assert.match(result.stdout+result.stderr,/syntax\/parser preflight failed|SyntaxError/);
  }finally{fs.rmSync(dir,{recursive:true,force:true});}
});

test('generation preflight fails closed when JavaScript has no direct runtime evidence',()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'biziq-preflight-'));try{
    const html=path.join(dir,'index.html');fs.writeFileSync(html,'<!doctype html><button id="x">X</button><script>const xButton=document.getElementById("x");xButton.onclick=()=>document.body.dataset.ok="1";</script>');
    const result=validate({target:'generation-preflight',file:html});assert.equal(result.ok,false);assert.match(result.stdout,/requires direct runtime-preflight evidence/);
  }finally{fs.rmSync(dir,{recursive:true,force:true});}
});

test('generation preflight rejects clean syntax with direct runtime initialization error',()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'biziq-preflight-'));try{
    const html=path.join(dir,'index.html'),runtime=path.join(dir,'runtime.json');fs.writeFileSync(html,'<!doctype html><script>const ok=1;</script>');
    fs.writeFileSync(runtime,JSON.stringify({provenance:'direct',result:'FAIL',document_loaded:true,page_errors:['ReferenceError: missingSymbol is not defined'],console_errors:[],failed_required_resources:[]}));
    const result=validate({target:'generation-preflight',file:html,plan:runtime});assert.equal(result.ok,false);assert.match(result.stdout,/runtime initialization\/load preflight failed/);
  }finally{fs.rmSync(dir,{recursive:true,force:true});}
});

test('generation preflight accepts parsed JavaScript with clean direct runtime evidence',()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'biziq-preflight-'));try{
    const html=path.join(dir,'index.html'),runtime=path.join(dir,'runtime.json');fs.writeFileSync(html,'<!doctype html><button id="export">Export</button><script>const exportButton=document.getElementById("export");exportButton.onclick=()=>document.body.dataset.ok="1";</script>');
    fs.writeFileSync(runtime,JSON.stringify({provenance:'direct',result:'PASS',document_loaded:true,page_errors:[],console_errors:[],failed_required_resources:[]}));
    const result=validate({target:'generation-preflight',file:html,plan:runtime});assert.equal(result.ok,true,result.stdout+result.stderr);
  }finally{fs.rmSync(dir,{recursive:true,force:true});}
});
