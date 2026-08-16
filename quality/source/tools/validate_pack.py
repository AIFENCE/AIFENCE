#!/usr/bin/env python3
"""BizIQ 4 integrity validator — Control-Plane Revision 1.8.8.

Default: full repository validation.
--overlay-only: validate the drag-and-drop Revision 1.7 package before extraction.
"""
from __future__ import annotations
import argparse,csv,json,re,sys,hashlib
from collections import defaultdict,Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_PACK="4.0.0"
EXPECTED_SCHEMA="3"
EXPECTED_DOMAINS=31
EXPECTED_CAPABILITIES=260
EXPECTED_CONTROLS=1300
EXPECTED_REGRESSION=780
EXPECTED_E2E_MIN=54

ap=argparse.ArgumentParser()
ap.add_argument("--overlay-only",action="store_true")
args=ap.parse_args()

errors=[];warnings=[]
def fail(x):errors.append(x)
def warn(x):warnings.append(x)
def read(p):
    try:return p.read_text(encoding="utf-8")
    except Exception as e:fail(f"Cannot read {p.relative_to(ROOT)}: {e}");return ""

md_files=sorted(ROOT.rglob("*.md"));texts={p:read(p) for p in md_files}
if not md_files:fail("No Markdown modules found.")

# Metadata and stable IDs.
pvs=defaultdict(list);svs=defaultdict(list);ids=defaultdict(list)
for p,t in texts.items():
    rel=str(p.relative_to(ROOT))
    pv=re.search(r"(?m)^Pack-Version:\s*([^\s]+)\s*$",t)
    sv=re.search(r"(?m)^Schema-Version:\s*([^\s]+)\s*$",t)
    if pv:pvs[pv.group(1)].append(rel)
    elif p.name not in {"PROJECT_TEMPLATE.md"} and not rel.startswith("benchmarks/"):warn(f"No Pack-Version metadata: {rel}")
    if sv:svs[sv.group(1)].append(rel)
    elif p.name not in {"PROJECT_TEMPLATE.md"} and not rel.startswith("benchmarks/"):warn(f"No Schema-Version metadata: {rel}")
    for m in re.finditer(r"<!--\s*id:\s*([^\s]+)\s*-->",t):ids[m.group(1)].append(rel)
for sid,locs in sorted(ids.items()):
    if len(locs)>1:fail(f"Duplicate stable ID {sid}: {', '.join(locs)}")
if pvs and set(pvs)!={EXPECTED_PACK}:fail(f"Pack-Version mismatch: {set(pvs)}")
if svs and set(svs)!={EXPECTED_SCHEMA}:fail(f"Schema-Version mismatch: {set(svs)}")

required_ids=[
"readme.control-plane-resolution","control-index.root","control-manifest.root",
"artifact-contracts.root","feature-compiler.root","component-compiler.root","genericity.root","genericity.dense-product-differentiation","feature-depth.b2b-decision-journey","visual-finish.dense-product-first-pass","completeness.dense-product-first-pass","accessibility-evidence.dense-product-first-pass","feature-depth.payments-analytics-level-5",
"critics.root","quality-floors.root","benchmarks.root","controls.domain.26","controls.domain.27",
"controls.domain.28","controls.domain.29","controls.domain.30","qa-gates.adversarial-acceptance-gate","qa-gates.revision-1-3-hardening","qa-gates.revision-1-4-quality-closure","craft.compiled-quality-loop","usability-closure.root","visual-finish.root","truth-boundaries.root","responsive-detail.root","quality-measurement.root","quality-measurement.render-state-normalization","benchmarks.render-state-normalization","benchmarks.runtime-1-0-5-fidelity","benchmark-status-1-6.root","qa-gates.benchmark-render-state-integrity","qa-gates.revision-1-6-operations-integrity","evals.operations-2-executable",
"semantic-routing.root","semantic-routing.negation","semantic-routing.context-graph","semantic-routing.composite","semantic-routing.reference-abstraction",
"retrieval-intelligence.root","retrieval-intelligence.phases","retrieval-intelligence.generated-shards","benchmark-pipeline.root","benchmark-pipeline.anchors","benchmark-pipeline.control-coverage","benchmark-pipeline.semantic-lint",
"evidence-adapter.root","evidence-adapter.browser","evidence-adapter.dense-product-first-pass","release-provenance.root","nonweb-first-pass.root","nonweb-first-pass.family-contracts","nonweb-first-pass.acceptance-thresholds","family-depth-closure.root","family-depth-closure.website","family-depth-closure.mobile","family-depth-closure.brand","family-depth-closure.email","family-depth-closure.cli","family-depth-closure.composite","family-depth-closure.acceptance","materialization-closure.root","materialization-closure.naturalization","materialization-closure.domain-materialization","materialization-closure.web-mobile","materialization-closure.brand-campaign","materialization-closure.nonweb-reading","materialization-closure.cli","materialization-closure.acceptance","emission-preflight.root","emission-preflight.naturalization-scan","emission-preflight.substance","emission-preflight.fixed-document-depth","emission-preflight.composite-continuity","emission-preflight.compact-containment","emission-preflight.universal-executable","emission-preflight.evidence","emission-preflight.acceptance","semantic-routing.dashboard-workspace","readme.revision-1-8-5","emission-preflight.semantic-equivalence","emission-preflight.fixed-document-render","accessibility-evidence.fixed-document","semantic-routing.revision-1-8-6","semantic-routing.revision-1-8-7","emission-preflight.presentation-slide-fit","contract.artifact.presentation-deck.slide-fit","readme.revision-1-8-7","benchmark-findings-1-8-7.root","readme.revision-1-8-generalization","readme.revision-1-8-1-family-depth","readme.revision-1-8-2-materialization","readme.revision-1-8-3-emission-preflight","qa-gates.revision-1-8-2-materialization","qa-gates.revision-1-8-3-emission-preflight","artifact-contracts.inheritance","readme.revision-1-7-semantic-retrieval","readme.revision-1-7-4-dense-product-first-pass","qa-gates.revision-1-7-4-dense-product-first-pass","qa-gates.revision-1-8-1-family-depth"
]
for sid in required_ids:
    if sid not in ids:fail(f"Required Revision 1.2 stable ID missing: {sid}")


# Canonical source-cleanliness and current-summary consistency.
for p,t in texts.items():
    rel=str(p.relative_to(ROOT))
    if re.search(r"\\n(?:#|<!--)",t): fail(f"Literal escaped newline before Markdown structure: {rel}")
readme_text=texts.get(ROOT/"README.md","")
compat=re.search(r"# Pack Version & Compatibility.*?```text\n(.*?)```",readme_text,re.S)
if not compat: fail("README compatibility block missing")
else:
    block=compat.group(1)
    for token in ["Control Plane Revision: 1.8.8","31 domains","260 capabilities","1,300 controls","780 regression conditions"]:
        if token not in readme_text: fail(f"README current architecture summary missing/stale: {token}")
qa_text=texts.get(ROOT/"QA_GATES.md","")
for token in ["BQ-0001–BQ-1300","all 260 capabilities"]:
    if token not in qa_text: fail(f"QA_GATES current control-plane summary missing/stale: {token}")

# JSON syntax.
for p in sorted(ROOT.rglob("*.json")):
    try:json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:fail(f"Invalid JSON {p.relative_to(ROOT)}: {e}")

# Artifact contracts.
contract_dir=ROOT/"contracts";contracts=sorted(contract_dir.glob("*.md")) if contract_dir.is_dir() else []
if len(contracts)!=16:fail(f"Expected 16 artifact contracts, found {len(contracts)}")
for token in [
"contract.artifact.marketing-website","contract.artifact.local-service-website","contract.artifact.saas-web-app",
"contract.artifact.dashboard","contract.artifact.ecommerce-marketplace","contract.artifact.regulated-public-interface",
"contract.artifact.document-report","contract.artifact.operations-workflow",
"contract.artifact.native-mobile-app","contract.artifact.presentation-deck","contract.artifact.spreadsheet-financial-model",
"contract.artifact.brand-identity","contract.artifact.email-campaign","contract.artifact.marketing-creative",
"contract.artifact.cli-developer-tool","contract.artifact.fixed-format-document"]:
    if token not in ids:fail(f"Artifact contract stable ID missing: {token}")

# Required schemas.
for rel in ["schemas/feature_spec.schema.json","schemas/component_spec.schema.json",
            "schemas/structural_fingerprint.schema.json","schemas/critique_report.schema.json",
            "schemas/artifact_acceptance.schema.json","schemas/benchmark_case.schema.json","schemas/responsive_composition.schema.json","schemas/document_depth.schema.json","schemas/accessibility_evidence.schema.json","schemas/completeness_ledger.schema.json","schemas/feature_depth_evidence.schema.json",
            "schemas/usability_evidence.schema.json","schemas/visual_finish_evidence.schema.json","schemas/truth_boundary.schema.json",
            "schemas/responsive_detail_evidence.schema.json","schemas/quality_measurement.schema.json",
            "schemas/operational_procedure.schema.json","schemas/procedure_authority.schema.json","schemas/decision_rights.schema.json",
            "schemas/kpi_definition.schema.json","schemas/operational_evidence.schema.json","schemas/role_accountability.schema.json",
            "schemas/context_graph.schema.json","schemas/artifact_graph.schema.json","schemas/execution_evidence.schema.json",
        "schemas/interaction_closure_manifest.schema.json","schemas/genericity_evidence.schema.json","schemas/decision_depth_evidence.schema.json","schemas/dense_product_quality_evidence.schema.json","schemas/artifact_family_quality_evidence.schema.json","schemas/family_depth_evidence.schema.json","schemas/materialization_evidence.schema.json","schemas/emission_substance_evidence.schema.json","schemas/universal_executable_runtime_evidence.schema.json","schemas/presentation_slide_fit_evidence.schema.json","schemas/benchmark_run.schema.json","schemas/release_provenance.schema.json"]:
    if not (ROOT/rel).is_file():fail(f"Schema missing: {rel}")

# Public benchmark corpus.
dev=ROOT/"benchmarks"/"v2_development_cases.json"
try:dev_cases=json.loads(dev.read_text(encoding="utf-8"))
except Exception as e:fail(f"Cannot parse benchmark dev set: {e}");dev_cases=[]
if len(dev_cases)!=48:fail(f"Expected 48 benchmark development cases, found {len(dev_cases)}")
if dev_cases and len({x.get("id") for x in dev_cases})!=48:fail("Duplicate Benchmark V2 development IDs")

# Targeted Revision 1.3 hardening corpus.
hard=ROOT/"benchmarks"/"v2_hardening_cases.json"
try: hard_cases=json.loads(hard.read_text(encoding="utf-8"))
except Exception as e: fail(f"Cannot parse hardening benchmark set: {e}"); hard_cases=[]
if len(hard_cases)!=20: fail(f"Expected 20 Revision 1.3 hardening cases, found {len(hard_cases)}")

# Targeted Revision 1.4 quality-closure corpus.
quality=ROOT/"benchmarks"/"v2_quality_closure_cases.json"
try: quality_cases=json.loads(quality.read_text(encoding="utf-8"))
except Exception as e: fail(f"Cannot parse quality-closure benchmark set: {e}"); quality_cases=[]
if len(quality_cases)!=20: fail(f"Expected 20 Revision 1.4 quality-closure cases, found {len(quality_cases)}")
if quality_cases and len({x.get("id") for x in quality_cases})!=20: fail("Duplicate Revision 1.4 quality-closure IDs")


# Revision 1.6 runtime-fidelity / quality-closure benchmark corpus.
runtime_quality=ROOT/"benchmarks"/"v2_runtime_fidelity_cases.json"
try: runtime_quality_cases=json.loads(runtime_quality.read_text(encoding="utf-8"))
except Exception as e: fail(f"Cannot parse Runtime 1.0.5 fidelity benchmark set: {e}"); runtime_quality_cases=[]
if len(runtime_quality_cases)!=12: fail(f"Expected 12 Runtime 1.0.5 fidelity benchmark cases, found {len(runtime_quality_cases)}")
if runtime_quality_cases and len({x.get("id") for x in runtime_quality_cases})!=12: fail("Duplicate Runtime 1.0.5 fidelity benchmark IDs")

# Revision 1.7 semantic-routing / retrieval corpus.
semantic=ROOT/"benchmarks"/"v2_semantic_routing_cases.json"
try: semantic_cases=json.loads(semantic.read_text(encoding="utf-8"))
except Exception as e: fail(f"Cannot parse Revision 1.7 semantic routing benchmark set: {e}"); semantic_cases=[]
if len(semantic_cases)!=30: fail(f"Expected 30 Revision 1.7 semantic routing cases, found {len(semantic_cases)}")
if semantic_cases and len({x.get("id") for x in semantic_cases})!=30: fail("Duplicate Revision 1.7 semantic routing IDs")

# Revision 1.7.1 interaction/mobile closure corpus derived from the real-artifact benchmark.
try: interaction_cases=json.loads((ROOT/"benchmarks"/"v3_interaction_closure_cases.json").read_text(encoding="utf-8"))
except Exception as e: fail(f"Cannot parse Revision 1.7.1 interaction closure cases: {e}"); interaction_cases=[]
if len(interaction_cases)!=3: fail(f"Expected 3 Revision 1.7.1 interaction closure cases, found {len(interaction_cases)}")
if interaction_cases and len({x.get("id") for x in interaction_cases})!=3: fail("Duplicate Revision 1.7.1 interaction closure IDs")
for c in interaction_cases:
    if not c.get("failure_pattern") or not c.get("acceptance") or not c.get("required_checks"): fail(f"Incomplete interaction closure case: {c.get('id')}")

# Revision 1.7.3 structural-genericity / B2B decision-depth corpus.
try: quality_floor_closure_cases=json.loads((ROOT/"benchmarks"/"v3_quality_floor_closure_cases.json").read_text(encoding="utf-8"))
except Exception as e: fail(f"Cannot parse Revision 1.7.3 quality-floor closure cases: {e}"); quality_floor_closure_cases=[]
if len(quality_floor_closure_cases)!=3: fail(f"Expected 3 Revision 1.7.3 quality-floor closure cases, found {len(quality_floor_closure_cases)}")
if quality_floor_closure_cases and len({x.get("id") for x in quality_floor_closure_cases})!=3: fail("Duplicate Revision 1.7.3 quality-floor closure IDs")

# Revision 1.7.4 dense-product first-pass quality corpus.
try: dense_first_pass_cases=json.loads((ROOT/"benchmarks"/"v3_dense_product_first_pass_cases.json").read_text(encoding="utf-8"))
except Exception as e: fail(f"Cannot parse Revision 1.7.4 dense-product first-pass cases: {e}"); dense_first_pass_cases=[]
if len(dense_first_pass_cases)!=3: fail(f"Expected 3 Revision 1.7.4 dense-product first-pass cases, found {len(dense_first_pass_cases)}")
if dense_first_pass_cases and len({x.get("id") for x in dense_first_pass_cases})!=3: fail("Duplicate Revision 1.7.4 dense-product first-pass IDs")
for c in quality_floor_closure_cases:
    if not c.get("failure_pattern") or not c.get("acceptance") or not c.get("required_checks"): fail(f"Incomplete quality-floor closure case: {c.get('id')}")

# Revision 1.8 generalization routing and adversarial corpora.
try: generalization_cases=json.loads((ROOT/"benchmarks"/"v4_generalization_holdout_routing_cases.json").read_text(encoding="utf-8"))
except Exception as e: fail(f"Cannot parse Revision 1.8 generalization routing cases: {e}"); generalization_cases=[]
if len(generalization_cases)!=36: fail(f"Expected 36 Revision 1.8 generalization routing cases, found {len(generalization_cases)}")
if generalization_cases and len({x.get("id") for x in generalization_cases})!=36: fail("Duplicate Revision 1.8 generalization routing IDs")
try: adversarial_cases=json.loads((ROOT/"benchmarks"/"v4_router_adversarial_cases.json").read_text(encoding="utf-8"))
except Exception as e: fail(f"Cannot parse Revision 1.8 adversarial routing cases: {e}"); adversarial_cases=[]
if len(adversarial_cases)!=480: fail(f"Expected 480 Revision 1.8 adversarial routing cases, found {len(adversarial_cases)}")
if adversarial_cases and len({x.get("id") for x in adversarial_cases})!=480: fail("Duplicate Revision 1.8 adversarial routing IDs")

# Revision 1.8 artifact-family first-pass closure.
family_text=(ROOT/"NONWEB_FIRST_PASS.md").read_text(encoding="utf-8") if (ROOT/"NONWEB_FIRST_PASS.md").is_file() else ""
for token in ["nonweb-first-pass.family-contracts","Native / Mobile App","Spreadsheet / Financial Model","CLI / Developer Tool","overall score >= 90/100","artifact_family_quality_evidence.schema.json"]:
    if token.lower() not in family_text.lower(): fail(f"Revision 1.8 artifact-family closure token missing: {token}")
if not (ROOT/"tools"/"validate_artifact_family_quality_evidence.py").is_file(): fail("Revision 1.8 artifact-family evidence validator missing")

# Revision 1.8.1 repeated-family depth / containment closure.
family_depth_text=(ROOT/"FAMILY_DEPTH_CLOSURE.md").read_text(encoding="utf-8") if (ROOT/"FAMILY_DEPTH_CLOSURE.md").is_file() else ""
for token in ["Website Decision Depth","Mobile Workflow Depth","Brand System Completeness","Campaign Sequence Depth","CLI Product Depth","Composite Narrow-Screen Containment","family_depth_evidence.schema.json"]:
    if token.lower() not in family_depth_text.lower(): fail(f"Revision 1.8.1 family-depth closure token missing: {token}")
if not (ROOT/"tools"/"validate_family_depth_evidence.py").is_file(): fail("Revision 1.8.1 family-depth evidence validator missing")
try: family_depth_cases=json.loads((ROOT/"benchmarks"/"v5_family_depth_closure_cases.json").read_text(encoding="utf-8"))
except Exception as e: fail(f"Cannot parse Revision 1.8.1 family-depth cases: {e}"); family_depth_cases=[]
if len(family_depth_cases)!=6: fail(f"Expected 6 Revision 1.8.1 family-depth cases, found {len(family_depth_cases)}")
if family_depth_cases and len({x.get("id") for x in family_depth_cases})!=6: fail("Duplicate Revision 1.8.1 family-depth IDs")


# Revision 1.8.2 domain materialization / naturalization closure.
materialization_text=(ROOT/"MATERIALIZATION_CLOSURE.md").read_text(encoding="utf-8") if (ROOT/"MATERIALIZATION_CLOSURE.md").is_file() else ""
for token in ["Naturalization Boundary","Concrete Domain Materialization","Brand & Campaign Materialization","Non-Web Reading & Decision Surfaces","CLI Interface Naturalization","materialization_evidence.schema.json"]:
    if token.lower() not in materialization_text.lower(): fail(f"Revision 1.8.2 materialization token missing: {token}")
if not (ROOT/"tools"/"validate_materialization_evidence.py").is_file(): fail("Revision 1.8.2 materialization evidence validator missing")
try: materialization_cases=json.loads((ROOT/"benchmarks"/"v6_materialization_closure_cases.json").read_text(encoding="utf-8"))
except Exception as e: fail(f"Cannot parse Revision 1.8.2 materialization cases: {e}"); materialization_cases=[]
if len(materialization_cases)!=10: fail(f"Expected 10 Revision 1.8.2 materialization cases, found {len(materialization_cases)}")
if materialization_cases and len({x.get("id") for x in materialization_cases})!=10: fail("Duplicate Revision 1.8.2 materialization IDs")

# Revision 1.8.3 post-emission naturalization/substance and universal executable preflight.
emission_text=(ROOT/"EMISSION_PREFLIGHT.md").read_text(encoding="utf-8") if (ROOT/"EMISSION_PREFLIGHT.md").is_file() else ""
for token in ["Finished-Surface Naturalization Scan","Emitted Material Substance","Universal Executable Grammar Preflight","validate_emission_preflight.py","validate_universal_executable_preflight.py"]:
    if token.lower() not in emission_text.lower(): fail(f"Revision 1.8.3 emission-preflight token missing: {token}")
for rel in ["tools/validate_emission_preflight.py","tools/validate_universal_executable_preflight.py","schemas/emission_substance_evidence.schema.json","schemas/universal_executable_runtime_evidence.schema.json"]:
    if not (ROOT/rel).is_file(): fail(f"Revision 1.8.3 emission-preflight file missing: {rel}")
try: emission_cases=json.loads((ROOT/"benchmarks"/"v7_emission_preflight_cases.json").read_text(encoding="utf-8"))
except Exception as e: fail(f"Cannot parse Revision 1.8.3 emission-preflight cases: {e}"); emission_cases=[]
if len(emission_cases)!=8: fail(f"Expected 8 Revision 1.8.3 emission-preflight cases, found {len(emission_cases)}")
if emission_cases and len({x.get("id") for x in emission_cases})!=8: fail("Duplicate Revision 1.8.3 emission-preflight IDs")

# Revision 1.8.4 family-aware emission adapters, OOXML/XLSX extraction, scaffold context, and composite routing closure.
for token in ["Family-Aware Emission Adapters","Namespace-Safe XLSX Surface Adapter","Context-Sensitive Scaffold Detection","family_emission_evidence.schema.json","validate_family_emission_evidence.py"]:
    if token.lower() not in emission_text.lower(): fail(f"Revision 1.8.4 family-emission token missing: {token}")
for rel in ["tools/validate_family_emission_evidence.py","schemas/family_emission_evidence.schema.json"]:
    if not (ROOT/rel).is_file(): fail(f"Revision 1.8.4 family-emission file missing: {rel}")
try: family_emission_cases=json.loads((ROOT/"benchmarks"/"v8_family_emission_adapter_cases.json").read_text(encoding="utf-8"))
except Exception as e: fail(f"Cannot parse Revision 1.8.4 family-emission cases: {e}"); family_emission_cases=[]
if len(family_emission_cases)!=12: fail(f"Expected 12 Revision 1.8.4 family-emission cases, found {len(family_emission_cases)}")
if family_emission_cases and len({x.get("id") for x in family_emission_cases})!=12: fail("Duplicate Revision 1.8.4 family-emission IDs")

# Revision 1.8.6 render-aware documents, semantic acceptance, and routing closure.
for rel in ["schemas/fixed_document_render_evidence.schema.json","tools/validate_fixed_document_render_evidence.py","tools/test_revision_1_8_6.py","benchmarks/v10_render_semantic_routing_cases.json"]:
    if not (ROOT/rel).is_file(): fail(f"Revision 1.8.6 file missing: {rel}")
if "Semantic-Equivalence Materialization".lower() not in emission_text.lower(): fail("Revision 1.8.6 semantic-equivalence section missing")
if "Render-Aware Fixed-Document Preflight".lower() not in emission_text.lower(): fail("Revision 1.8.6 fixed-document render section missing")
try: r186_cases=json.loads((ROOT/"benchmarks/v10_render_semantic_routing_cases.json").read_text())
except Exception as e: fail(f"Cannot parse Revision 1.8.6 regression cases: {e}"); r186_cases=[]
if len(r186_cases)!=8: fail(f"Expected 8 Revision 1.8.6 regression cases, found {len(r186_cases)}")

# Revision 1.8.5 fixed-document depth, composite continuity/compact containment, and dashboard/workspace boundary.
for token in ["Fixed-Document Findings & Implications Depth","Composite Project Continuity","Responsive Composite Pre-Freeze Containment Compiler"]:
    if token.lower() not in emission_text.lower(): fail(f"Revision 1.8.5 closure token missing: {token}")
semantic_text=(ROOT/"SEMANTIC_ROUTING.md").read_text(encoding="utf-8") if (ROOT/"SEMANTIC_ROUTING.md").is_file() else ""
if "Dashboard vs Workspace Boundary".lower() not in semantic_text.lower(): fail("Revision 1.8.5 dashboard/workspace routing boundary missing")
for rel in ["BENCHMARK_FINDINGS_1_8_5.md","benchmarks/v9_fixed_document_composite_containment_cases.json","tools/test_revision_1_8_5.py"]:
    if not (ROOT/rel).is_file(): fail(f"Revision 1.8.5 file missing: {rel}")
try: r185_cases=json.loads((ROOT/"benchmarks"/"v9_fixed_document_composite_containment_cases.json").read_text(encoding="utf-8"))
except Exception as e: fail(f"Cannot parse Revision 1.8.5 regression cases: {e}"); r185_cases=[]
if len(r185_cases)!=10: fail(f"Expected 10 Revision 1.8.5 regression cases, found {len(r185_cases)}")
if r185_cases and len({x.get("id") for x in r185_cases})!=10: fail("Duplicate Revision 1.8.5 regression IDs")


# Revision 1.8.7 artifact-graph phrase coverage and slide-fit preflight.
for rel in ["schemas/presentation_slide_fit_evidence.schema.json","tools/validate_presentation_slide_fit_evidence.py","tools/test_revision_1_8_7.py","benchmarks/v11_artifact_graph_slide_fit_cases.json","BENCHMARK_FINDINGS_1_8_7.md"]:
    if not (ROOT/rel).is_file(): fail(f"Revision 1.8.7 file missing: {rel}")
if "Presentation Slide-Fit & Render Preflight".lower() not in emission_text.lower(): fail("Revision 1.8.7 presentation slide-fit section missing")
try: r187_cases=json.loads((ROOT/"benchmarks/v11_artifact_graph_slide_fit_cases.json").read_text())
except Exception as e: fail(f"Cannot parse Revision 1.8.7 regression cases: {e}"); r187_cases=[]
if len(r187_cases)!=4: fail(f"Expected 4 Revision 1.8.7 regression cases, found {len(r187_cases)}")


# Revision 1.8.8 deliverable phrase normalization and modifier-tolerant composite parsing.
for rel in ["tools/test_revision_1_8_8.py","benchmarks/v12_deliverable_phrase_composite_cases.json","BENCHMARK_FINDINGS_1_8_8.md"]:
    if not (ROOT/rel).is_file(): fail(f"Revision 1.8.8 file missing: {rel}")
for token in ["semantic-routing.deliverable-phrase-normalization","semantic-routing.modifier-tolerant-composites"]:
    if token not in semantic_text: fail(f"Revision 1.8.8 semantic routing section missing: {token}")
try: r188_cases=json.loads((ROOT/"benchmarks/v12_deliverable_phrase_composite_cases.json").read_text())
except Exception as e: fail(f"Cannot parse Revision 1.8.8 routing cases: {e}"); r188_cases=[]
if len(r188_cases)!=40: fail(f"Expected 40 Revision 1.8.8 routing cases, found {len(r188_cases)}")
if r188_cases and len({x.get("id") for x in r188_cases})!=40: fail("Duplicate Revision 1.8.8 routing IDs")

# Targeted Revision 1.5 Operations 2.0 corpus.
ops2=ROOT/"benchmarks"/"v2_operations_2_cases.json"
try: ops2_cases=json.loads(ops2.read_text(encoding="utf-8"))
except Exception as e: fail(f"Cannot parse Operations 2.0 benchmark set: {e}"); ops2_cases=[]
if len(ops2_cases)!=20: fail(f"Expected 20 Revision 1.5 Operations 2.0 cases, found {len(ops2_cases)}")
if ops2_cases and len({x.get("id") for x in ops2_cases})!=20: fail("Duplicate Revision 1.5 Operations 2.0 IDs")

# Generic fingerprint library.
gfp=ROOT/"evals"/"generic_template_fingerprints.json"
try:gprints=json.loads(gfp.read_text(encoding="utf-8"))
except Exception as e:fail(f"Cannot parse generic fingerprint library: {e}");gprints=[]
if len(gprints)<10:fail("Expected at least 10 generic template fingerprints")
genericity_text=(ROOT/"GENERICITY.md").read_text(encoding="utf-8")
for token in ["genericity.dense-product-differentiation","Competitor-swap resistance","0.61","schemas/genericity_evidence.schema.json"]:
    if token not in genericity_text: fail(f"Revision 1.7.3 genericity closure token missing: {token}")

for rel,required in {
    "VISUAL_FINISH.md":["Dense-Product First-Pass Finish","surface roles","320px"],
    "COMPLETENESS.md":["Dense-Product First-Pass Completion Matrix","acceptance evidence"],
    "ACCESSIBILITY_EVIDENCE.md":["Dense-Product First-Pass Accessibility Closure","programmatically determinable feedback"],
    "FEATURE_DEPTH.md":["Payments & Analytics Level-5 Depth Closure","inspect transaction","decision/question"]
}.items():
    txt=texts.get(ROOT/rel,"")
    for token in required:
        if token.lower() not in txt.lower(): fail(f"Revision 1.7.4 dense-product quality token missing in {rel}: {token}")


# Overlay registry shards 26..28.
overlay_registry=[]
for n in (26,27,28,29,30,31):
    matches=list((ROOT/"control_registry").glob(f"{n:02d}-*.csv")) if (ROOT/"control_registry").is_dir() else []
    if len(matches)!=1:fail(f"Expected one registry shard for Domain {n}, found {len(matches)}")
    for fp in matches:
        with fp.open(encoding="utf-8",newline="") as f:overlay_registry.extend(list(csv.DictReader(f)))
if overlay_registry:
    nums=sorted(int(r["id"].split("-")[1]) for r in overlay_registry)
    if nums!=list(range(1001,1301)):fail("Revision registry shards are not contiguous BQ-1001..BQ-1300")
    caps=defaultdict(list)
    for r in overlay_registry:
        caps[(r["domain"],r["capability"])].append(r)
        if r["control_id"] not in ids:fail(f"Control stable ID missing: {r['control_id']}")
        if r["capability_id"] not in ids:fail(f"Capability stable ID missing: {r['capability_id']}")
    if len(caps)!=60:fail(f"Expected 60 capabilities across Domains 26–31, found {len(caps)}")
    required={"Contract","Procedure","Evidence Gate","Recovery","Regression"}
    for k,rs in caps.items():
        if len(rs)!=5 or {r["control"] for r in rs}!=required:fail(f"Capability lacks exact five controls: {k}")

# Overlay regression shards 26..28.
overlay_reg=[]
for n in (26,27,28,29,30,31):
    fp=ROOT/"evals"/f"control_regression_matrix_{n}.json"
    if not fp.is_file():fail(f"Missing regression shard: {fp.relative_to(ROOT)}")
    else:
        try:overlay_reg.extend(json.loads(fp.read_text(encoding="utf-8")))
        except Exception as e:fail(f"Cannot parse {fp.relative_to(ROOT)}: {e}")
if len(overlay_reg)!=180:fail(f"Expected 180 regression conditions across Domains 26–31, found {len(overlay_reg)}")
if overlay_reg:
    kinds=Counter(x.get("case") for x in overlay_reg)
    if kinds!={"normal":60,"ambiguous":60,"failure":60}:fail(f"Overlay regression balance incorrect: {dict(kinds)}")

# E2E.
try:cases=json.loads((ROOT/"evals"/"end_to_end_cases.json").read_text(encoding="utf-8"))
except Exception as e:fail(f"Cannot parse end-to-end cases: {e}");cases=[]
if len(cases)<EXPECTED_E2E_MIN:fail(f"Expected at least {EXPECTED_E2E_MIN} end-to-end cases, found {len(cases)}")
for cid in ["e2e.artifact-contract-resolution","e2e.structural-fingerprint-rejection",
            "e2e.quality-floor-no-average","e2e.blind-benchmark-integrity"]:
    if not any(x.get("id")==cid for x in cases):fail(f"Required E2E case missing: {cid}")

# Canonical architecture tokens.
index=texts.get(ROOT/"CONTROL_INDEX.md","");readme=texts.get(ROOT/"README.md","")
for token in ["31 domains","260 capabilities","1,300 controls","BQ-1300","27. Artifact Contracts","28. Adversarial Critique","29. Benchmark-Driven","30. Usability","31. Operational Procedure"]:
    if token not in index and token not in readme:fail(f"Architecture token missing: {token}")
if "do not preload all 31 shards" not in readme.lower():fail("README lazy-loading count is stale")

# Required tools.
for rel in ["tools/validate_pack.py","tools/prepare_benchmark.py","tools/score_benchmark.py","tools/fingerprint_similarity.py","tools/validate_operational_procedure.py","tools/validate_genericity_evidence.py","tools/validate_decision_depth_evidence.py","tools/test_operations_2.py"]:
    if not (ROOT/rel).is_file():fail(f"Required tool missing: {rel}")

if not args.overlay_only:
    # Full repository foundation check. Revision 1.2 is cumulative and expects
    # the original BizIQ 4 base pack to remain present.
    foundation_required = [
        "INDUSTRIES.md",
        "PROFILE_MATRIX.md",
        "CREATIVE.md",
        "ASSETS.md",
        "DESIGN.md",
        "FEATURES.md",
        "HALO.md",
        "JOBS.md",
        "MANIFEST.md",
        "STRUCTURE.md",
        "SECURITY.md",
        "LEGAL.md",
        "TERMINOLOGY.md",
        "control_registry.csv",
        "evals/control_regression_matrix.json",
        "controls/01-initialization-precedence-and-agent-control.md",
        "controls/25-pack-governance-versioning-evals-and-self-improvement.md",
    ]
    missing_foundation = [x for x in foundation_required if not (ROOT/x).is_file()]
    if missing_foundation:
        fail(
            "Base BizIQ pack is incomplete. The complete BizIQ package is cumulative, but "
            f"{len(missing_foundation)} required foundation path(s) are missing. "
            "Restore/re-extract the complete BizIQ package, then rerun validation. "
            "Missing: " + ", ".join(missing_foundation)
        )
        print(f"BizIQ validator mode=full: revision=1.8.8")
        for w in warnings:
            print("WARN:", w)
        print(f"FAIL: {len(errors)} error(s)")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    # Full taxonomy/module checks.
    industries=texts.get(ROOT/"INDUSTRIES.md","")
    pairs=re.findall(r"(?m)^#\s+([^\n]+)\n<!--\s*id:\s*(industry\.[^\s]+)\s*-->",industries)
    industry_ids={sid for _,sid in pairs}
    if not industry_ids:fail("No canonical industry IDs parsed")
    for fn,prefix in [("DESIGN.md","design.industry."),("FEATURES.md","features.industry."),("HALO.md","halo.industry."),("JOBS.md","jobs.industry.")]:
        tx=texts.get(ROOT/fn,"");mapped=set(re.findall(rf"<!--\s*id:\s*({re.escape(prefix)}[^\s]+)\s*-->",tx))
        converted={"industry."+x[len(prefix):] for x in mapped}
        if converted!=industry_ids:
            miss=sorted(industry_ids-converted);extra=sorted(converted-industry_ids)
            if miss:fail(f"{fn} missing industries: {', '.join(miss[:5])}")
            if extra:fail(f"{fn} unknown industries: {', '.join(extra[:5])}")

    profile=texts.get(ROOT/"PROFILE_MATRIX.md","")
    if "| Landscaping & Horticulture | `industry.landscaping-and-horticulture` |" not in profile.split("# Industry Matrix")[0]:
        fail("Landscaping mixed-model registry entry missing")

    creative=texts.get(ROOT/"CREATIVE.md","");assets=texts.get(ROOT/"ASSETS.md","");craft=texts.get(ROOT/"CRAFT.md","")
    for phrase in ["Production Visual Acceptance Gate","at least 3 strong current category references",
                   "at least 3 materially different directions","92–100",
                   "If the company name and logo could be replaced with a competitor's"]:
        if phrase not in creative:fail(f"CREATIVE guard missing: {phrase}")
    if "low-detail generic SVG" not in assets or "verified completed work" not in assets:fail("ASSETS proof-bearing guard incomplete")
    for phrase in ["Feature Depth Standard","Component Anatomy Standard","Production Craft Acceptance Gate","Compiled Quality Loop"]:
        if phrase not in craft:fail(f"CRAFT guard missing: {phrase}")

    for rel in ["tools/audit_control_coverage.py","tools/lint_control_semantics.py","tools/benchmark_pipeline.py","tools/validate_execution_evidence.py","tools/test_revision_1_7.py"]:
        if not (ROOT/rel).is_file(): fail(f"Revision 1.7 tool missing: {rel}")
    sem=texts.get(ROOT/"SEMANTIC_ROUTING.md",""); ret=texts.get(ROOT/"RETRIEVAL_INTELLIGENCE.md",""); ev=texts.get(ROOT/"EVIDENCE_ADAPTER.md","")
    for phrase in ["Token-Aware Industry Resolution","Negation-Aware Exposure Resolution","Composite Artifact Graph","Reference Inspiration Abstraction"]:
        if phrase not in sem: fail(f"SEMANTIC_ROUTING guard missing: {phrase}")
    for phrase in ["stable-ID capability sections","Phase Compiler","Generated Capability Shards"]:
        if phrase not in ret: fail(f"RETRIEVAL_INTELLIGENCE guard missing: {phrase}")
    if "Browser Evidence Profile" not in ev or "Evidence never upgrades an unexecuted check to PASS" not in ev: fail("EVIDENCE_ADAPTER executable evidence contract incomplete")

    # Full logical registry = root + native shards.
    reg_files=[]
    root_reg=ROOT/"control_registry.csv"
    if not root_reg.is_file():fail("control_registry.csv missing")
    else:reg_files.append(root_reg)
    if (ROOT/"control_registry").is_dir():reg_files.extend(sorted((ROOT/"control_registry").glob("*.csv")))
    registry=[]
    for fp in reg_files:
        with fp.open(encoding="utf-8",newline="") as f:registry.extend(list(csv.DictReader(f)))
    if len(registry)!=EXPECTED_CONTROLS:fail(f"Expected {EXPECTED_CONTROLS} controls, found {len(registry)}")
    if registry:
        cids=[r["id"] for r in registry]
        if sorted(cids)!=[f"BQ-{i:04d}" for i in range(1,EXPECTED_CONTROLS+1)]:fail("Full registry not exactly BQ-0001..BQ-1300")
        caps=defaultdict(list);domains=set();shards=set()
        for r in registry:
            caps[(r["domain"],r["capability"])].append(r);domains.add(r["domain"]);shards.add(r["shard"])
            if r["control_id"] not in ids:fail(f"Control stable ID missing: {r['control_id']}")
            if r["capability_id"] not in ids:fail(f"Capability stable ID missing: {r['capability_id']}")
            if not (ROOT/r["shard"]).is_file():fail(f"Control shard missing: {r['shard']}")
        if len(caps)!=EXPECTED_CAPABILITIES:fail(f"Expected {EXPECTED_CAPABILITIES} capabilities, found {len(caps)}")
        if len(domains)!=EXPECTED_DOMAINS:fail(f"Expected {EXPECTED_DOMAINS} domains, found {len(domains)}")
        if len(shards)!=EXPECTED_DOMAINS:fail(f"Expected {EXPECTED_DOMAINS} control shards, found {len(shards)}")
        required={"Contract","Procedure","Evidence Gate","Recovery","Regression"}
        for k,rs in caps.items():
            if len(rs)!=5 or {r["control"] for r in rs}!=required:fail(f"Bad capability stages: {k}")
        counts=Counter(r["control"] for r in registry)
        if any(counts[x]!=EXPECTED_CAPABILITIES for x in required):fail(f"Control type balance incorrect: {dict(counts)}")

    # Full logical regression = base + shards.
    matrix_files=[]
    base=ROOT/"evals"/"control_regression_matrix.json"
    if not base.is_file():fail("Base control regression matrix missing")
    else:matrix_files.append(base)
    matrix_files.extend(sorted((ROOT/"evals").glob("control_regression_matrix_*.json")))
    matrix=[];seen=set()
    for fp in matrix_files:
        part=json.loads(fp.read_text(encoding="utf-8"))
        for x in part:
            if x.get("id") in seen:fail(f"Duplicate regression ID: {x.get('id')}")
            seen.add(x.get("id"));matrix.append(x)
    if len(matrix)!=EXPECTED_REGRESSION:fail(f"Expected {EXPECTED_REGRESSION} regression conditions, found {len(matrix)}")
    kinds=Counter(x.get("case") for x in matrix)
    if kinds!={"normal":EXPECTED_CAPABILITIES,"ambiguous":EXPECTED_CAPABILITIES,"failure":EXPECTED_CAPABILITIES}:
        fail(f"Regression balance incorrect: {dict(kinds)}")


# Revision 1.6 operational implementation-integrity checks.
manifest=texts.get(ROOT/"MANIFEST.md","")
if "controls/01-*.md` through `controls/31-*.md" not in manifest: fail("MANIFEST control-plane domain range is stale")
if "control.bq-0001` through `control.bq-1300" not in manifest: fail("MANIFEST control range is stale")
if "CONTROL_MANIFEST.md`" not in manifest or "canonical" not in manifest[manifest.find("# Control Plane Registry"):manifest.find("# Control Plane Hooks")]: fail("MANIFEST does not delegate current control-plane metadata to CONTROL_MANIFEST")

d23=texts.get(ROOT/"controls/23-jobs-sops-and-operational-systems.md","")
if "Domain 23 / Domain 31 Ownership Boundary" not in d23: fail("Domain 23/31 specialization boundary missing")
if "ORGANIZATION-SPECIFIC" not in d23.upper() and "not-supplied" not in d23.lower(): fail("Domain 23 metric target-provenance semantics not harmonized")

try:
    ops_schema=json.loads((ROOT/"schemas"/"operational_procedure.schema.json").read_text(encoding="utf-8"))
    if ops_schema.get("additionalProperties") is not False: fail("Operational procedure schema is not closed")
    s=json.dumps(ops_schema)
    for ref in ["procedure_authority.schema.json","role_accountability.schema.json","decision_rights.schema.json","operational_evidence.schema.json","kpi_definition.schema.json"]:
        if ref not in s: fail(f"Operational procedure schema does not compose {ref}")
    for field in ["approval_state","procedure_version","authority_map","decision_rights","evidence_requirements","definition_of_done","handoffs","kpis"]:
        if field not in ops_schema.get("required",[]): fail(f"Operational procedure schema does not require {field}")
except Exception as e: fail(f"Cannot inspect operational procedure schema: {e}")

try:
    d31=json.loads((ROOT/"evals"/"control_regression_matrix_31.json").read_text(encoding="utf-8"))
    if len(d31)!=30: fail(f"Expected 30 executable Domain 31 regressions, found {len(d31)}")
    for x in d31:
        for k in ["input","expected_status","expected_assertions","must_not_contain"]:
            if k not in x: fail(f"Domain 31 regression {x.get('id')} missing executable field {k}")
        if x.get("case")=="failure" and not x.get("expected_error_contains"): fail(f"Domain 31 failure regression {x.get('id')} missing expected_error_contains")
except Exception as e: fail(f"Cannot inspect executable Domain 31 regressions: {e}")

# Execute Domain 31 behavior tests as part of pack integrity.
try:
    import subprocess
    proc=subprocess.run([sys.executable,str(ROOT/"tools"/"test_operations_2.py")],cwd=ROOT,text=True,capture_output=True)
    if proc.returncode!=0: fail("Operations 2.0 executable regressions failed: "+(proc.stdout+proc.stderr).strip().replace("\n"," | ")[:1600])
except Exception as e: fail(f"Could not execute Operations 2.0 regression runner: {e}")

# Execute Revision 1.7 governance diagnostics in a temporary directory so validation
# proves the tools remain runnable without mutating canonical or generated artifacts.
try:
    import tempfile
    with tempfile.TemporaryDirectory(prefix="biziq-governance-") as td:
        for tool,name in [("audit_control_coverage.py","coverage.json"),("lint_control_semantics.py","semantic-lint.json")]:
            out=Path(td)/name
            proc=subprocess.run([sys.executable,str(ROOT/"tools"/tool),"--out",str(out)],cwd=ROOT,text=True,capture_output=True)
            if proc.returncode!=0 or not out.is_file():
                fail(f"Revision 1.7 governance tool failed: {tool}: "+(proc.stdout+proc.stderr).strip().replace("\n"," | ")[:1200])
            else:
                try: json.loads(out.read_text(encoding="utf-8"))
                except Exception as e: fail(f"Revision 1.7 governance tool emitted invalid JSON: {tool}: {e}")
        bench_dir=Path(td)/"benchmark"
        proc=subprocess.run([sys.executable,str(ROOT/"tools"/"benchmark_pipeline.py"),"prepare",str(ROOT/"benchmarks"/"v2_semantic_routing_cases.json"),"--run-id","validator-smoke","--out",str(bench_dir)],cwd=ROOT,text=True,capture_output=True)
        if proc.returncode!=0: fail("Revision 1.7 benchmark pipeline prepare failed: "+(proc.stdout+proc.stderr).strip().replace("\n"," | ")[:1200])
        else:
            try:
                jobs=json.loads((bench_dir/"generation_jobs.json").read_text(encoding="utf-8"))["jobs"]
                key=json.loads((bench_dir/"private"/"blind_key.json").read_text(encoding="utf-8"))["items"]
                if len(jobs)!=60 or len(key)!=60: fail("Benchmark pipeline did not prepare exactly two conditions for all 30 semantic-routing cases")
            except Exception as e: fail(f"Benchmark pipeline smoke artifacts invalid: {e}")
except Exception as e: fail(f"Could not execute Revision 1.7 governance diagnostics: {e}")

print(f"BizIQ validator mode={'overlay' if args.overlay_only else 'full'}: revision=1.8.8")
for w in warnings:print("WARN:",w)
if errors:
    print(f"FAIL: {len(errors)} error(s)")
    for e in errors:print("  -",e)
    sys.exit(1)
print("PASS: BizIQ Control-Plane Revision 1.8.8 integrity checks passed.")
