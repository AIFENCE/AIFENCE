import fs from 'node:fs';

export function readText(file) { return fs.readFileSync(file, 'utf8'); }
export function normalizeName(s='') { return s.toLowerCase().replace(/[`*_]/g,'').replace(/[^a-z0-9]+/g,' ').trim(); }

export function parseMetadata(text) {
  const m = text.match(/^<!--\s*\n([\s\S]*?)\n-->/);
  const out={};
  if (!m) return out;
  for (const line of m[1].split(/\r?\n/)) {
    const i=line.indexOf(':'); if (i>0) out[line.slice(0,i).trim()]=line.slice(i+1).trim();
  }
  return out;
}

export function parseMarkdownTable(lines) {
  const rows=[];
  for (const line of lines) {
    if (!line.trim().startsWith('|')) continue;
    const cells=line.trim().slice(1,-1).split('|').map(x=>x.trim());
    if (cells.every(c=>/^:?-{3,}:?$/.test(c.replace(/\s/g,'')))) continue;
    rows.push(cells);
  }
  if (rows.length<2) return [];
  const headers=rows[0].map(h=>h.replace(/`/g,''));
  return rows.slice(1).map(cells=>Object.fromEntries(headers.map((h,i)=>[h,cells[i]??''])));
}

export function tableAfterHeading(text, heading) {
  const lines=text.split(/\r?\n/); const idx=lines.findIndex(l=>l.trim()===heading.trim());
  if (idx<0) return [];
  const table=[]; let begun=false;
  for (let i=idx+1;i<lines.length;i++) {
    if (lines[i].trim().startsWith('|')) { begun=true; table.push(lines[i]); continue; }
    if (begun) break;
  }
  return parseMarkdownTable(table);
}

export function extractSectionById(text, id) {
  const marker=`<!-- id: ${id} -->`; const pos=text.indexOf(marker); if(pos<0) return null;
  const before=text.slice(0,pos); const matches=[...before.matchAll(/^(#{1,6})\s+(.+)$/gm)];
  if(!matches.length) return text.slice(pos).split(/\n(?=# )/)[0].trim();
  const head=matches[matches.length-1]; const level=head[1].length; const start=head.index;
  const rest=text.slice(pos+marker.length); const re=new RegExp(`^#{1,${level}}\\s+.+$`,'m'); const next=re.exec(rest);
  const end=next ? pos+marker.length+next.index : text.length;
  return text.slice(start,end).trim();
}

export function parseCsv(text) {
  const rows=[]; let row=[], cell='', q=false;
  for(let i=0;i<text.length;i++){
    const ch=text[i];
    if(q){ if(ch==='"' && text[i+1]==='"'){cell+='"'; i++;} else if(ch==='"'){q=false;} else cell+=ch; }
    else if(ch==='"') q=true;
    else if(ch===','){row.push(cell);cell='';}
    else if(ch==='\n'){row.push(cell.replace(/\r$/,''));rows.push(row);row=[];cell='';}
    else cell+=ch;
  }
  if(cell.length||row.length){row.push(cell);rows.push(row);}
  const headers=rows.shift()||[];
  return rows.filter(r=>r.some(x=>x!=='')).map(r=>Object.fromEntries(headers.map((h,i)=>[h,r[i]??''])));
}

export function splitSemicolonModules(cell='') {
  return cell.split(/[;,]/).map(x=>x.trim()).filter(Boolean).map(x=>x.replace(/\s+when needed$/i,'').replace(/\s+when triggered$/i,'').replace(/\s+as applicable$/i,'').trim());
}
