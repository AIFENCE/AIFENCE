import fs from 'node:fs';
import path from 'node:path';
import { RUNTIME_ROOT } from './paths.js';

const raw = JSON.parse(fs.readFileSync(path.join(RUNTIME_ROOT, 'runtime.config.json'), 'utf8'));
export const config = Object.freeze(raw);
export const RUNTIME_VERSION = raw.runtimeVersion;
export const EXPECTED_CORE_REVISION = raw.coreRevision;
