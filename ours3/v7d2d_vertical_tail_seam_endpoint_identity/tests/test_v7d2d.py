from pathlib import Path
import csv,json
R=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/v7d2d_vertical_tail_seam_endpoint_identity');S=json.loads((R/'artifacts/pretest_summary.json').read_text());E=list(csv.DictReader(Path(S['TAIL_ENDPOINT_IDENTITY_CSV']).open()))
def test_fuselage_frozen():assert S['FUSELAGE_FROZEN'] and S['FUSELAGE_VALID_SEAM_TRACK_COUNT']==2 and S['FUSELAGE_SEAM_A_EVIDENCE_COVERAGE']==S['FUSELAGE_SEAM_B_EVIDENCE_COVERAGE']==1
def test_tail_chain_track_frozen():assert S['TAIL_WHOLE_CHAIN_TRACK_UNCHANGED'] and S['TAIL_CHAIN_TRACK_HASH_BEFORE']==S['TAIL_CHAIN_TRACK_HASH_AFTER']
def test_endpoint_side_descriptor():assert S['CHAIN_GEOMETRY_ENDPOINT_DESCRIPTOR_HASH_CONSISTENT']
def test_station_local_signed_side():assert all(r['ENDPOINT_0_SIGNED_SIDE'] and r['ENDPOINT_1_SIGNED_SIDE'] for r in E)
def test_endpoint_index_not_equal_side_identity():assert S['VERTICAL_TAIL_ENDPOINT_SIDE_IDENTITY_USED']
def test_forward_swap_state_generation():assert {r['SELECTED_STATE'] for r in E}<={'FORWARD','SWAP'}
def test_global_endpoint_state_solver():assert S['GLOBAL_ENDPOINT_SIDE_SOLVER_USED']
def test_joint_two_seam_assignment():assert all(r['SEAM_A_ENDPOINT']!=r['SEAM_B_ENDPOINT'] for r in E)
def test_two_seams_use_distinct_endpoints():assert all({r['SEAM_A_ENDPOINT'],r['SEAM_B_ENDPOINT']}=={'0','1'} for r in E)
def test_endpoint_array_swap_invariance():assert S['ENDPOINT_ARRAY_SWAP_INVARIANCE_PASS']
def test_spike_localization():assert S['SPIKE_STATION_ID']=='S07' and S['SPIKE_PREVIOUS_STATION']=='S05' and S['SPIKE_NEXT_STATION']=='S08'
def test_second_order_endpoint_cost():assert S['SEAM_SECOND_ORDER_DEPENDENCY_PASS']
def test_signed_side_dependency():assert S['SIGNED_SIDE_DEPENDENCY_PASS']
def test_global_vs_greedy_endpoint_identity():assert S['GLOBAL_ENDPOINT_SIDE_SOLVER_OUTPERFORMS_GREEDY']
def test_no_station_hardcode():assert S['PART_ID_HARDCODE_COUNT']==0
def test_no_final_geometry_metric_in_selection():assert not S['GT_USED_AS_INPUT'] and not S['FINAL_GEOMETRY_METRIC_USED_FOR_TRACK_SELECTION']
def test_no_master_curve_created():assert S['PRODUCTION_MASTER_CURVE_COUNT']==0 and not S['COMMON_CONTROL_NET_EXECUTED'] and not S['V7C_EXECUTED']
def test_track_recovery_ready_gate():assert not S['TRACK_RECOVERY_READY_FOR_V7D'] and S['VERTICAL_TAIL_VALID_SEAM_TRACK_COUNT']==0
def test_truthful_remaining_class():assert S['TAIL_REMAINING_AMBIGUITY_CLASS']=='CHAIN_GEOMETRY_AMBIGUOUS' and S['TAIL_REMAINING_SPIKE_CAUSE']=='CHAIN_GEOMETRY_ITSELF'
