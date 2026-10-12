from pathlib import Path
import csv,json
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/v7d2b_versioned_chain_evidence_repair')
S=json.loads((ROOT/'artifacts/pretest_summary.json').read_text())
def test_truthful_partial():
 assert S['CURRENT_GATE'].endswith('_PARTIAL') and not S['TRACK_RECOVERY_READY_FOR_V7D']
 assert S['FUSELAGE_STATIONS_WITH_2_TRACKABLE_CHAINS_AFTER']==4
 assert S['FUSELAGE_CHAIN_IDENTITY_COVERAGE_AFTER']==4/9
def test_versioned_complete_graphs():
 assert S['FUSELAGE_VERSIONED_EVIDENCE_REGENERATED'] and S['EVIDENCE_VERSION']=='V7D2B_REGENERATED'
 assert S['RAW_SECTION_GRAPH_FULL_GEOMETRY_PERSISTED'] and S['REJECTED_COMPONENT_GEOMETRY_PERSISTED']
 files=list((ROOT/'03_geometry_analyzer/CADPART_000/raw_section_graph').glob('S*.json'));assert len(files)==12
 for p in files:
  d=json.loads(p.read_text());assert d['nodes'] and d['edges'] and d['components'];assert 'SOURCE_INTERSECTION_SEGMENT_ID' in d['edges'][0]
def test_descriptor_contract():
 assert S['VERTICAL_TAIL_STALE_DESCRIPTOR_BUG_FIXED'] and S['DESCRIPTOR_DIRTY_GUARD_IMPLEMENTED']
 assert S['STALE_DESCRIPTOR_GUARD_TEST_PASS'] and S['DESCRIPTOR_RECOMPUTE_EFFECTIVE']
 assert S['CHAIN_GEOMETRY_DESCRIPTOR_HASH_CONSISTENT']
def test_track_truth():
 assert S['FUSELAGE_VALID_ENDPOINT_TRACK_COUNT']==0
 assert S['VERTICAL_TAIL_VALID_ENDPOINT_TRACK_COUNT']==0
 assert S['VERTICAL_TAIL_DIRECTION_FLIP_COUNT']==2
 assert not S['TAIL_CANONICAL_ORIENTATION_DEPENDENCY_PASS']
def test_frozen_tracker_and_runtime():
 assert not S['V7D1_TRACKER_CONFIG_CHANGED']
 assert S['OFFLINE_GEOMETRY_ANALYZER_REGENERATION']
 assert not S['RUNTIME_PROFILE_REMEASUREMENT'] and not S['RUNTIME_BOUNDARY_REDETECTION_FROM_MESH'] and not S['RUNTIME_CHAIN_REEXTRACTION']
def test_no_downstream_execution():
 assert not S['PRODUCTION_MASTER_CURVE_CREATED'] and not S['COMMON_CONTROL_NET_EXECUTED'] and not S['CONSTRAINED_REFIT_EXECUTED'] and not S['V7C_EXECUTED']
def test_no_gt_or_hardcode():
 assert not S['GT_USED_AS_INPUT'] and S['PART_ID_HARDCODE_COUNT']==0 and S['V7B_SOURCE_ARTIFACTS_UNCHANGED']
def test_csv_contracts():
 for key,count in [('EVIDENCE_COMPLETENESS_CSV',24),('TAIL_ORIENTATION_CSV',15)]:
  rows=list(csv.DictReader(Path(S[key]).open()));assert len(rows)==count
 rows=list(csv.DictReader(Path(S['FUSELAGE_FILTER_AUDIT_CSV']).open()));assert rows
 assert sum(r['OLD_FILTER_STATUS']=='NOT_PERSISTED' and r['NEW_FILTER_STATUS']=='ACCEPTED' for r in rows)==4
def test_endpoint_clustering():
 assert all(r['POTENTIAL_OVERMERGE_COUNT']==0 and r['POTENTIAL_UNDERMERGE_COUNT']==0 for r in S['fuselage_station_audit'])
def test_blocker_specific():
 assert set(S['BLOCKERS'])=={'FUSELAGE_SOURCE_SECTION_GEOMETRY_REALLY_ONE_CHAIN_OUTSIDE_S03_S06','TAIL_GEOMETRIC_CHAIN_IDENTITY_STILL_AMBIGUOUS'}
 assert S['TAIL_ORIENTATION_BUG_FIXED'] and S['TAIL_GEOMETRIC_CHAIN_IDENTITY_STILL_AMBIGUOUS']
 assert S['NEXT_FIX'].startswith('B_') and '_C_' in S['NEXT_FIX']
