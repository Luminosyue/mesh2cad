import json,hashlib
from pathlib import Path
import pytest
O=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/case09_semantic_surface_face_reduction_v4')
S=json.loads((O/'metrics/summary.json').read_text());D=json.loads((O/'metrics/wing_topology_diagnosis.json').read_text());F=json.loads((O/'00_frozen_v3/freeze_manifest.json').read_text());P={x['part_id']:x for x in S['part_qa']}
def test_v3_frozen(): assert S['V3_FROZEN'] and S['FROZEN_HASHES_MATCH']
def test_only_wings_modified(): assert [x['part_id'] for x in F['parts'] if x['role']=='TARGET']==['CADPART_001','CADPART_002']
def test_profile_representation_audit(): assert all(D['wings'][p]['PROFILE_REPRESENTATION']=='POLYLINE_WIRE' for p in ('CADPART_001','CADPART_002'))
def test_semantic_profile_fitter(): assert all((O/'02_semantic_profiles'/p/'section_semantic_profiles.json').is_file() for p in ('CADPART_001','CADPART_002'))
def test_upper_lower_single_curve(): assert all(all(x['upper_curve']['CAD_CURVE_COUNT']==x['lower_curve']['CAD_CURVE_COUNT']==1 for x in json.loads((O/'02_semantic_profiles'/p/'section_semantic_profiles.json').read_text())) for p in ('CADPART_001','CADPART_002'))
def test_profile_correspondence(): assert all(all(x['profile_correspondence']['orientation']=='UNIFIED' for x in json.loads((O/'02_semantic_profiles'/p/'section_semantic_profiles.json').read_text())) for p in ('CADPART_001','CADPART_002'))
def test_semantic_surface_graph(): assert all((O/'03_semantic_surface'/p/'semantic_surface_graph.json').is_file() for p in ('CADPART_001','CADPART_002'))
def test_sections_not_final_topology(): assert all(P[p]['SECTION_DERIVED_FACE_COUNT']==P[p]['SECTION_DERIVED_EDGE_COUNT']==0 for p in ('CADPART_001','CADPART_002'))
def test_global_upper_skin(): assert all(P[p]['UPPER_SKIN_FACE_COUNT']==1 for p in ('CADPART_001','CADPART_002'))
def test_global_lower_skin(): assert all(P[p]['LOWER_SKIN_FACE_COUNT']==1 for p in ('CADPART_001','CADPART_002'))
def test_no_section_boundary_faces(): assert all(P[p]['ARTIFICIAL_SECTION_EDGE_COUNT']==0 for p in ('CADPART_001','CADPART_002'))
def test_root_cap(): assert all(P[p]['ROOT_CAP_FACE_COUNT']==1 for p in ('CADPART_001','CADPART_002'))
def test_tip_cap(): assert all(P[p]['TIP_CAP_FACE_COUNT']==1 for p in ('CADPART_001','CADPART_002'))
def test_shared_leading_edge(): assert S['LEADING_EDGE_GROUNDED']
def test_shared_trailing_edge(): assert S['TRAILING_EDGE_GROUNDED']
def test_geometry_q2_minimum(): assert all(P[p]['Q'] in ('Q1','Q2') for p in ('CADPART_001','CADPART_002'))
def test_feature_boundary_preserved(): assert S['V4_FEATURE_BOUNDARY_RECALL']>=.99
def test_sharp_edge_preserved(): assert S['V4_SHARP_EDGE_RECALL']>=.95
def test_face_reduction(): assert all(P[p]['FACE_COUNT']<=6 and P[p]['FACE_COUNT']<P[p]['OLD_FACE_COUNT'] for p in ('CADPART_001','CADPART_002'))
def test_artificial_section_edges_zero(): assert sum(P[p]['ARTIFICIAL_SECTION_EDGE_COUNT'] for p in ('CADPART_001','CADPART_002'))==0
def test_structure_pass(): assert S['CAD_STRUCTURE_Q']=='PASS'
def test_mac_used_for_both_wings(): assert S['MAC_USED'] and S['MAC_TARGET_PARTS']==['CADPART_001','CADPART_002'] and all(json.loads((O/'04_mac'/p/'mac_run_summary.json').read_text())['MAC_RESULT']=='SUCCESS' for p in ('CADPART_001','CADPART_002'))
def test_source_transform_preserved(): assert json.loads((O/'06_assembly/assembly_manifest.json').read_text())['placements_preserved']
def test_xcaf_reassembly(): assert S['XCAF_ASSEMBLY_PRESENT'] and S['FINAL_COMPONENT_COUNT']==8
def test_final_step_reload(): assert S['FINAL_STEP_RELOAD'] and S['FINAL_BREP_VALID'] and Path(S['FINAL_STEP']).is_file()
def test_final_face_hard_target(): assert S['V4_FACES']<=156
def test_final_face_strong_target(): assert S['V4_FACES']<=150
def test_whole_geom_q1(): assert S['GEOM_Q']=='Q1' and S['CHAMFER']<=.01 and S['P95']<=.02 and S['COVERAGE02']>=.95
def test_grounding_validation_only(): assert S['GROUNDING_PROXY_USED'] and S['GROUNDING_QUERIES']==4
def test_mac_provenance(): assert all(json.loads(Path(P[p]['step']+'.provenance.json').read_text())['MAC_GENERATED'] is True for p in ('CADPART_001','CADPART_002'))
def test_profile_quality(): assert all(P[p]['PROFILE_QA']['PROFILE_NORMALIZED_CHAMFER_MAX']<=.003 and P[p]['PROFILE_QA']['PROFILE_P95_MAX']<=.008 for p in ('CADPART_001','CADPART_002'))
def test_frozen_hashes_byte_identical(): assert all(hashlib.sha256(Path(x['frozen_copy']).read_bytes()).hexdigest()==x['v3_sha256'] for x in F['parts'] if x['role']=='FROZEN')
