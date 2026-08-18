#!/usr/bin/env node
import http from 'node:http';
import { createMcpHandler } from '@modelcontextprotocol/server';
import { toNodeHandler } from '@modelcontextprotocol/node';
import { createAifenceServer } from './mcp-server.js';
const args=process.argv.slice(2); const val=(k,d)=>{const i=args.indexOf(k);return i>=0?args[i+1]:d}; const host=val('--host','127.0.0.1'); const port=Number(val('--port','3888')); const route=val('--path','/mcp');
if(!['127.0.0.1','localhost','::1'].includes(host) && !process.env.AIFENCE_ALLOW_REMOTE_HTTP){console.error('Refusing non-loopback bind without AIFENCE_ALLOW_REMOTE_HTTP=1. Put remote deployments behind authenticated TLS/reverse-proxy policy.');process.exit(2)}
const handler=createMcpHandler(createAifenceServer); const nodeHandler=toNodeHandler(handler);
const server=http.createServer(async(req,res)=>{if((req.url||'').split('?')[0]!==route){res.writeHead(404);res.end('Not found');return;} const h=(req.headers.host||'').split(':')[0]; if(['127.0.0.1','localhost','[::1]'].includes(host)&&!['127.0.0.1','localhost','[::1]','::1'].includes(h)){res.writeHead(403);res.end('Host rejected');return;} await nodeHandler(req,res);});
server.listen(port,host,()=>console.error(`AIFENCE Runtime MCP HTTP http://${host}:${port}${route}`));
