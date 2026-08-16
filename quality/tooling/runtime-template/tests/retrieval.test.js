import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {RUNTIME_ROOT} from '../src/paths.js';
import {CoreProvider} from '../src/core-provider.js';
import {BizIQRouter} from '../src/router.js';

const core=new CoreProvider();
const router=new BizIQRouter();

test('generated capability shards cover every registry capability',()=>{
  const registry=core.registry();
  const unique=[...new Map(registry.map(x=>[x.capability_id,x])).values()];
  const dir=path.join(RUNTIME_ROOT,'capability-shards');
  const files=fs.readdirSync(dir).filter(x=>x.endsWith('.md'));
  assert.equal(files.length,unique.length);
  for(const cap of unique.slice(0,10)){
    const file=path.join(dir,`${cap.capability_id}.md`);
    assert.ok(fs.existsSync(file),cap.capability_id);
    assert.match(fs.readFileSync(file,'utf8'),new RegExp(cap.capability_id.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')));
  }
});

test('capability lookup resolves exact stable section and controls',()=>{
  const cap=core.capability('controls.capability.operational-context-resolution');
  assert.equal(cap.capabilityId,'controls.capability.operational-context-resolution');
  assert.ok(cap.text.includes('BQ-1251'));
  assert.ok(Array.isArray(cap.controlIds));
  assert.ok(cap.controlIds.length>0);
});

test('normal plans retrieve stable sections instead of whole modules',()=>{
  for(const request of [
    'Create a premium production website for a landscaping company.',
    'Create a Stripe-like payments dashboard concept.',
    'Create a native iOS banking app with login and payments.'
  ]){
    const plan=router.plan(request);
    assert.ok(plan.retrievalActions.length>0,request);
    assert.equal(plan.retrievalActions.some(x=>x.kind==='module'),false,request);
    assert.ok(plan.retrievalBudget.stableSectionChars < plan.retrievalBudget.wholeModuleChars,request);
    assert.ok(plan.retrievalBudget.reductionRatio>0.5,request);
  }
});

test('contract inheritance remains explicit and deterministic',()=>{
  const local=router.plan('Create a production website for a landscaping company.');
  assert.deepEqual(local.artifactContracts[0].contractChain.slice(0,2),['marketing-website','local-service-website']);
  const fixed=router.plan('Create a print-ready PDF report.');
  assert.deepEqual(fixed.artifactContracts[0].contractChain.slice(0,2),['document-report','fixed-format-document']);
});
