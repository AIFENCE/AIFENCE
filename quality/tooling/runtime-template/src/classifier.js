import { normalizeName } from './parser.js';

const TYPE_RULES = [
  {type:'Marketplace / E-Commerce', re:/\b(e-?commerce|marketplace|storefront|online shop|shopping cart|checkout|product catalog)\b/i, weight:100},
  {type:'Dashboard', re:/\b(dashboard|command center|analytics board|reporting ui|scorecard|(?:contract renewal|service renewal|subscription renewal|customer renewal|renewal|portfolio|risk|revenue|finance|procurement|compliance|support|sales) (?:monitoring )?workspace)\b/i, weight:98},
  {type:'Native / Mobile App', re:/\b(?:native\s+(?:ios|android|mobile)(?:\s+[a-z0-9_\/-]+){0,6}\s+app|ios(?:\s+[a-z0-9_\/-]+){0,6}\s+app|android(?:\s+[a-z0-9_\/-]+){0,6}\s+app|mobile(?:\s+[a-z0-9_\/-]+){0,6}\s+app|iphone app|ipad app|swiftui app|jetpack compose app)\b/i, weight:97},
  {type:'Spreadsheet / Financial Model', re:/\b(spreadsheet(?:\s+[a-z0-9-]+){0,6}\s+model|excel(?:\s+[a-z0-9-]+){0,6}\s+model|google sheets(?:\s+[a-z0-9-]+){0,6}\s+model|financial model|budget model|forecast workbook|three[- ]statement model|spreadsheet|workbook|xlsx)\b/i, weight:96},
  {type:'Presentation / Deck', re:/\b(pitch deck|presentation|slide deck|slides|investor deck|keynote|powerpoint|pptx|executive(?:\s+[a-z0-9-]+){0,3}\s+deck|decision deck|board(?:\s+[a-z0-9-]+){0,3}\s+deck|(?:\d+[- ]slide\s+(?:[a-z0-9-]+\s+){0,4}deck)|board review deck|strategy deck|kickoff deck|briefing deck|operating plan deck|market trends briefing|(?:\d+[- ]slide(?:\s+[a-z0-9-]+){0,5}\s+briefing))\b/i, weight:95},
  {type:'Brand Identity / Logo', re:/\b(visual identity system|brand identity(?: system)?|identity system|logo system|visual identity|brand mark|logo)\b/i, weight:94},
  {type:'Email / Campaign', re:/\b((?:onboarding|invitation|reactivation|welcome|lifecycle|nurture|renewal|marketing|customer|member)[- ]email(?:\s+campaign|\s+sequence)?|email campaign|email sequence|newsletter campaign|drip campaign|invitation campaign|(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)[- ]email(?:\s+[a-z0-9-]+){0,4}\s+(?:sequence|campaign))\b/i, weight:93},
  {type:'Marketing Creative', re:/\b(ad creative|campaign creative|social creative|banner campaign|storyboard|video storyboard|creative concept|poster|billboard)\b/i, weight:92},
  {type:'CLI / Developer Tool', re:/\b(cli(?:\s+developer)?\s+tool|cli|command[- ]line(?:\s+utility|\s+tool)?|terminal tool|developer tool|devtool|command line utility)\b/i, weight:91},
  {type:'Fixed-Format Document / PDF', re:/\b(pdf|fixed analytical report|fixed[- ]format(?:\s+(?:document|report|memo))?|print[- ]ready report|print ready report|(?:print[- ]ready|board[- ]ready|publication[- ]ready|executive[- ]ready|client[- ]ready)\s+(?:(?:analytical|assessment|evaluation|findings|review|decision|implementation|compliance|operations?|strategy)\s+){0,3}(?:report|memo)|(?:assessment|evaluation|findings)\s+report\s+(?:pdf|document)|brochure pdf|whitepaper pdf|investment committee memo|policy memorandum|internal policy memo|experiment analysis report|system design report)\b/i, weight:90},
  {type:'Web App / SaaS / Portal', re:/\b(saas|web app|customer portal|admin portal|client portal|portal|workspace|queue|scheduler|crm|web platform)\b/i, weight:89},
  {type:'Website / Landing Page', re:/\b(website|landing page|marketing site|homepage|site redesign|web page|public site)\b/i, weight:88},
  {type:'Design System', re:/\b(design system|component library|design tokens)\b/i, weight:80},
  {type:'Feature Plan', re:/\b(feature plan|product spec|feature specification|requirements document)\b/i, weight:79},
  {type:'API', re:/\b(api|endpoint|openapi|rest api|graphql)\b/i, weight:78},
  {type:'Brand Strategy', re:/\b(brand strategy|positioning|messaging platform|brand platform)\b/i, weight:77},
  {type:'SEO/GEO/AEO Content', re:/\b(seo|geo|aeo|search optimization|answer engine)\b/i, weight:76},
  {type:'Security Architecture', re:/\b(security architecture|threat model|security design)\b/i, weight:75},
  {type:'Legal Policies', re:/\b(privacy policy|terms of service|legal policy|cookie policy)\b/i, weight:74},
  {type:'Org / Jobs / SOPs', re:/\b(sop|standard operating procedure|runbook|work instruction|operating procedure|job description|role specification|operations manual)\b/i, weight:73},
  {type:'Documentation / Repository Architecture', re:/\b(documentation|repository architecture|readme|developer guide|technical document|report|memo|postmortem)\b/i, weight:60},
];

const MODE=[['Prototype',/\bprototype\b/i],['MVP',/\bmvp\b/i],['Mockup',/\bmockup\b/i],['Wireframe',/\bwireframe\b/i],['Demo',/\bdemo\b/i],['Concept',/\bconcept(?: only)?\b/i]];
const FIDELITY=[
 ['Low-Fidelity',/\b(low[- ]?fidelity|lo[- ]?fi|rough wireframe|skeletal wireframe|rough sketch)\b/i],
 ['High-Fidelity',/\b(high[- ]?fidelity|hi[- ]?fi|premium|polished|production[- ]grade|production quality)\b/i],
 ['Exploratory',/\b(exploratory|rough concept|early concept)\b/i],
];
const VISUAL_TYPES=new Set(['Website / Landing Page','Web App / SaaS / Portal','Marketplace / E-Commerce','Dashboard','Native / Mobile App','Presentation / Deck','Brand Identity / Logo','Email / Campaign','Marketing Creative','Fixed-Format Document / PDF','Design System','Brand Strategy','Documentation / Repository Architecture']);

const INDUSTRY_ALIASES = [
  ['Landscaping & Horticulture', /\b(landscap(?:e|ing|er|ers)|lawn care|horticulture)\b/i],
  ['Nonprofits & NGOs', /\b(nonprofit|non-profit|ngo|charity|hospital foundation|community foundation|philanthrop(?:y|ic))\b/i],
  ['Dental Industry', /\b(dental|dentist|dentistry)\b/i],
  ['Healthcare', /\b(hospital|clinic|healthcare|medical practice|physician|patient care)\b/i],
  ['Museums', /\b(museum|museums)\b/i],
  ['Solar Energy', /\b(solar installer|solar energy|photovoltaic|pv installer)\b/i],
  ['Insurance', /\b(insurer|insurance company|claims insurer)\b/i],
  ['Robotics & Automation', /\b(industrial robotics|robotics integration|robotics integrator|automation integrator)\b/i],
  ['Transportation & Logistics', /\b(logistics|freight operator|freight|shipment operations)\b/i],
  ['Cybersecurity', /\b(cybersecurity|cyber incident|security operations|incident triage)\b/i],
  ['Public Transportation', /\b(public transit|regional transit|transit network)\b/i],
  ['Financial Services', /\b(fintech|banking|bank|credit union|wealth management|investment firm|payments company)\b/i],
  ['Software', /\b(software company|saas company|developer platform|cloud software)\b/i],
  ['Home Services', /\b(home services?|residential contractor|local contractor|plumbing company|hvac company|roofing company)\b/i],
];

const EXPOSURE_RULES = [
  {key:'authentication', positive:/\b(auth(?:entication)?|login|log in|sign in|account|password|session|sso|oauth)\b/i, negative:/\b(no|without|does not have|doesn't have|exclude|excluding|not using|do not use)\s+(?:user\s+)?(?:auth(?:entication)?|login|log in|sign in|accounts?|passwords?|sso|oauth)\b/i},
  {key:'permissions', positive:/\b(permissions?|role[- ]based|rbac|access control|admin roles?|user roles?|admin and operator permissions?|operator permissions?)\b/i, negative:/\b(no|without|exclude|excluding)\s+(?:permissions?|rbac|access control|roles?)\b/i},
  {key:'payments', positive:/\b(payments?|billing|checkout|card payments?|subscription charge|transactions?|money movement|payouts?)\b/i, negative:/\b(no|without|exclude|excluding|does not process|doesn't process)\s+(?:(?:financial|payment)\s+)?(?:payments?|billing|checkout|transactions?|money movement|payouts?)\b/i},
  {key:'sensitiveData', positive:/\b(health data|medical data|financial data|ssn|social security number|pii|personal data|patient data|bank data|biometric)\b/i, negative:/\b(?:no\s+(?:data collection|pii|personal data|health data|medical data|financial data|ssn|sensitive data|biometrics?)|without\s+(?:data collection|pii|personal data|health data|medical data|financial data|ssn|sensitive data|biometrics?)|(?:does not|doesn't) collect\s+(?:any\s+)?(?:data|pii|personal data|health data|medical data|financial data|ssn|sensitive data|biometrics?)|(?:exclude|excluding)\s+(?:pii|personal data|health data|medical data|financial data|ssn|sensitive data|biometrics?))\b/i},
  {key:'uploadsUgc', positive:/\b(upload|user[- ]generated|ugc|attachment|post content|comments?)\b/i, negative:/\b(no|without|exclude|excluding)\s+(?:uploads?|ugc|user[- ]generated content|attachments?|comments?)\b/i},
  {key:'location', positive:/\b(location data|gps|geolocation|tracking|movement history|live location)\b/i, negative:/\b(no|without|does not collect|doesn't collect|exclude|excluding)\s+(?:location data|gps|geolocation|tracking)\b/i},
  {key:'aiActions', positive:/\b(ai agent|autonomous agent|tool execution|model action|automated decision|autonomous action)\b/i, negative:/\b(no|without|exclude|excluding)\s+(?:ai agents?|autonomous actions?|automated decisions?)\b/i},
  {key:'minors', positive:/\b(minors?|children|child|students? under|youth)\b/i, negative:/\b(no|without|not for|exclude|excluding)\s+(?:minors?|children|students?|youth)\b/i},
  {key:'backend', positive:/\b(backend|back[- ]end|server|database|api integration|serverless|database)\b/i, negative:/\b(front[- ]end only|frontend only|no backend|without backend|static only|client[- ]side only)\b/i},
  {key:'publicFacing', positive:/\b(public|customer[- ]facing|consumer[- ]facing|marketing|website|landing page|homepage)\b/i, negative:/\b(internal(?: only)?|employee[- ]only|private internal|back office only)\b/i},
];

const PROFILE_RISK_EXPANSIONS={
 'financial-regulated':['financial-regulated'],
 'health-sensitive':['health-sensitive'],
 'security-identity':['security-identity'],
 'location-data':['location-data'],
 'education-or-minors':['education-or-minors'],
 'legal-regulated':['legal-regulated'],
 'automated-decisioning':['automated-decisioning'],
 'age-restricted':['age-restricted'],
 'physical-safety':['physical-safety'],
 'public-sector':['public-sector'],
 'critical-infrastructure':['critical-infrastructure'],
 'platform-trust-safety':['platform-trust-safety'],
};

const STOP = new Set(['industry','services','service','and','the','for','customer','experience','operations','business','solutions','technology','technologies','company','group','systems','system','global']);
function tokens(s=''){return normalizeName(s).split(' ').filter(Boolean);}
function meaningful(s=''){return tokens(s).filter(x=>x.length>2 && !STOP.has(x));}
function phraseRegex(phrase=''){const p=normalizeName(phrase).split(' ').filter(Boolean).map(x=>x.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('\\s+');return p?new RegExp(`\\b${p}\\b`,'i'):null;}
function uniq(a){return [...new Set(a)];}
function splitRiskOverlays(s=''){return s.replace(/`/g,'').split(',').map(x=>x.trim()).filter(x=>x&&x!=='standard');}
function expandProfileRisks(risks){return uniq(risks.flatMap(x=>[x,...(PROFILE_RISK_EXPANSIONS[x]||[])]));}

function industryAliasHit(request, profileRows){
  for(const [name,re] of INDUSTRY_ALIASES){
    if(!re.test(request)) continue;
    const row=profileRows.find(r=>normalizeName(r['Industry']||'')===normalizeName(name));
    if(row) return {row,score:0.98,specificity:name.length,reason:'semantic-alias'};
  }
  return null;
}

function industrySubjectText(request=''){
  let first=(request.split(/(?<=[.!?])\s+/)[0]||request).slice(0,360);
  // Capability negation describes artifact exposure, not business industry. Remove negated
  // spans before profile matching, then mask artifact/evaluation vocabulary that commonly
  // collides with industry names in adversarial and real holdout requests.
  first=first.replace(/\b(?:no|without|excluding?)\b[^,.;]{0,120}/gi,' ');
  first=first.replace(/\b(?:email[- ]shaped|email campaign|email sequence|onboarding email(?: campaign)?|invitation campaign|dashboard|command center|website|landing page|marketing site|homepage|public site|customer portal|admin portal|portal|mobile app|native app|spreadsheet|financial model|budget model|workbook|pitch deck|slide deck|presentation|\d+[- ]slide(?:\s+[a-z0-9-]+){0,4}\s+deck|pdf|fixed[- ]format|report|memo|memorandum|cli|command[- ]line|developer tool|insurance participation|architecture fit|adoption readiness|legal compliance|data recovery|recovery state|subscription assumptions|reporting deadline|dashboard metric|website url|portal reference|email[- ]shaped fields?|email fields?|education audience|payments? are explicitly disabled|payments? disabled)\b/gi,' ');
  return first;
}

export function inferIndustry(request, profileRows){
  const subject=industrySubjectText(request); const reqTokens=tokens(subject); const reqSet=new Set(reqTokens); const candidates=[];
  const alias=industryAliasHit(subject,profileRows); if(alias)candidates.push(alias);
  for(const row of profileRows){
    const name=row['Industry']||''; const ws=meaningful(name); if(!ws.length)continue;
    const exact=phraseRegex(name)?.test(subject) ?? false;
    const matched=ws.filter(w=>reqSet.has(w));
    let score=exact?1:matched.length/ws.length;
    // One generic token from a multi-token industry is insufficient. This prevents
    // foundation -> Foundation Models, homepage -> Home Services, report -> Port Operations.
    if(!exact && ws.length>1 && matched.length<2) score=0;
    if(!exact && ws.length===1 && matched.length===1) score=0.72;
    if(score>0)candidates.push({row,score,specificity:matched.reduce((a,w)=>a+w.length,0),reason:exact?'exact-phrase':'token-overlap'});
  }
  candidates.sort((a,b)=>b.score-a.score || b.specificity-a.specificity || (a.row['Industry']||'').localeCompare(b.row['Industry']||''));
  const best=candidates[0], second=candidates[1];
  if(!best || best.score<0.64) return {status:'unresolved',confidence:Number((best?.score??0).toFixed(2)),candidate:best?.row?.['Industry']??null,margin:null,reason:best?.reason??'no-match'};
  const margin=second?best.score-second.score:best.score;
  const ambiguous=second && margin<0.12 && best.score<0.99;
  const status=ambiguous?'candidate':(best.score>=0.9?'resolved':'candidate');
  const out={status,confidence:Number(best.score.toFixed(2)),margin:Number(margin.toFixed(2)),industry:best.row['Industry'],industryId:best.row['Industry ID'],reason:best.reason};
  if(status==='resolved') out.profiles={operating:best.row['Operating Profile'],product:best.row['Product Profile'],design:best.row['Design Profile'],halo:best.row['Halo Profile'],riskOverlays:best.row['Risk Overlays']};
  else out.candidate=best.row['Industry'];
  return out;
}

function detectArtifactTypes(request,hints={}){
  if(hints.creationType) return [{type:hints.creationType,index:0,weight:1000,source:'hint'}];
  const hits=[];
  for(const rule of TYPE_RULES){
    const m=rule.re.exec(request); if(m) hits.push({type:rule.type,index:m.index,end:m.index+m[0].length,weight:rule.weight,source:m[0]});
  }
  const inNegatedContext=(h)=>{
    const chunk=request.slice(Math.max(0,h.index-120),h.end+30);
    const rel=h.index-Math.max(0,h.index-120);
    const before=chunk.slice(0,rel);
    const lastContrast=Math.max(before.toLowerCase().lastIndexOf(' but '),before.toLowerCase().lastIndexOf(' however '),before.toLowerCase().lastIndexOf(' except '),before.lastIndexOf(';'),before.lastIndexOf('.'));
    const local=before.slice(lastContrast+1);
    return /\b(?:no|without|excluding?)\b[^.;]{0,100}$/i.test(local);
  };
  const decisionWorkspace=/\b(?:contract renewal|service renewal|subscription renewal|customer renewal|renewal|portfolio|risk|revenue|finance|procurement|compliance|support|sales) (?:monitoring )?workspace\b/i.test(request)
    && /\b(?:renewal|status|health|risk|deadline|expiration|portfolio|score|metric|review|monitor|forecast|evidence|decision|coverage)\b/i.test(request)
    && !/\b(?:record editor|edit records?|create records?|workflow builder|task management|case management|form builder|compose|authoring)\b/i.test(request);
  const incidental=(h)=>{
    const tail=request.slice(h.end,h.end+45).toLowerCase();
    if(inNegatedContext(h)) return true;
    if(h.type==='Dashboard' && /^(?:\s+)(?:metric|metrics|reference|references|field|fields|in appendix)\b/.test(tail)) return true;
    if(h.type==='Web App / SaaS / Portal' && /^(?:\s+)(?:reference|references|field|fields|url)\b/.test(tail)) return true;
    if(h.type==='Web App / SaaS / Portal' && /^workspace$/i.test(String(h.source||'').trim()) && decisionWorkspace) return true;
    if(h.type==='Website / Landing Page' && /^(?:\s+)(?:url|field|fields|reference|references)\b/.test(tail)) return true;
    return false;
  };
  const deoverlapped=hits.filter(h=>!(h.type==='Documentation / Repository Architecture' && hits.some(o=>o.type!=='Documentation / Repository Architecture' && o.index<=h.index && o.end>=h.end)));
  const filtered=deoverlapped.filter(h=>!incidental(h)).sort((a,b)=>a.index-b.index || b.weight-a.weight);
  if(filtered.length<=1) return filtered.length?filtered:[{type:'Documentation / Repository Architecture',index:0,weight:0,source:'fallback'}];
  // Core 1.8.8: preserve explicit enumerated multi-deliverable graphs while allowing
  // harmless child modifiers between the conjunction and artifact noun. Modifiers such as
  // public/internal/responsive/executive/customer-facing describe the child; they do not
  // terminate the coordinated deliverable list. Keep the modifier lexicon intentionally
  // bounded so prose that merely mentions multiple artifact nouns is not promoted to composite.
  const compactArtifactGaps=filtered.slice(1).map((h,i)=>request.slice(filtered[i].end??filtered[i].index,h.index));
  const harmlessModifier=String.raw`(?:public|internal|responsive|interactive|executive|customer[- ]facing|client[- ]facing|member[- ]facing|employee[- ]facing|mobile|web|native|print[- ]ready|production|premium|high[- ]fidelity)`;
  const compactGapRe=new RegExp(String.raw`^[\s,;/&+\-]*(?:(?:and|plus|along with|as well as)[\s,;/&+\-]*)?(?:(?:${harmlessModifier})[\s,;/&+\-]*){0,3}$`,'i');
  const explicitArtifactList=filtered.length>=3
    && compactArtifactGaps.every(g=>g.length<=64 && compactGapRe.test(g))
    && compactArtifactGaps.some(g=>/\b(?:and|plus|along with|as well as)\b/i.test(g));
  if(explicitArtifactList) return filtered;
  // Multiple artifact nouns are often incidental content. Compile a composite only when
  // deliverables are explicitly coordinated; otherwise prefer the most specific artifact class.
  const coordinated=(left,right)=>{
    const between=request.slice(left.end??left.index,right.index).toLowerCase();
    const shortAnd=/\band\b/.test(between) && between.trim().length<=45;
    return /\b(?:plus|along with|together with|as well as|and also)\b/.test(between)
      || shortAnd
      || /\bwith\s+(?:a|an|the)\s+(?:marketing|public|customer|admin|mobile|brand|financial|slide|presentation)\b/.test(between)
      || /\bboth\b/i.test(request.slice(Math.max(0,left.index-40),right.index));
  };
  const keep=[filtered[0]];
  for(let i=1;i<filtered.length;i++) if(coordinated(keep.at(-1),filtered[i])) keep.push(filtered[i]);
  if(keep.length>1) return keep;
  const specific=filtered.filter(h=>h.type!=='Documentation / Repository Architecture');
  const deliverableRank={'Spreadsheet / Financial Model':130,'Presentation / Deck':128,'Fixed-Format Document / PDF':126,'CLI / Developer Tool':124,'Email / Campaign':122,'Brand Identity / Logo':120,'Marketing Creative':118,'Native / Mobile App':116,'Marketplace / E-Commerce':110,'Dashboard':108,'Web App / SaaS / Portal':106,'Website / Landing Page':104};
  return specific.length?[specific.sort((a,b)=>(deliverableRank[b.type]??b.weight)-(deliverableRank[a.type]??a.weight) || a.index-b.index)[0]]:[filtered[0]];
}

function negatedSpans(request=''){
  // Capture coordinated lists such as "with no login or payments" without leaking negation
  // through contrast boundaries such as "no login, but payments enabled".
  const spans=[];
  const chunks=request.split(/[.;]|\bbut\b|\bhowever\b|\bexcept\b/i);
  for(const chunk of chunks){
    const re=/\b(?:no|without|excluding?|do not use|does not use|doesn't use)\b([^.;]{0,180})/ig;
    for(const m of chunk.matchAll(re)) spans.push(m[1]);
  }
  return spans;
}
function inferExposures(request,hints={}){
  const out={};
  const negated=negatedSpans(request);
  for(const rule of EXPOSURE_RULES){
    if(hints.exposures && Object.hasOwn(hints.exposures,rule.key)){
      out[rule.key]={state:hints.exposures[rule.key]?'present':'absent',source:'hint'};continue;
    }
    const coordinatedNegation=negated.some(span=>rule.positive.test(span));
    if(rule.negative.test(request) || coordinatedNegation) out[rule.key]={state:'absent',source:'explicit-negation'};
    else if(rule.positive.test(request)) out[rule.key]={state:'present',source:'request'};
    else out[rule.key]={state:'unknown',source:'unspecified'};
  }
  return out;
}

function inferBusinessModel(request){
  const rules=[['B2B',/\b(b2b|business customers?|enterprise|procurement|sales team|account executives?)\b/i],['B2C',/\b(b2c|consumers?|homeowners?|patients?|members?|shoppers?|diners?)\b/i],['Marketplace',/\b(marketplace|buyers? and sellers?|two[- ]sided|vendors?)\b/i],['Subscription',/\b(subscription|recurring revenue|membership|monthly plan|annual plan)\b/i],['Transactional',/\b(checkout|payments?|transactions?|orders?|bookings?)\b/i],['Public/Institutional',/\b(government|municipal|public sector|citizens?|agency)\b/i]];
  const hit=rules.find(([,re])=>re.test(request)); return hit?{value:hit[0],confidence:0.85,source:'request'}:{value:null,confidence:0,source:'unknown'};
}
function inferAudiences(request){
  const rules=[['Customers',/\b(customers?|clients?|buyers?|shoppers?|homeowners?)\b/i],['Administrators',/\b(admins?|administrators?|operators?|back office)\b/i],['Investors',/\b(investors?|investment committee|board)\b/i],['Employees',/\b(employees?|staff|team members?|crew)\b/i],['Patients',/\b(patients?)\b/i],['Citizens',/\b(citizens?|residents?|constituents?)\b/i],['Developers',/\b(developers?|engineers?|api users?)\b/i]];
  const hits=rules.filter(([,re])=>re.test(request)).map(([x])=>x); return hits.length?hits:['Unresolved'];
}
function inferUserRoles(request){
  const rules=[['Administrator',/\b(admins?|administrators?)\b/i],['Operator',/\b(operators?|dispatchers?|agents?)\b/i],['Manager',/\b(managers?|supervisors?|team leads?)\b/i],['Customer',/\b(customers?|clients?|members?|patients?|buyers?|homeowners?)\b/i],['Developer',/\b(developers?|engineers?|api users?)\b/i],['Investor/Board',/\b(investors?|investment committee|board members?)\b/i],['Employee',/\b(employees?|staff|field technicians?|crew)\b/i]];
  const hits=rules.filter(([,re])=>re.test(request)).map(([x])=>x); return hits.length?hits:['Unresolved'];
}
function inferPlatform(types){
  if(types.includes('Native / Mobile App'))return 'Native Mobile';
  if(types.some(x=>['Website / Landing Page','Web App / SaaS / Portal','Marketplace / E-Commerce','Dashboard'].includes(x)))return 'Web';
  if(types.includes('Spreadsheet / Financial Model'))return 'Spreadsheet';
  if(types.includes('Presentation / Deck'))return 'Slides';
  if(types.includes('CLI / Developer Tool'))return 'CLI';
  if(types.includes('Fixed-Format Document / PDF'))return 'Fixed Format';
  return 'Mixed/Unresolved';
}
function inferReferenceInspirations(request){
  const patterns=[/\b([A-Z][A-Za-z0-9.+-]{1,30})[- ]like\b/g,/\b(?:inspired by|similar to|like)\s+([A-Z][A-Za-z0-9.+-]{1,30})\b/g];
  const refs=[]; for(const re of patterns){for(const m of request.matchAll(re))refs.push(m[1]);}
  return uniq(refs).map(name=>({reference:name,mode:'abstract-principles-only',prohibit:'direct structural or visual cloning'}));
}

function deriveRiskGraph(industry,exposures,request){
  const base=industry.status==='resolved'?expandProfileRisks(splitRiskOverlays(industry.profiles?.riskOverlays||'')):[];
  const present=k=>exposures[k]?.state==='present';
  const security=[]; const legal=[]; const safety=[]; const trust=[];
  if(present('authentication'))security.push('authentication');
  if(present('permissions'))security.push('permissions');
  if(present('payments')){security.push('payments');legal.push('payments');}
  if(present('sensitiveData')){security.push('sensitive-data');legal.push('sensitive-data');}
  if(present('uploadsUgc')){security.push('uploads-ugc');legal.push('platform-trust-safety');trust.push('platform-trust-safety');}
  if(present('location')){security.push('location');legal.push('location-data');}
  if(present('aiActions')){security.push('ai-actions');legal.push('automated-decisioning');}
  if(present('minors'))legal.push('education-or-minors');
  for(const overlay of base){
    if(['financial-regulated','health-sensitive','legal-regulated','education-or-minors','public-sector','age-restricted','automated-decisioning','location-data'].includes(overlay)) legal.push(overlay);
    if(['security-identity','critical-infrastructure'].includes(overlay)) security.push(overlay);
    if(overlay==='platform-trust-safety'){trust.push(overlay);legal.push(overlay);}
    if(overlay==='physical-safety') safety.push(overlay);
    // Industry overlays do not manufacture data/feature exposure. Sensitive security
    // controls require matching actual exposure, except critical-infrastructure baseline.
    if(overlay==='financial-regulated' && (present('payments')||present('sensitiveData')))security.push(overlay);
    if(overlay==='health-sensitive' && present('sensitiveData'))security.push(overlay);
    if(overlay==='security-identity' && (present('authentication')||present('permissions')||present('sensitiveData')))security.push(overlay);
  }
  if(/\b(regulated|compliance|clinical|credit union|bank|legal advice|legal deadline|regulator)\b/i.test(request))legal.push('regulated');
  return {industryOverlays:base,security:uniq(security),legal:uniq(legal),safety:uniq(safety),trustSafety:uniq(trust),all:uniq([...base,...security,...legal,...safety,...trust])};
}

export function classifyRequest(request, profileRows=[], hints={}){
  const artifacts=detectArtifactTypes(request,hints);
  const types=uniq(artifacts.map(x=>x.type));
  const type=types[0];
  const explicitMode=hints.deliveryMode || MODE.find(([,re])=>re.test(request))?.[0];
  const mode=explicitMode || 'Production';
  const substantial=hints.substantial ?? !/\b(tiny|one[- ]line|single sentence|minor copy edit)\b/i.test(request);
  const explicitFidelity=hints.visualFidelity || FIDELITY.find(([,re])=>re.test(request))?.[0];
  let visualFidelity='Not-Applicable';
  if(types.some(x=>VISUAL_TYPES.has(x))){
    if(explicitFidelity) visualFidelity=explicitFidelity;
    else if(mode==='Wireframe') visualFidelity='Low-Fidelity';
    else if(mode==='Mockup' && /\b(rough|low[- ]?fi|lo[- ]?fi)\b/i.test(request)) visualFidelity='Low-Fidelity';
    else visualFidelity=substantial?'High-Fidelity':'Exploratory';
  }
  const productionIntent=mode==='Production';
  const qualityClosureIntent=substantial && (productionIntent || (types.some(x=>VISUAL_TYPES.has(x)) && visualFidelity==='High-Fidelity'));
  const industry=hints.industry ? {status:'user-supplied',confidence:1,margin:1,industry:hints.industry,reason:'hint'} : inferIndustry(request,profileRows);
  if(industry.status==='user-supplied'){
    const row=profileRows.find(r=>normalizeName(r.Industry||'')===normalizeName(hints.industry));
    if(row){industry.industryId=row['Industry ID'];industry.profiles={operating:row['Operating Profile'],product:row['Product Profile'],design:row['Design Profile'],halo:row['Halo Profile'],riskOverlays:row['Risk Overlays']};}
  }
  const exposures=inferExposures(request,hints);
  const riskGraph=deriveRiskGraph(industry,exposures,request);
  const contextGraph={
    industry:{value:industry.industry||industry.candidate||null,status:industry.status,confidence:industry.confidence,margin:industry.margin??null},
    subindustry:{value:hints.subindustry||null,status:hints.subindustry?'resolved':'unknown'},
    businessModel:inferBusinessModel(request),audiences:inferAudiences(request),userRoles:inferUserRoles(request),
    artifactExposure:exposures,publicOrInternal:exposures.publicFacing.state==='present'?'public':exposures.publicFacing.state==='absent'?'internal':'unknown',
    platform:inferPlatform(types),revenueModel:/\b(subscription|membership)\b/i.test(request)?'subscription':/\b(checkout|order|transaction|payment)\b/i.test(request)?'transactional':'unknown',
    dataClasses:[...(exposures.sensitiveData.state==='present'?['sensitive']:[]),...(exposures.location.state==='present'?['location']:[]),...(exposures.minors.state==='present'?['minors']:[])],
    authentication:exposures.authentication.state,transactions:exposures.payments.state,backendStatus:exposures.backend.state,
    integrationStatus:/\b(integration|api|webhook|stripe|salesforce|hubspot)\b/i.test(request)?'present':'unknown',jurisdiction:hints.jurisdiction||null,
    contentProvenance:/\b(sample|demo|placeholder|synthetic)\b/i.test(request)?'sample-or-demo':'unknown',implementationMaturity:mode,visualFidelity,
    referenceInspirations:inferReferenceInspirations(request)
  };
  const artifactGraph={kind:types.length>1?'composite':'single',nodes:types.map((t,i)=>({id:`artifact-${i+1}`,type:t,role:i===0?'primary':'supporting',source:artifacts.find(a=>a.type===t)?.source||null})),sharedContext:['brand','industry','truth-boundaries','risk','audience']};
  return {creationType:type,creationTypes:types,artifactGraph,deliveryMode:mode,implementationMaturity:mode,visualFidelity,productionIntent,qualityClosureIntent,substantial,industry,contextGraph,riskGraph,risks:riskGraph.all};
}
