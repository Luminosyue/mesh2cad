import json,sys
from pathlib import Path
import pytest
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
OUT=ROOT/'v11b_real_qwen_mac_open_shell_closure'
sys.path[:0]=[str(OUT),str(ROOT/'v10_geometry_gated_builder_contract_closure')]
from design_plan.validator import validate_plan
from planning.mac_adapter import fixture_adapter
S=json.load(open(OUT/'artifacts/pretest_summary.json'));Q=json.load(open(OUT/'artifacts/qwen_real_audit.json'));M=json.load(open(OUT/'artifacts/mac_real_audit.json'))
def reload(path):
 r=STEPControl_Reader();assert r.ReadFile(str(path))==IFSelect_RetDone;r.TransferRoots();shape=r.OneShape();assert BRepCheck_Analyzer(shape).IsValid();return shape
def test_gate():assert S['CURRENT_GATE'].endswith('_PASS') and S['V11B_PASS']
def test_real_qwen():assert S['REAL_QWEN_CALLS']>=1 and Q['ok'] and Q['attempts'][0]['usage']['total_tokens']>0
def test_qwen_strict_validators():
 v=Q['validation'];assert v['PLAN_SCHEMA_VALID'] and v['PLAN_GEOMETRY_VALID'] and v['PLAN_REFERENCE_VALID'] and v['PLAN_EXECUTABLE']
def test_qwen_fresh():assert S['REAL_QWEN_EXECUTABLE_PLAN_COUNT']>=1 and S['REAL_QWEN_EXECUTION_SUCCESS_COUNT']>=1 and S['REAL_QWEN_FRESH_BREP_COUNT']>=1
def test_qwen_no_auto_ref():assert S['QWEN_AUTO_REFERENCE_CORRECTION_COUNT']==0
def test_qwen_refs_exact():
 allowed=set(Q['inventories']['ALL_ALLOWED_EXACT_REFS']);p=Q['plan'];refs=[]
 for b in ('geometry_refs','topology_refs','feature_refs'):
  for x in (p.get(b) or {}).values():refs.extend(x if isinstance(x,list) else [x])
 assert refs and all(x in allowed for x in refs)
def test_qwen_no_placeholder():
 text=json.dumps(Q['plan']);assert '*_ref' not in text and 'PROFILE_X' not in text and 'AXIS_X' not in text and 'placeholder' not in text.lower()
def test_placeholder_counterfactual_rejected():
 p=dict(Q['plan']);p['geometry_refs']=dict(p['geometry_refs']);p['geometry_refs']['profile_ref']='MEASURED_SPEC.PROFILES.PROFILE_X'
 v=validate_plan(p,Q['attempts'][0]['validation'] and {'ALLOWED_BUILDERS':['EXTRUSION'],'BUILDER_ELIGIBILITY':{'EXTRUSION':{'valid':True}}},None)
 assert not v['PLAN_EXECUTABLE']
def test_mac_truthful_403():assert S['REAL_MAC_CALLS']==1 and S['MAC_EXTERNAL_RESOURCE_FAILURE'] and M['status_code']==403
def test_mac_not_faked():assert S['REAL_MAC_EXECUTABLE_PLAN_COUNT']==0 and S['MAC_FRESH_BREP_COUNT']==0 and S['MAC_CANDIDATE_COUNT']==0
def test_mac_adapter():
 p={'plan_version':'V11'};assert fixture_adapter({'planner_output':p})==p and S['MAC_TO_V11_ADAPTER_TEST_PASS']
def test_mac_safety_counts():assert S['MAC_INVALID_BUILDER_EXECUTED_COUNT']==S['MAC_UNMEASURED_PARAMETER_CONSUMED_COUNT']==S['MAC_DIRECT_OCC_BYPASS_COUNT']==0
def test_open_shell_gate():assert S['OPEN_SHELL_EXECUTABLE_PLAN_COUNT']>=1 and S['OPEN_SHELL_FRESH_BREP_COUNT']>=1
def test_open_shell_topology():assert S['OPEN_SHELL_SHARED_OCC_EDGE_COUNT']>=1 and S['OPEN_SHELL_PCURVE_COUNT']>=2 and S['OPEN_SHELL_TRIMMED_FACE_COUNT']>=2
def test_open_shell_not_historical():assert not S['OPEN_SHELL_HISTORICAL_STEP_REUSED'] and not S['HISTORICAL_STEP_REUSED']
def test_open_shell_construction_modules():
 d=S['details']['open_shell'];assert d['V7D3_FINAL_STEP_READ'] is False and len(d['V7D3_CONSTRUCTION_MODULES_USED'])==3
def test_open_shell_provenance():
 rows=S['details']['open_shell']['consumed'];assert len(rows)==4
 assert not any(str(x['SOURCE_FILE']).endswith('v7d3_vertical_tail_local_refit.step') for x in rows)
def test_fresh_steps_reload():
 assert len(S['FRESH_STEPS'])>=3
 for p in S['FRESH_STEPS']:reload(p)
def test_candidate_sources():assert S['QWEN_CANDIDATE_COUNT']>=1 and S['GEOMETRY_ALTERNATIVE_CANDIDATE_COUNT']>=1
def test_unified_no_bypass():assert S['EXECUTED_PARAMETER_WITHOUT_REF_COUNT']==S['INVALID_BUILDER_EXECUTED_COUNT']==S['DIRECT_PLAN_TO_OCC_BYPASS_COUNT']==0
def test_no_fallback_or_explosion():assert not S['FALLBACK_USED'] and S['GEOMETRY_EXPLOSION_COUNT']==0
def test_regressions():assert S['V10_REGRESSION_PASS'] and S['V7D3_REGRESSION_PASS'] and S['V11_FROZEN_UNCHANGED']
def test_existing_representatives():assert S['CASE09_VALID_LOFT_PLAN_EXECUTABLE'] and S['CASE09_VALID_LOFT_FRESH_BREP'] and S['YC4XCA_CADPART002_FRESH_BREP']
def test_no_blockers():assert S['BLOCKERS']==[]
