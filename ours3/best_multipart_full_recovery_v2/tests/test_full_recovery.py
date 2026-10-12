import csv, hashlib, json
from pathlib import Path
import pytest

R=Path(__file__).resolve().parents[1]; M=json.loads((R/'manifest/target_case_manifest.json').read_text()); S=json.loads((R/'metrics/summary.json').read_text()); P=json.loads((R/'metrics/part_results.json').read_text()); L=json.loads((R/'metrics/source_triangle_coverage_ledger.json').read_text())
def test_01_target_is_max_coverage_multipart_case(): assert M['TARGET_CASE']=='CASE_05' and M['OLD_CAD_AREA_COVERAGE']==pytest.approx(.5998369918162297)
def test_02_target_manifest_frozen(): assert M['FROZEN'] is True
def test_03_source_hash_frozen(): assert hashlib.sha256(Path(M['TARGET_SOURCE_OBJ']).read_bytes()).hexdigest()==M['SOURCE_SHA256']
def test_04_existing_q1_q2_reused(): assert M['REUSED_Q1_PARTS']==3 and M['REUSED_Q2_PARTS']==0
def test_05_reused_step_hashes(): assert len(M['REUSED_STEP_SHA256'])==3 and all(len(x)==64 for x in M['REUSED_STEP_SHA256'].values())
def test_06_source_triangle_ledger_unique(): assert len({x['source_triangle_id'] for x in L['triangles']})==L['TOTAL_SOURCE_TRIANGLES']==len(L['triangles'])
def test_07_coverage_states_exclusive(): assert L['EXCLUSIVE_PARTITION'] and all(x['state'] in {'RECOVERED_Q1','RECOVERED_Q2','RECOVERED_SURFACE_BREP','UNRECOVERED','EXCLUDED_INVALID_SOURCE'} for x in L['triangles'])
def test_08_no_reprocess_accepted_geometry(): assert {x['part_id'] for x in P if x.get('reused')}=={'CADPART_000','CADPART_004','CADPART_006'}
def test_09_remaining_geometry_complete(): assert (R/'parts/remaining_geometry.obj').stat().st_size>0
def test_10_merge_threshold_frozen(): assert M['MERGE_THRESHOLDS_V2']=={'AUTO_MERGE_MIN':.85,'REVIEW_MERGE_MIN':.65}
def test_11_physx_soft_only(): assert M['PHYSX_USED_FOR_PLACEMENT'] is False
def test_12_local_refinement_only(): assert S['LOCAL_P3_REFINEMENT_RUNS']==0
def test_13_area_priority():
 rows=list(csv.DictReader((R/'metrics/coverage_progress.csv').open())); assert [float(x['cumulative_cad_area_coverage']) for x in rows]==sorted(float(x['cumulative_cad_area_coverage']) for x in rows)
def test_14_backend_router(): assert all(x.get('backend') in {'MULTI_SECTION_LOFT','PRIMITIVE_CSG','FREEFORM_BSPLINE_BREP'} or x['quality']=='TRUE_FAILURE' for x in P)
def test_15_parametric_first(): assert all(x.get('trials',[{'candidate':{'backend':'PRIMITIVE_CSG'}}])[0]['candidate']['backend']=='PRIMITIVE_CSG' for x in P if 'trials' in x)
def test_16_loft_second(): assert all(len(x.get('trials',[]))<2 or x['trials'][1]['candidate']['backend']=='MULTI_SECTION_LOFT' for x in P)
def test_17_no_q3_silent_drop(): assert all(x['quality'] in {'Q1','Q2','S1','TRUE_FAILURE'} for x in P)
def test_18_surface_brep_fallback_recorded(): assert 'S1_THRESHOLDS' in M
def test_19_analytic_surface_priority(): assert all(x.get('backend')!='FREEFORM_BSPLINE_BREP' or len(x.get('trials',[]))>=2 for x in P)
def test_20_bspline_surface_fit_policy(): assert M['S1_THRESHOLDS']=={'chamfer_max':.03,'p95_max':.07,'coverage02_min':.80}
def test_21_mesh_guided_topology(): assert all('source_triangle_ids' in x for x in P)
def test_22_boundary_aware_fit(): assert all((R/'parts'/x['part_id']/'axial_sections_200.json').exists() or x.get('reused') or x.get('continued_from_old_q3') for x in P)
def test_23_no_unsafe_shapefix(): assert all(x.get('metrics',{}).get('brep_valid',True) for x in P if x['quality']!='TRUE_FAILURE')
def test_24_q1_thresholds(): assert M['Q_THRESHOLDS']['Q1']=={'chamfer_max':.01,'p95_max':.02,'coverage02_min':.95}
def test_25_q2_thresholds(): assert M['Q_THRESHOLDS']['Q2']=={'chamfer_max':.02,'p95_max':.05,'coverage02_min':.85}
def test_26_s1_separate(): assert S['PARTS_S1']==sum(x['quality']=='S1' for x in P)
def test_27_no_mesh_fake_cad(): assert all((R/'parts'/x['part_id']/'accepted/part.step').is_file() for x in P if x['quality']!='TRUE_FAILURE')
def test_28_coverage_partition(): assert S['TOTAL_CAD_AREA_COVERAGE']+S['FAILED_AREA_COVERAGE']==pytest.approx(1)
def test_29_coverage_monotonic():
 vals=[float(x['cumulative_cad_area_coverage']) for x in csv.DictReader((R/'metrics/coverage_progress.csv').open())];assert all(a<=b for a,b in zip(vals,vals[1:]))
def test_30_local_global_transform(): assert all(Path(x['transform']).is_file() for x in P if x['quality']!='TRUE_FAILURE')
def test_31_xcaf_independent_components(): assert S['ASSEMBLY_PART_COUNT']==sum(x['quality']!='TRUE_FAILURE' for x in P) and S['INDEPENDENT_PARTS_PRESERVED']
def test_32_assembly_reload(): assert S['ASSEMBLY_STEP_RELOAD_SUCCESS'] and Path(S['ASSEMBLY_STEP_PATH']).is_file()
def test_33_exact100_not_overclaimed(): assert S['EXACT_100_PERCENT_CAD_COVERAGE']==(L['FAILED_SOURCE_TRIANGLES']==0 and S['FAILED_AREA_COVERAGE']==0)
def test_34_no_mac_runs(): assert S['NEW_MAC_RUNS']==S['NEW_LLM_CAD_CALLS']==0
def test_35_no_gt(): assert S['STEP_GT_USED'] is S['ABC_DATA_USED'] is False
def test_36_viewer_and_visuals(): assert all(Path(S[k]).is_file() for k in ['FULL_CAD_GLB_PATH','MAIN_VISUAL_PATH','COVERAGE_MAP_PATH'])
def test_37_gate_not_overclaimed(): assert S['CURRENT_GATE']=='BEST_MULTIPART_FULL_RECOVERY_V2_FAIL' and S['FULL_CAD_ASSEMBLY_COMPLETE'] is False
