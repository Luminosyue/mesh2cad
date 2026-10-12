import json
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/case09_nonwing_semantic_recovery_v5_1')
S=json.loads((OUT/'artifacts/final_summary.json').read_text())
def test_wings_frozen(): assert S['WING_HASH_BEFORE']==S['WING_HASH_AFTER']
def test_no_mac_used(): assert S['MAC_USED'] is False
def test_no_remaining_9_cases(): assert S['REMAINING_9_CASES_STARTED'] is False
def test_target_parts_only(): assert set(S['parts'])=={'CADPART_000','CADPART_003','CADPART_004','CADPART_005','CADPART_006','CADPART_007'}
def test_handoff_artifacts(): 
    for p in S['parts']:
        d=OUT/'20_mac_handoff'/p
        assert (d/'semantic_surface_graph.json').is_file()
        assert (d/'cad_feature_graph.json').is_file()
        assert (d/'measured_cad_spec.json').is_file()
        assert (d/'design_intent_hypotheses.json').is_file()
        assert (d/'dual_modal_context/canonical_obj_tokens.txt').is_file()
        assert (d/'dual_modal_context/axonometric_render.png').is_file()
def test_face_provenance_before():
    for p in S['parts']: assert (OUT/'01_topology_audit'/p/'face_provenance_before.json').is_file()
def test_q3_not_selected_for_improvement():
    for p,r in S['parts'].items():
        if r['NATIVENESS_IMPROVED']: assert r['SELECTED']['GEOM_Q'] in ('Q1','Q2')
def test_visual_outputs():
    for p in S['parts']:
        assert (OUT/'artifacts'/p/'old_true_edges.png').is_file()
        assert (OUT/'artifacts'/p/'new_true_edges.png').is_file()
    assert (OUT/'artifacts/whole_v4_v5_1_true_edges.png').is_file()
