#!/usr/bin/env node
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { createBizIQServer } from './mcp-server.js';
serveStdio(createBizIQServer);
console.error('BizIQ Runtime MCP 1.0 serving stdio');
