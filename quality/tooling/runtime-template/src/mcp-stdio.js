#!/usr/bin/env node
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { createAifenceServer } from './mcp-server.js';
serveStdio(createAifenceServer);
console.error('AIFENCE Runtime MCP 1.0 serving stdio');
