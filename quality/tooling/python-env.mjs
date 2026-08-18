import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const REQUIREMENTS = path.join(ROOT, 'source', 'requirements.txt');

export function resolvePython(){
  const candidates = process.env.PYTHON
    ? [process.env.PYTHON]
    : (process.platform === 'win32' ? ['python', 'py'] : ['python3', 'python']);
  for(const candidate of candidates){
    const args = candidate === 'py' ? ['-3', '--version'] : ['--version'];
    const result = spawnSync(candidate, args, {encoding:'utf8'});
    if(result.status === 0) return {command:candidate, prefix:candidate === 'py' ? ['-3'] : []};
  }
  throw new Error('Python 3 was not found. Install Python 3.12+ or set the PYTHON environment variable.');
}

export function checkPythonDependencies(){
  const py = resolvePython();
  const code = [
    "import importlib.metadata as md",
    "import jsonschema, referencing",
    "print('jsonschema=' + md.version('jsonschema'))",
    "print('referencing=' + md.version('referencing'))",
  ].join(';');
  const result = spawnSync(py.command, [...py.prefix, '-c', code], {encoding:'utf8'});
  if(result.status !== 0){
    const detail = (result.stderr || result.stdout || '').trim();
    const error = new Error(
      `AIFENCE Python validation dependencies are missing or unusable.\n` +
      `Run: npm run setup:python\n` +
      `Requirements: source/requirements.txt` +
      (detail ? `\nPython detail: ${detail.split(/\r?\n/).at(-1)}` : '')
    );
    error.code = 'AIFENCE_PYTHON_DEPS';
    throw error;
  }
  return {py, versions:(result.stdout || '').trim()};
}

export function installPythonDependencies(){
  const py = resolvePython();
  const result = spawnSync(
    py.command,
    [...py.prefix, '-m', 'pip', 'install', '--disable-pip-version-check', '-r', REQUIREMENTS],
    {cwd:ROOT, stdio:'inherit'}
  );
  if(result.status !== 0) throw new Error(`Python dependency installation failed with exit code ${result.status ?? 'unknown'}.`);
  return py;
}
