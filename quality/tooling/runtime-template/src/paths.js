import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const RUNTIME_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const CORE_ROOT = path.join(RUNTIME_ROOT, 'core');
export const SKILL_ROOT = path.join(RUNTIME_ROOT, 'skill', 'aifence');
export const UI_FILE = path.join(RUNTIME_ROOT, 'ui', 'dashboard.html');
