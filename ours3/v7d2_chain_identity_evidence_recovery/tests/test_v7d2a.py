import csv,json
from pathlib import Path

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/v7d2_chain_identity_evidence_recovery')
S=json.loads((ROOT/'artifacts/final_summary.json').read_text())
ROWS=list(csv.DictReader((ROOT/'artifacts/evidence_completeness_matrix.csv').open()))

def test_gate_and_scope():
 assert S['CURRENT_GATE']=='V7D2A_EVIDENCE_AUDIT_PASS'
 assert S['AUDIT_ONLY'] and not S['DAG_WEIGHTS_CHANGED']
 assert not S['MISSING_STATIONS_INTERPOLATED'] and not S['MASTER_CURVE_CREATED']
 assert not S['CONSTRAINED_REFIT_EXECUTED'] and not S['V7C_EXECUTED'] and not S['SEWING_EXECUTED']
 assert not S['RUNTIME_GEOMETRY_REMEASUREMENT']

def test_matrix_complete():
 assert len(ROWS)==24
 required={'RAW_SECTION_INTERSECTION_AVAILABLE','RAW_SECTION_GRAPH_AVAILABLE','OPEN_CHAIN_AVAILABLE','OPEN_CHAIN_COUNT','CHAIN_GEOMETRY_PERSISTED','CHAIN_ENDPOINTS_PERSISTED','CHAIN_ORIENTATION_PERSISTED','CHAIN_IDENTITY_AVAILABLE','SEAM_ENDPOINT_CANDIDATE_AVAILABLE','FILTER_REJECTION_REASON'}
 assert required<=set(ROWS[0])

def test_fuselage_physical_ceiling():
 assert S['FUSELAGE_SECOND_TRACK_STATIONS']==['S03','S04','S05','S06']
 assert len(S['FUSELAGE_SUPPORT_STATIONS'])==9
 assert S['FUSELAGE_CHAIN_IDENTITY_COVERAGE']==4/9
 assert S['FUSELAGE_ENDPOINT_EVIDENCE_COVERAGE']==4/9

def test_raw_and_open_coverage():
 assert S['FUSELAGE_RAW_SECTION_COVERAGE']==1.0
 assert S['FUSELAGE_OPEN_CHAIN_COVERAGE']==9/12
 assert S['VERTICAL_TAIL_RAW_SECTION_COVERAGE']==1.0
 assert S['VERTICAL_TAIL_OPEN_CHAIN_COVERAGE']==8/12

def test_tail_identity_coverage():
 assert S['VERTICAL_TAIL_CHAIN_IDENTITY_COVERAGE']==6/8
 assert S['VERTICAL_TAIL_ENDPOINT_EVIDENCE_COVERAGE']==6/8

def test_graph_geometry_not_serialized():
 assert not S['RAW_SECTION_GRAPH_FULL_GEOMETRY_PERSISTED']
 assert S['RAW_SECTION_GRAPH_SUMMARY_PERSISTED']
 assert all(row['RAW_SECTION_GRAPH_AVAILABLE']=='False' for row in ROWS)

def test_tail_spikes_and_root_cause():
 assert S['VERTICAL_TAIL_CURVATURE_SPIKE_STATIONS']==['S04','S05']
 assert 'ORIENTATION' in S['VERTICAL_TAIL_DIRECTION_REVERSAL_ROOT_CAUSE']
 audit=json.loads(Path(S['VERTICAL_TAIL_AUDIT']).read_text())
 assert any(x['direction_reversal_detected'] for x in audit['persisted_track_direction_changes'])
 assert audit['source_logic_evidence']['descriptor_recomputed_after_reverse'] is False

def test_next_fix_and_integrity():
 assert S['FUSELAGE_MISSING_EVIDENCE_CLASS']=='CHAIN_EXTRACTION_MISSING'
 assert S['OFFLINE_GEOMETRY_ANALYZER_REGEN_REQUIRED']
 assert S['NEXT_FIX'].startswith('D_')
 assert S['UPSTREAM_EVIDENCE_UNCHANGED']
 assert S['BLOCKERS']==[]
