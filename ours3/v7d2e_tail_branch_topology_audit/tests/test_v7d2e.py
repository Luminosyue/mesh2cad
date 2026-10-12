import csv
import hashlib
import json
from pathlib import Path

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
OUT=ROOT/'v7d2e_tail_branch_topology_audit'
S=json.load(open(OUT/'artifacts/pretest_summary.json'))

def test_gate(): assert S['CURRENT_GATE'].endswith('_PASS') and S['TAIL_S07_ROOT_CAUSE_IDENTIFIED']
def test_root_cause_enum(): assert S['TAIL_S07_ROOT_CAUSE']=='MISSING_INTERMEDIATE_STATION_EVIDENCE'
def test_s06_raw(): assert S['S06_RAW_SECTION_AVAILABLE'] and S['details']['S06']['raw_segments']==276
def test_s06_full_graph():
 d=json.load(open(OUT/'evidence/raw_original_stations/S06.json'))
 assert len(d['intersection_segments'])==276 and len(d['nodes'])==d['node_count'] and len(d['edges'])==d['edge_count']
def test_s06_mixed_topology():
 d=S['details']['S06']; types=[x['topology'] for x in d['components']]
 assert types.count('OPEN_CHAIN')==3 and types.count('CLOSED_LOOP')==1
def test_s06_valid_dominant():
 d=S['details']['S06']; c=max(d['components'],key=lambda x:x['arc_length'])
 assert c['topology']=='OPEN_CHAIN' and c['component_id']=='COMP_000' and c['arc_length']>.9
def test_branch_graph(): assert S['TAIL_LOCAL_BRANCH_GRAPH_USED'] and S['TAIL_CURRENT_BRANCH_RANK']==1
def test_alternatives(): assert S['TAIL_ALTERNATIVE_BRANCH_COUNT']>=2 and S['SMOOTHER_BUT_WEAKER_BRANCH_REJECTED']
def test_adaptive_version(): assert S['OFFLINE_ADAPTIVE_EVIDENCE_REGEN'] and S['EVIDENCE_VERSION']=='V7D2E_ADAPTIVE_TAIL'
def test_adaptive_counts(): assert S['ADAPTIVE_STATION_COUNT']==7 and S['ADAPTIVE_VALID_CHAIN_COUNT']==7
def test_adaptive_reduces_spike(): assert S['TAIL_ADAPTIVE_TURNING_ANGLE'] < S['TAIL_CURRENT_TURNING_ANGLE'] and S['TAIL_ADAPTIVE_TURNING_ANGLE'] < 1.57079632679
def test_world_and_local_old_spike(): assert S['WORLD_SPACE_SPIKE_PRESENT'] and S['LOCAL_SPACE_SPIKE_PRESENT']
def test_frame_not_causal(): assert S['LOCAL_FRAME_FLIP_COUNT']==0 and not S['LOCAL_FRAME_CAUSAL'] and S['LOCAL_FRAME_ROTATION_ANGLE']==0
def test_topology_transition(): assert S['TAIL_SECTION_TOPOLOGY_TRANSITION'] and 'MIXED_OPEN_CLOSED' in S['TAIL_SECTION_TOPOLOGY_TRANSITION_TYPE']
def test_flip_bend_separated(): assert S['TAIL_IDENTITY_FLIP_COUNT']==0 and S['TAIL_SOURCE_SUPPORTED_GEOMETRIC_TURN_COUNT']==1
def test_not_wrong_branch(): assert not S['WRONG_PHYSICAL_CHAIN_BRANCH']
def test_not_true_bend(): assert not S['TRUE_SOURCE_GEOMETRIC_BEND']
def test_synthetic_identity_reversal(): assert S['IDENTITY_FLIP_DETECTED_SYNTHETIC']
def test_fuselage_frozen(): assert S['FUSELAGE_HASH_UNCHANGED'] and S['FUSELAGE_VALID_SEAM_TRACK_COUNT']==2 and S['FUSELAGE_COVERAGE']==1.0
def test_v7d3_frozen(): assert S['V7D3_ARTIFACT_HASH_UNCHANGED']
def test_tail_frozen(): assert S['TAIL_FROZEN_EVIDENCE_HASH_UNCHANGED']
def test_no_forbidden_metrics(): assert not S['GT_USED_AS_INPUT'] and not S['FINAL_CAD_METRIC_USED_FOR_DECISION']
def test_no_runtime_remeasure(): assert not S['RUNTIME_PROFILE_REMEASUREMENT'] and not S['RUNTIME_BOUNDARY_REDETECTION_FROM_MESH']
def test_no_downstream_geometry(): assert S['PRODUCTION_MASTER_CURVE_COUNT']==0 and not S['CONSTRAINED_REFIT_EXECUTED'] and not S['V7C_EXECUTED']
def test_csvs():
 for name in ['tail_branch_candidates.csv','tail_adaptive_evidence.csv','local_branch_graph_edges.csv']:
  with open(OUT/'artifacts'/name,newline='') as f: assert len(list(csv.DictReader(f)))>0
def test_debug_artifacts():
 for i,name in enumerate(['01_S04_S09_raw_section_graphs.png','02_all_chain_branches.png','03_current_branch.png','04_alternative_branches.png','05_station_gap_map.png','06_adaptive_station_locations.png','07_adaptive_section_chains.png','08_world_space_trajectory.png','09_local_space_trajectory.png','10_turning_angle_by_station.png','11_section_topology_state.png','12_local_frame_rotation.png','13_S07_root_cause_contact_sheet.png'],1):
  p=OUT/'artifacts/tail_branch_audit'/name; assert p.exists() and p.stat().st_size>10000
def test_mandatory_station_plots():
 for name in ['01_S05_all_components.png','02_S06_all_components.png','03_S07_all_components.png','04_S08_all_components.png','05_S05_S08_component_correspondence.png']:
  p=OUT/'artifacts'/name; assert p.exists() and p.stat().st_size>10000
def test_no_blockers(): assert S['BLOCKERS']==[]
