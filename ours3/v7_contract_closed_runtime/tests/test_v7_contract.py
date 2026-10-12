import json,inspect
from pathlib import Path
import pytest
O=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/v7_contract_closed_runtime');S=json.loads((O/'artifacts/final_summary.json').read_text())
def test_runtime_loads_measured_spec():assert S['MEASURED_SPEC_LOADED_BY_RUNTIME']
def test_runtime_axis_from_spec():assert S['AXIS_SOURCE']=='MEASURED_SPEC'
def test_runtime_does_not_argmax_axis():assert 'argmax' not in (O/'scripts/v7_runtime.py').read_text()
def test_runtime_uses_spec_stations():assert S['STATION_SOURCE']=='MEASURED_SPEC'
def test_geometry_analyzer_profiles_closed():assert S['GEOMETRY_ANALYZER_CLOSED_PROFILE_RATE']>0
def test_no_case09_stable_override():assert 'stable' not in (O/'scripts/v7_runtime.py').read_text().lower()
def test_no_silent_parameter_clamp():assert S['SILENT_PARAMETER_CLAMP_COUNT']==0
def test_loft_uses_loft_builder():assert S['parts']['CADPART_001']['contract']['executed_builder']=='LoftBuilder'
def test_revolution_uses_revolve_builder():
 from builders.registry import get_builder
 assert get_builder('REVOLUTION').name=='RevolutionBuilder'
def test_extrusion_uses_extrusion_builder():assert S['parts']['CADPART_000']['contract']['executed_builder']=='ExtrusionBuilder'
def test_different_hypotheses_use_distinct_builders():assert S['MULTICANDIDATE_BUILDERS_DISTINCT']
def test_multicandidate_collapse_detection():assert not S['MULTICANDIDATE_COLLAPSE']
def test_raw_feature_recall_not_rewritten():assert S['RAW_FEATURE_BOUNDARY_RECALL']==S['FINAL_FEATURE_BOUNDARY_RECALL']==.32
def test_section_derived_edges_not_constant():assert S['SECTION_DERIVED_EDGE_METRIC_REAL'] and all('RAW_TOPOLOGY_METRICS' in x for x in S['parts'].values())
def test_historical_step_not_fresh_result():assert not S['HISTORICAL_STEP_REUSED'] and S['FRESH_STEP_GENERATED']
def test_spec_span_perturbation_changes_geometry():assert S['SPEC_SPAN_PERTURBATION_EFFECTIVE']
def test_spec_axis_perturbation_changes_execution():assert S['SPEC_AXIS_PERTURBATION_EFFECTIVE']
def test_spec_station_perturbation_changes_execution():assert S['SPEC_STATION_PERTURBATION_EFFECTIVE']
def test_profile_source():assert S['PROFILE_SOURCE']=='GEOMETRY_ANALYZER'
def test_no_runtime_remeasurement():assert not S['RUNTIME_AXIS_REMEASUREMENT'] and not S['RUNTIME_STATION_REGENERATION']
def test_hypothesis_builder_match():assert S['HYPOTHESIS_BUILDER_MATCH']
def test_bspline_builder_selected():assert S['parts']['CADPART_005']['contract']['executed_builder']=='BSplineSkinBuilder'
def test_invalid_profiles_not_bbox():
 for x in S['parts'].values():assert all(f['status']=='PROFILE_INVALID' for f in x['analysis']['PROFILE_FAILURES'])
def test_candidate_contract_exists():assert all(Path(x['step']).parent.joinpath('candidate_execution_contract.json').is_file() for x in S['parts'].values())
def test_geometry_trace_exists():assert all(Path(x['step']).parent.joinpath('geometry_trace.json').is_file() for x in S['parts'].values())
def test_semantic_modes_truthful():assert S['SEMANTIC_SURFACE_MODE']==S['FEATURE_GRAPH_MODE']=='HYPOTHESIS_ONLY'
def test_feature_not_verified():assert S['SEMANTIC_FEATURE_Q']=='NOT_VERIFIED'
def test_physx_soft_prior_only():assert not S['PHYSX_GEOMETRIC_EFFECT']
def test_transform_restore_truthful():assert not S['TRANSFORM_RESTORE_EFFECTIVE']
def test_assembly_state_truthful():assert S['TOTAL_PARTS']==8 and S['VALID_PARTS']==3 and S['FAILED_PARTS']==5 and not S['ASSEMBLY_ELIGIBLE'] and S['ASSEMBLY_WRITTEN']
def test_batch9_not_fullstack_valid():assert S['BATCH9']['MAC_FULLSTACK_EVALUATION_INVALID']
def test_revolution_not_applicable_fails():
 from builders.registry import get_builder
 with pytest.raises(RuntimeError,match='REVOLUTION_NOT_APPLICABLE'):get_builder('REVOLUTION').build({},[],{'revolution_applicable':False})
def test_illegal_profile_count_fails():
 from contracts.evidence_authority import validate_requested_parameters
 with pytest.raises(ValueError,match='CONTRACT_VIOLATION'):validate_requested_parameters({'profile_count':999,'hypothesis':'LOFT'},{'profiles':[1,2]})
def test_requested_executed_equal():assert all(x['contract']['requested_profile_count']==x['contract']['executed_profile_count'] for x in S['parts'].values())
def test_gate_pass():assert S['CURRENT_GATE']=='V7_CONTRACT_CLOSED_RUNTIME_PASS' and S['CASE09_CONTRACT_PASS']
