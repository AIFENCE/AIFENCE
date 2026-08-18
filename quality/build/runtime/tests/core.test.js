import {EXPECTED_CORE_REVISION} from '../src/config.js';import test from 'node:test';import assert from 'node:assert/strict';import {CoreProvider} from '../src/core-provider.js';
const c=new CoreProvider();test('core hash lock and revision',()=>{const v=c.verifyCoreLock();assert.equal(v.ok,true);assert.equal(v.revision, EXPECTED_CORE_REVISION);assert.ok(v.checked>100)});test('control registry is complete',()=>{const r=c.registry();assert.equal(r.length,1300);assert.equal(r[0].id,'BQ-0001');assert.equal(r.at(-1).id,'BQ-1300')});test('stable section retrieval works',()=>{const s=c.stableSection('controls/31-operational-procedure-compilation-authority-and-measurement.md','controls.capability.operational-context-resolution');assert.match(s,/BQ-1251/)});

test('CoreProvider rejects traversal and unsupported paths', () => {
  const core = new CoreProvider();
  assert.throws(() => core.read('../README.md'), /traversal/i);
  assert.throws(() => core.read('/etc/passwd'), /Unsupported BizIQ path|traversal/i);
  assert.throws(() => core.read('src/cli.js'), /Unsupported BizIQ path/i);
});
