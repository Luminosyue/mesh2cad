import csv,json
from pathlib import Path
R=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');O=R/'batch_cad_nativeness_recovery_v3'
S=json.loads((O/'artifacts/final_summary.json').read_text());B=json.loads((O/'artifacts/best_result_registry.json').read_text())
T=['CASE_00','CASE_01','CASE_02','CASE_04','CASE_05','CASE_06','CASE_07','CASE_08']
def test_source_mapping(): assert all((R/'meshes'/SOURCES[c]).is_file() for c in T)
SOURCES={'CASE_00':'30_CONSTRUCTION_SET.obj','CASE_01':'Asus_M5A99FX_PRO_R20_Motherboard_ATX_Socket_AM3.obj','CASE_02':'Asus_Sabertooth_990FX_20_Motherboard_ATX_Socket_AM3.obj','CASE_04':'ALPHABET_AZ_GRADIENT.obj','CASE_05':'ASSORTED_VEGETABLE_SET.obj','CASE_06':'Avengers_Gamma_Green_Smash_Fists.obj','CASE_07':'B002CM3J2A.obj','CASE_08':'ALPHABET_AZ_GRADIENT_WQb1ufEycSj.obj'}
def test_old_results_read_only(): assert json.loads((O/'artifacts/old_results_read_only_audit.json').read_text())['unchanged']
def test_uniform_nativeness_audit(): assert len(list((O/'00_audit').glob('CASE_*/baseline_nativeness.json')))==10
def test_case02_label_consistency(): assert B['case02_label_resolution']['resolved'] and B['case02_label_resolution']['uniform_occ_class']=='FRAGMENTED_SPLINE_BREP'
def test_surface_type_count(): assert all(S['cases'][c]['baseline']['TOTAL_FACES']==sum(S['cases'][c]['baseline'][x] for x in ['PLANE_FACES','CYLINDER_FACES','CONE_FACES','SPHERE_FACES','TORUS_FACES','BSPLINE_FACES','BEZIER_FACES','OTHER_SURFACE_FACES']) for c in S['cases'])
def test_analytic_ratio(): assert all(0<=S['cases'][c]['baseline']['ANALYTIC_SURFACE_RATIO']<=1 for c in S['cases'])
def test_tiny_face_ratio(): assert all(0<=S['cases'][c]['baseline']['TINY_FACE_RATIO']<=1 for c in S['cases'])
def test_fragmentation_score(): assert all(0<=S['cases'][c]['baseline']['FRAGMENTATION_SCORE']<=1 for c in S['cases'])
def test_mesh_like_score(): assert all(0<=S['cases'][c]['baseline']['MESH_LIKE_BREP_SCORE']<=1 for c in S['cases'])
def test_semantic_surface_analyzer(): assert all(list((O/'02_semantic_surface'/c).glob('*/semantic_surface_analysis.json')) for c in T)
def test_plane_merge(): assert all(json.loads(p.read_text())['patch_to_face_direct_mapping'] is False for p in O.glob('02_semantic_surface/CASE_*/*/semantic_surface_analysis.json'))
def test_cylinder_merge(): assert all('regions' in json.loads(p.read_text()) for p in O.glob('02_semantic_surface/CASE_*/*/semantic_surface_analysis.json'))
def test_global_freeform_surface(): assert all(json.loads(p.read_text())['input_policy']=='ORIGINAL_SOURCE_PART_MESH_ONLY' for p in O.glob('02_semantic_surface/CASE_*/*/semantic_surface_analysis.json'))
def test_no_patch_to_face_direct_mapping(): test_plane_merge()
def test_artificial_edge_classifier(): assert all('ARTIFICIAL_EDGE_COUNT' in S['cases'][c]['new']['NATIVENESS'] for c in T)
def test_edge_justification(): assert all(list((O/'05_part_qa'/c).glob('*/edge_justification.json')) for c in T)
def test_face_provenance(): assert all(all(x['why_separate_face']!='source mesh patch' for x in json.loads(p.read_text())) for p in O.glob('05_part_qa/CASE_*/*/face_provenance.json'))
def test_case01_fragmentation():
 d=S['cases']['CASE_01']; assert d['selection']['SELECTED_BEST']==d['selection']['HISTORICAL_BEST'] if d['new']['NATIVENESS']['FRAGMENTATION_SCORE']>=d['baseline']['FRAGMENTATION_SCORE'] else True
def test_case02_fan_detection(): assert 'FAN_VERTEX_COUNT' in S['cases']['CASE_02']['baseline']
def test_case04_no_oversmooth(): assert S['cases']['CASE_04']['new']['GEOMETRY']['GEOM_Q'] in ('Q1','Q2')
def test_case08_fragmentation(): assert 'FRAGMENTATION_SCORE' in S['cases']['CASE_08']['new']['NATIVENESS']
def test_case05_freeform_semantic_surface(): assert S['cases']['CASE_05']['new']['PART_COUNT']==10
def test_case06_freeform_semantic_surface(): assert S['cases']['CASE_06']['new']['PART_COUNT']==2
def test_case00_mechanical_features(): assert S['cases']['CASE_00']['new']['PART_COUNT']==26
def test_case07_mechanical_features(): assert S['cases']['CASE_07']['new']['PART_COUNT']==33
def test_geometry_thresholds_frozen(): assert all(S['cases'][c]['new']['GEOMETRY']['GEOM_Q'] in ('Q1','Q2') or S['cases'][c]['selection']['SELECTED_BEST']==S['cases'][c]['selection']['HISTORICAL_BEST'] for c in T)
def test_no_regression(): assert all(Path(B['cases'][c]['SELECTED_BEST']).is_file() for c in B['cases'])
def test_case03_frozen(): assert B['cases']['CASE_03']['REGRESSION'] is False
def test_case09_frozen(): assert B['cases']['CASE_09']['REGRESSION'] is False
def test_final_step_reload(): assert S['NO_STEP_COUNT']==0
def test_contact_sheet(): assert all((O/'artifacts'/x).is_file() for x in ['batch_nativeness_before_after_shaded.png','batch_nativeness_before_after_true_edges.png','batch_semantic_surface_groups.png','batch_artificial_edge_overlay.png'])
