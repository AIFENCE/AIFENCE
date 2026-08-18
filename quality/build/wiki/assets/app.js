const $ = (s, root=document) => root.querySelector(s);
const $$ = (s, root=document) => [...root.querySelectorAll(s)];
const state = { data:null, docs:new Map(), route:'overview', searchIndex:[], selectedSearch:0 };

const esc = (s='') => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const slugify = (s='') => String(s).toLowerCase().replace(/[`*_]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,90) || 'section';
const inline = (s='') => {
  let x=esc(s);
  x=x.replace(/`([^`]+)`/g,'<code>$1</code>');
  x=x.replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>');
  x=x.replace(/\*([^*]+)\*/g,'<em>$1</em>');
  x=x.replace(/\[([^\]]+)\]\(([^)]+)\)/g,(_,label,href)=>{
    const clean=href.trim();
    const doc=resolveDocLink(clean);
    if(doc) return `<a href="#/${doc.slug}">${label}</a>`;
    const safe=/^(https?:|mailto:|#)/i.test(clean)?clean:'#';
    return `<a href="${esc(safe)}"${/^https?:/i.test(clean)?' target="_blank" rel="noreferrer"':''}>${label}</a>`;
  });
  return x;
};
function resolveDocLink(href){
  if(!state.data) return null;
  const base=href.split('#')[0].replace(/^\.\//,'');
  if(!base.endsWith('.md')) return null;
  const candidates=[base,`source/${base}`,`docs/${base}`];
  return state.data.documents.find(d=>candidates.includes(d.sourcePath)) || null;
}
function parseMarkdown(md=''){
  md=md.replace(/<!--([\s\S]*?)-->/g,'').replace(/\r\n?/g,'\n');
  const lines=md.split('\n');
  let html='', i=0, inCode=false, code=[], lang='', list=null, quote=[];
  const closeList=()=>{ if(list){html+=`</${list}>`; list=null;} };
  const flushQuote=()=>{ if(quote.length){html+=`<blockquote>${quote.map(q=>`<p>${inline(q)}</p>`).join('')}</blockquote>`;quote=[];} };
  while(i<lines.length){
    let line=lines[i];
    if(line.startsWith('```')){
      if(!inCode){closeList();flushQuote();inCode=true;lang=line.slice(3).trim();code=[];}
      else {html+=`<div class="code-block"><pre><code data-lang="${esc(lang)}">${esc(code.join('\n'))}</code></pre><button class="copy-button" type="button">Copy</button></div>`;inCode=false;lang='';code=[];}
      i++;continue;
    }
    if(inCode){code.push(line);i++;continue;}
    if(/^\s*\|.*\|\s*$/.test(line) && i+1<lines.length && /^\s*\|?\s*:?-{3,}/.test(lines[i+1])){
      closeList();flushQuote();
      const headers=line.trim().replace(/^\||\|$/g,'').split('|').map(x=>x.trim());
      i+=2; const rows=[];
      while(i<lines.length && /^\s*\|.*\|\s*$/.test(lines[i])){rows.push(lines[i].trim().replace(/^\||\|$/g,'').split('|').map(x=>x.trim()));i++;}
      html+='<div class="table-wrap"><table><thead><tr>'+headers.map(h=>`<th>${inline(h)}</th>`).join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr>'+headers.map((_,j)=>`<td>${inline(r[j]||'')}</td>`).join('')+'</tr>').join('')+'</tbody></table></div>';
      continue;
    }
    const hm=line.match(/^(#{1,6})\s+(.+)$/);
    if(hm){closeList();flushQuote();const level=hm[1].length;const title=hm[2].replace(/\s+#+$/,'').trim();const id=slugify(title);html+=`<h${level} id="${id}">${inline(title)}${level>1?`<a class="heading-anchor" href="#${id}" aria-label="Link to ${esc(title)}">#</a>`:''}</h${level}>`;i++;continue;}
    if(/^>\s?/.test(line)){closeList();quote.push(line.replace(/^>\s?/,''));i++;continue;} else flushQuote();
    const ul=line.match(/^\s*[-*+]\s+(.+)$/); const ol=line.match(/^\s*\d+[.)]\s+(.+)$/);
    if(ul||ol){const type=ul?'ul':'ol';if(list!==type){closeList();html+=`<${type}>`;list=type;}html+=`<li>${inline((ul||ol)[1])}</li>`;i++;continue;} else closeList();
    if(/^\s*---+\s*$/.test(line)){html+='<hr>';i++;continue;}
    if(!line.trim()){i++;continue;}
    let para=line.trim();
    while(i+1<lines.length && lines[i+1].trim() && !/^(#{1,6})\s+|^```|^>\s?|^\s*[-*+]\s+|^\s*\d+[.)]\s+|^\s*\|.*\|\s*$/.test(lines[i+1])){para+=' '+lines[++i].trim();}
    html+=`<p>${inline(para)}</p>`;i++;
  }
  closeList();flushQuote();
  return html;
}
function setTheme(theme){document.documentElement.dataset.theme=theme;localStorage.setItem('aifence-wiki-theme',theme);}
function initTheme(){const saved=localStorage.getItem('aifence-wiki-theme');setTheme(saved||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'));}
function renderNav(){
  $('#primaryNav').innerHTML=state.data.navigation.map(group=>`<div class="nav-group"><div class="nav-group-title">${esc(group.label)}</div>${group.items.map(item=>`<a class="nav-link" data-route="${esc(item.slug)}" href="#/${esc(item.slug)}"><span class="nav-dot"></span><span>${esc(item.title)}</span></a>`).join('')}</div>`).join('');
}
function updateActive(){$$('.nav-link').forEach(a=>a.classList.toggle('active',a.dataset.route===state.route));}
function overview(){
  const m=state.data.meta;
  const link=(slug,title,desc)=>`<a class="feature-link" href="#/${slug}"><strong>${esc(title)}</strong><span>${esc(desc)}</span></a>`;
  return `<section class="hero">
    <div class="hero-eyebrow">Source-driven production system</div>
    <h1>One control plane. Multiple AI runtimes.</h1>
    <p>AIFENCE turns canonical standards, controls, profiles, compilers, and validation into a portable quality system for production artifacts and operational work.</p>
    <div class="hero-actions"><a class="button primary" href="#/getting-started">Get started</a><a class="button" href="#/source-readme">Explore Core routing</a><a class="button" href="${esc(m.repositoryUrl)}" target="_blank" rel="noreferrer">View repository</a></div>
  </section>
  <section class="stat-grid" aria-label="AIFENCE architecture statistics">
    <div class="stat-card"><span class="stat-value">${m.domains}</span><span class="stat-label">Control domains</span></div>
    <div class="stat-card"><span class="stat-value">${m.capabilities}</span><span class="stat-label">Capabilities</span></div>
    <div class="stat-card"><span class="stat-value">${Number(m.controls).toLocaleString()}</span><span class="stat-label">Stable controls</span></div>
    <div class="stat-card"><span class="stat-value">${m.documents}</span><span class="stat-label">Markdown documents</span></div>
  </section>
  <section class="overview-grid">
    <div class="overview-card"><h2>Source → Build → Runtime</h2><p>Canonical policy stays in <code>source/</code>. Generated interoperability stays reproducible and disposable.</p><div class="arch-flow">
      <div class="arch-step"><strong>source/</strong><span>Standards, controls, contracts, profiles, operations, schemas, validators</span></div>
      <div class="arch-step"><strong>tooling/</strong><span>Deterministic generation, tests, release packaging, wiki generation</span></div>
      <div class="arch-step"><strong>build/</strong><span>Skill, MCP Runtime, CLI, UI, adapters, search index, wiki</span></div>
      <div class="arch-step"><strong>dist/</strong><span>Deterministic release archives generated for GitHub Releases</span></div>
    </div></div>
    <div class="overview-card"><h2>Build locally</h2><p>The same source validation used by CI runs before generated output is accepted.</p><div class="quick-command"><code>npm run setup:python\nnpm run build\nnpm test</code><button class="copy-button" type="button">Copy</button></div><div class="quick-command"><code>cd build/runtime\nnpm install\nnode src/cli.js doctor</code><button class="copy-button" type="button">Copy</button></div></div>
  </section>
  <section><h2>Explore the system</h2><p>Start with the architecture and routing model, then move into artifact compilation, Operations 2.0, and release validation.</p><div class="feature-links">
    ${link('repository-layout','Repository architecture','Canonical source and generated build boundaries')}
    ${link('source-readme','Core router','Initialization, production intent, profiles, and lazy loading')}
    ${link('artifact-contracts','Artifact contracts','Production acceptance contracts by artifact family')}
    ${link('feature-compiler','Feature compiler','Turn feature names into complete interaction specifications')}
    ${link('operations-compiler','Operations 2.0','Compile executable procedures with authority and evidence')}
    ${link('quality-floors','Quality floors','Non-averagable production acceptance thresholds')}
  </div></section>`;
}
async function loadDoc(doc){const r=await fetch(doc.contentPath,{cache:'no-store'});if(!r.ok)throw new Error(`Unable to load ${doc.sourcePath}`);return r.text();}
function articleHeader(doc){const source=doc.sourceUrl?`<a href="${esc(doc.sourceUrl)}" target="_blank" rel="noreferrer">View source on GitHub ↗</a>`:'';return `<header class="article-header"><div class="article-kicker">${esc(doc.category)}</div><h1>${esc(doc.title)}</h1>${doc.summary?`<div class="article-lede">${esc(doc.summary)}</div>`:''}<div class="article-meta"><span>${esc(doc.sourcePath)}</span>${source}</div></header>`;}
function renderToc(){const hs=$$('#article h2, #article h3');const toc=$('#toc');if(hs.length<2){toc.innerHTML='';return;}toc.innerHTML='<div class="toc-title">On this page</div>'+hs.map(h=>`<a class="depth-${h.tagName==='H3'?3:2}" href="#${h.id}">${esc(h.textContent.replace(/#$/,''))}</a>`).join('');}
function bindCopies(root=document){$$('.copy-button',root).forEach(btn=>btn.addEventListener('click',async()=>{const code=btn.parentElement.querySelector('code')?.textContent||'';try{await navigator.clipboard.writeText(code);btn.textContent='Copied';setTimeout(()=>btn.textContent='Copy',1200);}catch{btn.textContent='Select';}}));}
function renderBreadcrumbs(doc){$('#breadcrumbs').innerHTML=`<a href="#/overview">AIFENCE</a><span>/</span><span>${esc(doc?.category||'Overview')}</span>${doc?`<span>/</span><span>${esc(doc.title)}</span>`:''}`;}
function renderPageNav(){const flat=state.data.navigation.flatMap(g=>g.items);const idx=flat.findIndex(x=>x.slug===state.route);if(idx<0){$('#pageNav').innerHTML='';return;}const prev=flat[idx-1],next=flat[idx+1];$('#pageNav').innerHTML=`${prev?`<a href="#/${prev.slug}"><span>Previous</span><strong>← ${esc(prev.title)}</strong></a>`:'<span></span>'}${next?`<a class="next" href="#/${next.slug}"><span>Next</span><strong>${esc(next.title)} →</strong></a>`:''}`;}
async function route(){
  const raw=(location.hash||'#/overview').replace(/^#\/?/,'').split('#')[0]||'overview';state.route=raw;updateActive();closeSidebar();const article=$('#article');
  try{
    if(raw==='overview'){renderBreadcrumbs(null);article.innerHTML=overview();$('#toc').innerHTML='';$('#pageNav').innerHTML='';bindCopies(article);document.title='AIFENCE Wiki';window.scrollTo(0,0);return;}
    const doc=state.docs.get(raw)||state.docs.get('getting-started');renderBreadcrumbs(doc);article.innerHTML='<div class="loading-state"><span class="spinner"></span><span>Loading documentation…</span></div>';
    const md=await loadDoc(doc);const rendered=parseMarkdown(md).replace(/^<h1[^>]*>[\s\S]*?<\/h1>/,'');article.innerHTML=articleHeader(doc)+rendered;bindCopies(article);renderToc();renderPageNav();document.title=`${doc.title} · AIFENCE Wiki`;window.scrollTo(0,0);
  }catch(err){article.innerHTML=`<div class="error-card"><strong>Documentation could not be loaded.</strong><div>${esc(err.message)}</div></div>`;}
}
function closeSidebar(){$('#sidebar').classList.remove('open');$('#sidebarScrim').classList.remove('visible');$('#sidebarScrim').hidden=true;$('#menuButton').setAttribute('aria-expanded','false');}
function toggleSidebar(){const open=!$('#sidebar').classList.contains('open');$('#sidebar').classList.toggle('open',open);$('#sidebarScrim').hidden=!open;$('#sidebarScrim').classList.toggle('visible',open);$('#menuButton').setAttribute('aria-expanded',String(open));}
function searchDocs(query){const q=query.trim().toLowerCase();if(!q)return state.data.documents.slice(0,8);const terms=q.split(/\s+/).filter(Boolean);return state.searchIndex.map(doc=>{let score=0;const title=doc.title.toLowerCase();const text=doc.searchText.toLowerCase();for(const t of terms){if(title.includes(t))score+=8;if(doc.category.toLowerCase().includes(t))score+=3;if(text.includes(t))score+=1;}return{doc,score};}).filter(x=>x.score>0).sort((a,b)=>b.score-a.score||a.doc.title.localeCompare(b.doc.title)).slice(0,20).map(x=>x.doc);}
function renderSearch(){const results=searchDocs($('#searchInput').value);state.currentSearch=results;state.selectedSearch=Math.min(state.selectedSearch,Math.max(0,results.length-1));$('#searchResults').innerHTML=results.length?results.map((d,i)=>`<a class="search-result ${i===state.selectedSearch?'selected':''}" data-index="${i}" href="#/${d.slug}"><strong>${esc(d.title)}</strong><span>${esc(d.category)} · ${esc(d.summary||d.sourcePath)}</span></a>`).join(''):'<div class="search-empty">No matching documentation.</div>';}
function openSearch(){const d=$('#searchDialog');if(!d.open)d.showModal();state.selectedSearch=0;$('#searchInput').value='';renderSearch();setTimeout(()=>$('#searchInput').focus(),10);}
function closeSearch(){const d=$('#searchDialog');if(d.open)d.close();}
async function init(){initTheme();const r=await fetch('./wiki-index.json',{cache:'no-store'});state.data=await r.json();state.docs=new Map(state.data.documents.map(d=>[d.slug,d]));state.searchIndex=state.data.documents;$('#versionChip').textContent=`Core ${state.data.meta.coreRevision}`;$('#footerVersion').textContent=`Runtime ${state.data.meta.runtimeVersion} · Core ${state.data.meta.coreRevision}`;$('#integrityLabel').textContent=`${state.data.meta.documents} indexed docs · ${state.data.meta.controls.toLocaleString()} controls`;renderNav();await route();}
$('#themeButton').addEventListener('click',()=>setTheme(document.documentElement.dataset.theme==='dark'?'light':'dark'));
$('#menuButton').addEventListener('click',toggleSidebar);$('#sidebarScrim').addEventListener('click',closeSidebar);$('#searchTrigger').addEventListener('click',openSearch);
$('#searchInput').addEventListener('input',()=>{state.selectedSearch=0;renderSearch();});
$('#searchInput').addEventListener('keydown',e=>{if(e.key==='ArrowDown'){e.preventDefault();state.selectedSearch=Math.min(state.selectedSearch+1,(state.currentSearch?.length||1)-1);renderSearch();}if(e.key==='ArrowUp'){e.preventDefault();state.selectedSearch=Math.max(0,state.selectedSearch-1);renderSearch();}if(e.key==='Enter'&&state.currentSearch?.[state.selectedSearch]){location.hash=`#/${state.currentSearch[state.selectedSearch].slug}`;closeSearch();}});
$('#searchResults').addEventListener('click',e=>{if(e.target.closest('a'))closeSearch();});
window.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();openSearch();}if(e.key==='Escape')closeSidebar();});
window.addEventListener('hashchange',route);window.addEventListener('click',e=>{const a=e.target.closest('a[href^="#/"]');if(a&&$('#sidebar').classList.contains('open'))closeSidebar();});
init().catch(err=>{$('#article').innerHTML=`<div class="error-card">${esc(err.message)}</div>`;});
