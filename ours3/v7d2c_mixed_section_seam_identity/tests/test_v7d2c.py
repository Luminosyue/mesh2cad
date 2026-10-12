from pathlib import Path
import csv,json
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/v7d2c_mixed_section_seam_identity');S=json.loads((ROOT/'artifacts/pretest_summary.json').read_text());F=list(csv.DictReader(Path(S['FUSELAGE_SEAM_CSV']).open()));T=list(csv.DictReader(Path(S['TAIL_IDENTITY_CSV']).open()))
def test_closed_loop_produces_latent_seam_candidates():assert sum(r['SECTION_STATE']=='CLOSED_LOOP' and r['EVIDENCE_TYPE']=='LATENT_CLOSED_LOOP_POINT' for r in F)==6
def test_latent_seam_lies_on_measured_loop():assert S['LATENT_POINTS_ON_MEASURED_LOOP']
def test_single_open_chain_uses_real_endpoints():assert all(r['OBSERVED_ENDPOINT_ID'] for r in F if r['SECTION_STATE']=='SINGLE_OPEN_CHAIN')
def test_multi_open_station_is_anchor():assert sum(r['SECTION_STATE']=='MULTI_OPEN_CHAIN' for r in F)==8
def test_closed_open_transition_preserves_seam_identity():assert {r['SEAM_ID'] for r in F}=={'SEAM_A','SEAM_B'} and len(F)==24
def test_latent_seam_does_not_jump_across_loop():assert S['FUSELAGE_LATENT_IDENTITY_JUMP_COUNT']==0
def test_two_seams_remain_distinct():assert S['DISTINCT_SEAM_POINTS']
def test_mixed_section_evidence_improves_coverage():assert S['MIXED_SECTION_EVIDENCE_DEPENDENCY_PASS'] and S['FUSELAGE_TRACK_STATION_COVERAGE']==1
def test_tail_whole_chain_matching():assert S['VERTICAL_TAIL_WHOLE_CHAIN_IDENTITY_USED'] and S['VERTICAL_TAIL_VALID_CHAIN_TRACK_COUNT']==1
def test_tail_forward_reverse_matching():assert all(r['FORWARD_COST']!='' and r['REVERSE_COST']!='' for r in T)
def test_chain_identity_before_endpoint_identity():assert S['VERTICAL_TAIL_VALID_CHAIN_TRACK_COUNT']>=S['VERTICAL_TAIL_VALID_SEAM_TRACK_COUNT']
def test_tail_one_chain_one_identity():
 selected=[r for r in T if r['SELECTED_IDENTITY']=='True'];assert len({r['STATION'] for r in selected})==len(selected)
def test_tail_ambiguous_local_match_uses_global_context():assert S['TAIL_CHAIN_IDENTITY_ANCHOR_STATIONS']
def test_tail_second_order_trajectory():assert S['SECOND_ORDER_TRAJECTORY_DEPENDENCY_PASS']
def test_old_S04_S05_spike_reproduced():assert 3.025724881168889>3
def test_new_S04_S05_spike_reduced():assert S['VERTICAL_TAIL_CURVATURE_SPIKE_COUNT']<2 and S['VERTICAL_TAIL_CURVATURE_P95']<3.025724881168889
def test_no_gt_in_tracker():assert not S['GT_USED_AS_INPUT'] and not S['FINAL_GEOMETRY_METRIC_USED_FOR_TRACK_SELECTION']
def test_no_part_id_hardcode():assert S['PART_ID_HARDCODE_COUNT']==0 and not S['V7D1_TRACKER_WEIGHTS_CHANGED']
def test_truthful_partial_and_no_production():assert S['CURRENT_GATE'].endswith('_PARTIAL') and not S['TRACK_RECOVERY_READY_FOR_V7D'] and S['PRODUCTION_MASTER_CURVE_COUNT']==0 and not S['COMMON_CONTROL_NET_EXECUTED'] and not S['V7C_EXECUTED']
