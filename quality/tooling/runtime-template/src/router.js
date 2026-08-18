import { CoreProvider } from './core-provider.js';
import { classifyRequest } from './classifier.js';
import { tableAfterHeading, normalizeName } from './parser.js';
import { RUNTIME_VERSION } from './config.js';

const CONTRACT={
 'Website / Landing Page':'marketing-website','Web App / SaaS / Portal':'saas-web-app','Marketplace / E-Commerce':'ecommerce-marketplace','Dashboard':'dashboard',
 'Native / Mobile App':'native-mobile-app','Presentation / Deck':'presentation-deck','Spreadsheet / Financial Model':'spreadsheet-financial-model','Brand Identity / Logo':'brand-identity',
 'Email / Campaign':'email-campaign','Marketing Creative':'marketing-creative','CLI / Developer Tool':'cli-developer-tool','Fixed-Format Document / PDF':'fixed-format-document',
 'Org / Jobs / SOPs':'operations-workflow','Documentation / Repository Architecture':'document-report'
};
const CONTRACT_PARENTS={
 'local-service-website':['marketing-website'],'dashboard':['saas-web-app'],'ecommerce-marketplace':['marketing-website','saas-web-app'],'fixed-format-document':['document-report']
};
const MODULE_FILE={
 INDUSTRIES:'INDUSTRIES.md',ARTIFACT_CONTRACTS:'ARTIFACT_CONTRACTS.md',FEATURES:'FEATURES.md',DESIGN:'DESIGN.md',CREATIVE:'CREATIVE.md',CRAFT:'CRAFT.md',FEATURE_COMPILER:'FEATURE_COMPILER.md',GENERICITY:'GENERICITY.md',COMPONENT_COMPILER:'COMPONENT_COMPILER.md',CRITICS:'CRITICS.md',QUALITY_FLOORS:'QUALITY_FLOORS.md',HALO:'HALO.md',SEO_GEO_AEO:'SEO_GEO_AEO.md',TERMINOLOGY:'TERMINOLOGY.md',STRUCTURE:'STRUCTURE.md',ASSETS:'ASSETS.md',SECURITY:'SECURITY.md',LEGAL:'LEGAL.md',JOBS:'JOBS.md',ACCESSIBILITY_EVIDENCE:'ACCESSIBILITY_EVIDENCE.md',COMPLETENESS:'COMPLETENESS.md',TRUTH_BOUNDARIES:'TRUTH_BOUNDARIES.md',RESPONSIVE_COMPOSITION:'RESPONSIVE_COMPOSITION.md',DOCUMENT_CRAFT:'DOCUMENT_CRAFT.md',OPERATIONAL_PROCEDURE_COMPILER:'OPERATIONAL_PROCEDURE_COMPILER.md',PROCEDURE_AUTHORITY:'PROCEDURE_AUTHORITY.md',DECISION_RIGHTS:'DECISION_RIGHTS.md',OPERATIONAL_EVIDENCE:'OPERATIONAL_EVIDENCE.md',KPI_GOVERNANCE:'KPI_GOVERNANCE.md',FEATURE_DEPTH:'FEATURE_DEPTH.md',USABILITY_CLOSURE:'USABILITY_CLOSURE.md',VISUAL_FINISH:'VISUAL_FINISH.md',RESPONSIVE_DETAIL_CLOSURE:'RESPONSIVE_DETAIL_CLOSURE.md',QUALITY_MEASUREMENT:'QUALITY_MEASUREMENT.md',SEMANTIC_ROUTING:'SEMANTIC_ROUTING.md',RETRIEVAL_INTELLIGENCE:'RETRIEVAL_INTELLIGENCE.md',BENCHMARK_PIPELINE:'BENCHMARK_PIPELINE.md',EVIDENCE_ADAPTER:'EVIDENCE_ADAPTER.md',RELEASE_PROVENANCE:'RELEASE_PROVENANCE.md',NONWEB_FIRST_PASS:'NONWEB_FIRST_PASS.md',FAMILY_DEPTH_CLOSURE:'FAMILY_DEPTH_CLOSURE.md',MATERIALIZATION_CLOSURE:'MATERIALIZATION_CLOSURE.md',EMISSION_PREFLIGHT:'EMISSION_PREFLIGHT.md'
};
const INTERFACE_TYPES=['Website / Landing Page','Web App / SaaS / Portal','Marketplace / E-Commerce','Dashboard','Native / Mobile App'];
const WEB_TYPES=['Website / Landing Page','Web App / SaaS / Portal','Marketplace / E-Commerce','Dashboard'];
const VISUAL_ARTIFACT_TYPES=[...INTERFACE_TYPES,'Presentation / Deck','Brand Identity / Logo','Email / Campaign','Marketing Creative','Fixed-Format Document / PDF','Design System','Brand Strategy','Documentation / Repository Architecture'];
const PUBLIC_VISUAL_TYPES=['Website / Landing Page','Marketplace / E-Commerce','Presentation / Deck','Brand Identity / Logo','Email / Campaign','Marketing Creative'];
const FAMILY_CLOSURE_TYPES=new Set(['Native / Mobile App','Presentation / Deck','Spreadsheet / Financial Model','Brand Identity / Logo','Email / Campaign','Marketing Creative','CLI / Developer Tool','Fixed-Format Document / PDF']);
const FAMILY_DEPTH_TYPES=new Set(['Website / Landing Page','Native / Mobile App','Brand Identity / Logo','Email / Campaign','CLI / Developer Tool']);
const MATERIALIZATION_TYPES=new Set(['Website / Landing Page','Native / Mobile App','Brand Identity / Logo','Email / Campaign','CLI / Developer Tool','Presentation / Deck','Spreadsheet / Financial Model','Fixed-Format Document / PDF','Marketing Creative']);
const EMISSION_TYPES=new Set(['Website / Landing Page','Web App / SaaS / Portal','Marketplace / E-Commerce','Dashboard','Native / Mobile App','Presentation / Deck','Spreadsheet / Financial Model','Brand Identity / Logo','Email / Campaign','Marketing Creative','CLI / Developer Tool','Fixed-Format Document / PDF','Documentation / Repository Architecture']);
const EXECUTABLE_TYPES=new Set(['Website / Landing Page','Web App / SaaS / Portal','Marketplace / E-Commerce','Dashboard','Native / Mobile App','CLI / Developer Tool']);

const FAMILY_EMISSION_REQUIREMENTS={
 website:['decisions','proof_points','actions','uncertainties_or_objections','continuations'],
 'web-app':['user_jobs','actions','states','recovery_paths','outcomes'],
 dashboard:['decision_questions','evidence_views','actions','states','recovery_or_handoff'],
 mobile:['user_jobs','actions','states','recovery_paths','outcomes'],
 brand:['identity_rules','typography_rules','color_rules','composition_rules','imagery_or_iconography_rules','applications','misuse_constraints'],
 email:['audience_states','message_jobs','ctas','sequence_transitions','measurement_events','compliance_or_truth_boundaries'],
 cli:['commands','help_surfaces','configuration_rules','io_contracts','exit_semantics','recovery_guidance'],
 presentation:['storyline_beats','evidence_points','implications','decisions_or_requests','audience_takeaways'],
 spreadsheet:['inputs','calculations_or_outputs','scenarios','decision_surfaces','provenance_markers','editable_boundaries'],
 'fixed-document':['questions_or_issues','evidence_points','findings_or_conclusions','implications_or_actions','reader_takeaways','provenance_markers'],
 documentation:['questions_or_tasks','evidence_or_examples','instructions_or_findings','next_actions','provenance_markers'],
 'marketing-creative':['message_layers','proof_elements','ctas','visual_rules','channel_context'],
 composite:['shared_context_rules','shared_identifiers_or_assumptions','cross_artifact_continuity','child_acceptance_refs','project_provenance_boundaries']
};


const PHASE_BUDGETS={classification:6,contract:3,'feature-compilation':4,'creative-direction':5,'structural-fingerprint':3,'component-compilation':3,implementation:4,'render-inspection':4,critics:3,repair:1,acceptance:3};
const PRIORITY_RANK={P0:0,P1:1,P2:2,P3:3};
const PINNED_BY_PHASE={
 'feature-compilation':new Set(['Dense-UI adaptation','Cross-device continuity']),
 'creative-direction':new Set(['Differentiation ledger','Concept selection rubric','Brand-specific fingerprint','Anti-template heuristics','Memorability test']),
 'structural-fingerprint':new Set(['Repetition detector'])
};

const PHASE_CAPABILITIES={
 classification:['Authoritative-entry verification','Instruction-precedence ledger','Lazy-load budget','Requirement completeness model','Unknown-fact policy','Goal hierarchy','Audience resolution','Scope boundary','Canonical-industry confidence','Duplicate-subindustry disambiguation','Independent-profile dimensions','Profile confidence scores','Creation-type classifier','Production-vs-concept distinction','Deliverable acceptance contract','Risk-overlay composition','Risk-trigger re-evaluation'],
 contract:['Artifact Contract Resolution','Artifact Contract Completeness','Claim-evidence pairing','Evidence Assumption Sample Provenance'],
 'feature-compilation':['Feature Specification Compiler','Feature Information Action Model','User Job State Data Model','Feature Depth Resolution','Feature State Completeness','Feature Depth Closure','Responsive Feature Recomposition','Dense-UI adaptation','Cross-device continuity'],
 'creative-direction':['Benchmark quality filter','Differentiation ledger','Three-direction exploration quality','Concept selection rubric','Brand-specific fingerprint','Anti-template heuristics','Visual tension control','Memorability test','Brand-character synthesis'],
 'structural-fingerprint':['Structural Fingerprint Generation','Genericity Similarity Rejection','Section-purpose uniqueness','Macro-rhythm system','Hero composition diversity','Repetition detector'],
 'component-compilation':['Component Design Compiler','Component Variant State Matrix','Component Anatomy Quality','Feature To Component Mapping','Icon-system-selection','Iconography-coverage-audit','Card Surface Specificity','Interaction Affordance Microdetail'],
 implementation:['Semantic-component mapping','Component API discipline','No-dead-control gate','Implementation-fidelity review','Broken-path detection','Responsive recomposition','Mobile-first priority check','Performance-budget declaration','Cross-browser smoke testing'],
 'render-inspection':['Evidence-based completion','Rendered-pixel review','Visual-regression fixtures','Accessibility Evidence Matrix','Keyboard Focus & Dynamic Feedback','Perceptual Hierarchy Finish','Typographic Spatial Surface Calibration','Final Craft Evidence'],
 critics:['Visual Quality Critic','Feature Depth Critic','Accessibility Responsive Critic','Truth Implementation Critic','Genericity Critic'],
 repair:['Repair Plan Prioritization'],
 acceptance:['Completion Coverage Ledger','Category Floor Enforcement','Quality Floor Measurement Calibration','Quality-score evidence','Deliverable manifest','Self-contained delivery check','Handoff readiness']
};

function cleanModuleToken(x){return x.replace(/`/g,'').replace(/\b(optionally|usually)\b/ig,'').replace(/\bwhen needed\b/ig,'').replace(/\bwhen triggered\b/ig,'').replace(/\bas applicable\b/ig,'').trim();}
function parseModuleCell(cell){return cell.split(/[;,]/).map(cleanModuleToken).filter(x=>/^[A-Z][A-Z0-9_]+$/.test(x));}
function nums(s=''){return (s.match(/\b(?:0?[1-9]|[12][0-9]|3[01])\b/g)||[]).map(Number);}
function uniq(a){return [...new Set(a)];}
function present(c,key){return c.contextGraph?.artifactExposure?.[key]?.state==='present';}
function absent(c,key){return c.contextGraph?.artifactExposure?.[key]?.state==='absent';}

export class AifenceRouter {
 constructor(core=new CoreProvider()){this.core=core; this.readme=this.core.read('README.md'); this.index=this.core.read('CONTROL_INDEX.md');}
 creationRoutes(){return tableAfterHeading(this.readme,'# Creation-Type Router');}
 validationRoutes(){return tableAfterHeading(this.readme,'# Creation Validation Matrix');}
 bundles(){return tableAfterHeading(this.index,'# Activation Bundles');}
 routeFor(type){return this.creationRoutes().find(r=>normalizeName(r['Creation Type'])===normalizeName(type));}
 validationFor(type){return this.validationRoutes().find(r=>normalizeName(r['Creation Type'])===normalizeName(type));}
 contractFor(type,request,c){
   let base=CONTRACT[type]||null;
   if(type==='Website / Landing Page' && (/\b(local|plumb|hvac|electric|roof|tree care|remodel|contractor|home service|pest|lawn)\b/i.test(request)||/landscap/i.test(c.industry.industry||'')) && !/\b(industrial|municipal|enterprise|b2b platform)\b/i.test(request)) base='local-service-website';
   if(!base)return [];
   const chain=[...(CONTRACT_PARENTS[base]||[]),base];
   const regulated=c.riskGraph.legal.some(x=>['financial-regulated','health-sensitive','legal-regulated','education-or-minors','public-sector','regulated','age-restricted'].includes(x));
   const publicish=['Website / Landing Page','Marketplace / E-Commerce','Native / Mobile App','Web App / SaaS / Portal'].includes(type) && c.contextGraph.publicOrInternal!=='internal';
   if(regulated&&publicish&&!chain.includes('regulated-public-interface'))chain.push('regulated-public-interface');
   return uniq(chain);
 }
 bundleNamesFor(type,c,request){
   const names=['Core Creation'];
   if(c.industry.status!=='unresolved'||['Website / Landing Page','Web App / SaaS / Portal','Marketplace / E-Commerce','Org / Jobs / SOPs','Native / Mobile App','Brand Identity / Logo'].includes(type))names.push('Business Classification');
   if(c.substantial)names.push('Artifact Compilation');
   if(PUBLIC_VISUAL_TYPES.includes(type)||type==='Brand Strategy')names.push('Public-Facing Visual');
   if(INTERFACE_TYPES.includes(type))names.push('Front-End Product');
   if(present(c,'backend')||present(c,'authentication')||present(c,'permissions')||present(c,'payments')||present(c,'uploadsUgc')||/\b(api integration|webhook|database)\b/i.test(request))names.push('Stateful Application');
   if(['Website / Landing Page','SEO/GEO/AEO Content','Marketplace / E-Commerce'].includes(type))names.push('Search/Discovery');
   if(type==='Org / Jobs / SOPs')names.push('Operational System');
   if(['Documentation / Repository Architecture','Fixed-Format Document / PDF','Presentation / Deck'].includes(type))names.push('Document / Report');
   if(/\b(aifence|control plane|pack revision|control registry)\b/i.test(request))names.push('Pack Maintenance');
   return names;
 }
 capabilityPlan(c,domains,types){
   const phases=[]; const active=[]; const deferred=[]; const seen=new Set();
   const useVisual=types.some(t=>VISUAL_ARTIFACT_TYPES.includes(t));
   const useInteractive=types.some(t=>INTERFACE_TYPES.includes(t));
   for(const [phase,names] of Object.entries(PHASE_CAPABILITIES)){
     if(!c.substantial && !['classification','contract','acceptance'].includes(phase))continue;
     if(!useVisual && ['creative-direction','structural-fingerprint','component-compilation','render-inspection'].includes(phase))continue;
     if(!useInteractive && phase==='feature-compilation' && !types.some(t=>['Spreadsheet / Financial Model','CLI / Developer Tool'].includes(t)))continue;
     const candidates=[];
     for(const name of names){
       const cap=this.core.capability(name); if(!cap)continue;
       const d=Number(String(cap.domain).match(/^\d+/)?.[0]||0); if(d&&domains.length&&!domains.includes(d)&&![1,2,5,22,24,27,28].includes(d))continue;
       if(seen.has(cap.capabilityId))continue;seen.add(cap.capabilityId);
       const estimatedChars=cap.text?.length||0;
       candidates.push({capability:cap.capability,capabilityId:cap.capabilityId,domain:cap.domain,priority:cap.priority,path:cap.shard,phase,estimatedChars,estimatedTokens:Math.ceil(estimatedChars/4),reason:`${phase} capability required by resolved artifact/risk context`});
     }
     // Core 1.8 executes under a phase-local retrieval budget. P0/P1 and declaration order
     // determine the eager set; the remainder stays explicit and retrievable on demand rather
     // than silently disappearing or bloating first-pass context.
     candidates.sort((a,b)=>Number(!(PINNED_BY_PHASE[phase]?.has(a.capability)))-Number(!(PINNED_BY_PHASE[phase]?.has(b.capability))) || (PRIORITY_RANK[a.priority]??9)-(PRIORITY_RANK[b.priority]??9));
     const budget=PHASE_BUDGETS[phase]??candidates.length;
     const caps=candidates.slice(0,budget),later=candidates.slice(budget);
     active.push(...caps);
     deferred.push(...later.map(x=>({...x,deferredReason:'phase retrieval budget; retrieve on demand when triggered by evidence, critic, unresolved risk, or repair dependency'})));
     if(caps.length)phases.push({phase,budget,activeCapabilities:caps.map(x=>x.capabilityId),deferredCapabilities:later.map(x=>x.capabilityId),retrievalActions:caps.map(x=>({kind:'stable-section',path:x.path,id:x.capabilityId,reason:x.reason,estimatedChars:x.estimatedChars}))});
   }
   return {active,deferred,phases};
 }
 plan(request,hints={}){
   const c=classifyRequest(request,this.core.profileRows(),hints); const types=c.creationTypes;
   let modules=['SEMANTIC_ROUTING','RETRIEVAL_INTELLIGENCE','TRUTH_BOUNDARIES','COMPLETENESS','EVIDENCE_ADAPTER'];
   const bundleNames=[]; const artifactNodes=[];
   for(const node of c.artifactGraph.nodes){
     const route=this.routeFor(node.type); if(route)modules.push(...parseModuleCell(route['Primary Modules']||''));
     bundleNames.push(...this.bundleNamesFor(node.type,c,request));
     const chain=this.contractFor(node.type,request,c);const baseContract=chain.filter(x=>x!=='regulated-public-interface').at(-1)||chain.at(-1)||null;artifactNodes.push({...node,contractChain:chain,artifactContract:baseContract,overlays:chain.filter(x=>x==='regulated-public-interface')});
   }
   const uniqueBundles=uniq(bundleNames); const bundleRows=this.bundles().filter(r=>uniqueBundles.includes(r.Bundle));
   let domains=uniq(bundleRows.flatMap(r=>nums(r['Required domains'])));
   if(c.qualityClosureIntent)domains=uniq([...domains,30]);
   if(c.substantial&&types.some(t=>['Website / Landing Page','Web App / SaaS / Portal','Marketplace / E-Commerce','Dashboard','Native / Mobile App','Documentation / Repository Architecture','Fixed-Format Document / PDF','Presentation / Deck','Spreadsheet / Financial Model'].includes(t)))domains=uniq([...domains,29]);
   if(c.riskGraph.security.length)modules.push('SECURITY');
   if(c.riskGraph.legal.length|| (c.riskGraph.safety.length&&c.contextGraph.publicOrInternal!=='internal'))modules.push('LEGAL');
   if(types.some(t=>INTERFACE_TYPES.includes(t)))modules.push('ACCESSIBILITY_EVIDENCE','RESPONSIVE_COMPOSITION');
   if(domains.includes(11)&&c.substantial&&types.some(t=>VISUAL_ARTIFACT_TYPES.includes(t)))modules.push('ASSETS');
   if(domains.includes(29)&&types.some(t=>INTERFACE_TYPES.includes(t)))modules.push('FEATURE_DEPTH');
   if(domains.includes(30)){
     modules.push('QUALITY_MEASUREMENT');
     if(types.some(t=>INTERFACE_TYPES.includes(t)))modules.push('USABILITY_CLOSURE');
     if(types.some(t=>VISUAL_ARTIFACT_TYPES.includes(t)))modules.push('VISUAL_FINISH');
     if(types.some(t=>[...INTERFACE_TYPES,'Documentation / Repository Architecture','Org / Jobs / SOPs','Fixed-Format Document / PDF','Presentation / Deck'].includes(t)))modules.push('RESPONSIVE_DETAIL_CLOSURE');
   }
   if(types.some(t=>['Documentation / Repository Architecture','Fixed-Format Document / PDF','Presentation / Deck'].includes(t)))modules.push('DOCUMENT_CRAFT');
   if(types.some(t=>FAMILY_CLOSURE_TYPES.has(t)))modules.push('NONWEB_FIRST_PASS');
   if(c.qualityClosureIntent&&(types.some(t=>FAMILY_DEPTH_TYPES.has(t))||c.artifactGraph.kind==='composite'))modules.push('FAMILY_DEPTH_CLOSURE');
   if(c.qualityClosureIntent&&(types.some(t=>MATERIALIZATION_TYPES.has(t))||c.artifactGraph.kind==='composite'))modules.push('MATERIALIZATION_CLOSURE');
   if(c.qualityClosureIntent&&(types.some(t=>EMISSION_TYPES.has(t))||c.artifactGraph.kind==='composite'))modules.push('EMISSION_PREFLIGHT');
   if(types.includes('Org / Jobs / SOPs'))modules.push('JOBS','OPERATIONAL_PROCEDURE_COMPILER','PROCEDURE_AUTHORITY','DECISION_RIGHTS','OPERATIONAL_EVIDENCE','KPI_GOVERNANCE');
   if(/\b(benchmark|eval|regression|control coverage|lint)\b/i.test(request))modules.push('BENCHMARK_PIPELINE');
   if(/\b(release|ci|provenance|compatibility matrix|github actions)\b/i.test(request))modules.push('RELEASE_PROVENANCE');
   modules=uniq(modules).filter(m=>MODULE_FILE[m]&&this.core.exists(MODULE_FILE[m]));
   domains.sort((a,b)=>a-b);

   const cp=this.capabilityPlan(c,domains,types); const retrievalActions=[
     {kind:'stable-section',path:'README.md',id:'readme.creation-type-router',reason:'authoritative creation routing'},
     {kind:'stable-section',path:'SEMANTIC_ROUTING.md',id:'semantic-routing.root',reason:'semantic routing/context graph contract'},
     {kind:'stable-section',path:'RETRIEVAL_INTELLIGENCE.md',id:'retrieval-intelligence.root',reason:'capability-first lazy-loading contract'},
     ...cp.active.map(x=>({kind:'stable-section',path:x.path,id:x.capabilityId,phase:x.phase,reason:x.reason,estimatedChars:x.estimatedChars}))
   ];
   for(const n of artifactNodes)for(const contract of n.contractChain)retrievalActions.push({kind:'artifact-contract',path:`contracts/${contract}.md`,artifactId:n.id,reason:`${n.type} contract chain`});
   if(c.industry.status==='resolved'&&c.industry.industry)retrievalActions.push({kind:'profile',path:'PROFILE_MATRIX.md',industry:c.industry.industry,reason:'resolved semantic profile dimensions'});
   if(types.includes('Org / Jobs / SOPs')&&c.industry.profiles?.operating){const op=this.core.operationsRows().find(r=>normalizeName(r['Operating Profile'])===normalizeName(c.industry.profiles.operating));if(op?.File)retrievalActions.push({kind:'operations-profile',path:op.File.replace(/`/g,''),stableId:(op['Profile ID']||'').replace(/`/g,''),reason:'exact baseline operating-profile shard'});}

   const qa=[];for(const type of types){const vr=this.validationFor(type);if(vr)qa.push(vr['Required Validation']);}
   if(c.qualityClosureIntent)qa.push('Truth boundaries, completeness, direct implementation evidence, applicable quality floors, usability/visual closure when relevant, exhaustive enabled-control closure, 320/390 P0/P1 task preservation, and final adversarial review');
   if(types.includes('Org / Jobs / SOPs'))qa.push('Operational procedure schema + semantic validator + authority/evidence/KPI/lifecycle checks');
   const unresolved=[];
   if(c.industry.status==='candidate')unresolved.push({field:'industry/subindustry',blocking:false,action:`Candidate ${c.industry.candidate||c.industry.industry} is below semantic resolution confidence; do not activate its risk profile without corroboration.`});
   else if(c.industry.status==='unresolved'&&uniqueBundles.includes('Business Classification'))unresolved.push({field:'industry/subindustry',blocking:false,action:'Resolve only if industry-specific retrieval materially affects the artifact.'});
   if(c.riskGraph.legal.some(x=>['regulated','financial-regulated','health-sensitive','legal-regulated','public-sector'].includes(x))&&!c.contextGraph.jurisdiction)unresolved.push({field:'jurisdiction/authoritative sources',blocking:true,action:'Do not invent authoritative requirements; obtain current applicable sources before authoritative claims.'});

   const finalRetrievalActions=uniq(retrievalActions.map(x=>JSON.stringify(x))).map(x=>JSON.parse(x));
   let stableChars=0;
   for(const action of finalRetrievalActions){
     try{
       if(action.kind==='stable-section')stableChars+=this.core.stableSection(action.path,action.id).length;
       else if(action.kind==='artifact-contract')stableChars+=this.core.read(action.path).length;
       else if(action.kind==='profile'){const row=this.core.profileRows().find(r=>normalizeName(r.Industry||'')===normalizeName(action.industry||''));stableChars+=JSON.stringify(row||{}).length;}
       else if(action.kind==='operations-profile')stableChars+=action.stableId?this.core.stableSection(action.path,action.stableId).length:this.core.read(action.path).length;
     }catch{}
   }
   let moduleChars=0;for(const m of modules){try{moduleChars+=this.core.read(MODULE_FILE[m]).length;}catch{}}
   const retrievalBudget={stableSectionChars:stableChars,stableSectionTokenEstimate:Math.ceil(stableChars/4),wholeModuleChars:moduleChars,wholeModuleTokenEstimate:Math.ceil(moduleChars/4),reductionRatio:moduleChars?Number((1-stableChars/moduleChars).toFixed(3)):0,retrievalActionCount:finalRetrievalActions.length,policy:'Core 1.8 phase-local budget: execute eager stable sections first; deferredCapabilities are explicit on-demand retrieval candidates triggered by evidence, critics, unresolved risk, or repair dependencies'};
   const evidencePlan=artifactNodes.flatMap(node=>{
     const type=node.type; const base={artifactId:node.id,artifactType:type};
     if(WEB_TYPES.includes(type))return [{...base,profile:'browser',required:c.qualityClosureIntent,checks:['generation JavaScript preflight','viewport captures','overflow/clipping','console errors','broken resources','dead controls','interactive control closure','mobile task preservation','keyboard critical path','focus visibility','state coverage','accessibility evidence','responsive transformations','dense product visual finish','dense product completeness','dense product accessibility','dense product feature depth',...(type==='Website / Landing Page'?['website decision depth']:[])]}];
     if(type==='Spreadsheet / Financial Model')return [{...base,profile:'spreadsheet',required:true,checks:['recalculation','formula errors','cross-sheet links','scenario mutation','file-open integrity']}];
     if(type==='Presentation / Deck')return [{...base,profile:'presentation',required:true,checks:['slide bounds','title/subtitle fit','body/visual overlap','edge clipping','font fallback','image quality','contrast','export rendering']}];
     if(type==='Fixed-Format Document / PDF')return [{...base,profile:'document',required:true,checks:['page rendering','clipping','table breaks','links','reading order when required']}];
     if(type==='CLI / Developer Tool')return [{...base,profile:'cli',required:true,checks:['help','happy path','invalid input','exit codes','stdout/stderr','failure recovery','cli product depth']}];
     if(type==='Native / Mobile App')return [{...base,profile:'native-mobile',required:true,checks:['compact/large device states','permissions','keyboard/safe areas','interruption/recovery','mobile workflow depth']}];
     return [];
   });

   const generationPreflight=artifactNodes.filter(node=>WEB_TYPES.includes(node.type)).map(node=>({
     artifactId:node.id,artifactType:node.type,required:c.substantial,
     schema:'schemas/generation_preflight_evidence.schema.json',validator:'tools/validate_generation_preflight.py',
     syntaxPolicy:'Extract executable inline/local JavaScript and pass a real parser before rendered acceptance.',
     runtimePolicy:'When JavaScript is present, direct runtime evidence must prove document load with zero page errors, artifact-attributable console errors, or failed required resources.',
     implicitDomGlobalPolicy:'Do not rely on element IDs becoming global variables; bind DOM nodes explicitly, especially when IDs collide with JavaScript reserved/contextual words.',
     failClosed:true
   }));
   if(generationPreflight.length) finalRetrievalActions.push({kind:'stable-section',path:'QA_GATES.md',id:'qa-gates.generation-compiler-preflight',phase:'implementation',reason:'Revision 1.7.3 generated-JavaScript syntax/runtime fail-closed preflight'});
   const interactionClosure=artifactNodes.filter(node=>WEB_TYPES.includes(node.type)).map(node=>({
     artifactId:node.id,artifactType:node.type,required:c.qualityClosureIntent,
     manifestSchema:'schemas/interaction_closure_manifest.schema.json',taskPriorities:['P0','P1'],requiredMobileViewports:[320,390],
     enabledControlPolicy:'Every enabled visible control must be accounted for and directly exercised; zero dead controls.',
     mobileTaskPolicy:'Every declared P0/P1 desktop task must remain reachable and completable at 320/390 through an equivalent mobile composition.',
     failClosed:true
   }));
   const denseProductTypes=new Set(['Web App / SaaS / Portal','Dashboard']);
   const genericityClosure=artifactNodes.filter(node=>denseProductTypes.has(node.type)&&c.qualityClosureIntent).map(node=>({
     artifactId:node.id,artifactType:node.type,required:true,schema:'schemas/genericity_evidence.schema.json',validator:'tools/validate_genericity_evidence.py',
     minStructuralDecisions:3,minSubstantiveDecisions:2,minGrammarFamilies:4,minTaskStructureLinks:3,maxTemplateSimilarity:0.60,
     competitorSwapPolicy:'At least two non-cosmetic structural decisions must stop fitting if the product/domain is replaced by an unrelated competitor.',failClosed:true
   }));
   const productFlavor=/\b(payment|payments|transaction|transactions|settlement|charge|refund|dispute)\b/i.test(request)?'payments':(/\b(analytics|metric|metrics|kpi|cohort|retention|forecast|segment|segments|insight)\b/i.test(request)?'analytics':'general');
   const denseProductQualityClosure=artifactNodes.filter(node=>denseProductTypes.has(node.type)&&c.qualityClosureIntent).map(node=>({
     artifactId:node.id,artifactType:node.type,artifactFamily:node.type==='Dashboard'?'dashboard':'saas-web-app',productFlavor,required:true,
     schema:'schemas/dense_product_quality_evidence.schema.json',validator:'tools/validate_dense_product_quality_evidence.py',
     requiredViewports:[1440,390,320],requiredSections:['visual_finish','completeness','accessibility','feature_depth'],
     visualPolicy:'First-pass rendered hierarchy, density/rhythm, semantic surface roles, typography roles, control geometry, and material state surfaces must be finished before acceptance.',
     completenessPolicy:'Every P0/P1 feature must close all applicable coverage rows; silent omission is NON-PASS.',
     accessibilityPolicy:'Every P0/P1 critical path requires direct named-control, keyboard/focus, programmatic-feedback, non-color, target/readability, error-association, and 320/390 reflow evidence.',
     featureDepthPolicy:productFlavor==='payments'?'Level-5 payments loop: find/filter/segment → inspect transaction → status/risk/context → action/recovery → result/feedback → continue.':(productFlavor==='analytics'?'Level-5 analytics loop: decision/question → evidence/source → comparison/segmentation → interpretation/guardrail → inspect/drill-down → next action/handoff → continued state.':'At least three Level-5 P0/P1 features spanning investigation, action/recovery, and continuity/comparison.'),
     failClosed:true
   }));
   const artifactFamilyQualityClosure=artifactNodes.filter(node=>FAMILY_CLOSURE_TYPES.has(node.type)&&c.qualityClosureIntent).map(node=>({
     artifactId:node.id,artifactType:node.type,required:true,schema:'schemas/artifact_family_quality_evidence.schema.json',validator:'tools/validate_artifact_family_quality_evidence.py',
     familyProfile:({'Native / Mobile App':'mobile','Presentation / Deck':'presentation','Spreadsheet / Financial Model':'spreadsheet','Brand Identity / Logo':'brand','Email / Campaign':'email','Marketing Creative':'marketing-creative','CLI / Developer Tool':'cli','Fixed-Format Document / PDF':'fixed-document'})[node.type],
     failClosed:true,
     policy:'First-pass acceptance requires direct family-specific completeness, accessibility, implementation, depth, finish, and anti-genericity evidence; unavailable evidence is UNVERIFIED rather than PASS.'
   }));
   const familyDepthMap={'Website / Landing Page':'website','Native / Mobile App':'mobile','Brand Identity / Logo':'brand','Email / Campaign':'email','CLI / Developer Tool':'cli'};
   const familyDepthClosure=artifactNodes.filter(node=>FAMILY_DEPTH_TYPES.has(node.type)&&c.qualityClosureIntent).map(node=>({
     artifactId:node.id,artifactType:node.type,familyProfile:familyDepthMap[node.type],required:true,
     schema:'schemas/family_depth_evidence.schema.json',validator:'tools/validate_family_depth_evidence.py',
     requiredCriticalMinimum:9.0,failClosed:true,
     policy:node.type==='Website / Landing Page'?'Compile primary + secondary visitor decision paths with proof, objection/uncertainty, next action, continuation, truth boundary, and narrow-screen equivalent.':
       (node.type==='Native / Mobile App'?'Compile at least one P0 and one P1 workflow through state, interruption/error, recovery, continuation, and compact/adaptive surfaces.':
       (node.type==='Brand Identity / Logo'?'Compile a usable identity system across mark, typography, color, composition, iconography, imagery, rules, and at least three applications.':
       (node.type==='Email / Campaign'?'Compile the campaign as a lifecycle sequence with audience state, message job, proof boundary, CTA, measurement, fallback, and next state.':'Compile CLI discoverability/help plus primary jobs with config precedence, deterministic output/error/exit semantics, recovery, tests, and safety boundaries.')))
   }));
   const compositeDepthClosure=(c.artifactGraph.kind==='composite'&&c.qualityClosureIntent)?[{
     artifactId:'project-composite',artifactType:'Composite',familyProfile:'composite',required:true,
     schema:'schemas/family_depth_evidence.schema.json',validator:'tools/validate_family_depth_evidence.py',
     childArtifactIds:artifactNodes.map(x=>x.id),requiresNarrowScreen:artifactNodes.some(x=>INTERFACE_TYPES.includes(x.type)),requiredViewports:[320,390],failClosed:true,
     generationPrerequisites:['shrinkable flex/grid descendants use min-width:0','media/inputs bounded by containing block','long tokens and URLs wrap','fixed/min widths bounded below compact viewport','tables/data regions have explicit compact strategy','project shell cannot impose desktop-only child widths'],preFreezeViewports:[320,390],policy:'Each child keeps independent contract/QA; shared context must be explicit. Responsive children compile width-safe primitives before freeze and require direct 320/390 no-overflow/no-clipping/P0-P1-path-preservation evidence.'
   }]:[];
   const materializationMap={'Website / Landing Page':'website','Native / Mobile App':'mobile','Brand Identity / Logo':'brand','Email / Campaign':'email','CLI / Developer Tool':'cli','Presentation / Deck':'presentation','Spreadsheet / Financial Model':'spreadsheet','Fixed-Format Document / PDF':'fixed-document','Marketing Creative':'marketing-creative'};
   const materializationClosure=artifactNodes.filter(node=>MATERIALIZATION_TYPES.has(node.type)&&c.qualityClosureIntent).map(node=>({
     artifactId:node.id,artifactType:node.type,familyProfile:materializationMap[node.type],required:true,
     schema:'schemas/materialization_evidence.schema.json',validator:'tools/validate_materialization_evidence.py',
     prohibitedProductionVocabulary:['P0','P1','decision depth closure','truth boundary','feature depth','quality gate','genericity','artifact contract','evidence plan','acceptance ledger','QA gate'],
     minimumConcreteRecords:{website:5,mobile:5,brand:6,email:4,cli:4,presentation:4,spreadsheet:4,'fixed-document':4,'marketing-creative':4}[materializationMap[node.type]],
     failClosed:true,policy:'Materialize internal requirements into domain-specific user-facing content/data/states/actions/proof needs. Production copy must use user/business vocabulary and must not expose internal AIFENCE/compiler/QA labels.'
   }));
   const compositeMaterializationClosure=(c.artifactGraph.kind==='composite'&&c.qualityClosureIntent)?[{
     artifactId:'project-composite',artifactType:'Composite',familyProfile:'composite',required:true,schema:'schemas/materialization_evidence.schema.json',validator:'tools/validate_materialization_evidence.py',childArtifactIds:artifactNodes.map(x=>x.id),failClosed:true,policy:'Each child must independently materialize domain-specific jobs/content/states while shared vocabulary remains natural and consistent across the project.'
   }]:[];

   const emissionFamilyMap={'Website / Landing Page':'website','Web App / SaaS / Portal':'web-app','Marketplace / E-Commerce':'web-app','Dashboard':'dashboard','Native / Mobile App':'mobile','Brand Identity / Logo':'brand','Email / Campaign':'email','CLI / Developer Tool':'cli','Presentation / Deck':'presentation','Spreadsheet / Financial Model':'spreadsheet','Fixed-Format Document / PDF':'fixed-document','Marketing Creative':'marketing-creative','Documentation / Repository Architecture':'documentation'};
   const emissionAcceptance=artifactNodes.filter(node=>EMISSION_TYPES.has(node.type)&&c.qualityClosureIntent).map(node=>({
     artifactId:node.id,artifactType:node.type,familyProfile:emissionFamilyMap[node.type],required:true,
     schema:'schemas/family_emission_evidence.schema.json',validator:'tools/validate_family_emission_evidence.py',
     directSurfaceScan:true,minimumSurfaceMarkers:6,minimumDomainTerms:3,familySemantics:FAMILY_EMISSION_REQUIREMENTS[emissionFamilyMap[node.type]]||[],
     prohibitedProductionVocabulary:['P0','P1','decision depth closure','truth boundary','feature depth','quality gate','genericity','artifact contract','evidence plan','acceptance ledger','QA gate','materialization closure','emission preflight'],
     scaffoldPolicy:'context-sensitive-family-native',ooxmlAdapter:node.type==='Spreadsheet / Financial Model'?'namespace-safe-xlsx':undefined,
     fixedDocumentDepth:node.type==='Fixed-Format Document / PDF'?{minimumFindings:3,minimumImplicationsOrActions:3,minimumEvidencePoints:4,minimumProvenanceMarkers:2,minimumReaderTakeaways:2}:undefined,
     failClosed:true,policy:'After generation and before freeze, scan the emitted production-facing surfaces themselves. Internal orchestration vocabulary remains forbidden; material substance is validated with family-native semantics rather than a universal workflow-shaped schema. Fixed documents additionally require distinct findings, implications/actions, evidence density, provenance, and reader takeaways.'
   }));
   if(c.artifactGraph.kind==='composite'&&c.qualityClosureIntent) emissionAcceptance.push({artifactId:'project-composite',artifactType:'Composite',familyProfile:'composite',required:true,schema:'schemas/family_emission_evidence.schema.json',validator:'tools/validate_family_emission_evidence.py',childArtifactIds:artifactNodes.map(x=>x.id),familySemantics:FAMILY_EMISSION_REQUIREMENTS.composite,directSurfaceScan:true,continuityRequirements:{minimumSharedContextRules:3,minimumSharedIdentifiersOrAssumptions:2,minimumCrossArtifactContinuity:3,minimumChildAcceptanceRefs:2,minimumProjectProvenanceBoundaries:2},failClosed:true,policy:'Every child surface must naturalize independently; project-level evidence must prove shared context, shared identifiers/assumptions, project provenance, cross-artifact continuity/handoffs, and child acceptance references without forcing child families into one semantic shape.'});
   const universalExecutablePreflight=artifactNodes.filter(node=>EXECUTABLE_TYPES.has(node.type)&&c.qualityClosureIntent).map(node=>({
     artifactId:node.id,artifactType:node.type,required:true,validator:'tools/validate_universal_executable_preflight.py',runtimeSchema:'schemas/universal_executable_runtime_evidence.schema.json',
     syntaxScope:'all supported emitted executable files',runtimeRequired:true,failClosed:true,
     policy:'Parse emitted executable files with their language grammar and require direct runtime evidence for executable interfaces/tools. Syntax failure, missing runtime evidence, or unexpected runtime failure blocks acceptance.'
   }));

   const artifactFamilyAcceptance=artifactNodes.map(node=>{
     const interactive=[...INTERFACE_TYPES].includes(node.type);
     const fixed=['Presentation / Deck','Spreadsheet / Financial Model','Fixed-Format Document / PDF','Brand Identity / Logo','Email / Campaign','Marketing Creative','CLI / Developer Tool'].includes(node.type);
     return {artifactId:node.id,artifactType:node.type,overallMinimum:90,universalStrictComparisonMinimum:9.0,
       releaseCriticalMinimum:9.0,
       criticalDimensions:interactive?['truthfulness','implementation correctness','completeness','usability','responsiveness','accessibility','feature depth']:(fixed?['truthfulness','implementation correctness','completeness','accessibility','feature depth']:['truthfulness','implementation correctness','completeness']),
       nonCriticalMinimum:8.5,
       catastrophicFailureBlocks:true};
   });
   const b2bComplex=c.contextGraph.businessModel?.value==='B2B' || /\b(enterprise|procurement|technical evaluation|security review|implementation planning|sales engineering)\b/i.test(request);
   const decisionDepthClosure=artifactNodes.filter(node=>node.type==='Website / Landing Page'&&b2bComplex&&c.qualityClosureIntent).map(node=>({
     artifactId:node.id,artifactType:node.type,required:true,schema:'schemas/decision_depth_evidence.schema.json',validator:'tools/validate_decision_depth_evidence.py',
     journeyType:'b2b-complex',minDecisionPaths:2,requiredPathFields:['buyer decision','evidence/proof','fit/qualification','objection/risk','next action','downstream state','artifact surface'],failClosed:true
   }));
   for(const x of genericityClosure) finalRetrievalActions.push({kind:'stable-section',path:'GENERICITY.md',id:'genericity.dense-product-differentiation',phase:'structural-fingerprint',reason:'dense-product benchmark-derived structural differentiation closure'});
   for(const x of decisionDepthClosure) finalRetrievalActions.push({kind:'stable-section',path:'FEATURE_DEPTH.md',id:'feature-depth.b2b-decision-journey',phase:'feature-compilation',reason:'complex-B2B benchmark-derived buyer decision-depth closure'});
   for(const x of artifactFamilyQualityClosure) finalRetrievalActions.push({kind:'stable-section',path:'NONWEB_FIRST_PASS.md',id:'nonweb-first-pass.family-contracts',phase:'acceptance',reason:`Core 1.8 ${x.familyProfile} first-pass family quality closure`});
   for(const x of familyDepthClosure) finalRetrievalActions.push({kind:'stable-section',path:'FAMILY_DEPTH_CLOSURE.md',id:`family-depth-closure.${x.familyProfile}`,phase:x.familyProfile==='website'?'feature-compilation':'acceptance',reason:`Core 1.8.1 ${x.familyProfile} depth closure`});
   for(const x of compositeDepthClosure) finalRetrievalActions.push({kind:'stable-section',path:'FAMILY_DEPTH_CLOSURE.md',id:'family-depth-closure.composite',phase:'acceptance',reason:'Core 1.8.1 composite narrow-screen containment closure'});
   for(const x of materializationClosure){
     const sid=x.familyProfile==='website'||x.familyProfile==='mobile'?'materialization-closure.web-mobile':(x.familyProfile==='brand'||x.familyProfile==='email'?'materialization-closure.brand-campaign':(x.familyProfile==='cli'?'materialization-closure.cli':'materialization-closure.nonweb-reading'));
     finalRetrievalActions.push({kind:'stable-section',path:'MATERIALIZATION_CLOSURE.md',id:sid,phase:'feature-compilation',reason:`Core 1.8.2 ${x.familyProfile} concrete domain materialization/naturalization`});
     finalRetrievalActions.push({kind:'stable-section',path:'MATERIALIZATION_CLOSURE.md',id:'materialization-closure.naturalization',phase:'acceptance',reason:'Core 1.8.2 production-facing vocabulary naturalization boundary'});
   }
   for(const x of compositeMaterializationClosure) finalRetrievalActions.push({kind:'stable-section',path:'MATERIALIZATION_CLOSURE.md',id:'materialization-closure.domain-materialization',phase:'feature-compilation',reason:'Core 1.8.2 composite child materialization closure'});
   for(const x of emissionAcceptance){
     finalRetrievalActions.push({kind:'stable-section',path:'EMISSION_PREFLIGHT.md',id:'emission-preflight.naturalization-scan',phase:'acceptance',reason:`Core 1.8.3 ${x.familyProfile} finished-surface naturalization scan`});
     finalRetrievalActions.push({kind:'stable-section',path:'EMISSION_PREFLIGHT.md',id:'emission-preflight.family-adapters',phase:'acceptance',reason:`Core 1.8.4 ${x.familyProfile} family-native emission adapter`});
     if(x.familyProfile==='spreadsheet') finalRetrievalActions.push({kind:'stable-section',path:'EMISSION_PREFLIGHT.md',id:'emission-preflight.xlsx-adapter',phase:'acceptance',reason:'Core 1.8.4 namespace-safe XLSX surface extraction'});
     if(x.familyProfile==='presentation') finalRetrievalActions.push({kind:'stable-section',path:'EMISSION_PREFLIGHT.md',id:'emission-preflight.presentation-slide-fit',phase:'render-inspection',reason:'Core 1.8.7 direct title/subtitle/body/visual slide-fit preflight'});
     if(x.familyProfile==='fixed-document'){ finalRetrievalActions.push({kind:'stable-section',path:'EMISSION_PREFLIGHT.md',id:'emission-preflight.fixed-document-depth',phase:'feature-compilation',reason:'Core 1.8.5 fixed-document findings/implications depth closure'}); finalRetrievalActions.push({kind:'stable-section',path:'EMISSION_PREFLIGHT.md',id:'emission-preflight.fixed-document-render',phase:'render-inspection',reason:'Core 1.8.6 render-aware PDF geometry/accessibility preflight'}); }
     if(x.familyProfile==='composite') finalRetrievalActions.push({kind:'stable-section',path:'EMISSION_PREFLIGHT.md',id:'emission-preflight.composite-continuity',phase:'feature-compilation',reason:'Core 1.8.5 composite project continuity closure'});
     finalRetrievalActions.push({kind:'stable-section',path:'EMISSION_PREFLIGHT.md',id:'emission-preflight.scaffold-context',phase:'acceptance',reason:'Core 1.8.4 context-sensitive scaffold detection'}); finalRetrievalActions.push({kind:'stable-section',path:'EMISSION_PREFLIGHT.md',id:'emission-preflight.semantic-equivalence',phase:'acceptance',reason:'Core 1.8.6 conservative semantic materialization matching'});
   }
   for(const x of compositeDepthClosure) finalRetrievalActions.push({kind:'stable-section',path:'EMISSION_PREFLIGHT.md',id:'emission-preflight.compact-containment',phase:'implementation',reason:'Core 1.8.5 responsive composite pre-freeze containment compiler'});
   for(const x of universalExecutablePreflight) finalRetrievalActions.push({kind:'stable-section',path:'EMISSION_PREFLIGHT.md',id:'emission-preflight.universal-executable',phase:'implementation',reason:'Core 1.8.3 universal executable syntax/runtime preflight'});
   for(const x of denseProductQualityClosure){
     finalRetrievalActions.push({kind:'stable-section',path:'VISUAL_FINISH.md',id:'visual-finish.dense-product-first-pass',phase:'render-inspection',reason:'Revision 1.7.4 dense-product first-pass visual finish closure'});
     finalRetrievalActions.push({kind:'stable-section',path:'COMPLETENESS.md',id:'completeness.dense-product-first-pass',phase:'acceptance',reason:'Revision 1.7.4 exhaustive P0/P1 completion closure'});
     finalRetrievalActions.push({kind:'stable-section',path:'ACCESSIBILITY_EVIDENCE.md',id:'accessibility-evidence.dense-product-first-pass',phase:'render-inspection',reason:'Revision 1.7.4 direct dense-product accessibility closure'});
     finalRetrievalActions.push({kind:'stable-section',path:'FEATURE_DEPTH.md',id:'feature-depth.payments-analytics-level-5',phase:'feature-compilation',reason:'Revision 1.7.4 workflow-specific dense-product Level-5 depth closure'});
   }
   const specializedActions=uniq(finalRetrievalActions.map(x=>JSON.stringify(x))).map(x=>JSON.parse(x));
   let specializedChars=0;
   for(const action of specializedActions){
     if(!((action.path==='GENERICITY.md'&&action.id==='genericity.dense-product-differentiation')||(action.path==='FEATURE_DEPTH.md'&&action.id==='feature-depth.b2b-decision-journey')||(action.path==='VISUAL_FINISH.md'&&action.id==='visual-finish.dense-product-first-pass')||(action.path==='COMPLETENESS.md'&&action.id==='completeness.dense-product-first-pass')||(action.path==='ACCESSIBILITY_EVIDENCE.md'&&action.id==='accessibility-evidence.dense-product-first-pass')||(action.path==='FEATURE_DEPTH.md'&&action.id==='feature-depth.payments-analytics-level-5')||(action.path==='NONWEB_FIRST_PASS.md'&&action.id==='nonweb-first-pass.family-contracts')||(action.path==='FAMILY_DEPTH_CLOSURE.md'&&action.id?.startsWith('family-depth-closure.'))||(action.path==='MATERIALIZATION_CLOSURE.md'&&action.id?.startsWith('materialization-closure.'))||(action.path==='EMISSION_PREFLIGHT.md'&&action.id?.startsWith('emission-preflight.'))))continue;
     try{specializedChars+=this.core.stableSection(action.path,action.id).length;}catch{}
   }
   if(specializedChars){retrievalBudget.stableSectionChars+=specializedChars;retrievalBudget.stableSectionTokenEstimate=Math.ceil(retrievalBudget.stableSectionChars/4);retrievalBudget.retrievalActionCount=specializedActions.length;retrievalBudget.reductionRatio=moduleChars?Number((1-retrievalBudget.stableSectionChars/moduleChars).toFixed(3)):0;}

   const primary=artifactNodes[0];
   return {
     runtimeVersion:RUNTIME_VERSION,coreRevision:this.core.revision(),request,
     classification:{...c,artifactGraph:{...c.artifactGraph,nodes:artifactNodes}},contextGraph:c.contextGraph,riskGraph:c.riskGraph,
     artifactContract:primary?.artifactContract||null,artifactContracts:artifactNodes.map(x=>({artifactId:x.id,type:x.type,contractChain:x.contractChain,artifactContract:x.artifactContract})),
     activationBundles:uniqueBundles,activeDomains:domains,activeModules:modules,activeCapabilities:cp.active,deferredCapabilities:cp.deferred,phases:cp.phases,retrievalBudget,
     retrievalActions:specializedActions,evidencePlan,generationPreflight,interactionClosure,genericityClosure,denseProductQualityClosure,artifactFamilyQualityClosure,familyDepthClosure,compositeDepthClosure,materializationClosure,compositeMaterializationClosure,emissionAcceptance,universalExecutablePreflight,artifactFamilyAcceptance,decisionDepthClosure,qa:uniq(qa.filter(Boolean)),unresolved,
     executionRules:[
       'README.md is authoritative; do not preload the entire AIFENCE core.',
       'Use phases[].retrievalActions and activeCapabilities as the primary execution interface; activeModules is compatibility/debug metadata.',
       c.artifactGraph.kind==='composite'?'Compile and validate each artifact node independently while sharing only explicit project context.':null,
       c.productionIntent?'Production intent is active; do not silently downgrade to MVP/prototype/mockup.':`Explicit ${c.deliveryMode} implementation mode is active; preserve truth and safety requirements.`,
       c.visualFidelity==='High-Fidelity'&&!c.productionIntent?'High-fidelity visual intent remains active even in non-production implementation modes; do not lower visual craft, usability closure, or final-finish standards unless explicitly requested.':null,
       c.contextGraph.referenceInspirations.length?'Translate named references into abstract qualities only; produce an original structural fingerprint and do not clone distinctive trade dress/layout.':null,
       'Unknown business facts remain unknown; sample/demo/backend boundaries must be explicit.',
       'Before rendered acceptance of a substantial web artifact, run fail-closed generation preflight: executable JavaScript must parse with a real parser and direct runtime initialization must show zero page/console/resource failures; do not rely on implicit DOM globals.',
       'Before production/high-fidelity interactive acceptance, compile an interaction-closure manifest; every enabled visible control must be directly exercised with zero dead controls, and every declared P0/P1 task must directly PASS at 320 and 390 through an equivalent mobile composition.',
       genericityClosure.length?'High-fidelity dense-product genericity is fail-closed: compile task-derived structural differentiation evidence with at least four meaningful grammar families, competitor-swap resistance, and best generic-template similarity below 0.61.':null,
       denseProductQualityClosure.length?'High-fidelity dense-product first-pass quality is fail-closed: visual finish, exhaustive P0/P1 completeness, direct accessibility critical-path evidence, and Level-5 feature depth must each PASS independently before acceptance; payments/analytics use workflow-specific depth loops.':null,
       artifactFamilyQualityClosure.length?'Core 1.8 artifact-family closure is fail-closed for mobile, presentations, spreadsheets/models, fixed documents, brand, email/creative, and CLI output: use direct family-specific evidence and family-adjusted release thresholds; retain the universal 9.0 rubric for cross-family benchmark comparability.':null,
       (familyDepthClosure.length||compositeDepthClosure.length)?'Core 1.8.1 family-depth closure is fail-closed for public websites, mobile workflows, brand systems, email sequences, CLI product surfaces, and responsive composites; evidence must prove depth/completeness rather than decorative breadth, and responsive composite children must pass direct 320/390 containment.':null,
       (materializationClosure.length||compositeMaterializationClosure.length)?'Core 1.8.2 materialization is fail-closed: compile domain-specific content/data/states/actions/proof needs into natural user-facing language, prohibit internal AIFENCE/compiler/QA vocabulary from production surfaces, and reject generic records that could transplant unchanged into an unrelated industry.':null,
       emissionAcceptance.length?'Core 1.8.4 emission acceptance is fail-closed: preserve the Core 1.8.3 finished-surface naturalization scan, then validate concrete substance through the artifact family’s native semantics; spreadsheet surfaces use namespace-safe OOXML extraction and scaffold detection is context-sensitive.':null,
       emissionAcceptance.some(x=>x.familyProfile==='fixed-document')?'Core 1.8.6 fixed-document acceptance is render-aware and fail-closed: rendered pages must have zero material collisions/clipping with direct reading-order/table-order/accessibility evidence; Core 1.8.5 fixed-document depth remains fail-closed: material reports require at least three distinct findings/conclusions, three implications/actions, four evidence points, two provenance markers, and two reader-facing takeaways; topic coverage alone is insufficient.':null,
       emissionAcceptance.some(x=>x.familyProfile==='composite')?'Core 1.8.5 composite continuity is fail-closed: child artifacts must share explicit assumptions/identifiers, provenance boundaries, visible handoffs, and child acceptance references rather than merely being bundled together.':null,
       compositeDepthClosure.length?'Core 1.8.5 composite compact containment is a pre-freeze compiler rule and final evidence gate: every responsive child must use width-safe primitives and directly pass 320/390 with zero overflow/clipping and preserved critical paths.':null,
       universalExecutablePreflight.length?'Core 1.8.3 universal executable preflight is fail-closed: parse every emitted executable file and require direct runtime evidence for executable interfaces/tools.':null,
       decisionDepthClosure.length?'Complex B2B marketing feature depth is fail-closed: compile at least two buyer decision paths linking evidence, fit, objection/risk, next action, downstream state, and observable artifact surfaces.':null,
       'Evidence-required gates may PASS only from direct evidence or an explicitly approved equivalent; unavailable evidence remains visible.'
     ].filter(Boolean)
   };
 }
}
