import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

export const RUNTIME_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const REPO_ROOT = path.resolve(RUNTIME_ROOT, '..', '..');
export const REPO_SOURCE_ROOT = path.join(REPO_ROOT, 'source');
export const BUNDLED_CORE_ROOT = path.join(RUNTIME_ROOT, 'core');
const envCore = process.env.AIFENCE_SOURCE_DIR ? path.resolve(process.env.AIFENCE_SOURCE_DIR) : null;
export const CORE_ROOT = envCore || (fs.existsSync(path.join(BUNDLED_CORE_ROOT,'README.md')) ? BUNDLED_CORE_ROOT : REPO_SOURCE_ROOT);
export const SKILL_ROOT = path.join(RUNTIME_ROOT, 'skill', 'aifence');
export const UI_FILE = path.join(RUNTIME_ROOT, 'ui', 'dashboard.html');
