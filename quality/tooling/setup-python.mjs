#!/usr/bin/env node
import {checkPythonDependencies, installPythonDependencies} from './python-env.mjs';

try {
  installPythonDependencies();
  const checked = checkPythonDependencies();
  console.log('PASS: BizIQ Python validation environment ready');
  if(checked.versions) console.log(checked.versions);
} catch (error) {
  console.error(`SETUP FAIL: ${error.message}`);
  process.exit(1);
}
