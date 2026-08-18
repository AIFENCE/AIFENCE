#!/usr/bin/env node
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const SITE=path.join(ROOT,'build','wiki');
const args=process.argv.slice(2);const val=(k,d)=>{const i=args.indexOf(k);return i>=0?args[i+1]:d};
const host=val('--host','127.0.0.1');const port=Number(val('--port','4173'));
const types={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.md':'text/markdown; charset=utf-8','.svg':'image/svg+xml'};
if(!fs.existsSync(path.join(SITE,'index.html'))){console.error('build/wiki missing; run npm run build first');process.exit(1)}
const server=http.createServer((req,res)=>{
  let u;try{u=new URL(req.url||'/',`http://${req.headers.host||'localhost'}`)}catch{res.writeHead(400);res.end('Bad request');return;}
  let rel=decodeURIComponent(u.pathname).replace(/^\/+/, '')||'index.html';
  const target=path.resolve(SITE,rel);if(target!==SITE&&!target.startsWith(SITE+path.sep)){res.writeHead(403);res.end('Forbidden');return;}
  const p=fs.existsSync(target)&&fs.statSync(target).isFile()?target:path.join(SITE,'index.html');
  res.writeHead(200,{'Content-Type':types[path.extname(p)]||'application/octet-stream','Cache-Control':'no-store'});fs.createReadStream(p).pipe(res);
});
server.listen(port,host,()=>console.log(`AIFENCE Wiki http://${host}:${port}`));
