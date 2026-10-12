import json
from pathlib import Path
R=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/v7d1_robust_global_seam_track_recovery');S=json.loads((R/'artifacts/pretest_summary.json').read_text())
def test_global_graph_used():assert S['GLOBAL_SEAM_GRAPH_USED']
def test_greedy_not_final():assert not S['GREEDY_LOCAL_PAIRING_FINAL_DECISION']
def test_station_monotonic_fuselage():assert S['FUSELAGE_STATION_MONOTONICITY_PASS']
def test_station_monotonic_tail():assert S['VERTICAL_TAIL_STATION_MONOTONICITY_PASS']
def test_fuselage_coverage_evidence_bound():assert S['FUSELAGE_TRACK_STATION_COVERAGE']==4/9
def test_tail_coverage_evidence_bound():assert S['VERTICAL_TAIL_TRACK_STATION_COVERAGE']==6/8
def test_fuselage_missing_support_not_synthetic():assert S['FUSELAGE_SKIPPED_STATION_COUNT']==5
def test_tail_missing_support_not_synthetic():assert S['VERTICAL_TAIL_SKIPPED_STATION_COUNT']==2
def test_fuselage_gap_detected():assert S['FUSELAGE_MAX_STATION_GAP']>=2
def test_direction_flip_detected_tail():assert S['VERTICAL_TAIL_DIRECTION_FLIP_COUNT']==2
def test_curvature_spike_detected_tail():assert S['VERTICAL_TAIL_CURVATURE_SPIKE_COUNT']==2
def test_no_bad_track_curve():assert S['MASTER_DESIGN_CURVE_COUNT']==0
def test_no_production_refit():assert not S['PRODUCTION_BOUNDARY_CONSTRAINED_REFIT_USED']
def test_diagnostic_refit_separated():assert not S['DIAGNOSTIC_REFIT_USED']
def test_master_count_consistent_with_tracks():assert S['TRACK_RECOVERY_PASS']==(S['MASTER_DESIGN_CURVE_COUNT']>0)
def test_part_id_hardcode_zero():assert S['PART_ID_HARDCODE_COUNT']==0
def test_gt_not_input():assert not S['GT_USED_AS_INPUT']
def test_no_runtime_remeasure():assert not S['RUNTIME_PROFILE_REMEASUREMENT']
def test_no_runtime_resection():assert not S['RUNTIME_BOUNDARY_REDETECTION_FROM_MESH']
def test_v7b_regression():assert S['V7B_REGRESSION_PASS']
def test_contract_regression():assert S['V7_CONTRACT_REGRESSION_PASS']
def test_no_v7c_rerun_from_rejected_tracks():assert S['V7C_RERUN_SHARED_OCC_EDGE_COUNT']==0
def test_endpoint_candidate_count():assert S['TOTAL_ENDPOINT_CANDIDATES']==40
def test_pair_candidate_count():assert S['TOTAL_PAIR_CANDIDATES']==40
def test_candidate_csv_exists():assert (R/'artifacts/seam_track_candidates.csv').is_file()
def test_summary_csv_exists():assert (R/'artifacts/seam_track_summary.csv').is_file()
def test_honest_partial():assert S['CURRENT_GATE'].endswith('PARTIAL')
def test_fuselage_geometry_not_regressed_by_rejected_track():assert S['FUSELAGE_CHAMFER_AFTER']==S['FUSELAGE_CHAMFER_BEFORE']
def test_tail_geometry_not_changed_without_accepted_track():assert S['VERTICAL_TAIL_HAUSDORFF_AFTER']==S['VERTICAL_TAIL_HAUSDORFF_BEFORE']
def test_debug_images():assert len(list((R/'artifacts/v7d1_debug').glob('CADPART_*/*.png')))==24

