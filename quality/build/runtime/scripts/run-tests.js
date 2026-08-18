#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const RUNTIME_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const testsDir = path.join(RUNTIME_ROOT, 'tests');
const testFiles = fs.readdirSync(testsDir, {withFileTypes:true})
  .filter(entry => entry.isFile() && entry.name.endsWith('.test.js'))
  .map(entry => path.join('tests', entry.name))
  .sort();

if(testFiles.length === 0){
  console.error('RUNTIME TEST FAIL: no tests/*.test.js files found');
  process.exit(1);
}

const result = spawnSync(process.execPath, ['--test', ...testFiles], {
  cwd: RUNTIME_ROOT,
  stdio: 'inherit',
  shell: false
});

if(result.error){
  console.error(`RUNTIME TEST FAIL: ${result.error.message}`);
  process.exit(1);
}
process.exit(result.status ?? 1);
