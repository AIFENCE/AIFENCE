import fs from 'node:fs';import path from 'node:path';import {RUNTIME_ROOT,SKILL_ROOT} from './paths.js';
function mkdir(p,dry){if(!dry)fs.mkdirSync(p,{recursive:true})}function cp(src,dst,dry){if(dry)return;fs.cpSync(src,dst,{recursive:true,force:true})}
function backup(p,dry){if(fs.existsSync(p)&&!dry){const b=`${p}.biziq-backup`; if(!fs.existsSync(b))fs.copyFileSync(p,b);}}
function mergeJson(file,patch,dry){let cur={};if(fs.existsSync(file)){try{cur=JSON.parse(fs.readFileSync(file,'utf8'))}catch{throw new Error(`Refusing to modify invalid JSON: ${file}`)}} const merge=(a,b)=>{for(const[k,v]of Object.entries(b)){if(v&&typeof v==='object'&&!Array.isArray(v)){a[k]=merge({...((a[k]&&typeof a[k]==='object')?a[k]:{})},v)}else a[k]=v}return a};const next=merge(cur,patch);if(!dry){mkdir(path.dirname(file),false);backup(file,false);fs.writeFileSync(file,JSON.stringify(next,null,2)+'\n')}return next}
function skill(target,dry){const d=path.join(target,'.agents','skills','biziq');mkdir(path.dirname(d),dry);cp(SKILL_ROOT,d,dry);return d}
const mcpCmd=()=>({command:process.execPath,args:[path.join(RUNTIME_ROOT,'src','mcp-stdio.js')]});
export function install(targetKind,{project=process.cwd(),dryRun=false}={}){const p=path.resolve(project);const changed=[]; const ensureSkill=()=>{const d=skill(p,dryRun);changed.push(d)};
 if(['skill','all','openai','gemini','vscode'].includes(targetKind))ensureSkill();
 if(['claude','all'].includes(targetKind)){const d=path.join(p,'.claude','skills','biziq');cp(SKILL_ROOT,d,dryRun);changed.push(d);const f=path.join(p,'.mcp.json');mergeJson(f,{mcpServers:{biziq:mcpCmd()}},dryRun);changed.push(f)}
 if(['gemini','all'].includes(targetKind)){const f=path.join(p,'.gemini','settings.json');mergeJson(f,{mcpServers:{biziq:mcpCmd()}},dryRun);changed.push(f)}
 if(['vscode','all'].includes(targetKind)){const f=path.join(p,'.vscode','mcp.json');mergeJson(f,{servers:{biziq:{type:'stdio',...mcpCmd()}}},dryRun);changed.push(f)}
 if(['cursor','all'].includes(targetKind)){const f=path.join(p,'.cursor','mcp.json');mergeJson(f,{mcpServers:{biziq:mcpCmd()}},dryRun);changed.push(f)}
 if(!['skill','claude','gemini','vscode','cursor','openai','all'].includes(targetKind))throw new Error('install target: skill|claude|gemini|vscode|cursor|openai|all');
 return {ok:true,target:targetKind,project:p,dryRun,changed};}
