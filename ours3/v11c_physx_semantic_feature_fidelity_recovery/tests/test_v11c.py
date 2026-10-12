import json
from pathlib import Path
import pytest

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/v11c_physx_semantic_feature_fidelity_recovery')
S=json.loads((ROOT/'artifacts/v11c_summary.json').read_text())

@pytest.mark.parametrize('key',[
 'PHYSX_SEMANTIC_FEATURE_PRIOR_IMPLEMENTED','GLOBAL_OBJECT_SEMANTIC_CONTEXT_USED','SEMANTIC_FEATURE_GRAPH_IMPLEMENTED',
 'PART_RELATION_GRAPH_IMPLEMENTED','PATTERN_RECOVERY_IMPLEMENTED','CAD_CONSTRUCTION_PRIOR_IMPLEMENTED',
 'FIDELITY_AWARE_RANKING_USED','FIDELITY_QA_IMPLEMENTED','BBOX_PROXY_DETECTOR_IMPLEMENTED',
 'PHYSX_SEMANTIC_PRIOR_DEPENDENCY_PASS','WRONG_PHYSX_ROLE_CANNOT_OVERRIDE_GEOMETRY','SEMANTIC_PRIOR_RESPECTS_V10_GATE',
 'GEOMETRY_ONLY_PATH_REMAINS_AVAILABLE','V10_REGRESSION_PASS','V11_REGRESSION_PASS','V11B_REGRESSION_PASS','V7D3_REGRESSION_PASS'])
def test_true_contract(key):assert S[key] is True

@pytest.mark.parametrize('key',['BUILDER_ELIGIBILITY_CHANGED_BY_SEMANTICS_COUNT','INVALID_BUILDER_EXECUTED_COUNT','EXECUTED_PARAMETER_WITHOUT_REF_COUNT','DIRECT_PLAN_TO_OCC_BYPASS_COUNT','GEOMETRY_EXPLOSION_COUNT','PART_ID_HARDCODE_COUNT','CASE_ID_HARDCODE_COUNT'])
def test_zero_safety(key):assert S[key]==0

def test_artifacts():
 for name in ['global_semantic_context.json','semantic_part_roles.csv','part_relation_graph.json','pattern_groups.json','symmetry_groups.json','semantic_construction_prior.csv','builder_ranking_before_after.csv','fidelity_qa.csv','cross_case_semantic_summary.csv','v11c_source_vs_cad_contact_sheet.png']:
  assert (ROOT/'artifacts'/name).is_file()
def test_part_contracts():
 parts=list((ROOT/'cases').glob('*/CADPART_*'));assert len(parts)==S['PARTS_ANALYZED']
 for p in parts:
  for rel in ['semantic/physx_raw.json','semantic/geometry_semantic_compatibility.json','semantic/accepted_role.json','semantic/construction_prior.json','candidates/candidate_ranking.json','candidates/fidelity_metrics.json']:assert (p/rel).is_file()
def test_strong_semantics():
 assert S['CASE09_MAIN_WING_ROLE_RECOVERED'];assert S['ROAD_WHEEL_PATTERN_RECOVERED'];assert S['TANK_HULL_ROLE_RECOVERED'];assert S['TANK_TURRET_ROLE_RECOVERED'];assert S['TANK_GUN_BARREL_ROLE_RECOVERED']
def test_real_planner():assert S['REAL_QWEN_CALLS']>=1 and S['REAL_QWEN_EXECUTABLE_PLAN_COUNT']>=1 and S['REAL_MAC_CALLS']>=1
def test_pass():assert S['V11C_PASS'] and S['CURRENT_GATE'].endswith('_PASS') and not S['BLOCKERS']
