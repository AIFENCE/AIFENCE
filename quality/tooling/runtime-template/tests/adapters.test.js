import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import os from 'node:os';import {RUNTIME_ROOT} from '../src/paths.js';import {install} from '../src/installer.js';
for(const rel of ['adapters/claude-code/.claude-plugin/plugin.json','adapters/claude-code/.mcp.json','adapters/gemini-cli/gemini-extension.json','adapters/vscode-copilot/mcp.json','adapters/cursor/mcp.json'])test(`valid JSON ${rel}`,()=>assert.doesNotThrow(()=>JSON.parse(fs.readFileSync(path.join(RUNTIME_ROOT,rel),'utf8'))));
test('project installer dry run touches only project paths',()=>{const p=fs.mkdtempSync(path.join(os.tmpdir(),'biziq-install-'));const x=install('all',{project:p,dryRun:true});assert.equal(x.ok,true);assert.ok(x.changed.every(f=>path.resolve(f).startsWith(path.resolve(p))));assert.equal(fs.readdirSync(p).length,0)});
test('project installer merges without clobbering existing config',()=>{const p=fs.mkdtempSync(path.join(os.tmpdir(),'biziq-install-'));fs.mkdirSync(path.join(p,'.vscode'));fs.writeFileSync(path.join(p,'.vscode','mcp.json'),JSON.stringify({servers:{existing:{type:'http',url:'https://example.invalid'}}}));install('vscode',{project:p});const j=JSON.parse(fs.readFileSync(path.join(p,'.vscode','mcp.json')));assert.ok(j.servers.existing);assert.ok(j.servers.biziq);assert.ok(fs.existsSync(path.join(p,'.vscode','mcp.json.biziq-backup')))});

test('install all mutates only project-scoped adapter namespaces and preserves existing JSON', () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'biziq-install-all-'));
  try {
    fs.mkdirSync(path.join(tmp, '.cursor'), { recursive: true });
    fs.writeFileSync(path.join(tmp, '.cursor', 'mcp.json'), JSON.stringify({ mcpServers: { existing: { command: 'keep-me' } }, untouched: true }, null, 2));
    const result = install('all', { project: tmp, dryRun: false });
    assert.equal(result.ok, true);
    assert.ok(fs.existsSync(path.join(tmp, '.agents', 'skills', 'biziq', 'SKILL.md')));
    assert.ok(fs.existsSync(path.join(tmp, '.claude', 'skills', 'biziq', 'SKILL.md')));
    assert.ok(fs.existsSync(path.join(tmp, '.mcp.json')));
    assert.ok(fs.existsSync(path.join(tmp, '.gemini', 'settings.json')));
    assert.ok(fs.existsSync(path.join(tmp, '.vscode', 'mcp.json')));
    const cursor = JSON.parse(fs.readFileSync(path.join(tmp, '.cursor', 'mcp.json'), 'utf8'));
    assert.equal(cursor.mcpServers.existing.command, 'keep-me');
    assert.equal(cursor.untouched, true);
    assert.ok(cursor.mcpServers.biziq.command);
    assert.ok(fs.existsSync(path.join(tmp, '.cursor', 'mcp.json.biziq-backup')));
    const backup = JSON.parse(fs.readFileSync(path.join(tmp, '.cursor', 'mcp.json.biziq-backup'), 'utf8'));
    assert.equal(backup.mcpServers.existing.command, 'keep-me');
    assert.equal(backup.mcpServers.biziq, undefined);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
