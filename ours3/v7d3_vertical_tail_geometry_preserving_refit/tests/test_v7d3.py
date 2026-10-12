import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SUMMARY=json.loads((ROOT/"artifacts/pretest_summary.json").read_text())


def test_fuselage_frozen(): assert SUMMARY["FUSELAGE_FROZEN"] and SUMMARY["FUSELAGE_INPUT_HASH"]==SUMMARY["FUSELAGE_OUTPUT_HASH"]
def test_tail_v7b_baseline_loaded(): assert SUMMARY["VERTICAL_TAIL_CHAMFER_V7B"]==0.010298782545970303
def test_local_boundary_strip_selection(): assert SUMMARY["BOUNDARY_STRIP_ROWS"] in {2,3,5}
def test_far_interior_control_points_frozen(): assert SUMMARY["V7D3_INTERIOR_P95_DEVIATION_FROM_V7B"]<1e-12
def test_boundary_row_matches_master_curve(): assert SUMMARY["VERTICAL_TAIL_A_B_BOUNDARY_P95"]<1e-12
def test_local_refit_preserves_shared_edge(): assert SUMMARY["VERTICAL_TAIL_SHARED_OCC_EDGE_COUNT"]>=1 and SUMMARY["SHARED_EDGE_IDENTITY_PRESERVED"]
def test_pcurve_revalidated_after_refit(): assert SUMMARY["PCURVE_REVALIDATED"] and SUMMARY["VERTICAL_TAIL_PCURVE_COUNT"]>=2
def test_trimmed_faces_remain_valid(): assert SUMMARY["VERTICAL_TAIL_TRIMMED_FACE_COUNT"]>=2
def test_interior_anchor_reduces_drift(): assert SUMMARY["INTERIOR_ANCHOR_DEPENDENCY_PASS"]
def test_global_vs_local_refit(): assert SUMMARY["LOCAL_REFIT_OUTPERFORMS_GLOBAL"]
def test_deformation_budget(): assert SUMMARY["V7D3_MAX_CONTROL_POINT_DISPLACEMENT"]<SUMMARY["V7D_MAX_CONTROL_POINT_DISPLACEMENT"]
def test_boundary_influence_locality(): assert SUMMARY["LOCAL_BOUNDARY_INFLUENCE_TEST_PASS"] and SUMMARY["LOCAL_REFIT_LOCALITY_VALID"]
def test_master_boundary_flip_audit(): assert isinstance(SUMMARY["TAIL_ACCEPTED_MASTER_BOUNDARY_CONTAINS_ENDPOINT_FLIP"],bool)
def test_master_boundary_repair_ablation(): assert isinstance(SUMMARY["MASTER_BOUNDARY_REPAIR_CAUSAL"],bool)
def test_no_profile_sample_edges(): assert SUMMARY["PROFILE_SAMPLE_DERIVED_EDGE_COUNT"]==0
def test_no_forced_sewing(): assert SUMMARY["FORCED_SEWING_COUNT"]==0
def test_no_large_tolerance_sewing(): assert not SUMMARY["LARGE_TOLERANCE_SEWING_REQUIRED"]
def test_main_wing_regression(): assert SUMMARY["MAIN_WING_REGRESSION_PASS"]


def test_runtime_inputs_remain_frozen():
    assert not SUMMARY["RUNTIME_PROFILE_REMEASUREMENT"]
    assert not SUMMARY["RUNTIME_BOUNDARY_REDETECTION_FROM_MESH"]
    assert not SUMMARY["RUNTIME_MASTER_BOUNDARY_RECOMPUTED"]


def test_geometry_improves_over_v7d():
    assert SUMMARY["VERTICAL_TAIL_CHAMFER_V7D3"]<SUMMARY["VERTICAL_TAIL_CHAMFER_V7D"]
    assert SUMMARY["VERTICAL_TAIL_HAUSDORFF_V7D3"]<SUMMARY["VERTICAL_TAIL_HAUSDORFF_V7D"]
