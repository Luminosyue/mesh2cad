import hashlib, json
from pathlib import Path

R=Path("/data/home/cuiyuehan/project/mesh2cad/ours3/single_part_high_fidelity_recovery_v1")
C=R/"case/REAL_03_part_000"; A=R/"artifacts"; O=R/"round_1"
def j(p):return json.loads(Path(p).read_text())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def test_target_is_old_q2_case(): assert j(A/"frozen_case_audit.json")["OLD_Q"]=="Q2"
def test_source_mesh_sha_frozen():
 a=j(A/"frozen_case_audit.json"); assert h(C/"source_part.obj")==a["SOURCE_SHA256"]==a["FROZEN_SOURCE_SHA256"]
def test_no_whole_object(): assert j(C/"detailed_cad_spec_v1.json")["target_part_id"]=="part_000"
def test_no_p3_rerun(): assert not j(C/"detailed_cad_spec_v1.json")["provenance"]["P3_rerun"]
def test_no_physx_rerun(): assert not j(C/"detailed_cad_spec_v1.json")["provenance"]["PhysX_rerun"]
def test_revolution_axis(): assert j(A/"high_fidelity_geometry_analysis.json")["REVOLUTION_AXIS_CONFIDENCE"]>=.8
def test_axial_profile_generated(): assert sum(1 for _ in open(C/"axial_radius_profile.csv"))-1>=200
def test_feature_graph_schema(): assert j(C/"cad_feature_graph_v1.json")["schema_version"]=="cad_feature_graph_v1"
def test_high_conf_features_enter_spec(): assert len(j(C/"detailed_cad_spec_v1.json")["HARD_MEASURED_GEOMETRY"]["required_features"])==3
def test_low_conf_features_not_hard(): assert all(x["confidence"]>=.8 for x in j(C/"detailed_cad_spec_v1.json")["HARD_MEASURED_GEOMETRY"]["required_features"])
def test_no_simplest_solid_prompt():
 p=(C/"mac_high_fidelity_prompt_v1.txt").read_text(); assert "NOT to produce the simplest approximation" in p and "Construct the simplest" not in p
def test_feature_checklist(): assert "FEATURE_CHECKLIST" in (C/"mac_high_fidelity_prompt_v1.txt").read_text()
def test_alignment_fix_reused(): assert j(O/"metrics.json")["canonical_to_source_transform_reused"]
def test_no_icp(): assert not j(O/"metrics.json")["icp_used"]
def test_fresh_step_tessellation(): assert j(O/"metrics.json")["fresh_tessellation"] and (O/"fresh_step_tessellation.stl").exists()
def test_residual_clusters(): assert "clusters" in j(O/"residual_clusters.json")
def test_max_three_mac_runs(): assert sum(1 for p in R.glob("round_*/mac_run_result.json") if j(p).get("llm_calls",0)>0)<=3
def test_q_thresholds_unchanged():
 p=(R/"scripts/high_fidelity_pipeline.py").read_text(); assert '"chamfer": .01' in p and '"coverage02": .85' in p
def test_best_round_metric_selection(): assert j(O/"metrics.json")["quality_class"]=="Q1_STRONG_PAIR"
def test_best_step_brep_valid(): assert j(O/"metrics.json")["brep_valid"] and (O/"generated.step").exists()
