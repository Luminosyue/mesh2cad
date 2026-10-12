import hashlib,json,re
from pathlib import Path
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/case09_futurecad_grounded_repair_v3');S=json.loads((ROOT/'metrics/summary.json').read_text());M=json.loads((ROOT/'target_part_manifest.json').read_text());TARGETS=['CADPART_001','CADPART_002','CADPART_006'];FROZEN=['CADPART_000','CADPART_003','CADPART_004','CADPART_005','CADPART_007']
def sha(p):
 h=hashlib.sha256();h.update(Path(p).read_bytes());return h.hexdigest()
def test_v2_frozen():assert S['V2_FROZEN'] and S['FROZEN_HASHES_MATCH']
def test_only_q3_parts_modified():assert S['TARGET_PARTS']==TARGETS and S['FROZEN_PARTS']==FROZEN
def test_5_q2_parts_hash_frozen():
 for x in M['parts']:
  if x['part_id'] in FROZEN:assert sha(x['v3_frozen_copy'])==x['v2_sha256']
def test_geometry_rootcause():assert all((ROOT/'01_rootcause'/p/'feature_error.json').is_file() and json.loads((ROOT/'01_rootcause'/p/'feature_error.json').read_text())['ROOT_CAUSE']!='MAC_RESULT_Q3' for p in TARGETS)
def test_error_maps():assert all((ROOT/'01_rootcause'/p/'geometry_error_map.glb').is_file() and (ROOT/'01_rootcause'/p/'geometry_error_map.png').is_file() for p in TARGETS)
def test_profile_correspondence():assert all((ROOT/'01_rootcause'/p/'profile_correspondence_before_after.png').is_file() for p in TARGETS[:2])
def test_wing_candidates():
 h=json.loads((ROOT/'02_measurements/repair_hypothesis_manifest.json').read_text());assert all(len(h[p])==3 for p in TARGETS[:2])
def test_propeller_pattern_measurement():
 p=next(x for x in S['part_qa'] if x['part_id']=='CADPART_006');assert p['MASTER_BLADE_RECOVERED'] and p['PATTERN_RECOVERED'] and p['PROPELLER_MASTER_BLADE_COUNT']==1 and p['PROPELLER_PATTERN_COUNT']==1
def test_brep_primitive_graph():
 for p in TARGETS:
  g=json.loads((ROOT/'04_grounding'/p/'brep_primitive_graph.json').read_text());assert g['faces'] and g['edges'] and g['vertices'];assert {'uv_bounds','outer_wire','inner_wires'}<=set(g['faces'][0]);assert {'tangent_samples','convex_concave_estimate'}<=set(g['edges'][0])
def test_grounding_queries_positive():assert S['GROUNDING_QUERIES_TOTAL']>0
def test_grounding_not_centroid_only():
 for p in TARGETS:
  assert all(not x['nearest_centroid_only'] and len(x['ranking_components'])==5 for x in json.loads((ROOT/'04_grounding'/p/'grounding_results.json').read_text()))
def test_grounding_confidence():
 for p in TARGETS:
  assert all('confidence' in x and 'margin' in x and 'top1_score' in x and 'top2_score' in x for x in json.loads((ROOT/'04_grounding'/p/'grounding_results.json').read_text()))
def test_source_feature_validation():assert all((ROOT/'04_grounding'/p/'grounding_geometry_validation.json').is_file() for p in TARGETS)
def test_no_fixed_index_selection():
 pat=re.compile(r'(?:faces|edges)\s*\(\s*\)\s*\[\s*\d+');assert all(not pat.search((ROOT/'05_part_qa'/p/'final_generated_code.py').read_text()) for p in TARGETS);assert S['FIXED_INDEX_SELECTION_COUNT']==0
def test_grounding_execution_trace():assert S['GROUNDING_PROXY_ACTUALLY_USED'] and S['GROUNDING_EXECUTED_OPS']==4 and all(x['operation_executed'] for p in TARGETS[:2] for x in json.loads((ROOT/'04_grounding'/p/'grounding_execution_trace.json').read_text()))
def test_mac_repair_feedback():assert all((ROOT/'03_mac_repair'/p/'repair_input.json').is_file() for p in TARGETS)
def test_max_mac_rounds():
 m=json.loads((ROOT/'metrics/mac_v3_aggregate.json').read_text());assert all(c['repair_rounds']<=2 for p in m['parts'] for c in p['candidates'])
def test_three_mac_hypotheses_each():
 m=json.loads((ROOT/'metrics/mac_v3_aggregate.json').read_text());assert all(len(p['candidates'])==3 for p in m['parts'])
def test_q3_not_accepted():assert all(p['NEW_Q'] in ('Q1','Q2') for p in S['part_qa'] if p['part_id'] in TARGETS)
def test_all_target_q3_fixed():assert S['TARGET_Q3_FIXED_COUNT']==3 and S['PART_Q3_COUNT']==0
def test_q_thresholds_frozen():assert S['GEOM_Q']=='Q1' and S['CHAMFER']<=.01 and S['P95']<=.02 and S['COVERAGE02']>=.99
def test_feature_threshold():assert S['V3_FEATURE_BOUNDARY_RECALL']>=.99
def test_sharp_improved():assert S['V3_SHARP_EDGE_RECALL']>S['V2_SHARP_EDGE_RECALL']
def test_unmet_sharp_target_reported():assert not S['SHARP_EDGE_TARGET_MET'] and S['CURRENT_GATE'].endswith('PARTIAL_PASS') and S['BLOCKERS']==['SHARP_EDGE_RECALL_TARGET_0.97_NOT_REACHED']
def test_structure_pass():assert S['CAD_STRUCTURE_Q']=='PASS' and S['V3_FACES']<=220 and S['V3_STRIP_EDGE_RATIO']<.06
def test_wing_structure():assert S['WING_SURFACE_GROUPS']=={'CADPART_001':1,'CADPART_002':1} and S['WING_STRIP_EDGES']==0
def test_xcaf_assembly():assert S['XCAF_ASSEMBLY_PRESENT'] and S['FINAL_COMPONENT_COUNT']==8
def test_final_step_reload():
 r=STEPControl_Reader();assert r.ReadFile(S['FINAL_STEP'])==IFSelect_RetDone and r.TransferRoots()>0 and BRepCheck_Analyzer(r.OneShape()).IsValid()
def test_grounding_ablation():assert set(S['GROUNDING_ABLATION_IMPROVED_PARTS'])==set(TARGETS[:2]) and all((ROOT/'05_part_qa'/p/'does_grounding_help.json').is_file() for p in TARGETS)
def test_futurecad_attribution():assert S['FUTURECAD_PAPER_MECHANISM_USED'] and not S['FUTURECAD_OFFICIAL_CODE_AVAILABLE'] and not S['FUTURECAD_OFFICIAL_USED'] and S['GROUNDING_MODE']=='FUTURECAD_COMPATIBLE_BREP_GROUNDING_V1'
def test_visuals():assert all(Path(S[k]).is_file() for k in ['COMPARISON_FIGURE','TRUE_EDGE_FIGURE','GROUNDING_FIGURE'])
