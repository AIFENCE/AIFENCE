#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {checkPythonDependencies} from './python-env.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SOURCE = path.join(ROOT, 'source');
const BUILD = path.join(ROOT, 'build');
const RUNTIME_TEMPLATE = path.join(ROOT, 'tooling', 'runtime-template');
const SKILL_TEMPLATE = path.join(ROOT, 'tooling', 'templates', 'skill');
const ADAPTER_TEMPLATE = path.join(ROOT, 'tooling', 'templates', 'adapters');
const WIKI_TEMPLATE = path.join(ROOT, 'tooling', 'wiki-template');
const args = new Set(process.argv.slice(2));
const quiet = args.has('--quiet');
const noValidate = args.has('--no-validate');

function log(...x){ if(!quiet) console.log(...x); }
function trace(...x){ if(process.env.AIFENCE_TRACE) console.error('[build-trace]',...x); }
function fail(msg){ console.error(`BUILD FAIL: ${msg}`); process.exit(1); }
function read(p){ return fs.readFileSync(p, 'utf8'); }
function write(p, text){ fs.mkdirSync(path.dirname(p), {recursive:true}); fs.writeFileSync(p, text); }
function writeJson(p, obj){ write(p, JSON.stringify(obj, null, 2) + '\n'); }
const TEXT_EXTENSIONS = new Set(['.md','.json','.js','.mjs','.cjs','.txt','.yml','.yaml','.html','.css','.csv','.py','.toml','.xml','.sh','.bat','.ps1']);
function isTextPath(p){ const base=path.basename(p); return TEXT_EXTENSIONS.has(path.extname(p).toLowerCase()) || base.startsWith('.') || ['LICENSE','NOTICE'].includes(base); }
function canonicalBytes(p){
  const raw=fs.readFileSync(p);
  if(!isTextPath(p)) return raw;
  // Git repositories can normalize CRLF/CR text to LF on checkout. Build identity
  // therefore hashes canonical text bytes rather than platform-specific checkout bytes.
  return Buffer.from(raw.toString('utf8').replace(/\r\n?/g,'\n'),'utf8');
}
function sha(p){ return crypto.createHash('sha256').update(canonicalBytes(p)).digest('hex'); }
function rel(p, base=ROOT){ return path.relative(base,p).replaceAll(path.sep,'/'); }
function copyDir(src,dst){ fs.cpSync(src,dst,{recursive:true,force:true}); }
function walk(dir){
  const out=[];
  for(const entry of fs.readdirSync(dir,{withFileTypes:true})){
    const p=path.join(dir,entry.name);
    if(entry.isDirectory()) out.push(...walk(p)); else if(entry.isFile()) out.push(p);
  }
  return out.sort();
}
function purgeTransient(dir){
  if(!fs.existsSync(dir)) return;
  for(const entry of fs.readdirSync(dir,{withFileTypes:true})){
    const p=path.join(dir,entry.name);
    if(entry.isDirectory() && ['__pycache__','.pytest_cache','.cache'].includes(entry.name)){fs.rmSync(p,{recursive:true,force:true});continue;}
    if(entry.isDirectory()) purgeTransient(p);
    else if(/\.(?:pyc|pyo)$/.test(entry.name)) fs.rmSync(p,{force:true});
  }
}
function metadata(text){
  const m=text.match(/^<!--\s*\n([\s\S]*?)\n-->/);
  const out={};
  if(!m) return out;
  for(const line of m[1].split(/\r?\n/)){
    const i=line.indexOf(':'); if(i<0) continue;
    out[line.slice(0,i).trim()]=line.slice(i+1).trim();
  }
  return out;
}
function headings(text){
  const lines=text.split(/\r?\n/); const out=[];
  for(let i=0;i<lines.length;i++){
    const hm=lines[i].match(/^(#{1,6})\s+(.+?)\s*$/); if(!hm) continue;
    let id=null;
    for(let j=i+1;j<Math.min(lines.length,i+5);j++){
      const im=lines[j].match(/<!--\s*id:\s*([^\s]+)\s*-->/); if(im){id=im[1];break;}
      if(/^#{1,6}\s+/.test(lines[j])) break;
    }
    out.push({level:hm[1].length,title:hm[2].trim(),id,line:i+1});
  }
  return out;
}
function extractSection(text,title){
  const lines=text.split(/\r?\n/); let start=-1, level=0;
  for(let i=0;i<lines.length;i++){
    const m=lines[i].match(/^(#{1,6})\s+(.+?)\s*$/);
    if(m && m[2].trim().toLowerCase()===title.toLowerCase()){ start=i; level=m[1].length; break; }
  }
  if(start<0) return '';
  let end=lines.length;
  for(let i=start+1;i<lines.length;i++){
    const m=lines[i].match(/^(#{1,6})\s+/); if(m && m[1].length<=level){end=i;break;}
  }
  return lines.slice(start,end).join('\n').trim();
}
function extractStableSection(text,id){
  const marker=`<!-- id: ${id} -->`; const pos=text.indexOf(marker); if(pos<0) return '';
  const before=text.slice(0,pos); const matches=[...before.matchAll(/^(#{1,6})\s+(.+)$/gm)];
  if(!matches.length) return '';
  const head=matches.at(-1); const level=head[1].length; const start=head.index;
  const rest=text.slice(pos+marker.length); const re=new RegExp(`^#{1,${level}}\\s+.+$`,'m'); const next=re.exec(rest);
  const end=next ? pos+marker.length+next.index : text.length;
  return text.slice(start,end).trim();
}
function parseCsv(text){
  const rows=[]; let row=[], cell='', quoted=false;
  for(let i=0;i<text.length;i++){
    const c=text[i];
    if(quoted){
      if(c==='"' && text[i+1]==='"'){cell+='"';i++;}
      else if(c==='"') quoted=false; else cell+=c;
    } else {
      if(c==='"') quoted=true;
      else if(c===','){row.push(cell);cell='';}
      else if(c==='\n'){row.push(cell.replace(/\r$/,'')); rows.push(row); row=[]; cell='';}
      else cell+=c;
    }
  }
  if(cell.length||row.length){row.push(cell);rows.push(row);}
  const header=rows.shift()||[];
  return rows.filter(r=>r.some(x=>x!=='')).map(r=>Object.fromEntries(header.map((h,i)=>[h,r[i]??''])));
}
function render(text,vars){
  return text.replace(/\{\{([A-Z0-9_]+)\}\}/g,(_,k)=>String(vars[k]??`{{${k}}}`));
}
function copyRendered(src,dst,vars){
  for(const p of walk(src)){
    const r=rel(p,src); const target=path.join(dst,r);
    const ext=path.extname(p).toLowerCase();
    const textual=['.md','.json','.js','.mjs','.txt','.yml','.yaml','.html','.css'].includes(ext) || path.basename(p).startsWith('.');
    fs.mkdirSync(path.dirname(target),{recursive:true});
    if(textual) fs.writeFileSync(target, render(read(p),vars)); else fs.copyFileSync(p,target);
  }
}

function firstHeading(text, fallback='Document'){
  const h=text.match(/^#\s+(.+?)\s*$/m); return h ? h[1].replace(/[`*_]/g,'').trim() : fallback;
}
function plainSummary(text, limit=190){
  const clean=text.replace(/<!--([\s\S]*?)-->/g,'').replace(/```[\s\S]*?```/g,' ').split(/\r?\n/).filter(line=>{
    const t=line.trim(); return t && !/^#{1,6}\s/.test(t) && !/^[-|]?[|:-]{3,}/.test(t) && !/^\|/.test(t);
  }).join(' ').replace(/[`*_>#]/g,'').replace(/\s+/g,' ').trim();
  if(clean.length<=limit) return clean; return clean.slice(0,limit-1).replace(/\s+\S*$/,'')+'…';
}
function wikiSlugFor(sourcePath){
  const fixed={
    'README.md':'project-readme','docs/REPOSITORY_LAYOUT.md':'repository-layout','docs/BUILD_SYSTEM.md':'build-system','docs/RELEASES.md':'releases','CONTRIBUTING.md':'contributing','CHANGELOG.md':'project-changelog',
    'source/README.md':'source-readme','source/CONTROL_INDEX.md':'control-index','source/CONTROL_MANIFEST.md':'control-manifest','source/PROFILE_MATRIX.md':'profile-matrix','source/ARTIFACT_CONTRACTS.md':'artifact-contracts','source/TRUTH_BOUNDARIES.md':'truth-boundaries',
    'source/FEATURES.md':'features','source/FEATURE_COMPILER.md':'feature-compiler','source/COMPONENT_COMPILER.md':'component-compiler','source/DESIGN.md':'design','source/CREATIVE.md':'creative','source/CRAFT.md':'craft','source/GENERICITY.md':'genericity','source/RESPONSIVE_COMPOSITION.md':'responsive','source/ACCESSIBILITY_EVIDENCE.md':'accessibility',
    'source/JOBS.md':'jobs','source/OPERATIONAL_PROCEDURE_COMPILER.md':'operations-compiler','source/PROCEDURE_AUTHORITY.md':'procedure-authority','source/DECISION_RIGHTS.md':'decision-rights','source/OPERATIONAL_EVIDENCE.md':'operational-evidence','source/KPI_GOVERNANCE.md':'kpi-governance',
    'source/QA_GATES.md':'qa-gates','source/QUALITY_FLOORS.md':'quality-floors','source/COMPLETENESS.md':'completeness','source/CRITICS.md':'critics','source/INDUSTRIES.md':'industries','source/SECURITY.md':'security','source/LEGAL.md':'legal','source/SEO_GEO_AEO.md':'seo-geo-aeo','source/TERMINOLOGY.md':'terminology','source/STRUCTURE.md':'structure','source/BENCHMARKS.md':'benchmarks'
  };
  if(fixed[sourcePath]) return fixed[sourcePath];
  return sourcePath.toLowerCase().replace(/\.md$/,'').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
}
function wikiCategory(sourcePath){
  if(!sourcePath.startsWith('source/')) return 'Project';
  if(sourcePath.startsWith('source/controls/')) return 'Control Domains';
  if(sourcePath.startsWith('source/contracts/')) return 'Artifact Contracts';
  if(sourcePath.startsWith('source/operations/')) return 'Operations Profiles';
  if(/(?:OPERATIONAL|PROCEDURE|DECISION_RIGHTS|KPI_GOVERNANCE|JOBS)/.test(sourcePath)) return 'Operations 2.0';
  if(/(?:DESIGN|CREATIVE|CRAFT|FEATURE|COMPONENT|GENERICITY|RESPONSIVE|ACCESSIBILITY)/.test(sourcePath)) return 'Product & Design';
  if(/(?:QA_|QUALITY|COMPLETENESS|CRITICS|BENCHMARK|EVALS)/.test(sourcePath)) return 'Quality & Evaluation';
  return 'Core & Reference';
}

function lockTree(dir,exclude=[]){
  const ex=new Set(exclude); const files={};
  for(const p of walk(dir)){
    const r=rel(p,dir); if(ex.has(r)) continue; files[r]=sha(p);
  }
  return files;
}

if(!fs.existsSync(path.join(SOURCE,'README.md'))) fail('source/README.md is missing');
if(!noValidate){
  let python;
  try { python = checkPythonDependencies().py; }
  catch(error){ fail(error.message); }
  for(const tool of ['tools/validate_pack.py']){
    const p=path.join(SOURCE,tool); if(!fs.existsSync(p)) fail(`required source validator missing: ${tool}`);
    const r=spawnSync(python.command,[...python.prefix,'-B',p],{cwd:SOURCE,encoding:'utf8',env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});
    if(r.status!==0){ process.stdout.write(r.stdout||''); process.stderr.write(r.stderr||''); fail(`${tool} failed`); }
    if(r.stdout?.trim()) log(r.stdout.trim());
  }
}
trace('validators complete');

// Validators may create Python bytecode; generated caches are never canonical source.
purgeTransient(SOURCE);
trace('transient purge complete');

const readme=read(path.join(SOURCE,'README.md'));
const md=metadata(readme);
const coreRevision=md['Control-Plane-Revision'];
const packVersion=md['Pack-Version'];
const sourceUpdated=md['Last-Updated'] || 'unknown';
if(!coreRevision) fail('README.md has no Control-Plane-Revision metadata');
if(!packVersion) fail('README.md has no Pack-Version metadata');

const rootPkg=JSON.parse(read(path.join(ROOT,'package.json')));
const runtimeVersion=rootPkg.version;
const sourceFiles=walk(SOURCE);
trace('source walk complete',sourceFiles.length);
const markdownFiles=sourceFiles.filter(p=>p.endsWith('.md'));
const sourceTreeSha=crypto.createHash('sha256').update(sourceFiles.map(p=>`${rel(p,SOURCE)}:${sha(p)}`).join('\n')).digest('hex');
const sourceIndex={
  generatedFromSourceUpdated: sourceUpdated,
  packVersion,
  coreRevision,
  documents: markdownFiles.map(p=>({
    path:rel(p,SOURCE), sha256:sha(p), metadata:metadata(read(p)), headings:headings(read(p))
  }))
};

let registry=[];
for(const p of [path.join(SOURCE,'control_registry.csv'), ...walk(path.join(SOURCE,'control_registry')).filter(p=>p.endsWith('.csv'))]) registry.push(...parseCsv(read(p)));
const controls=registry.length;
const domains=new Set(registry.map(r=>r.domain).filter(Boolean));
const capabilities=new Set(registry.map(r=>`${r.domain}::${r.capability_id||r.capability}`).filter(Boolean));
const ids=registry.map(r=>r.id).filter(Boolean);
if(controls===0 || domains.size===0 || capabilities.size===0) fail('control registry could not be derived');
const contracts=fs.readdirSync(path.join(SOURCE,'contracts')).filter(x=>x.endsWith('.md')).sort().map(x=>x.replace(/\.md$/,''));
const operations=fs.readdirSync(path.join(SOURCE,'operations')).filter(x=>x.endsWith('.md')).sort().map(x=>x.replace(/\.md$/,''));

const vars={
  RUNTIME_VERSION:runtimeVersion,
  CORE_REVISION:coreRevision,
  PACK_VERSION:packVersion,
  DOMAIN_COUNT:domains.size,
  CAPABILITY_COUNT:capabilities.size,
  CONTROL_COUNT:controls,
  CONTROL_FIRST:ids[0]||'',
  CONTROL_LAST:ids.at(-1)||'',
  CONTRACT_COUNT:contracts.length,
  OPERATIONS_PROFILE_COUNT:operations.length
};

trace('removing prior build');
fs.rmSync(BUILD,{recursive:true,force:true});
trace('prior build removed');
fs.mkdirSync(BUILD,{recursive:true});
writeJson(path.join(BUILD,'SOURCE_INDEX.json'), sourceIndex);
writeJson(path.join(BUILD,'BUILD_MANIFEST.json'), {
  generated:true,
  generatedFromSourceUpdated:sourceIndex.generatedFromSourceUpdated,
  generator:'tooling/build.mjs',
  runtimeVersion, coreRevision, packVersion,
  source:{documents:markdownFiles.length,files:sourceFiles.length,sha256:sourceTreeSha},
  architecture:{domains:domains.size,capabilities:capabilities.size,controls,firstControl:ids[0],lastControl:ids.at(-1)},
  contracts, operationsProfiles:operations
});
write(path.join(BUILD,'README.md'), `# Generated AIFENCE Build\n\nDo not edit files in this directory by hand. They are generated from \`source/\` by \`node tooling/build.mjs\`.\n\n- Runtime: ${runtimeVersion}\n- Core revision: ${coreRevision}\n- Domains: ${domains.size}\n- Capabilities: ${capabilities.size}\n- Controls: ${controls}\n\nRun \`npm run build\` after changing canonical source files.\n`);

// Derived capability shards: exact stable sections for context-efficient retrieval.
const capabilityShardRoot=path.join(BUILD,'capability-shards');
const capGroups=new Map();
for(const r of registry){ const id=r.capability_id||r.capability; if(!capGroups.has(id))capGroups.set(id,r); }
for(const [id,r] of [...capGroups.entries()].sort((a,b)=>a[0].localeCompare(b[0]))){
  const src=path.join(SOURCE,r.shard); const section=extractStableSection(read(src),id);
  if(!section) fail(`cannot derive capability shard ${id} from ${r.shard}`);
  const name=id.replace(/[^a-z0-9._-]+/ig,'-');
  write(path.join(capabilityShardRoot,`${name}.md`),`<!-- GENERATED from source/${r.shard}#${id}; canonical truth remains source/. -->\n\n${section}\n`);
}

// Skill build: template + source-derived progressive references.
const skillRoot=path.join(BUILD,'skill','aifence');
copyRendered(SKILL_TEMPLATE,skillRoot,vars);
const generatedHeader=(sources)=>`<!-- GENERATED from ${sources.join(', ')} by tooling/build.mjs. Do not hand edit. -->\n\n`;
const routingParts=['Retrieval Rules','Creation-Type Router','Routing by Task','Context Efficiency Protocol'].map(x=>extractSection(readme,x)).filter(Boolean);
write(path.join(skillRoot,'references','routing.md'),generatedHeader(['source/README.md'])+'# Routing reference\n\n'+routingParts.join('\n\n'));
const truthText=read(path.join(SOURCE,'TRUTH_BOUNDARIES.md'));
const truthParts=['Canonical Status Vocabulary','Visible Truth Boundaries','Sample & Simulated Product Semantics','Recommendation Boundary','Regulated & High-Risk Escalation'].map(x=>extractSection(truthText,x)).filter(Boolean);
write(path.join(skillRoot,'references','truth.md'),generatedHeader(['source/TRUTH_BOUNDARIES.md'])+'# Truth reference\n\n'+truthParts.join('\n\n'));
const qaText=read(path.join(SOURCE,'QA_GATES.md'));
const qaCandidates=['Creation Quality Smoke Tests','Claim Standard','Compiled Artifact Gate','Adversarial Acceptance Gate','Control Plane Release Gate'];
const revisionHeadings=headings(qaText).filter(h=>/^Revision \d+(?:\.\d+)* .* Gate$/i.test(h.title));
if(revisionHeadings.length) qaCandidates.push(revisionHeadings.at(-1).title);
const qaParts=qaCandidates.map(x=>extractSection(qaText,x)).filter(Boolean);
const qaSummary=`Current generated architecture: ${domains.size} domains / ${capabilities.size} capabilities / ${controls} controls (${ids[0]}–${ids.at(-1)}).`;
write(path.join(skillRoot,'references','qa.md'),generatedHeader(['source/QA_GATES.md','source/control_registry*.csv'])+'# QA reference\n\n'+qaSummary+'\n\n'+qaParts.join('\n\n'));
const opText=read(path.join(SOURCE,'OPERATIONAL_PROCEDURE_COMPILER.md'));
const authText=read(path.join(SOURCE,'PROCEDURE_AUTHORITY.md'));
const rightsText=read(path.join(SOURCE,'DECISION_RIGHTS.md'));
const kpiText=read(path.join(SOURCE,'KPI_GOVERNANCE.md'));
const opParts=[extractSection(opText,'Compiler Entry Conditions'),extractSection(opText,'Real-World Accuracy Gate'),extractSection(opText,'Compilation Acceptance'),extractSection(authText,'Authority Classes'),extractSection(rightsText,'Mandatory Rights Vocabulary'),extractSection(kpiText,'No Invented Targets'),extractSection(kpiText,'Formula Integrity')].filter(Boolean);
write(path.join(skillRoot,'references','operations.md'),generatedHeader(['source/OPERATIONAL_PROCEDURE_COMPILER.md','source/PROCEDURE_AUTHORITY.md','source/DECISION_RIGHTS.md','source/KPI_GOVERNANCE.md'])+'# Operations reference\n\n'+opParts.join('\n\n'));

// Adapter build.
const adapterRoot=path.join(BUILD,'adapters');
copyRendered(ADAPTER_TEMPLATE,adapterRoot,vars);
// Every skill-capable adapter gets the exact same generated skill.
for(const target of [path.join(adapterRoot,'claude-code','skills','aifence'),path.join(adapterRoot,'gemini-cli','skills','aifence'),path.join(adapterRoot,'generic','aifence')]){
  fs.rmSync(target,{recursive:true,force:true}); copyDir(skillRoot,target);
}

// Runtime build.
const runtimeRoot=path.join(BUILD,'runtime');
copyRendered(RUNTIME_TEMPLATE,runtimeRoot,vars);
// Replace repo-sensitive paths implementation.
write(path.join(runtimeRoot,'src','paths.js'),`import fs from 'node:fs';\nimport path from 'node:path';\nimport {fileURLToPath} from 'node:url';\n\nexport const RUNTIME_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');\nexport const REPO_ROOT = path.resolve(RUNTIME_ROOT, '..', '..');\nexport const REPO_SOURCE_ROOT = path.join(REPO_ROOT, 'source');\nexport const BUNDLED_CORE_ROOT = path.join(RUNTIME_ROOT, 'core');\nconst envCore = process.env.AIFENCE_SOURCE_DIR ? path.resolve(process.env.AIFENCE_SOURCE_DIR) : null;\nexport const CORE_ROOT = envCore || (fs.existsSync(path.join(BUNDLED_CORE_ROOT,'README.md')) ? BUNDLED_CORE_ROOT : REPO_SOURCE_ROOT);\nexport const SKILL_ROOT = path.join(RUNTIME_ROOT, 'skill', 'aifence');\nexport const UI_FILE = path.join(RUNTIME_ROOT, 'ui', 'dashboard.html');\n`);
// Dynamic package/config.
const runtimePkg={
  name:'aifence-runtime',version:runtimeVersion,private:false,type:'module',
  description:'Portable AIFENCE Runtime generated from canonical AIFENCE source.',
  bin:{aifence:'./src/cli.js'}, engines:{node:'>=20'},
  scripts:{test:'node scripts/run-tests.js',doctor:'node src/cli.js doctor',status:'node src/cli.js status','mcp:stdio':'node src/mcp-stdio.js','mcp:http':'node src/mcp-http.js',ui:'node src/ui-server.js',verify:'node scripts/verify-runtime.js && node src/cli.js verify && node scripts/run-tests.js'},
  dependencies:{'@modelcontextprotocol/server':'2.0.0','@modelcontextprotocol/node':'2.0.0-beta.5',zod:'4.4.3'}
};
writeJson(path.join(runtimeRoot,'package.json'),runtimePkg);
writeJson(path.join(runtimeRoot,'runtime.config.json'),{
  runtimeVersion,coreRevision,packVersion,sourcePath:'../../source',bundledCorePath:'./core',defaultMode:'production',
  generatedFrom:'source/',architecture:{domains:domains.size,capabilities:capabilities.size,controls},
  mcp:{stdio:true,http:{enabled:true,defaultHost:'127.0.0.1',defaultPort:3888,path:'/mcp'},appUi:{resourceUri:'ui://aifence/status'}},
  install:{scope:'project',globalRequiresExplicitFlag:true,mergeExistingConfig:true,backupBeforeMutation:true},
  compatibility:{coreRevisionExact:coreRevision,policy:'exact-generated-core'},
  retrieval:{primaryUnit:'stable-capability-section',generatedShardPath:'./capability-shards',activeModulesRole:'compatibility-debug-only'}
});
writeJson(path.join(runtimeRoot,'CORE_LOCK.json'),{aifence_quality_revision:coreRevision,pack_version:packVersion,source_root:'source/',files:Object.fromEntries(sourceFiles.map(p=>[rel(p,SOURCE),sha(p)]))});
writeJson(path.join(runtimeRoot,'SOURCE_INDEX.json'),sourceIndex);
// Runtime installer needs generated Skill and adapters.
copyDir(skillRoot,path.join(runtimeRoot,'skill','aifence'));
copyDir(adapterRoot,path.join(runtimeRoot,'adapters'));
copyDir(capabilityShardRoot,path.join(runtimeRoot,'capability-shards'));

// Make runtime tests source-version/count dynamic.
const coreTest=path.join(runtimeRoot,'tests','core.test.js');
if(fs.existsSync(coreTest)){
  let t=read(coreTest).replace("assert.equal(v.revision,'1.6')",'assert.equal(v.revision, EXPECTED_CORE_REVISION)').replace("assert.equal(r.length,1300)",`assert.equal(r.length,${controls})`).replace("assert.equal(r.at(-1).id,'BQ-1300')",`assert.equal(r.at(-1).id,'${ids.at(-1)}')`);
  t="import {EXPECTED_CORE_REVISION} from '../src/config.js';"+t;
  write(coreTest,t);
}
const runtimeTest=path.join(runtimeRoot,'tests','runtime.test.js');
if(fs.existsSync(runtimeTest)) write(runtimeTest,read(runtimeTest).replace("assert.equal(s.controls,1300)",`assert.equal(s.controls,${controls})`));

// Wiki / GitHub Pages build: source-driven documentation shell + on-demand Markdown corpus.
const wikiRoot=path.join(BUILD,'wiki');
copyRendered(WIKI_TEMPLATE,wikiRoot,vars);
const wikiContentRoot=path.join(wikiRoot,'content');
const wikiInputs=[];
for(const rootDoc of ['README.md','CHANGELOG.md','CONTRIBUTING.md']){
  const p=path.join(ROOT,rootDoc); if(fs.existsSync(p)) wikiInputs.push({path:p,sourcePath:rootDoc});
}
const docsDir=path.join(ROOT,'docs');
if(fs.existsSync(docsDir)) for(const p of walk(docsDir).filter(p=>p.endsWith('.md'))) wikiInputs.push({path:p,sourcePath:rel(p,ROOT)});
for(const p of markdownFiles) wikiInputs.push({path:p,sourcePath:'source/'+rel(p,SOURCE)});
const wikiDocuments=[];
for(const item of wikiInputs){
  const text=read(item.path); const sourcePath=item.sourcePath; const contentPath='content/'+sourcePath;
  const target=path.join(wikiRoot,contentPath); write(target,text.replace(/\r\n?/g,'\n'));
  wikiDocuments.push({
    slug:wikiSlugFor(sourcePath),title:firstHeading(text,path.basename(sourcePath,'.md')),category:wikiCategory(sourcePath),summary:plainSummary(text),sourcePath,contentPath:'./'+contentPath,
    sourceUrl:`https://github.com/NeuralBinary/AIFENCE/blob/main/${sourcePath}`,
    headings:headings(text).filter(h=>h.level<=3).map(h=>({level:h.level,title:h.title,id:h.id})),
    searchText:(firstHeading(text,'')+' '+plainSummary(text,700)+' '+headings(text).map(h=>h.title).join(' ')).replace(/\s+/g,' ').trim()
  });
}
const gettingStarted=`# Getting Started

AIFENCE keeps canonical standards in \`source/\` and generates portable interoperability under \`build/\`.

## Clone and validate

\`\`\`bash
npm run setup:python
npm run build
npm test
\`\`\`

The build validates AIFENCE Core ${coreRevision}, runs Operations 2.0 executable regressions, regenerates the Skill/Runtime/adapters/wiki, and verifies generated integrity locks.

## Start the Runtime

\`\`\`bash
cd build/runtime
npm install
node src/cli.js doctor
node src/cli.js verify
\`\`\`

## Plan a production request

\`\`\`bash
node src/cli.js plan "Create a premium production website for a local landscaping company"
\`\`\`

## MCP transports

\`\`\`bash
node src/cli.js mcp --stdio
node src/cli.js mcp --http --host 127.0.0.1 --port 3888
\`\`\`

## Project installation

After linking the Runtime CLI with \`npm link\`, install integrations into a project scope:

\`\`\`bash
aifence install all --project . --dry-run
aifence install all --project .
\`\`\`

AIFENCE intentionally does not mutate global/home configuration automatically.
`;
const runtimeGuide=`# Runtime & Integrations

Runtime **${runtimeVersion}** exposes AIFENCE Core **${coreRevision}** through a portable Skill, CLI, MCP server, local UI, and platform adapters.

## Runtime responsibilities

- classify production requests and resolve artifact contracts;
- resolve independent operating/product/design/halo/risk profiles;
- retrieve bounded source sections instead of preloading the control plane;
- expose stable control, contract, profile, compiler, validation, and status operations;
- preserve Core authority: generated adapters never override \`source/\`.

## Generated integrations

The build produces adapters for Claude, Gemini, VS Code/Copilot, Cursor, OpenAI/Codex, and a generic Skill/MCP integration. All adapters are generated from the same Runtime and Skill source rather than maintained as independent AIFENCE forks.

## Core relationship

Inside this repository Runtime reads \`source/\` directly. Standalone Runtime release archives vendor that same tree as \`core/\` and verify it through \`CORE_LOCK.json\`.
`;
for(const [slug,title,category,text] of [['getting-started','Getting Started','Project',gettingStarted],['runtime-integrations','Runtime & Integrations','Runtime',runtimeGuide]]){
  const contentPath=`content/generated/${slug}.md`; write(path.join(wikiRoot,contentPath),text);
  wikiDocuments.unshift({slug,title,category,summary:plainSummary(text),sourcePath:`generated/${slug}.md`,contentPath:'./'+contentPath,sourceUrl:null,headings:headings(text).filter(h=>h.level<=3),searchText:(title+' '+plainSummary(text,700)+' '+headings(text).map(h=>h.title).join(' ')).replace(/\s+/g,' ').trim()});
}
const wikiBySlug=new Map(wikiDocuments.map(d=>[d.slug,d]));
const navSpec=[
  ['Project',['getting-started','repository-layout','build-system','runtime-integrations','releases','contributing','project-changelog']],
  ['Core',['source-readme','control-index','control-manifest','profile-matrix','artifact-contracts','truth-boundaries']],
  ['Product & Design',['features','feature-compiler','component-compiler','design','creative','craft','genericity','responsive','accessibility']],
  ['Operations 2.0',['jobs','operations-compiler','procedure-authority','decision-rights','operational-evidence','kpi-governance']],
  ['Quality & Reference',['qa-gates','quality-floors','completeness','critics','industries','security','legal','seo-geo-aeo','terminology','structure','benchmarks']]
];
const navigation=navSpec.map(([label,slugs])=>({label,items:slugs.map(slug=>wikiBySlug.get(slug)).filter(Boolean).map(d=>({slug:d.slug,title:d.title}))}));
writeJson(path.join(wikiRoot,'wiki-index.json'),{
  generated:true,meta:{project:'AIFENCE',runtimeVersion,coreRevision,packVersion,domains:domains.size,capabilities:capabilities.size,controls,documents:markdownFiles.length,contracts:contracts.length,operationsProfiles:operations.length,repositoryUrl:'https://github.com/NeuralBinary/AIFENCE',sourceUpdated},
  navigation,documents:wikiDocuments.sort((a,b)=>a.category.localeCompare(b.category)||a.title.localeCompare(b.title))
});


// Build provenance hashes the generated tree before lock/provenance self-reference.
const preLockTree=lockTree(BUILD,['BUILD_LOCK.json','BUILD_PROVENANCE.json','runtime/RUNTIME_LOCK.json']);
const buildTreeSha=crypto.createHash('sha256').update(Object.entries(preLockTree).map(([k,v])=>`${k}:${v}`).join('\n')).digest('hex');
writeJson(path.join(BUILD,'BUILD_PROVENANCE.json'),{
  runtime_version:runtimeVersion,core_revision:coreRevision,pack_version:packVersion,source_tree_sha256:sourceTreeSha,build_sha256:buildTreeSha,
  build_hash_scope:'generated tree excluding BUILD_LOCK.json, BUILD_PROVENANCE.json, runtime/RUNTIME_LOCK.json',
  compatibility:{runtime_core_policy:'exact-generated-core',core_revision:coreRevision},node:rootPkg.engines?.node||'>=20',python:'source/requirements.txt + CI matrix',archives:[]
});

// Runtime lock is generated last and excludes itself.
writeJson(path.join(runtimeRoot,'RUNTIME_LOCK.json'),{runtime_version:runtimeVersion,core_revision:coreRevision,files:lockTree(runtimeRoot,['RUNTIME_LOCK.json'])});

// Build lock spans all generated files except itself.
writeJson(path.join(BUILD,'BUILD_LOCK.json'),{runtimeVersion,coreRevision,files:lockTree(BUILD,['BUILD_LOCK.json'])});

log(`AIFENCE build complete`);
trace('all generation and locks complete');
log(`Core ${coreRevision} · Runtime ${runtimeVersion}`);
log(`${domains.size} domains · ${capabilities.size} capabilities · ${controls} controls`);
log(`${markdownFiles.length} Markdown source documents indexed`);
log(`${contracts.length} contracts · ${operations.length} operations profiles`);
log(`Generated: ${rel(BUILD)}/`);
