import json
from pathlib import Path

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/v7d_boundary_constrained_open_shell_refit')
S=json.loads((ROOT/'artifacts/pretest_summary.json').read_text())

def test_endpoint_pairing_not_index_hardcoded(): assert S['PART_ID_HARDCODE_COUNT']==0
def test_endpoint_track_continuity(): assert S['INVALID_ENDPOINT_TRACK_COUNT']==2
def test_endpoint_flip_detection(): assert S['parts']['CADPART_005']['evidence']['track_metrics']['TRACK_DIRECTION_FLIP_COUNT']==2
def test_master_curve_from_measured_evidence(): assert all(r['evidence']['station_samples'] for r in S['parts'].values())
def test_master_curve_provenance(): assert all(r['evidence']['shared_boundary_candidate_id'] for r in S['parts'].values())
def test_master_curve_fit(): assert S['MASTER_CURVE_P95_FIT_ERROR']<.01
def test_invalid_master_curve_rejected(): assert S['INVALID_MASTER_CURVE_REJECTED']
def test_surface_boundary_is_constrained_diagnostic(): assert S['BOUNDARY_CONSTRAINED_SURFACE_REFIT_USED']
def test_surface_boundary_matches_master_curve_diagnostic(): assert all(r['constrained_boundary']['p95']<1e-9 for r in S['parts'].values())
def test_two_surfaces_share_master_curve_diagnostic(): assert S['DIAGNOSTIC_MASTER_CURVE_COUNT']==2
def test_boundary_constraint_ablation(): assert S['BOUNDARY_CONSTRAINT_ABLATION_PASS']
def test_master_curve_perturbation_changes_surface(): assert S['MASTER_CURVE_PERTURBATION_EFFECTIVE']
def test_wrong_endpoint_pairing_detected(): assert S['WRONG_ENDPOINT_PAIRING_DETECTED']
def test_no_mesh_resection(): assert S['RUNTIME_BOUNDARY_REDETECTION_FROM_MESH'] is False
def test_no_bbox_boundary(): assert all(not r['evidence'].get('bbox_generated',False) for r in S['parts'].values())
def test_no_convex_hull_boundary(): assert all(not r['evidence'].get('convex_hull_generated',False) for r in S['parts'].values())
def test_no_fake_cap(): assert S['PART_ID_HARDCODE_COUNT']==0
def test_no_part_id_hardcode(): assert S['PART_ID_HARDCODE_COUNT']==0
def test_fuselage_boundary_error_improves_diagnostic(): assert S['FUSELAGE_V7D_A_B_BOUNDARY_P95']<S['FUSELAGE_V7C_RECONCILIATION_P95']
def test_vertical_tail_boundary_error_improves_diagnostic(): assert S['VERTICAL_TAIL_V7D_A_B_BOUNDARY_P95']<S['VERTICAL_TAIL_V7C_RECONCILIATION_P95']
def test_vertical_tail_side_localization_preserved(): assert S['VERTICAL_TAIL_WORST_REGION_BEFORE']=='SIDE'
def test_shared_edge_preview_on_surface_a_fuselage(): assert S['FUSELAGE_EDGE_TO_SURFACE_A_P95']<1e-6
def test_shared_edge_preview_on_surface_b_fuselage(): assert S['FUSELAGE_EDGE_TO_SURFACE_B_P95']<1e-6
def test_v7b_regression(): assert S['V7B_REGRESSION_PASS']
def test_v7_contract_regression(): assert S['V7_CONTRACT_REGRESSION_PASS']
def test_honest_partial(): assert S['CURRENT_GATE'].endswith('PARTIAL') and not S['CASE09_V7D_PASS']
def test_rejected_tracks_not_formal_master_curves(): assert S['MASTER_DESIGN_CURVE_COUNT']==0
def test_no_formal_v7c_rerun_from_rejected_evidence(): assert S['V7C_RERUN_SHARED_OCC_EDGE_COUNT']==0
def test_fuselage_geometry_regression_detected(): assert S['FUSELAGE_GEOMETRY_REGRESSION']
def test_tail_diagnostic_geometry_improves(): assert S['VERTICAL_TAIL_HAUSDORFF_AFTER']<S['VERTICAL_TAIL_HAUSDORFF_BEFORE']

