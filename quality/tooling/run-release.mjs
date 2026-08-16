#!/usr/bin/env node
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {resolvePython} from './python-env.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
try {
  const python = resolvePython();
  const result = spawnSync(
    python.command,
    [...python.prefix, path.join(ROOT, 'tooling', 'release.py')],
    {cwd:ROOT, stdio:'inherit', env:process.env}
  );
  process.exit(result.status ?? 1);
} catch(error) {
  console.error(`RELEASE FAIL: ${error.message}`);
  process.exit(1);
}
