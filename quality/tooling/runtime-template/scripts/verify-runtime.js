#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { RUNTIME_ROOT } from '../src/paths.js';

const lockPath = path.join(RUNTIME_ROOT, 'RUNTIME_LOCK.json');
if (!fs.existsSync(lockPath)) {
  console.error('FAIL: RUNTIME_LOCK.json is missing.');
  process.exit(2);
}
const lock = JSON.parse(fs.readFileSync(lockPath, 'utf8'));
const failures = [];
let checked = 0;
for (const [rel, expected] of Object.entries(lock.files || {})) {
  const file = path.join(RUNTIME_ROOT, rel);
  if (!fs.existsSync(file)) {
    failures.push({ rel, reason: 'missing' });
    continue;
  }
  const got = crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
  checked++;
  if (got !== expected) failures.push({ rel, reason: 'hash', expected, got });
}
if (failures.length) {
  console.error(`FAIL: Runtime lock mismatches: ${failures.length}`);
  for (const f of failures.slice(0, 20)) console.error(JSON.stringify(f));
  process.exit(1);
}
console.log(`PASS: AIFENCE Runtime lock verified (${checked} files).`);
