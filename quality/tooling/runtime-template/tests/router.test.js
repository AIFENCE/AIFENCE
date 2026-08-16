import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import {BizIQRouter} from '../src/router.js';import {classifyRequest} from '../src/classifier.js';const r=new BizIQRouter();
test('parses core-owned creation routes and bundles',()=>{assert.ok(r.creationRoutes().length>=13);assert.ok(r.bundles().length>=9)});
test('landscaping website is production visual with contract',()=>{const p=r.plan('Create a premium production website for a local landscaping company.');assert.equal(p.classification.creationType,'Website / Landing Page');assert.equal(p.classification.deliveryMode,'Production');assert.ok(p.activeDomains.includes(26));assert.ok(p.activeDomains.includes(30));assert.equal(p.artifactContract,'local-service-website');assert.ok(p.activeModules.includes('TRUTH_BOUNDARIES'))});
test('operations activates Domain 31 and compiler',()=>{const p=r.plan('Create an SOP for a landscaping crew lead handling customer scope changes.');assert.equal(p.classification.creationType,'Org / Jobs / SOPs');assert.ok(p.activeDomains.includes(31));assert.ok(p.activeModules.includes('OPERATIONAL_PROCEDURE_COMPILER'));assert.equal(p.artifactContract,'operations-workflow');assert.equal(p.classification.industry.industry,'Landscaping & Horticulture');assert.ok(p.classification.risks.includes('physical-safety'));assert.ok(p.retrievalActions.some(x=>x.path==='operations/agriculture.md'))});
test('explicit prototype prevents production default',()=>{const p=r.plan('Create a prototype dashboard for testing navigation.');assert.equal(p.classification.deliveryMode,'Prototype');assert.equal(p.classification.productionIntent,false)});
test('production space website routes assets and final closure modules',()=>{const p=r.plan('Create a front end only premium space industry website with custom imagery.');assert.equal(p.classification.creationType,'Website / Landing Page');assert.ok(p.activeDomains.includes(29));assert.ok(p.activeDomains.includes(30));for(const m of ['ASSETS','FEATURE_DEPTH','USABILITY_CLOSURE','VISUAL_FINISH','QUALITY_MEASUREMENT'])assert.ok(p.activeModules.includes(m),`missing ${m}`)});
test('stripe-like payments dashboard concept remains high fidelity',()=>{const p=r.plan('Create a separate Stripe-like payments dashboard concept, front end only.');assert.equal(p.classification.creationType,'Dashboard');assert.equal(p.classification.deliveryMode,'Concept');assert.equal(p.classification.productionIntent,false);assert.equal(p.classification.visualFidelity,'High-Fidelity');assert.equal(p.classification.qualityClosureIntent,true);assert.ok(p.activeDomains.includes(30));for(const m of ['FEATURE_DEPTH','USABILITY_CLOSURE','VISUAL_FINISH','RESPONSIVE_DETAIL_CLOSURE','QUALITY_MEASUREMENT','LEGAL'])assert.ok(p.activeModules.includes(m),`missing ${m}`);assert.ok(p.classification.risks.includes('payments'));const ep=p.evidencePlan.find(x=>x.artifactType==='Dashboard');for(const check of ['interactive control closure','mobile task preservation'])assert.ok(ep.checks.includes(check));const ic=p.interactionClosure.find(x=>x.artifactType==='Dashboard');assert.equal(ic.required,true);assert.deepEqual(ic.requiredMobileViewports,[320,390]);assert.ok(p.activeCapabilities.some(x=>x.capability==='Dense-UI adaptation'));assert.ok(p.activeCapabilities.some(x=>x.capability==='Cross-device continuity'))});
test('financial exposure activates payment security while industry overlay remains distinct',()=>{const p=r.plan('Create a payments dashboard for a financial services company.');assert.ok(p.classification.risks.includes('financial-regulated'));assert.ok(p.classification.risks.includes('payments'));assert.ok(p.riskGraph.security.includes('payments'));assert.ok(p.activeModules.includes('LEGAL'));assert.ok(p.activeModules.includes('SECURITY'))});
test('explicit low-fidelity concept does not force final visual closure',()=>{const p=r.plan('Create a low-fidelity dashboard concept for navigation exploration.');assert.equal(p.classification.visualFidelity,'Low-Fidelity');assert.equal(p.classification.qualityClosureIntent,false);assert.ok(!p.activeDomains.includes(30))});

test('all classifier fixtures resolve without throwing and return bounded plans', () => {
  const fixturePath = new URL('./fixtures/requests.json', import.meta.url);
  const fixtures = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));
  for (const fx of fixtures) {
    const p = r.plan(fx.request, fx.options || {});
    assert.ok(p.classification?.creationType, fx.request);
    assert.ok(Array.isArray(p.activeModules));
    assert.ok(Array.isArray(p.retrievalActions));
    assert.ok(p.activeModules.length < 40, `unbounded module activation for ${fx.request}`);
  }
});

test('semantic industry matching rejects substring collisions',()=>{
  const a=r.plan('Create a donor website for a hospital foundation.');
  assert.notEqual(a.classification.industry.industry,'Foundation Models');
  const b=r.plan('Create a homepage for a consulting firm.');
  assert.notEqual(b.classification.industry.industry,'Home Services');
  const c=r.plan('Write a quarterly report for a consulting firm.');
  assert.notEqual(c.classification.industry.industry,'Port Operations');
});
test('negated exposures suppress security activation',()=>{
  const p=r.plan('Create a public banking website with no login, no financial transactions, no PII collection, and no backend.');
  assert.equal(p.contextGraph.authentication,'absent');
  assert.equal(p.contextGraph.transactions,'absent');
  assert.equal(p.contextGraph.backendStatus,'absent');
  assert.equal(p.riskGraph.security.length,0);
  assert.ok(p.activeModules.includes('LEGAL'));
  assert.ok(!p.activeModules.includes('SECURITY'));
});
test('expanded creation types resolve first-class contracts',()=>{
  const cases=[
    ['Create a native iOS banking app','Native / Mobile App','native-mobile-app'],
    ['Create an investor pitch deck','Presentation / Deck','presentation-deck'],
    ['Build a three-statement financial model spreadsheet','Spreadsheet / Financial Model','spreadsheet-financial-model'],
    ['Design a logo and visual identity','Brand Identity / Logo','brand-identity'],
    ['Create a lifecycle email campaign','Email / Campaign','email-campaign'],
    ['Create a video storyboard for an ad campaign','Marketing Creative','marketing-creative'],
    ['Build a CLI developer tool','CLI / Developer Tool','cli-developer-tool'],
    ['Create a print-ready report PDF','Fixed-Format Document / PDF','fixed-format-document']
  ];
  for(const [req,type,contract] of cases){const p=r.plan(req);assert.equal(p.classification.creationType,type,req);assert.equal(p.artifactContract,contract,req);}
});
test('composite request compiles artifact graph and contract chains',()=>{
  const p=r.plan('Create a customer portal with a marketing homepage.');
  assert.equal(p.classification.artifactGraph.kind,'composite');
  assert.ok(p.classification.creationTypes.includes('Web App / SaaS / Portal'));
  assert.ok(p.classification.creationTypes.includes('Website / Landing Page'));
  assert.equal(p.artifactContracts.length,2);
});
test('runtime plan is capability and phase scoped',()=>{
  const p=r.plan('Create a premium production website for a landscaping company.');
  assert.ok(p.activeCapabilities.length>5);
  assert.ok(p.phases.some(x=>x.phase==='classification'));
  assert.ok(p.retrievalActions.some(x=>x.kind==='stable-section'&&x.id?.startsWith('controls.capability.')));
  assert.ok(p.retrievalBudget.stableSectionChars<p.retrievalBudget.wholeModuleChars);
  assert.equal(p.retrievalBudget.policy.includes('phase-local budget'),true);
});
test('reference inspiration is abstracted rather than cloned',()=>{
  const p=r.plan('Create a Stripe-like payments dashboard concept.');
  assert.equal(p.contextGraph.referenceInspirations[0]?.reference,'Stripe');
  assert.equal(p.contextGraph.referenceInspirations[0]?.mode,'abstract-principles-only');
  assert.ok(p.executionRules.some(x=>x.includes('original structural fingerprint')));
});
test('deterministic semantic fuzz matrix resists collisions and negation regressions',()=>{
  const collisionSubjects=['hospital foundation','homepage redesign','quarterly report','transportation report','home page','foundation fundraiser'];
  for(const subject of collisionSubjects){
    for(const suffix of ['for a consulting firm','for a nonprofit','for a healthcare organization']){
      const p=r.plan(`Create a ${subject} ${suffix}.`);
      if(subject.includes('foundation')) assert.notEqual(p.classification.industry.industry,'Foundation Models');
      if(subject.includes('home')) assert.notEqual(p.classification.industry.industry,'Home Services');
      if(subject.includes('report')) assert.notEqual(p.classification.industry.industry,'Port Operations');
    }
  }
  const negations=[
    ['no login','authentication'],['without authentication','authentication'],['no payments','payments'],['without transactions','payments'],
    ['does not collect PII','sensitiveData'],['no uploads','uploadsUgc'],['without location data','location'],['no backend','backend'],['front-end only','backend']
  ];
  for(const [phrase,key] of negations){
    for(const prefix of ['Create a premium website','Create a dashboard concept','Create a mobile app prototype']){
      const p=r.plan(`${prefix} ${phrase}.`);assert.equal(p.contextGraph.artifactExposure[key].state,'absent',`${prefix} ${phrase}`);
    }
  }
});
test('30-case semantic routing benchmark corpus resolves expected contract chains',()=>{
  const cases=JSON.parse(r.core.read('benchmarks/v2_semantic_routing_cases.json'));
  assert.equal(cases.length,30);
  for(const c of cases){
    const p=r.plan(c.prompt);
    const resolved=[...new Set(p.artifactContracts.flatMap(x=>x.contractChain))];
    for(const expected of c.artifact_contracts) assert.ok(resolved.includes(expected),`${c.id}: expected ${expected}; got ${resolved.join(', ')}`);
  }
});

test('dense app plans fail closed on benchmark-derived interaction weaknesses',()=>{
  for(const req of ['Create a payments operations dashboard.','Create a SaaS workflow editor with list and detail pane.','Create an analytics dashboard with period filters and navigation.']){
    const p=r.plan(req);const ic=p.interactionClosure[0];assert.ok(ic?.required,req);assert.ok(p.activeModules.includes('RESPONSIVE_DETAIL_CLOSURE'),req);const ep=p.evidencePlan[0];assert.ok(ep.checks.includes('interactive control closure'),req);assert.ok(ep.checks.includes('mobile task preservation'),req);
  }
});

test('dense product routing activates differentiation capabilities and closure',()=>{
  for(const req of ['Create a premium SaaS workflow product with a queue and detail editor.','Create a premium analytics dashboard for revenue operations.']){
    const p=r.plan(req);
    for(const d of [6,7,9])assert.ok(p.activeDomains.includes(d),`${req}: missing domain ${d}`);
    for(const cap of ['Differentiation ledger','Concept selection rubric','Brand-specific fingerprint','Anti-template heuristics','Memorability test','Repetition detector'])assert.ok(p.activeCapabilities.some(x=>x.capability===cap),`${req}: missing ${cap}`);
    assert.ok(p.genericityClosure?.[0]?.required,req);
    assert.equal(p.genericityClosure[0].maxTemplateSimilarity,0.60);
    assert.equal(p.genericityClosure[0].minGrammarFamilies,4);
    assert.ok(p.retrievalActions.some(x=>x.path==='GENERICITY.md'&&x.id==='genericity.dense-product-differentiation'),req);
  }
});

test('complex B2B marketing compiles decision depth closure',()=>{
  const p=r.plan('Create a premium B2B technology website for enterprise procurement teams evaluating integrations and implementation risk.');
  assert.equal(p.contextGraph.businessModel.value,'B2B');
  assert.ok(p.decisionDepthClosure?.[0]?.required);
  assert.equal(p.decisionDepthClosure[0].minDecisionPaths,2);
  assert.ok(p.retrievalActions.some(x=>x.path==='FEATURE_DEPTH.md'&&x.id==='feature-depth.b2b-decision-journey'));
  assert.ok(p.executionRules.some(x=>x.includes('buyer decision paths')));
});

test('low fidelity dense product does not force 1.7.2 genericity closure',()=>{
  const p=r.plan('Create a low-fidelity SaaS workflow wireframe.');
  assert.equal(p.classification.qualityClosureIntent,false);
  assert.equal(p.genericityClosure.length,0);
});

test('substantial web plans require fail-closed generation preflight',()=>{const p=r.plan('Create a production payments operations dashboard with filters and transaction recovery.');assert.ok(p.generationPreflight?.length);assert.equal(p.generationPreflight[0].failClosed,true);assert.ok(p.retrievalActions.some(x=>x.id==='qa-gates.generation-compiler-preflight'));assert.ok(p.evidencePlan[0].checks.includes('generation JavaScript preflight'));});

test('Revision 1.7.4 payments dashboard requires dense-product first-pass quality closure',()=>{
  const p=r.plan('Create a separate Stripe-like payments dashboard concept, front end only. Include transactions, filters, detail, recovery, and responsive behavior.');
  assert.ok(p.denseProductQualityClosure?.[0]?.required);
  assert.equal(p.denseProductQualityClosure[0].productFlavor,'payments');
  assert.deepEqual(p.denseProductQualityClosure[0].requiredViewports,[1440,390,320]);
  for(const id of ['visual-finish.dense-product-first-pass','completeness.dense-product-first-pass','accessibility-evidence.dense-product-first-pass','feature-depth.payments-analytics-level-5']) assert.ok(p.retrievalActions.some(x=>x.id===id),`missing ${id}`);
  for(const check of ['dense product visual finish','dense product completeness','dense product accessibility','dense product feature depth']) assert.ok(p.evidencePlan[0].checks.includes(check),`missing ${check}`);
});

test('Revision 1.7.4 analytics dashboard resolves analytics workflow-specific depth',()=>{
  const p=r.plan('Create a production analytics dashboard with metrics, cohorts, retention segments, drill-down, comparison, evidence context, and next actions.');
  assert.ok(p.denseProductQualityClosure?.[0]?.required);
  assert.equal(p.denseProductQualityClosure[0].productFlavor,'analytics');
  assert.match(p.denseProductQualityClosure[0].featureDepthPolicy,/decision\/question/);
});

test('Revision 1.7.4 SaaS dense-product closure stays general but fail-closed',()=>{
  const p=r.plan('Create a high-fidelity SaaS workflow concept with editable detail, error recovery, search, and filters.');
  assert.ok(p.denseProductQualityClosure?.[0]?.required);
  assert.equal(p.denseProductQualityClosure[0].productFlavor,'general');
  assert.equal(p.denseProductQualityClosure[0].failClosed,true);
});

test('Core 1.8 phase-local retrieval budgets expose deferred capabilities instead of preloading them',()=>{
  const p=r.plan('Create a high-fidelity internal claims operations dashboard for a fictional insurer with triage, inspection, escalation, recovery, and sample data.');
  assert.ok(p.deferredCapabilities.length>0);
  assert.ok(p.phases.every(x=>x.activeCapabilities.length<=x.budget));
  assert.match(p.retrievalBudget.policy,/phase-local budget/i);
  assert.ok(p.retrievalBudget.stableSectionTokenEstimate<45000,`unexpected eager retrieval budget ${p.retrievalBudget.stableSectionTokenEstimate}`);
});

test('Core 1.8 non-web families compile fail-closed family quality closure and thresholds',()=>{
  const cases=[
    ['Design a production-quality mobile commuter app for a fictional transit network.','mobile'],
    ['Create a 6-slide quarterly board review deck with sample metrics.','presentation'],
    ['Create an annual SaaS operating budget spreadsheet with formulas and scenarios.','spreadsheet'],
    ['Create a brand identity concept for a fictional coffee roaster.','brand'],
    ['Create a 4-email onboarding sequence for a fictional SaaS product.','email'],
    ['Create a local CLI tool that audits a CSV.','cli'],
    ['Create a polished fixed-format system design report PDF.','fixed-document']
  ];
  for(const [req,family] of cases){
    const p=r.plan(req);assert.ok(p.activeModules.includes('NONWEB_FIRST_PASS'),req);
    const q=p.artifactFamilyQualityClosure.find(x=>x.familyProfile===family);assert.ok(q?.required,req);assert.equal(q.failClosed,true);
    const a=p.artifactFamilyAcceptance.find(x=>x.artifactId===q.artifactId);assert.equal(a.overallMinimum,90);assert.equal(a.releaseCriticalMinimum,9);
    assert.ok(p.retrievalActions.some(x=>x.id==='nonweb-first-pass.family-contracts'),req);
  }
});

test('Core 1.8 36-case generalization routing holdout resolves exact artifact graphs',()=>{
  const cases=JSON.parse(r.core.read('benchmarks/v4_generalization_holdout_routing_cases.json'));assert.equal(cases.length,36);
  for(const c of cases){const p=r.plan(c.prompt);assert.deepEqual([...p.classification.creationTypes].sort(),[...c.expected_types].sort(),`${c.id}: ${p.classification.creationTypes.join(', ')}`);}
});

test('Core 1.8 adversarial routing corpus passes corrected semantic oracle',()=>{
  const cases=JSON.parse(r.core.read('benchmarks/v4_router_adversarial_cases.json'));assert.equal(cases.length,480);
  const rows=r.core.profileRows();
  for(const c of cases){
    const cl=classifyRequest(c.request,rows);const got=cl.creationTypes||[];
    if((c.types||[]).length)assert.deepEqual([...got].sort(),[...c.types].sort(),`${c.id} artifact types`);
    for(const [k,v] of Object.entries(c.exposures||{})){
      if(k==='expectedIndustry')continue;
      assert.equal(cl.contextGraph.artifactExposure[k]?.state,v,`${c.id} exposure ${k}`);
    }
    if(Object.prototype.hasOwnProperty.call(c.exposures||{},'expectedIndustry')){
      const expected=c.exposures.expectedIndustry;
      if(expected===null)assert.notEqual(cl.industry.status,'resolved',`${c.id} unexpected ${cl.industry.industry}`);
      else assert.equal(cl.industry.industry,expected,`${c.id} industry`);
    }
  }
});

test('Core 1.8.1 family-depth closure activates for repeated holdout failure families',()=>{
  const cases=[
    ['Create a production public website for a fictional specialty contractor with proof, qualification, primary conversion, secondary evaluation, and responsive behavior.','website'],
    ['Create a production native mobile appointment app with booking, rescheduling, interruption recovery, and adaptive compact/large device states.','mobile'],
    ['Create a complete brand identity system for a fictional B2B software company including mark, type, color, composition, iconography, imagery, usage rules, and applications.','brand'],
    ['Create a four-email onboarding campaign for a fictional SaaS product with audience states, sequence progression, CTAs, measurement events, and fallbacks.','email'],
    ['Create a production CLI developer tool with root help, a primary audit command, config precedence, deterministic output, exit codes, invalid-input recovery, and tests.','cli']
  ];
  for(const [req,family] of cases){
    const p=r.plan(req);assert.ok(p.activeModules.includes('FAMILY_DEPTH_CLOSURE'),req);
    const q=p.familyDepthClosure.find(x=>x.familyProfile===family);assert.ok(q?.required,req);assert.equal(q.failClosed,true);
    assert.ok(p.retrievalActions.some(x=>x.path==='FAMILY_DEPTH_CLOSURE.md'&&x.id===`family-depth-closure.${family}`),req);
  }
});

test('Core 1.8.1 composite closure requires narrow-screen containment for responsive children',()=>{
  const p=r.plan('Create a cohesive brand identity concept plus a front-end-only responsive marketing website for a fictional bakery, with shared identity decisions and independent child QA at 320 and 390 pixels.');
  assert.equal(p.classification.artifactGraph.kind,'composite');
  assert.equal(p.compositeDepthClosure.length,1);assert.equal(p.compositeDepthClosure[0].requiresNarrowScreen,true);
  assert.deepEqual(p.compositeDepthClosure[0].requiredViewports,[320,390]);
  assert.ok(p.retrievalActions.some(x=>x.id==='family-depth-closure.composite'));
});

test('Core 1.8.2 materialization closure activates and naturalizes production-facing output',()=>{
  const cases=[
    ['Create a production public website for a commercial roofing company with concrete services, qualification, proof requirements, and conversion states.','website'],
    ['Create a production native mobile inspection app for commercial property teams with offline recovery and sign-off states.','mobile'],
    ['Create a production brand identity for an industrial robotics integrator with usable rules and applications.','brand'],
    ['Create a four-email onboarding campaign for a payroll platform with concrete lifecycle states and recovery.','email'],
    ['Create a production CLI for validating logistics manifests with ergonomic help, errors, exit semantics, and recovery.','cli'],
    ['Create an executive presentation deck for a battery storage deployment program with decision evidence and next-state actions.','presentation'],
    ['Create a spreadsheet financial model for multi-site restaurant expansion with scenarios, assumptions, and decision outputs.','spreadsheet'],
    ['Create a fixed-format implementation readiness report for a hospital network with findings, actions, provenance, and accessible reading order.','fixed-document']
  ];
  for(const [req,family] of cases){
    const p=r.plan(req);assert.ok(p.activeModules.includes('MATERIALIZATION_CLOSURE'),req);
    const q=p.materializationClosure.find(x=>x.familyProfile===family);assert.ok(q?.required,req);assert.equal(q.failClosed,true);
    assert.ok(q.prohibitedProductionVocabulary.includes('P0'));assert.ok(q.minimumConcreteRecords>=4);
    assert.ok(p.retrievalActions.some(x=>x.path==='MATERIALIZATION_CLOSURE.md'&&x.id==='materialization-closure.naturalization'),req);
  }
});

test('Core 1.8.2 composite materialization keeps child depth independent',()=>{
  const p=r.plan('Create a complete brand identity plus a production marketing website and onboarding email campaign for a managed IT provider, with shared natural terminology and independent deliverables.');
  assert.equal(p.classification.artifactGraph.kind,'composite');
  assert.equal(p.compositeMaterializationClosure.length,1);
  assert.equal(p.compositeMaterializationClosure[0].failClosed,true);
  assert.ok(p.retrievalActions.some(x=>x.path==='MATERIALIZATION_CLOSURE.md'&&x.id==='materialization-closure.domain-materialization'));
});

test('Core 1.8.3 finished-surface naturalization remains active under later family adapters',()=>{
  const cases=[
    ['Create a production website for an occupied commercial roofing contractor with concrete repair/replacement qualification, drainage findings, warranty uncertainty, and request states.','website'],
    ['Create a production mobile field inspection app with asset-specific states, sync recovery, and sign-off outcomes.','mobile'],
    ['Create a production brand identity system for an industrial metrology company.','brand'],
    ['Create a four-email production onboarding campaign for a treasury operations platform.','email'],
    ['Create an executive presentation deck for a grid interconnection program.','presentation'],
    ['Create a spreadsheet financial model for multi-location clinic staffing.','spreadsheet'],
    ['Create a fixed-format implementation report for a municipal water utility.','fixed-document']
  ];
  for(const [req,family] of cases){
    const p=r.plan(req);assert.ok(p.activeModules.includes('EMISSION_PREFLIGHT'),req);
    const q=p.emissionAcceptance.find(x=>x.familyProfile===family);assert.ok(q?.required,req);assert.equal(q.directSurfaceScan,true);assert.equal(q.failClosed,true);
    assert.ok(p.retrievalActions.some(x=>x.path==='EMISSION_PREFLIGHT.md'&&x.id==='emission-preflight.naturalization-scan'),req);
    assert.ok(p.retrievalActions.some(x=>x.path==='EMISSION_PREFLIGHT.md'&&x.id==='emission-preflight.family-adapters'),req);
  }
});

test('Core 1.8.3 executable interfaces and CLI require universal syntax/runtime preflight',()=>{
  for(const req of [
    'Create a production front-end-only customer portal with JavaScript interactions.',
    'Create a production analytics dashboard with filters and drill-down controls.',
    'Create a production Node CLI for validating laboratory sample manifests with help, happy, and invalid-input paths.',
    'Create a production native mobile inventory app with executable interaction logic.'
  ]){
    const p=r.plan(req);assert.ok(p.activeModules.includes('EMISSION_PREFLIGHT'),req);
    assert.ok(p.universalExecutablePreflight.length>=1,req);
    for(const q of p.universalExecutablePreflight){assert.equal(q.runtimeRequired,true);assert.equal(q.failClosed,true);assert.equal(q.validator,'tools/validate_universal_executable_preflight.py');}
    assert.ok(p.retrievalActions.some(x=>x.path==='EMISSION_PREFLIGHT.md'&&x.id==='emission-preflight.universal-executable'),req);
  }
});


test('Core 1.8.4 uses family-native emission adapters and namespace-safe spreadsheet extraction',()=>{
  const cases=[
    ['Create a production website for a commercial waterproofing contractor with buyer proof and qualification.','website',['decisions','proof_points']],
    ['Create a production brand identity system for a precision robotics company.','brand',['identity_rules','applications','misuse_constraints']],
    ['Create a four-email production onboarding campaign for a procurement platform.','email',['audience_states','sequence_transitions','measurement_events']],
    ['Create a production Node CLI for validating research manifests.','cli',['commands','io_contracts','exit_semantics']],
    ['Create an executive presentation deck for a district-energy expansion program.','presentation',['storyline_beats','evidence_points','audience_takeaways']],
    ['Create a spreadsheet financial model for a field service staffing plan.','spreadsheet',['inputs','scenarios','decision_surfaces']],
    ['Create a fixed-format implementation report for a transit authority.','fixed-document',['questions_or_issues','evidence_points','findings_or_conclusions']]
  ];
  for(const [req,family,semanticKeys] of cases){
    const p=r.plan(req); const q=p.emissionAcceptance.find(x=>x.familyProfile===family); assert.ok(q,req);
    assert.equal(q.schema,'schemas/family_emission_evidence.schema.json'); assert.equal(q.validator,'tools/validate_family_emission_evidence.py');
    for(const key of semanticKeys) assert.ok(q.familySemantics.includes(key),`${req} missing ${key}`);
    assert.ok(p.retrievalActions.some(x=>x.path==='EMISSION_PREFLIGHT.md'&&x.id==='emission-preflight.family-adapters'),req);
    assert.ok(p.retrievalActions.some(x=>x.path==='EMISSION_PREFLIGHT.md'&&x.id==='emission-preflight.scaffold-context'),req);
    if(family==='spreadsheet') assert.ok(p.retrievalActions.some(x=>x.path==='EMISSION_PREFLIGHT.md'&&x.id==='emission-preflight.xlsx-adapter'),req);
  }
});

test('Core 1.8.4 preserves deck plus spreadsheet as an exact composite graph',()=>{
  const p=r.plan('Create an executive decision deck plus spreadsheet scenario model for a fictional community-solar project. Share assumptions and provenance across both deliverables.');
  assert.equal(p.classification.artifactGraph.kind,'composite');
  const types=p.classification.artifactGraph.nodes.map(x=>x.type);
  assert.ok(types.includes('Presentation / Deck')); assert.ok(types.includes('Spreadsheet / Financial Model'));
  const c=p.emissionAcceptance.find(x=>x.familyProfile==='composite'); assert.ok(c?.required); assert.equal(c.validator,'tools/validate_family_emission_evidence.py');
});


test('Core 1.8.5 deepens fixed-document emission and composite continuity',()=>{
  const doc=r.plan('Create a production fixed-format safety findings report for a fictional cold-storage operator with evidence, conclusions, implications, and source boundaries.');
  const dq=doc.emissionAcceptance.find(x=>x.familyProfile==='fixed-document'); assert.ok(dq?.required);
  assert.deepEqual(dq.fixedDocumentDepth,{minimumFindings:3,minimumImplicationsOrActions:3,minimumEvidencePoints:4,minimumProvenanceMarkers:2,minimumReaderTakeaways:2});
  assert.ok(dq.familySemantics.includes('reader_takeaways'));
  assert.ok(doc.retrievalActions.some(x=>x.path==='EMISSION_PREFLIGHT.md'&&x.id==='emission-preflight.fixed-document-depth'));

  const comp=r.plan('Create an executive presentation deck plus spreadsheet scenario model for a fictional transit electrification program, sharing assumptions, scenario names, provenance, and handoff decisions.');
  const cq=comp.emissionAcceptance.find(x=>x.familyProfile==='composite'); assert.ok(cq?.required);
  assert.ok(cq.familySemantics.includes('shared_identifiers_or_assumptions'));
  assert.ok(cq.familySemantics.includes('project_provenance_boundaries'));
  assert.equal(cq.continuityRequirements.minimumCrossArtifactContinuity,3);
  assert.ok(comp.retrievalActions.some(x=>x.path==='EMISSION_PREFLIGHT.md'&&x.id==='emission-preflight.composite-continuity'));
});

test('Core 1.8.5 compiles responsive composite containment before freeze',()=>{
  const p=r.plan('Create a production brand identity plus public website for a fictional marine sensing company.');
  assert.equal(p.classification.artifactGraph.kind,'composite');
  const q=p.compositeDepthClosure[0]; assert.ok(q?.required); assert.deepEqual(q.preFreezeViewports,[320,390]);
  assert.ok(q.generationPrerequisites.some(x=>x.includes('min-width:0')));
  assert.ok(p.retrievalActions.some(x=>x.path==='EMISSION_PREFLIGHT.md'&&x.id==='emission-preflight.compact-containment'));
});

test('Core 1.8.5 distinguishes decision-monitoring workspaces from authoring workspaces',()=>{
  const a=r.plan('Create a production contract renewal workspace for account leaders to monitor renewal health, deadlines, risk, evidence, and decisions.');
  assert.equal(a.classification.creationType,'Dashboard');
  const b=r.plan('Create a production contract editing workspace where legal operations users create records, edit terms, and manage approval workflows.');
  assert.equal(b.classification.creationType,'Web App / SaaS / Portal');
});


test('Core 1.8.6 closes renewal-monitoring workspace and fixed-report plus deck routing',()=>{
  const a=r.plan('Create a production service renewal monitoring workspace for account leaders to track health, deadlines, risk, evidence, and decisions.');
  assert.equal(a.classification.creationType,'Dashboard');
  const b=r.plan('Create a fixed analytical report plus executive decision deck for leadership.');
  const types=b.classification.artifactGraph.nodes.map(x=>x.type).sort();
  assert.deepEqual(types,['Fixed-Format Document / PDF','Presentation / Deck'].sort());
});

test('Core 1.8.6 routes render-aware fixed-document acceptance',()=>{
  const p=r.plan('Create a production fixed analytical report PDF for an operations review.');
  assert.ok(p.retrievalActions.some(x=>x.id==='emission-preflight.fixed-document-render'));
  assert.ok(p.retrievalActions.some(x=>x.id==='emission-preflight.semantic-equivalence'));
});


test('Core 1.8.7 recognizes qualified Excel model phrasings',()=>{
 for(const req of ['Create an Excel staffing scenario model for a fictional operator.','Create an Excel maintenance replacement model for a fictional fleet.']){const p=r.plan(req);assert.equal(p.classification.creationType,'Spreadsheet / Financial Model',req)}
});

test('Core 1.8.7 preserves explicit three-child artifact lists',()=>{
 const p=r.plan('Create a brand identity, onboarding email campaign, and landing page for a fictional tutoring service.');
 const t=p.classification.artifactGraph.nodes.map(x=>x.type);for(const q of ['Brand Identity / Logo','Email / Campaign','Website / Landing Page'])assert.ok(t.includes(q),q);assert.equal(p.classification.artifactGraph.kind,'composite');
});

test('Core 1.8.7 routes presentation slide-fit preflight',()=>{
 const p=r.plan('Create a production executive decision deck for a fictional utility modernization program.');
 assert.ok(p.retrievalActions.some(x=>x.path==='EMISSION_PREFLIGHT.md'&&x.id==='emission-preflight.presentation-slide-fit'));
 assert.ok(p.evidencePlan.some(x=>x.profile==='presentation'&&x.checks.includes('title/subtitle fit')));
});

test('Core 1.8.8 recognizes finished fixed-deliverable phrase variants',()=>{
 for(const req of ['Create a print-ready assessment report for a fictional operator.','Create a board-ready analytical report for a fictional utility.','Create a publication-ready evaluation report for a fictional nonprofit.']){
   const p=r.plan(req); assert.equal(p.classification.creationType,'Fixed-Format Document / PDF',req);
 }
});

test('Core 1.8.8 preserves modifier-tolerant explicit artifact lists',()=>{
 const p=r.plan('Create a brand identity, onboarding email campaign, and public landing page for a fictional tutoring service.');
 const t=p.classification.artifactGraph.nodes.map(x=>x.type);
 for(const q of ['Brand Identity / Logo','Email / Campaign','Website / Landing Page']) assert.ok(t.includes(q),q);
 assert.equal(p.classification.artifactGraph.kind,'composite');
});
