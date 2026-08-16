#!/usr/bin/env python3
from pathlib import Path
import json, zipfile, hashlib, shutil, os
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'build'; SOURCE=ROOT/'source'; DIST=ROOT/'dist'
if not (BUILD/'BUILD_MANIFEST.json').exists(): raise SystemExit('Run npm run build first')
meta=json.loads((BUILD/'BUILD_MANIFEST.json').read_text())
rv=meta['runtimeVersion']; cv=meta['coreRevision']
if DIST.exists(): shutil.rmtree(DIST)
DIST.mkdir()
STAMP=(1980,1,1,0,0,0)
TEXT_EXTENSIONS={'.md','.json','.js','.mjs','.cjs','.txt','.yml','.yaml','.html','.css','.csv','.py','.toml','.xml','.sh','.bat','.ps1'}
def canonical_bytes(p):
    data=p.read_bytes()
    if p.suffix.lower() in TEXT_EXTENSIONS or p.name.startswith('.') or p.name in {'LICENSE','NOTICE'}:
        try:
            return data.decode('utf-8').replace('\r\n','\n').replace('\r','\n').encode('utf-8')
        except UnicodeDecodeError:
            return data
    return data
def add_tree(z,src,prefix=''):
    for p in sorted(src.rglob('*')):
        rel=p.relative_to(src)
        if any(part in {'__pycache__','.pytest_cache','.cache','node_modules','dist'} for part in rel.parts): continue
        if p.suffix in {'.pyc','.pyo'}: continue
        if p.is_file():
            arc=(Path(prefix)/rel).as_posix()
            info=zipfile.ZipInfo(arc,STAMP); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=(0o644&0xFFFF)<<16
            z.writestr(info,canonical_bytes(p))
def make(name,parts):
    out=DIST/name
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for src,prefix in parts: add_tree(z,src,prefix)
    with zipfile.ZipFile(out) as z:
        bad=z.testzip();
        if bad: raise SystemExit(f'ZIP integrity failure {name}: {bad}')
    return out
packages=[]
packages.append(make(f'BizIQ-Source-{cv}.zip',[(SOURCE,'')]))
# Standalone runtime vendors canonical source as core and generated integrations.
packages.append(make(f'BizIQ-Runtime-{rv}-Core-{cv}.zip',[(BUILD/'runtime',''),(SOURCE,'core')]))
packages.append(make(f'BizIQ-Skill-{rv}.zip',[(BUILD/'skill','')]))
packages.append(make(f'BizIQ-Claude-Plugin-{rv}.zip',[(BUILD/'adapters'/'claude-code','')]))
packages.append(make(f'BizIQ-Gemini-Extension-{rv}.zip',[(BUILD/'adapters'/'gemini-cli','')]))
packages.append(make(f'BizIQ-Platform-Adapters-{rv}.zip',[(BUILD/'adapters','')]))
packages.append(make(f'BizIQ-Wiki-{rv}.zip',[(BUILD/'wiki','')]))
manifest={'runtimeVersion':rv,'coreRevision':cv,'compatibility':{'policy':'exact-generated-core','coreRevision':cv},'packages':[]}
for p in packages:
    manifest['packages'].append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
(DIST/'release-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
build_provenance_path=BUILD/'BUILD_PROVENANCE.json'
build_provenance=json.loads(build_provenance_path.read_text()) if build_provenance_path.exists() else {}
provenance=dict(build_provenance)
provenance.update({
    'runtime_version':rv,
    'core_revision':cv,
    'pack_version':meta.get('packVersion'),
    'source_tree_sha256':meta.get('source',{}).get('sha256'),
    'build_sha256':build_provenance.get('build_sha256'),
    'build_provenance_sha256':hashlib.sha256(build_provenance_path.read_bytes()).hexdigest() if build_provenance_path.exists() else None,
    'release_manifest_sha256':hashlib.sha256((DIST/'release-manifest.json').read_bytes()).hexdigest(),
    'compatibility':{'runtime_core_policy':'exact-generated-core','core_revision':cv},
    'archives':[{'name':x['file'],'sha256':x['sha256'],'bytes':x['bytes']} for x in manifest['packages']],
    'reproducibility':{'zip_timestamp':'1980-01-01T00:00:00Z','text_line_endings':'LF','sorted_entries':True},
})
(DIST/'release-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
prov_schema=json.loads((SOURCE/'schemas'/'release_provenance.schema.json').read_text())
prov_errors=sorted(Draft202012Validator(prov_schema).iter_errors(provenance),key=lambda e:list(e.path))
if prov_errors: raise SystemExit('Release provenance schema failure: '+' | '.join(e.message for e in prov_errors[:5]))
print(f'Release packages created in {DIST}')
for x in manifest['packages']: print(x['file'],x['sha256'])
