#!/usr/bin/env node
import crypto from 'node:crypto';

function canonicalText(text){ return text.replace(/\r\n?/g,'\n'); }
function hash(text){ return crypto.createHash('sha256').update(Buffer.from(canonicalText(text),'utf8')).digest('hex'); }

const fixtures = [
  ['id,name\nBQ-0001,Alpha\n', 'id,name\r\nBQ-0001,Alpha\r\n'],
  ['# Heading\n\nBody\n', '# Heading\r\n\r\nBody\r\n'],
  ['{"a":1}\n', '{"a":1}\r\n'],
];
for(const [lf,crlf] of fixtures){
  if(hash(lf)!==hash(crlf)){
    console.error('FAIL: canonical text hashing differs across LF/CRLF');
    process.exit(1);
  }
}
console.log(`PASS: ${fixtures.length} canonical LF/CRLF portability fixtures`);
