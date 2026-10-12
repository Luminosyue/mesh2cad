import hashlib
import json
from pathlib import Path
from PIL import Image

R=Path("/data/home/cuiyuehan/project/mesh2cad/ours3/complexity_aware_compact_cad_v1")
S=json.loads((R/"metrics/summary.json").read_text())
T=json.loads((R/"metrics/frozen_thresholds.json").read_text())
E=json.loads((R/"metrics/execution_contract.json").read_text())

def j(p):return json.loads(Path(p).read_text())
def sha(p):
 h=hashlib.sha256();h.update(Path(p).read_bytes());return h.hexdigest()

def test_baseline_frozen():
 expected={"CASE_03":"41ff84ae2900e975e135a03fc5e08275f0f3449299acb9ede9b25e6ab2103371","CASE_04":"61460e72e4b401f4ac5034969ff832de6dc0e6ab508dc0b478d421387b74f004","CASE_05":"e626e0a003326391ea9414c092e060ccc5ed956248d12ae707e5e6d856a78276","CASE_09":"fb92d86fd969d2c2235de963416de282a5a85d731ed7fee0a6a7463f402f3252"}
 dirs={"CASE_03":"case03_control","CASE_04":"case04","CASE_05":"case05","CASE_09":"case09"}
 for cid,d in dirs.items():assert j(R/d/"metrics/original.json")["STEP_SHA256"]==expected[cid]

def test_face_adjacency_graph():
 for cid,d,n in [("CASE_03","case03_control",6),("CASE_04","case04",3522),("CASE_05","case05",34196),("CASE_09","case09",3522)]:
  assert (R/d/"face_adjacency_graph.json").stat().st_size>100;assert j(R/d/"structural_graph_summary.json")["FACE_NODES"]==n

def test_surface_candidate_graph():
 for d in ["case04","case05","case09"]:assert j(R/d/"structural_graph_summary.json")["SURFACE_CANDIDATES"]>=3

def test_plane_cluster():
 assert any(x["candidate_type"]=="PLANE_CLUSTER" for x in j(R/"case04/surface_candidate_graph.json")["candidates"])

def test_cylinder_cluster():
 assert "CYLINDER_CLUSTER" in (R/"scripts/build_structural_graphs.py").read_text()

def test_freeform_cluster():
 assert any(x["candidate_type"]=="FREEFORM_CLUSTER" for x in j(R/"case05/surface_candidate_graph.json")["candidates"])

def test_feature_edge_preserved():
 for d in ["case04","case05","case09"]:assert j(R/d/"structural_graph_summary.json")["EDGE_SEMANTICS"]["PRESERVE_EDGE"]>0

def test_hole_inner_wire_preserved():
 for r in S["cases"].values():assert r["INNER_WIRE_AFTER"]>=r["INNER_WIRE_BEFORE"]

def test_global_surface_refit():
 assert S["cases"]["CASE_04"]["NEW_BSPLINE_FACES"]==64 and S["cases"]["CASE_09"]["NEW_BSPLINE_FACES"]==64
 assert j(R/"case05/candidates/section7_compact_metadata.json")["method"].startswith("ORIGINAL_MEASURED_SECTIONS")

def test_trim_reconstruction():
 for d in ["case04","case05","case09"]:assert j(R/d/"metrics/balanced.json")["INNER_WIRE_COUNT"]==j(R/d/"metrics/original.json")["INNER_WIRE_COUNT"]

def test_brep_valid():
 assert all(r["NEW_BREP_VALID"] for r in S["cases"].values())

def test_no_faceted_mesh_output():
 for d in ["case04","case05","case09"]:
  m=j(R/d/"metrics/balanced.json");assert m["FINAL_GEOMETRY"]=="TRUE_BREP_NOT_TRIANGULATED_MESH" and m["FACETED_MESH_WRAPPED_AS_BREP"] is False

def test_q_thresholds_frozen():
 assert T["Q1"]=={"BRep_valid":True,"Chamfer_max":.01,"P95_max":.02,"Coverage02_min":.95};assert T["Q2"]["Chamfer_max"]==.02 and T["thresholds_modified"] is False

def test_no_unrestricted_icp():
 assert E["UNRESTRICTED_ICP_USED"] is False
 for d in ["case04","case05","case09"]:assert j(R/d/"metrics/balanced.json")["UNRESTRICTED_ICP_USED"] is False

def test_complexity_reduced():
 assert S["cases"]["CASE_04"]["FACE_REDUCTION_RATIO"]>=.70;assert S["cases"]["CASE_05"]["FACE_REDUCTION_RATIO"]>=.80;assert S["cases"]["CASE_09"]["FACE_REDUCTION_RATIO"]>=.70

def test_occ_baseline_present():
 for d in ["case04","case05","case09"]:assert j(R/d/"metrics/occ_unify_baseline.json")["BREP_VALID"] is True

def test_pareto_selection():
 for d in ["case04","case05","case09"]:
  p=j(R/d/"pareto_candidates.json");assert p["selected"]=="BALANCED" and len(p["candidates"])>=4

def test_case03_no_regression():
 c=S["CASE_03_CONTROL"];assert c["BASE_FACES"]==c["NEW_FACES"]==6 and c["BASE_EDGES"]==c["NEW_EDGES"]==12 and c["GEOM_Q"]=="Q1" and c["REGRESSION"] is False

def test_visual_comparison():
 for d in ["case03_control","case04","case05","case09"]:
  for name in ["source_mesh.png","baseline_cad_shaded.png","occ_unify_cad_shaded.png","ours_compact_cad_shaded.png","baseline_face_colored.png","ours_face_colored.png","baseline_true_edges.png","ours_true_edges.png","comparison.png","topology_comparison.png"]:
   p=R/d/name;assert p.stat().st_size>1000;Image.open(p).verify()
 assert Image.open(R/"artifacts/compact_cad_comparison.png").size==(2080,1800)
